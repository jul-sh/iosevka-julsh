#!/usr/bin/env bash

set -e

cd "$(git rev-parse --show-toplevel)"

# Source the Nix environment
source sources/scripts/setup_shell.sh

# Run the build script to generate TTFs
python3 sources/scripts/build_fonts.py

echo "Build complete!"
