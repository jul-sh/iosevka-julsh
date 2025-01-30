#!/bin/bash

# Build Docker image
docker build -t fontforge-iosevka .

# Set common Docker run options
DOCKER_RUN_OPTIONS="--rm \
    -v $(pwd)/scripts:/app/scripts \
    -v $(pwd)/workdir:/app/workdir \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/private-build-plans.toml:/app/private-build-plans.toml \
    fontforge-iosevka \
    python3 scripts/build_fonts.py"

# Create required directories
mkdir -p output workdir

# Run in interactive mode if not in CI, otherwise run non-interactively
if [ -z "$CI" ]; then
    docker run -it $DOCKER_RUN_OPTIONS
else
    docker run $DOCKER_RUN_OPTIONS
fi
