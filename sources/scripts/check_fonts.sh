#!/usr/bin/env bash

set -e

cd "$(git rev-parse --show-toplevel)"

# Ensure output directory exists and contains TTF files
if [ ! -d "sources/output" ]; then
    echo "ERROR: sources/output directory does not exist"
    exit 1
fi

# Find all TTF files recursively
TTF_FILES=$(find sources/output -type f -name "*.ttf")
if [ -z "$TTF_FILES" ]; then
    echo "ERROR: No TTF files found in sources/output directory or subdirectories"
    exit 1
fi

# Run Fontbakery checks on fonts
fontbakery check-googlefonts \
    -C --succinct --loglevel WARN \
    --ghmarkdown sources/output/report.md \
    $TTF_FILES
