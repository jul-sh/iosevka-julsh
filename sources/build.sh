#!/usr/bin/env bash
#
# To run this script with all necessary dependencies provided, simply use Nix.
# Nix isolates builds by creating a reproducible environment, making it easy
# to define exactly which version of all build tools are used.
#
# To download and install Nix, visit:
#   https://nixos.org/download.html
# and follow the installation instructions listed there.
#
# Once installed, you can run this script using Nix by executing:
#   nix develop --experimental-features 'nix-command flakes' ./sources#default -c ./sources/build.sh

set -e

cd "$(git rev-parse --show-toplevel)"

# Run font building
python3 sources/scripts/build_fonts.py
