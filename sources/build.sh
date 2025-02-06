#!/usr/bin/env bash

set -e

cd "$(git rev-parse --show-toplevel)"

# Source the Nix environment
source sources/scripts/setup_shell.sh

# Run the build script to generate TTFs
python3 sources/scripts/build_fonts.py

# Generate webfonts for each font family
echo "Generating webfonts..."
for family_dir in sources/output/*/; do
    if [ -d "$family_dir" ]; then
        ttf_dir="${family_dir}ttf"
        if [ -d "$ttf_dir" ]; then
            echo "Processing webfonts for: ${family_dir}"
            python3 sources/scripts/generate_webfonts.py "$ttf_dir" "$family_dir"
        fi
    fi
done

echo "Build complete!"
