#!/usr/bin/env bash

set -e

cd "$(git rev-parse --show-toplevel)"

# Set default font directory if not provided
FONT_DIR=${1:-"sources/output"}

# Ensure font directory exists and contains TTF files
if [ ! -d "$FONT_DIR" ]; then
    echo "ERROR: $FONT_DIR directory does not exist"
    exit 1
fi

# Find all TTF files recursively
TTF_FILES=$(find "$FONT_DIR" -type f -name "*.ttf")
if [ -z "$TTF_FILES" ]; then
    echo "ERROR: No TTF files found in $FONT_DIR directory or subdirectories"
    exit 1
fi

# Run Fontbakery checks on fonts. Don't fail on errors.
fontbakery check-googlefonts \
    -C --succinct --loglevel WARN \
    --ghmarkdown "$FONT_DIR/report.md" \
    $TTF_FILES || true
