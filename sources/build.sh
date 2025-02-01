#!/bin/bash
set -e

cd "$(git rev-parse --show-toplevel)"
cd sources

# Create required directories
mkdir -p output workdir

# Run font building
bash scripts/docker_run.sh "python3 scripts/build_fonts.py"
