#!/usr/bin/env python3
"""
Cricket Playbook - Shared Logging Configuration
================================================
Provides consistent logging setup across all Python scripts.

Usage:
    from utils.logging_config import setup_logger

    logger = setup_logger(__name__)

    logger.info("Starting stat pack generation for %s", team)
    logger.debug("Query returned %d rows", len(results))
    logger.warning("Missing data for player: %s", player_name)
    logger.error("Failed to generate stat pack: %s", str(e))

Author: Brad Stevens (Ops Lead)
Version: 1.0.0
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
LOGS_DIR = PROJECT_DIR / "outputs" / "logs"


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_file_name: Optional[str] = None,
) -> logging.Logger:
    """
    Configure and return a logger with consistent formatting.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Logging level (default: INFO)
        log_to_file: Whether to also log to a file (default: False)
        log_file_name: Custom log file name (default: auto-generated from date)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Starting process")
        2026-02-05 10:30:45 | INFO | module_name | Starting process
    """
    # Get or create logger
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler with colored output hints
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Format: timestamp | level | module | message
    console_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_to_file:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        if log_file_name is None:
            # Auto-generate filename with date
            date_str = datetime.now().strftime("%Y%m%d")
            log_file_name = f"cricket_playbook_{date_str}.log"

        log_path = LOGS_DIR / log_file_name

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)  # File gets all messages

        # More detailed format for file
        file_format = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger (avoid duplicate messages)
    logger.propagate = False

    return logger


def get_script_logger(script_path: str, log_to_file: bool = False) -> logging.Logger:
    """
    Convenience function to create a logger from a script's __file__ path.

    Args:
        script_path: The __file__ of the calling script
        log_to_file: Whether to enable file logging

    Returns:
        Configured logger with script name as identifier

    Example:
        >>> logger = get_script_logger(__file__)
        >>> logger.info("Script started")
    """
    script_name = Path(script_path).stem
    return setup_logger(script_name, log_to_file=log_to_file)


class LoggingContext:
    """
    Context manager for temporary logging level changes.

    Example:
        >>> with LoggingContext(logger, logging.DEBUG):
        ...     logger.debug("This will be logged")
        >>> logger.debug("This won't be logged if level was INFO")
    """

    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.new_level = level
        self.old_level = logger.level

    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)
        return False


# Pre-configured log levels for common scenarios
LOG_LEVELS = {
    "quiet": logging.WARNING,
    "normal": logging.INFO,
    "verbose": logging.DEBUG,
}


def set_log_level_from_env(logger: logging.Logger, env_var: str = "LOG_LEVEL") -> None:
    """
    Set logger level from environment variable.

    Args:
        logger: Logger instance to configure
        env_var: Name of environment variable (default: LOG_LEVEL)

    Environment variable values:
        - quiet: Only warnings and errors
        - normal: Info and above (default)
        - verbose: Debug and above
        - DEBUG, INFO, WARNING, ERROR: Standard levels
    """
    import os

    level_str = os.environ.get(env_var, "normal").lower()

    if level_str in LOG_LEVELS:
        logger.setLevel(LOG_LEVELS[level_str])
    elif hasattr(logging, level_str.upper()):
        logger.setLevel(getattr(logging, level_str.upper()))
