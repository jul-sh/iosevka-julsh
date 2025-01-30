#!/bin/bash
set -e

# Run Fontbakery checks on fonts in place without copying
fontbakery check-googlefonts \
    -C --succinct --loglevel WARN \
    --ghmarkdown /app/output/report.md \
    /app/output/*.ttf
