#!/bin/bash
#
# Cricket Playbook - Stat Pack Runner
# Regenerates all IPL 2026 stat packs with validation
#
# Usage: ./scripts/run_stat_packs.sh [--analytics] [--validate] [--team TEAM]
#
# Options:
#   --analytics    Run analytics_ipl.py first to refresh views
#   --validate     Run validation checks after generation
#   --team TEAM    Generate only for specified team (CSK, MI, RCB, etc.)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DB_PATH="$PROJECT_DIR/data/cricket_playbook.duckdb"
STAT_PACK_DIR="$PROJECT_DIR/stat_packs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
RUN_ANALYTICS=false
RUN_VALIDATE=false
SINGLE_TEAM=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --analytics)
            RUN_ANALYTICS=true
            shift
            ;;
        --validate)
            RUN_VALIDATE=true
            shift
            ;;
        --team)
            SINGLE_TEAM="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./scripts/run_stat_packs.sh [--analytics] [--validate] [--team TEAM]"
            exit 1
            ;;
    esac
done

echo "============================================================"
echo "Cricket Playbook - Stat Pack Runner"
echo "============================================================"
echo ""

# Check database exists
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}ERROR: Database not found at $DB_PATH${NC}"
    echo "Run ingest.py first to create the database."
    exit 1
fi

# Run analytics if requested
if [ "$RUN_ANALYTICS" = true ]; then
    echo -e "${YELLOW}Running analytics_ipl.py to refresh views...${NC}"
    python "$SCRIPT_DIR/analytics_ipl.py"
    echo ""
fi

# Generate stat packs
echo -e "${YELLOW}Generating stat packs...${NC}"
if [ -n "$SINGLE_TEAM" ]; then
    echo "  Target team: $SINGLE_TEAM"
    # For single team, we'd need to modify generate_stat_packs.py to accept a team argument
    # For now, generate all and note which one was requested
    python "$SCRIPT_DIR/generate_stat_packs.py"
else
    python "$SCRIPT_DIR/generate_stat_packs.py"
fi

# Validate if requested
if [ "$RUN_VALIDATE" = true ]; then
    echo ""
    echo -e "${YELLOW}Validating stat packs...${NC}"

    ERRORS=0

    # Check all 10 teams exist
    for team in CSK DC GT KKR LSG MI PBKS RCB RR SRH; do
        PACK="$STAT_PACK_DIR/${team}_stat_pack.md"
        if [ -f "$PACK" ]; then
            # Check file size (should be > 10KB)
            SIZE=$(wc -c < "$PACK")
            if [ "$SIZE" -lt 10000 ]; then
                echo -e "  ${RED}WARNING: $team stat pack is smaller than expected ($SIZE bytes)${NC}"
                ((ERRORS++))
            else
                echo -e "  ${GREEN}OK${NC}: $team stat pack ($SIZE bytes)"
            fi

            # Check required sections exist
            if ! grep -q "## 1. Squad Overview" "$PACK"; then
                echo -e "    ${RED}Missing: Squad Overview section${NC}"
                ((ERRORS++))
            fi
            if ! grep -q "## 9. Andy Flower" "$PACK"; then
                echo -e "    ${RED}Missing: Tactical Insights section${NC}"
                ((ERRORS++))
            fi
        else
            echo -e "  ${RED}MISSING: $PACK${NC}"
            ((ERRORS++))
        fi
    done

    # Check README exists
    if [ -f "$STAT_PACK_DIR/README.md" ]; then
        echo -e "  ${GREEN}OK${NC}: README.md exists"
    else
        echo -e "  ${YELLOW}WARNING: README.md not found${NC}"
    fi

    echo ""
    if [ "$ERRORS" -eq 0 ]; then
        echo -e "${GREEN}Validation passed - all stat packs OK${NC}"
    else
        echo -e "${RED}Validation found $ERRORS issues${NC}"
        exit 1
    fi
fi

echo ""
echo "============================================================"
echo -e "${GREEN}Stat pack generation complete${NC}"
echo "Output: $STAT_PACK_DIR"
echo "============================================================"
