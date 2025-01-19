#!/usr/bin/env python3
"""
Script to build custom Iosevka fonts from private build plans.

Steps:
  1) Clone/update a specific commit of the Iosevka repo.
  2) Install npm dependencies.
  3) Parse build plan names from `private-build-plans.toml`.
  4) For each plan:
     - Build TTF fonts
     - Optionally adjust whitespace (non-mono only)
     - Generate WOFF2 webfonts (subset to Basic Latin)
"""

import os
import re
import shutil
import subprocess
import sys
import fontforge  # Make sure python3-fontforge is installed

###############################################################################
# Configuration
###############################################################################

IOSEVKA_REPO_URL = "https://github.com/be5invis/Iosevka.git"
IOSEVKA_REPO_BRANCH = "v17.0.1"
IOSEVKA_REPO_COMMIT = "398451d7c541ae2c83425d240b4d7bc5e70e5a07"

OUTPUT_DIR = "/app/output"
WORKDIR = "/app/workdir"
REPO_DIR = os.path.join(WORKDIR, "iosevka-repo")
PRIVATE_TOML = "/app/private-build-plans.toml"

###############################################################################
# Utilities
###############################################################################

def run_cmd(command, cwd=None):
    """
    Execute a shell command and raise an error if it fails.
    """
    print(f"[cmd] {command}")
    subprocess.check_call(command, shell=True, cwd=cwd)

###############################################################################
# Steps
###############################################################################

def prep_environment():
    """
    Prepare the environment:
      - Create WORKDIR if needed
      - Clone or update the Iosevka repo
      - Check out the specified commit
      - Copy private build plans
      - Install npm dependencies
      - Clean OUTPUT_DIR
    """
    os.makedirs(WORKDIR, exist_ok=True)
    os.chdir(WORKDIR)

    # Clone or update the repository
    if os.path.isdir(REPO_DIR):
        print("[prep_environment] Updating existing Iosevka repository...")
        run_cmd(f"git fetch origin {IOSEVKA_REPO_BRANCH}", cwd=REPO_DIR)
        run_cmd(f"git reset --hard {IOSEVKA_REPO_COMMIT}", cwd=REPO_DIR)
        run_cmd("git clean -fdx", cwd=REPO_DIR)
    else:
        print("[prep_environment] Cloning Iosevka repository...")
        run_cmd(f"git clone --depth 1 --branch {IOSEVKA_REPO_BRANCH} {IOSEVKA_REPO_URL} iosevka-repo")
        run_cmd(f"git reset --hard {IOSEVKA_REPO_COMMIT}", cwd=REPO_DIR)

    # Copy private build plans
    print("[prep_environment] Copying private build plans...")
    shutil.copyfile(PRIVATE_TOML, os.path.join(REPO_DIR, "private-build-plans.toml"))

    # Install npm dependencies
    print("[prep_environment] Installing npm dependencies...")
    os.chdir(REPO_DIR)
    run_cmd("npm ci")

    # Clean the output directory
    if os.path.isdir(OUTPUT_DIR):
        print(f"[prep_environment] Cleaning output directory: '{OUTPUT_DIR}'...")
        for item in os.listdir(OUTPUT_DIR):
            item_path = os.path.join(OUTPUT_DIR, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            else:
                shutil.rmtree(item_path)
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_build_plans():
    """
    Parse PRIVATE_TOML for lines like [buildPlans.planName].
    Return all discovered planName values in a list.
    """
    plans = []
    pattern = re.compile(r'^\[buildPlans\.(.+)\]$')

    with open(PRIVATE_TOML, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            if match:
                plans.append(match.group(1))

    return plans

def adjust_whitespace(input_folder):
    """
    For each .ttf in 'input_folder':
      - Reduce space character width to 85% of original
      - Add kerning for punctuation (.,;:!?)
      - Overwrite the font file in place
    """
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".ttf"):
            file_path = os.path.join(input_folder, file_name)
            print(f"[adjust_whitespace] Processing {file_name}...")

            font = fontforge.open(file_path)

            # Adjust space width
            space_glyph = font[0x20]
            original_width = space_glyph.width
            space_glyph.width = original_width * 0.85

            # Create a kerning lookup
            font.addLookup(
                "kern_punct", "gpos_pair", None,
                (("kern", (("DFLT", ("dflt")),)),)
            )
            font.addLookupSubtable("kern_punct", "kern_punct_subtable")

            # Shift punctuation left by ~0.15ch
            punctuation = [0x2E, 0x2C, 0x3B, 0x3A, 0x21, 0x3F]  # . , ; : ! ?
            for punct in punctuation:
                if punct in font:
                    for g in font.glyphs():
                        if g.isWorthOutputting():
                            font[punct].addPosSub(
                                "kern_punct_subtable",
                                g.glyphname,
                                0, 0,
                                int(original_width * -0.15), 0
                            )

            font.generate(file_path)  # Overwrite
            font.close()
            print(f"[adjust_whitespace] Overwrote font in place: {file_path}")

    print("[adjust_whitespace] Processing complete.")

def generate_webfonts(input_folder, webfont_output_folder):
    """
    For each .ttf in 'input_folder':
      - Subset to Basic Latin (U+0000..U+007F)
      - Generate a .woff2 in 'webfont_output_folder'
    """
    os.makedirs(webfont_output_folder, exist_ok=True)

    basic_latin = range(0x0000, 0x0080)

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".ttf"):
            input_path = os.path.join(input_folder, file_name)
            woff2_path = os.path.join(
                webfont_output_folder,
                file_name.replace(".ttf", ".woff2")
            )

            print(f"[webfont] Processing {file_name}...")
            font = fontforge.open(input_path)

            # Keep only Basic Latin glyphs
            font.selection.none()
            for char in basic_latin:
                # The snippet below intentionally does a "select then invert"
                if font.selection.select(("more", None), char):
                    font.selection.select(("less", None), char)
            font.selection.invert()
            font.clear()

            # Generate WOFF2
            font.generate(woff2_path, flags=("opentype",))
            font.close()

            print(f"[webfont] Saved WOFF2 webfont: {woff2_path}")

    print("[webfont] Processing complete. All webfonts have been generated.")

def build_one_plan(plan_name):
    """
    Build a single plan:
      - `npm run build -- ttf::<plan_name>`
      - Copy TTFs to OUTPUT_DIR/plan_name
      - Adjust whitespace unless plan_name contains 'mono'
      - Generate WOFF2 webfonts (subset to Basic Latin)
    """
    print(f"\n--- Building plan '{plan_name}' ---")

    plan_dist_dir = os.path.join(REPO_DIR, "dist", plan_name, "ttf")
    plan_out_dir = os.path.join(OUTPUT_DIR, plan_name)
    webfont_out_dir = os.path.join(OUTPUT_DIR, plan_name + "-webfonts")

    os.makedirs(plan_out_dir, exist_ok=True)
    os.makedirs(webfont_out_dir, exist_ok=True)

    # 1) Build TTF
    print(f"[build_one_plan] Building TTF for plan '{plan_name}'...")
    run_cmd(f"npm run build -- ttf::{plan_name}", cwd=REPO_DIR)

    # 2) Copy TTFs
    if not os.path.isdir(plan_dist_dir):
        print(f"[build_one_plan] ERROR: Dist folder not found: {plan_dist_dir}")
        return

    for filename in os.listdir(plan_dist_dir):
        if filename.endswith(".ttf"):
            shutil.copy2(os.path.join(plan_dist_dir, filename), plan_out_dir)

    # 3) Adjust whitespace if not mono
    if "mono" not in plan_name.lower():
        print(f"[build_one_plan] Adjusting whitespace in '{plan_name}'...")
        adjust_whitespace(plan_out_dir)
    else:
        print(f"[build_one_plan] Skipping whitespace adjustment (mono plan).")

    # 4) Generate webfonts
    print(f"[build_one_plan] Generating webfonts for '{plan_name}'...")
    generate_webfonts(plan_out_dir, webfont_out_dir)

def main():
    """
    Main entry point. Prepares environment, reads build plans,
    and builds each plan.
    """
    prep_environment()

    build_plans = get_build_plans()
    print("[main] Discovered build plans:", build_plans)

    for plan_name in build_plans:
        build_one_plan(plan_name)

    print("\nAll font builds completed successfully.")

if __name__ == "__main__":
    main()
