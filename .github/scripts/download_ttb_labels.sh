#!/bin/bash
#
# Download TTB COLA label images for all TTB IDs
#
# This script can be run manually or in CI/CD automation.
# It downloads front and back label images from the TTB website
# for all unique TTB IDs found in _data/whiskeyindex.csv
#
# Usage:
#   ./download_ttb_labels.sh [options]
#
# Options:
#   --ttbid TTBID       Download labels for a specific TTB ID only
#   --limit N           Only process first N TTB IDs (for testing)
#   --no-skip-existing  Re-download all, even if images exist
#   --help              Show help
#
# Examples:
#   ./download_ttb_labels.sh --ttbid 24002001000457
#   ./download_ttb_labels.sh --limit 10
#   ./download_ttb_labels.sh --ttbid 24002001000458 --no-skip-existing
#

set -e  # Exit on error

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to repo root
cd "$REPO_ROOT"

echo "=========================================="
echo "TTB Label Image Downloader"
echo "=========================================="
echo "Repository: $REPO_ROOT"
echo "Labels directory: $REPO_ROOT/labels"
echo ""

# Run the Python script
python3 "$SCRIPT_DIR/download_ttb_labels.py" "$@"

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✓ Download completed successfully"
else
    echo "✗ Download completed with some failures"
fi

exit $exit_code
