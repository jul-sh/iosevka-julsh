#!/usr/bin/env nix-shell
#!nix-shell -i bash ../shell.nix

set -e

cd "$(git rev-parse --show-toplevel)"

# Create required directories
mkdir -p sources/output sources/workdir

# Run font building
python3 sources/scripts/build_fonts.py
