#!/usr/bin/env bash

set -e

cd "$(git rev-parse --show-toplevel)"

# Create required directories
mkdir -p sources/output sources/workdir

# Run font building
python3 sources/scripts/build_fonts.py
