#!/bin/bash
set -e

# Ensure output directory exists and contains TTF files
if [ ! -d "/app/fonts" ] || [ -z "$(ls -A /app/fonts/*.ttf 2>/dev/null)" ]; then
    echo "ERROR: No TTF files found in /app/output directory"
    exit 1
fi

# Run Fontbakery checks on fonts in place without copying
fontbakery check-googlefonts \
    -C --succinct --loglevel WARN \
    --ghmarkdown /app/fonts/report.md \
    /app/fonts/ttf/*.ttf
