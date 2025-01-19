#!/bin/bash
set -e

# Variables
IOSEVKA_REPO_URL="https://github.com/be5invis/Iosevka.git"
IOSEVKA_REPO_BRANCH="v17.0.1"
IOSEVKA_REPO_COMMIT="398451d7c541ae2c83425d240b4d7bc5e70e5a07"
OUTPUT_DIR="/app/output"
WORKDIR="/app/workdir"

echo "Starting font build process..."

# Preparation Section
prep_environment() {
    cd "$WORKDIR"

    # Clone or update Iosevka repository
    if [ -d "iosevka-repo" ]; then
        echo "Updating existing Iosevka repository..."
        cd iosevka-repo
        git fetch origin $IOSEVKA_REPO_BRANCH
        git reset --hard $IOSEVKA_REPO_COMMIT
        git clean -fdx
    else
        echo "Cloning Iosevka repository..."
        git clone --depth 1 --branch $IOSEVKA_REPO_BRANCH $IOSEVKA_REPO_URL iosevka-repo
        cd iosevka-repo
        git reset --hard $IOSEVKA_REPO_COMMIT
    fi
    echo "Iosevka repository is now at the correct commit."

    # Copy the private build plan
    echo "Copying private build plan..."
    cp /app/private-build-plans.toml ./
    echo "Private build plan copied."

    # Install dependencies
    echo "Installing dependencies..."
    npm ci
    echo "Dependencies installed."

    # Ensure the output directory is clean
    if [ -d "$OUTPUT_DIR" ]; then
        echo "Cleaning output directory..."
        rm -rf "$OUTPUT_DIR"/* || { echo "Failed to clean output directory contents. Exiting."; exit 1; }
    fi
}

# Build Iosevka Julsh Mono
build_julsh_mono() {
    mkdir -p "$OUTPUT_DIR/iosevka-julsh-mono/" "$OUTPUT_DIR/iosevka-julsh-mono-webfonts"
    echo "Building Iosevka Julsh Mono..."
    npm run build -- ttf::iosevka-julsh-mono
    echo "Iosevka Julsh Mono built successfully."

    echo "Copying Iosevka Julsh Mono fonts to output..."
    cp dist/iosevka-julsh-mono/ttf/* "$OUTPUT_DIR/iosevka-julsh-mono/"
    echo "Iosevka Julsh Mono fonts copied to output directory."

    # Generate webfonts for Iosevka Julsh Mono
    echo "Generating webfonts for Iosevka Julsh Mono..."
    python3 /app/scripts/webfont.py "$OUTPUT_DIR/iosevka-julsh-mono" "$OUTPUT_DIR/iosevka-julsh-mono-webfonts"
    echo "Webfonts generated for Iosevka Julsh Mono."
}

# Build Iosevka Julsh
build_julsh() {
    mkdir -p "$OUTPUT_DIR/iosevka-julsh" "$OUTPUT_DIR/iosevka-julsh-webfonts"
    echo "Building Iosevka Julsh..."
    npm run build -- ttf::iosevka-julsh
    echo "Iosevka Julsh built successfully."

    # Copy the built TTFs into the output folder
    echo "Copying Iosevka Julsh fonts to output..."
    cp dist/iosevka-julsh/ttf/* "$OUTPUT_DIR/iosevka-julsh/"
    echo "Iosevka Julsh fonts copied."

    # Run the Python adjustment script on the generated fonts
    echo "Running whitespace adjustment script on Iosevka Julsh..."
    python3 /app/scripts/adjust_whitespace.py "$OUTPUT_DIR/iosevka-julsh"
    echo "Whitespace adjustment completed."

    # Generate webfonts for Iosevka Julsh
    echo "Generating webfonts for Iosevka Julsh..."
    python3 /app/scripts/webfont.py "$OUTPUT_DIR/iosevka-julsh" "$OUTPUT_DIR/iosevka-julsh-webfonts"
    echo "Webfonts generated for Iosevka Julsh."
}

# Main execution
prep_environment

# Run build processes in parallel
build_julsh_mono &
build_julsh &

# Wait for all background processes to complete
wait

echo "All fonts have been generated and saved to $OUTPUT_DIR"
echo "Font build process completed successfully."
