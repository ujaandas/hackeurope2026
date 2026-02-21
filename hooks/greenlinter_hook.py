#!/usr/bin/env python3
"""GreenLinter pre-commit hook - analyzes staged C++ files for energy anti-patterns."""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

API_URL = os.environ.get("GREENLINTER_API_URL", "http://localhost:8000")
ENABLED = os.environ.get("GREENLINTER_ENABLED", "true").lower() == "true"
PROVIDER = os.environ.get("GREENLINTER_PROVIDER", "ollama")
EXTENSIONS = (".cpp", ".hpp", ".cc", ".h", ".c")


def get_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True,
    )
    return [f for f in result.stdout.strip().split("\n") if f and any(f.endswith(ext) for ext in EXTENSIONS)]


def get_staged_content(filename):
    result = subprocess.run(
        ["git", "show", f":{filename}"],
        capture_output=True, text=True,
    )
    return result.stdout


def call_api(files):
    payload = json.dumps({
        "files": [{"filename": f["filename"], "code": f["code"]} for f in files],
        "provider": PROVIDER,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{API_URL}/api/hook",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"  Warning: Could not reach GreenLinter API: {e}", file=sys.stderr)
        return None


def main():
    if not ENABLED:
        sys.exit(0)

    staged = get_staged_files()
    if not staged:
        sys.exit(0)

    print("=" * 60)
    print("GreenLinter: Analyzing staged files for energy efficiency")
    print("=" * 60)

    files = [{"filename": f, "code": get_staged_content(f)} for f in staged]
    response = call_api(files)

    if not response:
        print("  Skipping optimization (API unavailable)")
        sys.exit(0)

    had_optimizations = False

    for result in response.get("results", []):
        filename = result["filename"]
        if result["had_issues"]:
            had_optimizations = True
            # Write optimized code back to working tree
            with open(filename, "w") as f:
                f.write(result["optimized_code"])
            # Re-stage the file
            subprocess.run(["git", "add", filename])
            print(f"  Optimized: {filename}")
            print(f"    Patterns found: {result['patterns_count']}")
            print(f"    Est. energy saved: {result['savings_kwh']:.4f} kWh/year")
            print(f"    Est. CO2 saved: {result['savings_co2']:.4f} kg/year")
            print(f"    Est. cost saved: {result['savings_eur']:.4f} EUR/year")
        else:
            print(f"  Clean: {filename} (no energy anti-patterns detected)")

    if had_optimizations:
        print()
        print("=" * 60)
        print("GreenLinter: Files optimized for energy efficiency!")
        print("Review changes with: git diff --cached")
        print("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    main()
