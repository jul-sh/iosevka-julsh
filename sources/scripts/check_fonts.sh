#!/bin/bash
set -e

# Ensure output directory exists and contains TTF files
if [ ! -d "/git_repo/fonts" ] || [ -z "$(ls -A /git_repo/fonts/*.ttf 2>/dev/null)" ]; then
    echo "ERROR: No TTF files found in /git_repo/sources/output directory"
    exit 1
fi

# Run Fontbakery checks on fonts in place without copying
fontbakery check-googlefonts \
    -C --succinct --loglevel WARN \
    --ghmarkdown /git_repo/fonts/report.md \
    /git_repo/fonts/ttf/*.ttf
