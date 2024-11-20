# Main build target
build: build-docker-image
ifeq ($(CI),)
	$(MAKE) run-local
else
	$(MAKE) run-ci
endif

# Build Docker image
build-docker-image:
	docker build -t fontforge-iosevka .

# Set common Docker run options
DOCKER_RUN_OPTIONS = --rm \
    -v $$(pwd)/scripts:/app/scripts \
    -v $$(pwd)/workdir:/app/workdir \
    -v $$(pwd)/output:/app/output \
    -v $$(pwd)/private-build-plans.toml:/app/private-build-plans.toml \
    fontforge-iosevka \
    bash scripts/build_fonts.sh

# Run in CI environment (GitHub Actions)
run-ci:
	mkdir -p output workdir
	docker run $(DOCKER_RUN_OPTIONS)

# Run in interactive mode for local development
run-local:
	mkdir -p output workdir
	docker run -it $(DOCKER_RUN_OPTIONS)

.PHONY: build build-docker-image run-ci run-local
