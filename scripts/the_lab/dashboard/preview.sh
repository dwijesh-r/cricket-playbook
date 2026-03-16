#!/bin/bash
# Local preview server for Statsledge dashboard
# Run this to preview changes before pushing to Netlify
#
# Usage: ./preview.sh [port]
# Default port: 8888

PORT=${1:-8888}
DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "  Statsledge Local Preview"
echo "  ────────────────────────"
echo "  http://localhost:${PORT}"
echo ""
echo "  Press Ctrl+C to stop"
echo ""

cd "$DIR" && python3 -m http.server "$PORT"
