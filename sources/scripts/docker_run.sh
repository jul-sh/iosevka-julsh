#!/bin/bash
set -e

# Function to run commands in Docker
run_in_docker() {
    local cmd="$*"
    local interactive=${2:-false}

    # Build Docker image if it doesn't exist
    if ! docker image inspect fontforge-iosevka >/dev/null 2>&1; then
        docker build -t fontforge-iosevka "$(git rev-parse --show-toplevel)/sources"
    fi

    # Set common Docker run options
    DOCKER_RUN_OPTIONS="--rm \
        -v $(git rev-parse --show-toplevel)/sources/scripts:/app/scripts \
        -v $(git rev-parse --show-toplevel)/sources/workdir:/app/workdir \
        -v $(git rev-parse --show-toplevel)/sources/output:/app/output \
        -v $(git rev-parse --show-toplevel)/fonts:/app/fonts \
        -v $(git rev-parse --show-toplevel)/sources/private-build-plans.toml:/app/private-build-plans.toml"

    if [ "$interactive" = true ] && [ -z "$CI" ]; then
        docker run -it $DOCKER_RUN_OPTIONS fontforge-iosevka bash -c "$cmd"
    else
        docker run $DOCKER_RUN_OPTIONS fontforge-iosevka bash -c "$cmd"
    fi
}

# If script is called directly, run the command in docker
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_in_docker "$@"
fi
