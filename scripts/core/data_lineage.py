#!/usr/bin/env python3
"""
Cricket Playbook - Data Lineage Tracking (TKT-140)
===================================================
Provides comprehensive data lineage tracking for the Cricket Playbook data pipeline.

This module enables tracking of:
- Source file origins for all ingested data
- Transformation chains for derived metrics
- Record-level traceability back to source files

Usage:
    # As a module
    from scripts.core.data_lineage import LineageTracker

    tracker = LineageTracker()
    tracker.record_ingest("data/raw/ipl_2024.json", "fact_ball", 15000)
    sources = tracker.get_lineage("fact_ball")

    # CLI usage
    python -m scripts.core.data_lineage --trace fact_ball 12345
    python -m scripts.core.data_lineage --sources dim_player
    python -m scripts.core.data_lineage --transform-chain strike_rate

Ticket: TKT-140
Author: Cricket Playbook Team
Version: 1.0.0
"""

import argparse
import functools
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import duckdb

from scripts.utils.logging_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"
LINEAGE_VERSION = "1.0.0"

# Type variable for decorator
F = TypeVar("F", bound=Callable[..., Any])


# =============================================================================
# Lineage Metadata Schema
# =============================================================================


@dataclass
class LineageMetadata:
    """
    Schema for lineage metadata tracking.

    Attributes:
        source_file: Original JSON file path (relative to project root)
        ingested_at: Timestamp of ingestion (ISO 8601 format)
        ingested_by: Script name and version that performed ingestion
        record_count: Number of records from this source
        checksum: SHA-256 hash of source file for change detection
        table_name: Target table where data was loaded
        lineage_id: Unique identifier for this lineage record
    """

    source_file: str
    ingested_at: str
    ingested_by: str
    record_count: int
    checksum: str
    table_name: str
    lineage_id: str = field(default="")

    def __post_init__(self) -> None:
        """Generate lineage_id if not provided."""
        if not self.lineage_id:
            # Create deterministic ID from source + table + timestamp
            id_input = f"{self.source_file}:{self.table_name}:{self.ingested_at}"
            self.lineage_id = hashlib.sha256(id_input.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)


@dataclass
class TransformMetadata:
    """
    Schema for transformation lineage tracking.

    Attributes:
        transform_id: Unique identifier for this transformation
        metric_name: Name of the derived metric
        source_tables: List of tables used as input
        source_columns: List of columns used in computation
        transform_logic: Description or SQL of the transformation
        created_at: Timestamp when transform was registered
        created_by: Script or function that created the transform
    """

    metric_name: str
    source_tables: List[str]
    source_columns: List[str]
    transform_logic: str
    created_at: str
    created_by: str
    transform_id: str = field(default="")

    def __post_init__(self) -> None:
        """Generate transform_id if not provided."""
        if not self.transform_id:
            id_input = f"{self.metric_name}:{self.created_at}"
            self.transform_id = hashlib.sha256(id_input.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Convert lists to JSON strings for SQL storage
        data["source_tables"] = json.dumps(data["source_tables"])
        data["source_columns"] = json.dumps(data["source_columns"])
        return data


# =============================================================================
# LineageTracker Class
# =============================================================================


class LineageTracker:
    """
    Main class for tracking data lineage in the Cricket Playbook pipeline.

    This class provides methods to:
    - Record ingestion events linking source files to target tables
    - Query lineage information for tables and records
    - Trace records back to their source files
    - Track transformation chains for derived metrics

    Example:
        >>> tracker = LineageTracker()
        >>> tracker.initialize_tables()
        >>> tracker.record_ingest("data/raw/ipl.json", "fact_ball", 50000)
        >>> sources = tracker.get_lineage("fact_ball")
        >>> print(f"fact_ball has {len(sources)} source files")
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the LineageTracker.

        Args:
            db_path: Path to the DuckDB database. Defaults to project database.
        """
        self.db_path = db_path or DB_PATH
        self._conn: Optional[duckdb.DuckDBPyConnection] = None

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
        return self._conn

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "LineageTracker":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def initialize_tables(self) -> None:
        """
        Create the data_lineage and transform_lineage tables in DuckDB.

        This method is idempotent - safe to call multiple times.
        """
        # Create data_lineage table for tracking source file ingestions
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS data_lineage (
                lineage_id VARCHAR PRIMARY KEY,
                source_file VARCHAR NOT NULL,
                table_name VARCHAR NOT NULL,
                ingested_at TIMESTAMP NOT NULL,
                ingested_by VARCHAR NOT NULL,
                record_count INTEGER NOT NULL,
                checksum VARCHAR NOT NULL
            )
        """)

        # Create transform_lineage table for tracking derived metrics
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transform_lineage (
                transform_id VARCHAR PRIMARY KEY,
                metric_name VARCHAR NOT NULL,
                source_tables VARCHAR NOT NULL,
                source_columns VARCHAR NOT NULL,
                transform_logic VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL,
                created_by VARCHAR NOT NULL
            )
        """)

        # Create indexes for efficient querying
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_lineage_table
            ON data_lineage(table_name)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_lineage_source
            ON data_lineage(source_file)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_transform_metric
            ON transform_lineage(metric_name)
        """)

        logger.info("Lineage tables initialized successfully")

    def compute_file_checksum(self, file_path: Union[str, Path]) -> str:
        """
        Compute SHA-256 checksum of a file.

        Args:
            file_path: Path to the file (absolute or relative to project root)

        Returns:
            SHA-256 hex digest of file contents

        Raises:
            FileNotFoundError: If the file does not exist
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

    def record_ingest(
        self,
        source_file: str,
        table_name: str,
        record_count: int,
        ingested_by: Optional[str] = None,
        checksum: Optional[str] = None,
    ) -> LineageMetadata:
        """
        Record an ingestion event linking a source file to a target table.

        Args:
            source_file: Path to the source file (relative to project root)
            table_name: Name of the target table
            record_count: Number of records ingested from this source
            ingested_by: Script name and version (auto-detected if not provided)
            checksum: File checksum (computed if not provided)

        Returns:
            LineageMetadata object with the recorded information

        Example:
            >>> tracker.record_ingest("data/raw/ipl_matches.json", "dim_match", 150)
        """
        # Auto-detect ingested_by if not provided
        if ingested_by is None:
            ingested_by = f"data_lineage.py v{LINEAGE_VERSION}"

        # Compute checksum if not provided
        if checksum is None:
            try:
                checksum = self.compute_file_checksum(source_file)
            except FileNotFoundError:
                # Use placeholder for archived/zip sources
                checksum = hashlib.sha256(source_file.encode()).hexdigest()
                logger.warning("Could not compute checksum for %s, using path hash", source_file)

        # Create metadata object
        metadata = LineageMetadata(
            source_file=source_file,
            ingested_at=datetime.now().isoformat(),
            ingested_by=ingested_by,
            record_count=record_count,
            checksum=checksum,
            table_name=table_name,
        )

        # Insert into database
        self.conn.execute(
            """
            INSERT INTO data_lineage
            (lineage_id, source_file, table_name, ingested_at, ingested_by, record_count, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (lineage_id) DO UPDATE SET
                ingested_at = EXCLUDED.ingested_at,
                record_count = EXCLUDED.record_count,
                checksum = EXCLUDED.checksum
            """,
            [
                metadata.lineage_id,
                metadata.source_file,
                metadata.table_name,
                metadata.ingested_at,
                metadata.ingested_by,
                metadata.record_count,
                metadata.checksum,
            ],
        )

        logger.info(
            "Recorded lineage: %s -> %s (%d records)",
            source_file,
            table_name,
            record_count,
        )

        return metadata

    def get_lineage(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get all sources that contributed to a table.

        Args:
            table_name: Name of the table to query lineage for

        Returns:
            List of lineage records as dictionaries

        Example:
            >>> sources = tracker.get_lineage("fact_ball")
            >>> for src in sources:
            ...     print(f"{src['source_file']}: {src['record_count']} records")
        """
        result = self.conn.execute(
            """
            SELECT
                lineage_id,
                source_file,
                table_name,
                ingested_at,
                ingested_by,
                record_count,
                checksum
            FROM data_lineage
            WHERE table_name = ?
            ORDER BY ingested_at DESC
            """,
            [table_name],
        ).fetchall()

        columns = [
            "lineage_id",
            "source_file",
            "table_name",
            "ingested_at",
            "ingested_by",
            "record_count",
            "checksum",
        ]

        return [dict(zip(columns, row)) for row in result]

    def trace_record(self, table_name: str, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Trace a specific record back to its source file.

        This method queries the target table for the record's source_file column
        and then looks up the corresponding lineage metadata.

        Args:
            table_name: Name of the table containing the record
            record_id: Primary key value of the record

        Returns:
            Dictionary with source file and lineage information, or None if not found

        Example:
            >>> trace = tracker.trace_record("fact_ball", "1234567_1_5_3")
            >>> if trace:
            ...     print(f"Record came from: {trace['source_file']}")
        """
        # Determine the primary key column name based on table naming conventions
        pk_column = self._get_primary_key_column(table_name)

        try:
            # Query for the source_file of the specific record
            result = self.conn.execute(
                f"""
                SELECT source_file
                FROM {table_name}
                WHERE {pk_column} = ?
                """,
                [record_id],
            ).fetchone()

            if result is None:
                logger.warning("Record %s not found in table %s", record_id, table_name)
                return None

            source_file = result[0]

            # Look up lineage metadata for this source file
            lineage = self.conn.execute(
                """
                SELECT
                    lineage_id,
                    source_file,
                    table_name,
                    ingested_at,
                    ingested_by,
                    record_count,
                    checksum
                FROM data_lineage
                WHERE source_file = ? AND table_name = ?
                ORDER BY ingested_at DESC
                LIMIT 1
                """,
                [source_file, table_name],
            ).fetchone()

            if lineage:
                columns = [
                    "lineage_id",
                    "source_file",
                    "table_name",
                    "ingested_at",
                    "ingested_by",
                    "record_count",
                    "checksum",
                ]
                trace_result = dict(zip(columns, lineage))
                trace_result["record_id"] = record_id
                trace_result["pk_column"] = pk_column
                return trace_result
            else:
                # Return basic trace info if lineage record not found
                return {
                    "record_id": record_id,
                    "pk_column": pk_column,
                    "source_file": source_file,
                    "lineage_id": None,
                    "note": "Source file found in record but no lineage entry exists",
                }

        except duckdb.CatalogException:
            logger.error("Table %s does not exist", table_name)
            return None
        except duckdb.BinderException as e:
            logger.error("Column %s not found in table %s: %s", pk_column, table_name, e)
            return None

    def _get_primary_key_column(self, table_name: str) -> str:
        """
        Determine the primary key column name for a table.

        Uses naming conventions:
        - dim_* tables: <entity>_id (e.g., dim_player -> player_id)
        - fact_* tables: <fact>_id (e.g., fact_ball -> ball_id)
        - Other tables: id or first column

        Args:
            table_name: Name of the table

        Returns:
            Primary key column name
        """
        if table_name.startswith("dim_"):
            entity = table_name.replace("dim_", "")
            return f"{entity}_id"
        elif table_name.startswith("fact_"):
            fact = table_name.replace("fact_", "")
            return f"{fact}_id"
        else:
            return "id"

    def register_transform(
        self,
        metric_name: str,
        source_tables: List[str],
        source_columns: List[str],
        transform_logic: str,
        created_by: Optional[str] = None,
    ) -> TransformMetadata:
        """
        Register a transformation that creates a derived metric.

        Args:
            metric_name: Name of the derived metric
            source_tables: List of tables used as input
            source_columns: List of columns used in computation
            transform_logic: Description or SQL of the transformation
            created_by: Script or function that created the transform

        Returns:
            TransformMetadata object with the recorded information

        Example:
            >>> tracker.register_transform(
            ...     metric_name="strike_rate",
            ...     source_tables=["fact_ball"],
            ...     source_columns=["batter_runs", "is_legal_ball"],
            ...     transform_logic="SUM(batter_runs) * 100.0 / SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END)",
            ...     created_by="analytics_ipl.py"
            ... )
        """
        if created_by is None:
            created_by = f"data_lineage.py v{LINEAGE_VERSION}"

        metadata = TransformMetadata(
            metric_name=metric_name,
            source_tables=source_tables,
            source_columns=source_columns,
            transform_logic=transform_logic,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
        )

        data = metadata.to_dict()

        self.conn.execute(
            """
            INSERT INTO transform_lineage
            (transform_id, metric_name, source_tables, source_columns, transform_logic, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (transform_id) DO UPDATE SET
                source_tables = EXCLUDED.source_tables,
                source_columns = EXCLUDED.source_columns,
                transform_logic = EXCLUDED.transform_logic,
                created_at = EXCLUDED.created_at
            """,
            [
                data["transform_id"],
                data["metric_name"],
                data["source_tables"],
                data["source_columns"],
                data["transform_logic"],
                data["created_at"],
                data["created_by"],
            ],
        )

        logger.info("Registered transform: %s", metric_name)

        return metadata

    def get_transform_chain(self, metric_name: str) -> List[Dict[str, Any]]:
        """
        Show how a derived metric was computed.

        Retrieves the transformation chain including source tables, columns,
        and the transformation logic used to compute the metric.

        Args:
            metric_name: Name of the derived metric

        Returns:
            List of transformation records as dictionaries

        Example:
            >>> chain = tracker.get_transform_chain("strike_rate")
            >>> for t in chain:
            ...     print(f"Metric: {t['metric_name']}")
            ...     print(f"Logic: {t['transform_logic']}")
        """
        result = self.conn.execute(
            """
            SELECT
                transform_id,
                metric_name,
                source_tables,
                source_columns,
                transform_logic,
                created_at,
                created_by
            FROM transform_lineage
            WHERE metric_name = ?
            ORDER BY created_at DESC
            """,
            [metric_name],
        ).fetchall()

        columns = [
            "transform_id",
            "metric_name",
            "source_tables",
            "source_columns",
            "transform_logic",
            "created_at",
            "created_by",
        ]

        transforms = []
        for row in result:
            t = dict(zip(columns, row))
            # Parse JSON strings back to lists
            t["source_tables"] = json.loads(t["source_tables"])
            t["source_columns"] = json.loads(t["source_columns"])
            transforms.append(t)

        return transforms

    def get_all_lineage_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all lineage information.

        Returns:
            Dictionary containing counts and summaries of lineage data
        """
        # Count records by table
        table_counts = self.conn.execute(
            """
            SELECT
                table_name,
                COUNT(*) as source_count,
                SUM(record_count) as total_records
            FROM data_lineage
            GROUP BY table_name
            ORDER BY table_name
            """
        ).fetchall()

        # Count transforms
        transform_count = self.conn.execute("SELECT COUNT(*) FROM transform_lineage").fetchone()[0]

        return {
            "tables": [
                {
                    "table_name": row[0],
                    "source_count": row[1],
                    "total_records": row[2],
                }
                for row in table_counts
            ],
            "transform_count": transform_count,
        }


# =============================================================================
# Integration Helper
# =============================================================================


def with_lineage_tracking(
    tracker: Optional[LineageTracker] = None,
    table_name: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Decorator for tracking transforms applied to data.

    This decorator wraps functions that compute derived metrics, automatically
    recording the transformation in the lineage system.

    Args:
        tracker: LineageTracker instance (creates new one if not provided)
        table_name: Target table name for the transform

    Returns:
        Decorated function

    Example:
        >>> @with_lineage_tracking(table_name="agg_player_stats")
        ... def calculate_strike_rate(balls_df):
        ...     return balls_df.groupby('batter_id').apply(
        ...         lambda x: x['batter_runs'].sum() * 100 / x['is_legal_ball'].sum()
        ...     )
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal tracker
            if tracker is None:
                tracker = LineageTracker()

            # Execute the function
            result = func(*args, **kwargs)

            # Record the transform
            try:
                tracker.register_transform(
                    metric_name=func.__name__,
                    source_tables=[table_name] if table_name else [],
                    source_columns=[],  # Would need introspection to populate
                    transform_logic=func.__doc__ or f"Function: {func.__name__}",
                    created_by=f"{func.__module__}.{func.__name__}",
                )
            except Exception as e:
                logger.warning("Failed to record transform lineage: %s", e)

            return result

        return wrapper  # type: ignore

    return decorator


def wrap_ingest_with_lineage(
    ingest_func: Callable[..., int],
    tracker: Optional[LineageTracker] = None,
) -> Callable[..., int]:
    """
    Wrap an existing ingest function to add lineage tracking.

    This function wraps ingest operations to automatically record
    lineage metadata when data is loaded.

    Args:
        ingest_func: The original ingest function to wrap
        tracker: LineageTracker instance (creates new one if not provided)

    Returns:
        Wrapped function that records lineage

    Example:
        >>> def load_matches(file_path: str, table_name: str) -> int:
        ...     # Load data and return record count
        ...     return 100
        ...
        >>> tracked_load = wrap_ingest_with_lineage(load_matches)
        >>> tracked_load("data/raw/matches.json", "dim_match")
    """

    @functools.wraps(ingest_func)
    def wrapper(source_file: str, table_name: str, *args: Any, **kwargs: Any) -> int:
        nonlocal tracker
        if tracker is None:
            tracker = LineageTracker()

        # Call the original function
        record_count = ingest_func(source_file, table_name, *args, **kwargs)

        # Record lineage
        try:
            tracker.record_ingest(
                source_file=source_file,
                table_name=table_name,
                record_count=record_count,
                ingested_by=f"{ingest_func.__module__}.{ingest_func.__name__}",
            )
        except Exception as e:
            logger.warning("Failed to record ingest lineage: %s", e)

        return record_count

    return wrapper


class IngestLineageContext:
    """
    Context manager for batch lineage recording during ingestion.

    This provides a convenient way to track multiple ingestion operations
    as a single batch, which is useful for the main ingest.py script.

    Example:
        >>> with IngestLineageContext() as ctx:
        ...     for zip_file in zip_files:
        ...         process_zip(zip_file)
        ...         ctx.record("data/raw/file.json", "fact_ball", 5000)
    """

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the context with optional custom database path."""
        self.tracker = LineageTracker(db_path)
        self.records: List[LineageMetadata] = []

    def __enter__(self) -> "IngestLineageContext":
        """Enter context and ensure tables exist."""
        self.tracker.initialize_tables()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and close connection."""
        self.tracker.close()

    def record(
        self,
        source_file: str,
        table_name: str,
        record_count: int,
        ingested_by: Optional[str] = None,
        checksum: Optional[str] = None,
    ) -> LineageMetadata:
        """Record an ingestion event."""
        metadata = self.tracker.record_ingest(
            source_file=source_file,
            table_name=table_name,
            record_count=record_count,
            ingested_by=ingested_by,
            checksum=checksum,
        )
        self.records.append(metadata)
        return metadata


# =============================================================================
# CLI Interface
# =============================================================================


def format_lineage_output(records: List[Dict[str, Any]], format_type: str = "text") -> str:
    """
    Format lineage records for display.

    Args:
        records: List of lineage records
        format_type: Output format ("text" or "json")

    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(records, indent=2, default=str)

    if not records:
        return "No lineage records found."

    lines = []
    for i, record in enumerate(records, 1):
        lines.append(f"\n{'=' * 60}")
        lines.append(f"Lineage Record #{i}")
        lines.append(f"{'=' * 60}")
        for key, value in record.items():
            lines.append(f"  {key}: {value}")

    return "\n".join(lines)


def format_transform_output(transforms: List[Dict[str, Any]], format_type: str = "text") -> str:
    """
    Format transform records for display.

    Args:
        transforms: List of transform records
        format_type: Output format ("text" or "json")

    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(transforms, indent=2, default=str)

    if not transforms:
        return "No transform records found."

    lines = []
    for i, t in enumerate(transforms, 1):
        lines.append(f"\n{'=' * 60}")
        lines.append(f"Transform #{i}: {t['metric_name']}")
        lines.append(f"{'=' * 60}")
        lines.append(f"  Transform ID: {t['transform_id']}")
        lines.append(f"  Source Tables: {', '.join(t['source_tables'])}")
        lines.append(f"  Source Columns: {', '.join(t['source_columns'])}")
        lines.append("  Transform Logic:")
        lines.append(f"    {t['transform_logic']}")
        lines.append(f"  Created At: {t['created_at']}")
        lines.append(f"  Created By: {t['created_by']}")

    return "\n".join(lines)


def main() -> int:
    """
    CLI entry point for data lineage queries.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Data Lineage Tracking for Cricket Playbook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get all sources for a table
  python -m scripts.core.data_lineage --sources dim_player

  # Trace a specific record
  python -m scripts.core.data_lineage --trace fact_ball 1234567_1_5_3

  # Get transform chain for a metric
  python -m scripts.core.data_lineage --transform-chain strike_rate

  # Get lineage summary
  python -m scripts.core.data_lineage --summary

  # Initialize lineage tables
  python -m scripts.core.data_lineage --init
        """,
    )

    # Action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--sources",
        metavar="TABLE",
        help="Get all sources that contributed to a table",
    )
    action_group.add_argument(
        "--trace",
        nargs=2,
        metavar=("TABLE", "RECORD_ID"),
        help="Trace a specific record back to source",
    )
    action_group.add_argument(
        "--transform-chain",
        metavar="METRIC",
        help="Show how a derived metric was computed",
    )
    action_group.add_argument(
        "--summary",
        action="store_true",
        help="Get summary of all lineage information",
    )
    action_group.add_argument(
        "--init",
        action="store_true",
        help="Initialize lineage tables in the database",
    )

    # Optional arguments
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--db",
        metavar="PATH",
        help="Path to DuckDB database (default: data/cricket_playbook.duckdb)",
    )

    args = parser.parse_args()

    # Set up database path
    db_path = Path(args.db) if args.db else DB_PATH

    if not db_path.exists() and not args.init:
        print(f"Error: Database not found at {db_path}")
        print("Run ingestion first or specify database with --db")
        return 1

    try:
        with LineageTracker(db_path) as tracker:
            if args.init:
                tracker.initialize_tables()
                print("Lineage tables initialized successfully.")
                return 0

            elif args.sources:
                records = tracker.get_lineage(args.sources)
                print(format_lineage_output(records, args.format))

            elif args.trace:
                table_name, record_id = args.trace
                result = tracker.trace_record(table_name, record_id)
                if result:
                    print(format_lineage_output([result], args.format))
                else:
                    print(f"Record {record_id} not found in {table_name}")
                    return 1

            elif args.transform_chain:
                transforms = tracker.get_transform_chain(args.transform_chain)
                print(format_transform_output(transforms, args.format))

            elif args.summary:
                summary = tracker.get_all_lineage_summary()
                if args.format == "json":
                    print(json.dumps(summary, indent=2))
                else:
                    print("\n" + "=" * 60)
                    print("DATA LINEAGE SUMMARY")
                    print("=" * 60)
                    print("\nTable Lineage:")
                    for table in summary["tables"]:
                        print(
                            f"  {table['table_name']}: "
                            f"{table['source_count']} sources, "
                            f"{table['total_records']:,} records"
                        )
                    print(f"\nTransform Definitions: {summary['transform_count']}")

        return 0

    except duckdb.CatalogException as e:
        print("Error: Lineage tables not found. Run with --init first.")
        logger.error("Catalog error: %s", e)
        return 1
    except Exception as e:
        print(f"Error: {e}")
        logger.error("Unexpected error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
