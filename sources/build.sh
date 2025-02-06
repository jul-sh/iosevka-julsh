#!/usr/bin/env bash
#
# To run this script with all necessary dependencies provided, simply use Nix.
# Nix isolates builds by creating a reproducible environment, making it easy
# to define exactly which version of all build tools are used.
#
# To download and install Nix, visit:
#   https://nixos.org/download.html
# and follow the installation instructions listed there.

set -e

cd "$(git rev-parse --show-toplevel)"

nix develop --experimental-features 'nix-command flakes' ./sources#default -c python3 sources/scripts/build_fonts.py
