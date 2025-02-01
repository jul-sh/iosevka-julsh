#!/usr/bin/env python3
"""
Build custom Iosevka fonts from private build plans.

Steps:
  1. Clone or update the Iosevka repo at a specific commit.
  2. Install npm dependencies.
  3. Parse plan names from `private-build-plans.toml`.
  4. For each plan:
     - Build TTFs
     - Optionally adjust whitespace (for non-mono plans)
     - Generate subsetted (Basic Latin) WOFF2 webfonts.
"""

import os
import re
import shutil
import subprocess
import sys
import traceback
from typing import List, Optional

# Make sure python3-fontforge is installed on your system
try:
    import fontforge
except ImportError:
    print("ERROR: Could not import fontforge. Please ensure python3-fontforge is installed.")
    print("On Ubuntu/Debian: sudo apt-get install python3-fontforge")
    sys.exit(1)

###############################################################################
# Configuration
###############################################################################

IOSEVKA_REPO_URL: str = "https://github.com/be5invis/Iosevka.git"
IOSEVKA_REPO_BRANCH: str = "v32.4.0"
IOSEVKA_REPO_COMMIT: str = "a5d26cb87836c7245dcae2c741663017245cdd18"

OUTPUT_DIR: str = "sources/output"
WORKDIR: str = "sources/workdir"
REPO_DIR: str = os.path.join(WORKDIR, "iosevka-repo")
PRIVATE_TOML: str = "sources/private-build-plans.toml"

# Whitespace Adjustment Config
SPACE_WIDTH_REDUCTION: float = 0.24 # %

###############################################################################
# Utilities
###############################################################################

def run_cmd(command: str, cwd: Optional[str] = None) -> None:
    """Executes a shell command and raises an error if it fails.

    Args:
        command: The shell command to execute.
        cwd: Optional working directory to run command in.

    Raises:
        subprocess.CalledProcessError: If command execution fails.
    """
    print(f"[cmd] {command}")
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        print(f"Command was: {command}")
        print(f"Working directory: {cwd or os.getcwd()}")
        raise

###############################################################################
# Environment Preparation
###############################################################################

def prep_environment() -> None:
    """Prepares the build environment.

    Ensures WORKDIR exists, clones/updates Iosevka repo, checks out specified commit,
    copies build plans, installs dependencies, and cleans output directory.

    Raises:
        FileNotFoundError: If private build plans file is missing.
        Exception: If any preparation step fails.
    """
    try:
        os.makedirs(WORKDIR, exist_ok=True)

        # Clone or update the repository
        if os.path.isdir(REPO_DIR):
            print("[prep_environment] Updating existing Iosevka repository...")
            run_cmd(f"git fetch origin {IOSEVKA_REPO_BRANCH}", cwd=REPO_DIR)
            run_cmd(f"git reset --hard {IOSEVKA_REPO_COMMIT}", cwd=REPO_DIR)
            run_cmd("git clean -fdx", cwd=REPO_DIR)
        else:
            print("[prep_environment] Cloning Iosevka repository...")
            run_cmd(
                f"git clone --depth 1 --branch {IOSEVKA_REPO_BRANCH} {IOSEVKA_REPO_URL} {REPO_DIR}"
            )
            # List contents of cloned repo to verify
            print("[prep_environment] Listing cloned repository contents...")
            run_cmd(f"git reset --hard {IOSEVKA_REPO_COMMIT}", cwd=REPO_DIR)

        # Copy private build plans
        print("[prep_environment] Copying private build plans...")
        if not os.path.exists(PRIVATE_TOML):
            raise FileNotFoundError(f"Private build plans file not found: {PRIVATE_TOML}")
        shutil.copyfile(PRIVATE_TOML, os.path.join(REPO_DIR, "private-build-plans.toml"))

        # Install npm dependencies
        print("[prep_environment] Installing npm dependencies...")
        run_cmd("npm ci", cwd=REPO_DIR)

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

    except Exception as e:
        print(f"ERROR during environment preparation: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise

###############################################################################
# Build Plan Parsing
###############################################################################

def get_build_plans() -> List[str]:
    """Parses build plan names from private-build-plans.toml.

    Returns:
        List of build plan names, excluding variant plans containing dots.

    Raises:
        FileNotFoundError: If build plans file is missing.
        Exception: If parsing fails.
    """
    try:
        plans: List[str] = []
        pattern = re.compile(r'^\[buildPlans\.(.+)\]$')
        with open(PRIVATE_TOML, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                match = pattern.match(line)
                if match:
                    plan_name = match.group(1)
                    if '.' not in plan_name:
                        plans.append(plan_name)

        if not plans:
            print("WARNING: No build plans found in private-build-plans.toml")

        return plans
    except FileNotFoundError:
        print(f"ERROR: Build plans file not found: {PRIVATE_TOML}")
        raise
    except Exception as e:
        print(f"ERROR parsing build plans: {str(e)}")
        raise

###############################################################################
# Whitespace Adjustment
###############################################################################

def adjust_whitespace(input_folder: str) -> None:
    """Adjusts whitespace metrics in TTF files.

    For each TTF in input_folder:
      - Scales space to 85% of original width (integer)
      - Creates kerning lookup to shift punctuation left ~0.15ch
      - Overwrites existing font file

    Args:
        input_folder: Directory containing TTF files to process.

    Raises:
        FileNotFoundError: If input folder doesn't exist.
        ValueError: If font is missing required characters.
        Exception: If font processing fails.
    """
    if not os.path.isdir(input_folder):
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    ttf_files = [f for f in os.listdir(input_folder) if f.endswith(".ttf")]
    if not ttf_files:
        print(f"WARNING: No TTF files found in {input_folder}")
        return

    for file_name in ttf_files:
        file_path = os.path.join(input_folder, file_name)
        print(f"[adjust_whitespace] Processing {file_name}...")

        try:
            font = fontforge.open(file_path)
        except Exception as e:
            print(f"ERROR: Failed to open font file {file_path}")
            print(f"FontForge error: {str(e)}")
            raise

        try:
            # Adjust space width (must be an integer)
            if 0x20 not in font:
                raise ValueError("Font missing required space character (U+0020)")

            space_glyph = font[0x20]
            orig_width = space_glyph.width
            # Reduce space width bys and shift punctuation left by same amount
            new_space_width = int(round(orig_width * (1 - SPACE_WIDTH_REDUCTION)))
            space_glyph.width = new_space_width

            # Create a kerning lookup
            try:
                font.addLookup("kern_punct", "gpos_pair", None, (("kern", (("DFLT", ("dflt")),)),))
                font.addLookupSubtable("kern_punct", "kern_punct_subtable")
            except Exception as e:
                print(f"ERROR: Failed to create kerning lookup in {file_name}")
                print(f"FontForge error: {str(e)}")
                raise

            # We want punctuation to shift left by ~0.15ch
            #   => Negative x offset in the "right" glyph's placement
            punctuation = [
                0x2E,  # period
                0x2C,  # comma
                0x3B,  # semicolon
                0x3A,  # colon
                0x21,  # exclamation mark
                0x3F,  # question mark
                0x27,  # apostrophe
                0x22,  # quotation mark
                0x2D,  # hyphen
                0x2026 # ellipsis
            ]
            shift_val = int(round(orig_width * -SPACE_WIDTH_REDUCTION))

            for punct in punctuation:
                if punct not in font:
                    print(f"WARNING: Font missing punctuation character U+{punct:04X}")
                    continue

                punct_glyph = font[punct]
                for g in font.glyphs():
                    if g.isWorthOutputting():
                        try:
                            # addPosSub requires 10 args for pair-position:
                            #  1) subtable name
                            #  2) "other glyph" or glyph set
                            #  3,4,5,6) xPlacement1, yPlacement1, xAdvance1, yAdvance1
                            #  7,8,9,10) xPlacement2, yPlacement2, xAdvance2, yAdvance2
                            # We want the *second* glyph offset to be shift_val in xPlacement2
                            # => We'll keep the first glyph offset at 0
                            punct_glyph.addPosSub(
                                "kern_punct_subtable",
                                g.glyphname,
                                0,  # xPlacement1
                                0,  # yPlacement1
                                0,  # xAdvance1
                                0,  # yAdvance1
                                shift_val,  # xPlacement2
                                0,          # yPlacement2
                                0,          # xAdvance2
                                0           # yAdvance2
                            )
                        except Exception as e:
                            print(f"ERROR: Failed to add kerning for {punct_glyph.glyphname} with {g.glyphname}")
                            print(f"FontForge error: {str(e)}")
                            raise

            # Overwrite existing file
            try:
                font.generate(file_path)
                print(f"[adjust_whitespace] Overwrote font in place: {file_path}")
            except Exception as e:
                print(f"ERROR: Failed to save modified font to {file_path}")
                print(f"FontForge error: {str(e)}")
                raise
            finally:
                font.close()

        except Exception as e:
            print(f"ERROR: Failed to process font {file_path}")
            print(f"FontForge error: {str(e)}")
            raise

    print("[adjust_whitespace] Processing complete.")

###############################################################################
# Webfont Generation
###############################################################################

def generate_webfonts(input_folder: str, webfont_output_folder: str) -> None:
    """Generates WOFF2 webfonts from TTF files.

    For each TTF in input_folder:
      - Subsets to Basic Latin (U+0000..U+007F)
      - Generates .woff2 in webfont_output_folder

    Args:
        input_folder: Directory containing source TTF files.
        webfont_output_folder: Directory to output WOFF2 files.
    """
    os.makedirs(webfont_output_folder, exist_ok=True)

    for file_name in os.listdir(input_folder):
        if not file_name.endswith(".ttf"):
            continue

        input_path = os.path.join(input_folder, file_name)
        woff2_path = os.path.join(webfont_output_folder, file_name.replace(".ttf", ".woff2"))

        print(f"[webfont] Processing {file_name}...")
        font = fontforge.open(input_path)

        # Keep only U+0000..U+007F
        font.selection.none()
        font.selection.select(("ranges", None), 0x0000, 0x007F)
        font.selection.invert()
        font.clear()

        font.generate(woff2_path, flags=("opentype",))
        font.close()

        print(f"[webfont] Saved WOFF2 webfont: {woff2_path}")

    print("[webfont] Processing complete. All webfonts have been generated.")

###############################################################################
# Single Plan Build
###############################################################################

def build_one_plan(plan_name: str) -> None:
    """Builds a single font plan.

    Steps:
      1. npm run build -- ttf::<plan_name>
      2. Copy TTFs to OUTPUT_DIR/<plan_name>
      3. Adjust whitespace if plan_name not 'mono'
      4. Generate WOFF2 webfonts

    Args:
        plan_name: Name of the build plan to process.
    """
    print(f"\n--- Building plan '{plan_name}' ---")

    plan_dist_dir = os.path.join(REPO_DIR, "dist", plan_name, "TTF")
    plan_out_dir = os.path.join(OUTPUT_DIR, plan_name)
    webfont_out_dir = os.path.join(OUTPUT_DIR, plan_name + "-webfonts")

    os.makedirs(plan_out_dir, exist_ok=True)
    os.makedirs(webfont_out_dir, exist_ok=True)

    # 1) Build TTF
    print(f"[build_one_plan] Building TTF for '{plan_name}'...")
    run_cmd(f"npm run build -- ttf::{plan_name}", cwd=REPO_DIR)

    # 2) Copy TTFs
    if not os.path.isdir(plan_dist_dir):
        print(f"[build_one_plan] ERROR: Dist folder not found: {plan_dist_dir}")
        raise FileNotFoundError(f"Dist folder not found: {plan_dist_dir}")

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

###############################################################################
# Main
###############################################################################

def main() -> None:
    """Main entry point.

    Prepares environment, gathers build plans, and builds each plan in turn.
    """
    print(f"[main] Working directory: {os.getcwd()}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(WORKDIR, exist_ok=True)
    try:
        prep_environment()

        build_plans = get_build_plans()
        print("[main] Discovered build plans:", build_plans)

        for plan_name in build_plans:
            try:
                build_one_plan(plan_name)
            except Exception as e:
                print(f"ERROR building plan '{plan_name}': {str(e)}")
                print("Traceback:")
                traceback.print_exc()
                raise

        print("\nAll font builds completed successfully.")
    except Exception as e:
        print(f"\nERROR: Font build failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
