#!/usr/bin/env python3
r"""
Pre-commit hook to validate document naming conventions.

Naming Convention: documentname_MMDDYY_v*
Pattern: ^[a-z0-9_]+_\d{6}_v\d+\.(md|pdf)$

Examples that PASS:
  - sprint_4_checkin_response_020426_v1.md
  - founder_review_013026_v1.pdf

Examples that FAIL:
  - review_1.pdf (no date/version)
  - SPRINT_4_STATUS.md (uppercase, no date)

Monitored directories:
  - reviews/founder/
  - reviews/sprint/
  - docs/sprints/

Exempt files:
  - README.md
  - Files in root directories
  - Config files
"""

import re
import sys
from pathlib import Path

# Naming convention pattern: lowercase_with_underscores_MMDDYY_vN.ext
NAMING_PATTERN = re.compile(r"^[a-z0-9_]+_\d{6}_v\d+\.(md|pdf)$")

# Directories to monitor for naming conventions
MONITORED_DIRS = [
    "reviews/founder",
    "reviews/sprint",
    "docs/sprints",
]

# Files exempt from naming convention
EXEMPT_FILES = [
    "README.md",
    ".gitkeep",
]

# File extensions to check
VALID_EXTENSIONS = [".md", ".pdf"]


def is_monitored_file(filepath: str) -> bool:
    """Check if file is in a monitored directory."""
    path = Path(filepath)

    # Check if file has a valid extension
    if path.suffix.lower() not in VALID_EXTENSIONS:
        return False

    # Check if file is in a monitored directory
    for monitored_dir in MONITORED_DIRS:
        if monitored_dir in str(path):
            return True

    return False


def is_exempt(filepath: str) -> bool:
    """Check if file is exempt from naming convention."""
    path = Path(filepath)
    filename = path.name

    # Check if filename is in exempt list
    if filename in EXEMPT_FILES:
        return True

    # Config files are exempt
    if filename.startswith("."):
        return True

    return False


def validate_filename(filepath: str) -> tuple[bool, str]:
    """
    Validate filename against naming convention.

    Returns:
        tuple: (is_valid, error_message)
    """
    path = Path(filepath)
    filename = path.name

    if NAMING_PATTERN.match(filename):
        return True, ""

    # Provide helpful error message
    issues = []

    # Check for uppercase
    if any(c.isupper() for c in filename.rsplit(".", 1)[0]):
        issues.append("contains uppercase letters (should be lowercase)")

    # Check for date pattern (6 digits)
    if not re.search(r"_\d{6}_", filename):
        issues.append("missing date in MMDDYY format")

    # Check for version pattern
    if not re.search(r"_v\d+\.", filename):
        issues.append("missing version (e.g., _v1)")

    # Check extension
    if path.suffix.lower() not in VALID_EXTENSIONS:
        issues.append("invalid extension (use .md or .pdf)")

    error_msg = f"Invalid filename: {filename}"
    if issues:
        error_msg += f" - {', '.join(issues)}"
    error_msg += "\n  Expected format: documentname_MMDDYY_v*.md/pdf"
    error_msg += "\n  Example: sprint_4_checkin_response_020426_v1.md"

    return False, error_msg


def main() -> int:
    """
    Main function to check naming conventions.

    Returns:
        int: Exit code (0 for success/warnings only, non-zero for errors)
    """
    # Get files from command line arguments (passed by pre-commit)
    files = sys.argv[1:] if len(sys.argv) > 1 else []

    if not files:
        return 0

    warnings = []
    checked_count = 0

    for filepath in files:
        # Skip if not a monitored file
        if not is_monitored_file(filepath):
            continue

        # Skip exempt files
        if is_exempt(filepath):
            continue

        checked_count += 1
        is_valid, error_msg = validate_filename(filepath)

        if not is_valid:
            warnings.append(f"  WARNING: {error_msg}")

    # Print summary
    if warnings:
        print("=" * 60)
        print("NAMING CONVENTION CHECK (Warning Only)")
        print("=" * 60)
        print(f"Checked {checked_count} file(s) in monitored directories\n")
        for warning in warnings:
            print(warning)
        print()
        print("Naming convention: documentname_MMDDYY_v*.md/pdf")
        print("This is a WARNING - commit will proceed.")
        print("=" * 60)

    # Always return 0 (warning only, non-blocking)
    return 0


if __name__ == "__main__":
    sys.exit(main())
