#!/usr/bin/env python3
import os
import re
import shutil
import subprocess

# Constants
IOSEVKA_REPO_URL = "https://github.com/be5invis/Iosevka.git"
IOSEVKA_REPO_BRANCH = "v17.0.1"
IOSEVKA_REPO_COMMIT = "398451d7c541ae2c83425d240b4d7bc5e70e5a07"

OUTPUT_DIR = "/app/output"
WORKDIR = "/app/workdir"
REPO_DIR = os.path.join(WORKDIR, "iosevka-repo")
PRIVATE_TOML = "/app/private-build-plans.toml"

def run_cmd(command, cwd=None):
    """
    Utility to run a shell command, raising an error if it fails.
    """
    print(f"[cmd] {command}")
    subprocess.check_call(command, shell=True, cwd=cwd)

def prep_environment():
    """
    Clone (or update) the Iosevka repo, check out the target commit,
    copy the private build plans, and install npm dependencies.
    """
    # Ensure workdir exists
    os.makedirs(WORKDIR, exist_ok=True)
    os.chdir(WORKDIR)

    # Clone or update the repository
    if os.path.isdir(REPO_DIR):
        print("Updating existing Iosevka repository...")
        run_cmd(f"git fetch origin {IOSEVKA_REPO_BRANCH}", cwd=REPO_DIR)
        run_cmd(f"git reset --hard {IOSEVKA_REPO_COMMIT}", cwd=REPO_DIR)
        run_cmd("git clean -fdx", cwd=REPO_DIR)
    else:
        print("Cloning Iosevka repository...")
        run_cmd(f"git clone --depth 1 --branch {IOSEVKA_REPO_BRANCH} {IOSEVKA_REPO_URL} iosevka-repo")

        # Check out correct commit
        run_cmd(f"git reset --hard {IOSEVKA_REPO_COMMIT}", cwd=REPO_DIR)

    # Copy private build plans
    print("Copying private build plans...")
    shutil.copyfile(PRIVATE_TOML, os.path.join(REPO_DIR, "private-build-plans.toml"))

    # Install dependencies
    print("Installing npm dependencies...")
    os.chdir(REPO_DIR)
    run_cmd("npm ci")

    # Clean output directory
    if os.path.isdir(OUTPUT_DIR):
        print(f"Cleaning output directory '{OUTPUT_DIR}'...")
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
    Parse private-build-plans.toml to discover all build plan names automatically.

    Expects lines of the form:
      [buildPlans.iosevka-julsh]
      [buildPlans.iosevka-julsh-mono]
      [buildPlans.iosevka-julsh-prose]
      ...
    Returns a list of those keys (e.g. ['iosevka-julsh', 'iosevka-julsh-mono', 'iosevka-julsh-prose', ...]).
    """
    plans = []
    pattern = re.compile(r'^\[buildPlans\.(.+)\]$')

    with open(PRIVATE_TOML, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            if match:
                plan_name = match.group(1)
                plans.append(plan_name)
    return plans

def build_one_plan(plan_name):
    """
    1. Runs 'npm run build -- ttf::<plan_name>'
    2. Copies TTFs into /app/output/<plan_name>/
    3. If plan_name doesn't contain 'mono', run the whitespace adjustment script
    4. Generate webfonts
    """
    print(f"\n--- Building plan '{plan_name}' ---")

    plan_dist_dir = os.path.join(REPO_DIR, "dist", plan_name, "ttf")
    plan_out_dir = os.path.join(OUTPUT_DIR, plan_name)
    webfont_out_dir = os.path.join(OUTPUT_DIR, plan_name + "-webfonts")

    os.makedirs(plan_out_dir, exist_ok=True)
    os.makedirs(webfont_out_dir, exist_ok=True)

    # 1) Build
    print(f"Building TTF for plan '{plan_name}'...")
    run_cmd(f"npm run build -- ttf::{plan_name}", cwd=REPO_DIR)

    # 2) Copy TTFs from dist to output
    if not os.path.isdir(plan_dist_dir):
        print(f"ERROR: Dist folder not found for plan '{plan_name}': {plan_dist_dir}")
        return

    for f in os.listdir(plan_dist_dir):
        if f.endswith(".ttf"):
            shutil.copy2(os.path.join(plan_dist_dir, f), plan_out_dir)

    # 3) Optionally adjust whitespace
    if "mono" not in plan_name.lower():
        print(f"Adjusting whitespace in '{plan_name}' TTFs...")
        run_cmd(f"python3 /app/scripts/adjust_whitespace.py {plan_out_dir}")
    else:
        print(f"Skipping whitespace adjustment for '{plan_name}' (contains 'mono').")

    # 4) Generate webfonts
    print(f"Generating webfonts for '{plan_name}'...")
    run_cmd(f"python3 /app/scripts/webfont.py {plan_out_dir} {webfont_out_dir}")

def main():
    prep_environment()

    # Discover all build plans from private-build-plans.toml
    build_plans = get_build_plans()
    print("Discovered build plans:", build_plans)

    # Build each plan in turn
    for plan_name in build_plans:
        build_one_plan(plan_name)

    print("\nAll font builds completed successfully.")

if __name__ == "__main__":
    main()
