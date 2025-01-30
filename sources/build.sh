#!/bin/bash
set -e

cd "$(git rev-parse --show-toplevel)"
cd sources


# Build Docker image
docker build -t fontforge-iosevka .

# Set common Docker run options
DOCKER_RUN_OPTIONS="--rm \
    -v $(pwd)/scripts:/app/scripts \
    -v $(pwd)/workdir:/app/workdir \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/private-build-plans.toml:/app/private-build-plans.toml"

# Create required directories
mkdir -p output workdir

# Run font building and checking
if [ -z "$CI" ]; then
    docker run -it $DOCKER_RUN_OPTIONS fontforge-iosevka bash -c "python3 scripts/build_fonts.py && scripts/check_fonts.sh"
else
    docker run $DOCKER_RUN_OPTIONS fontforge-iosevka bash -c "python3 scripts/build_fonts.py && scripts/check_fonts.sh"
fi
