#!/usr/bin/env python3
"""
Cricket Playbook - Generate All Outputs (Entry Point)
=====================================================
Owner: Ime Udoka (MLOps & Infrastructure Lead)
Epic: EPIC-008 (CI/CD & Automation)

Single entry point to run all generator scripts in sequence.
Runs: stat packs, depth charts, predicted XIIs, and 2023+ analytics.

Usage:
    python scripts/generators/generate_outputs.py
    python scripts/generators/generate_outputs.py --skip-2023
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

GENERATORS_DIR = Path(__file__).parent
PROJECT_ROOT = GENERATORS_DIR.parent.parent

GENERATORS = [
    {
        "name": "Stat Packs",
        "script": "generate_stat_packs.py",
        "owner": "Tom Brady & Stephen Curry",
    },
    {
        "name": "Depth Charts",
        "script": "generate_depth_charts.py",
        "owner": "Stephen Curry",
    },
    {
        "name": "Predicted XIIs",
        "script": "generate_predicted_xii.py",
        "owner": "Stephen Curry",
    },
    {
        "name": "2023+ Analytics",
        "script": "generate_all_2023_outputs.py",
        "owner": "Stephen Curry",
        "flag": "2023",
    },
]


def main():
    skip_2023 = "--skip-2023" in sys.argv

    print("=" * 70)
    print("Cricket Playbook - Generate All Outputs")
    print("Owner: Ime Udoka (MLOps & Infrastructure Lead)")
    print("=" * 70)
    print()

    results = []
    total_start = time.time()

    for i, gen in enumerate(GENERATORS, 1):
        if skip_2023 and gen.get("flag") == "2023":
            print(f"[{i}/{len(GENERATORS)}] Skipping {gen['name']} (--skip-2023)")
            results.append({"name": gen["name"], "status": "SKIPPED", "time": 0})
            continue

        script_path = GENERATORS_DIR / gen["script"]
        if not script_path.exists():
            print(f"[{i}/{len(GENERATORS)}] MISSING: {gen['script']}")
            results.append({"name": gen["name"], "status": "MISSING", "time": 0})
            continue

        print(f"[{i}/{len(GENERATORS)}] Running {gen['name']} ({gen['owner']})...")
        start = time.time()

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(PROJECT_ROOT),
                capture_output=False,
                timeout=300,
            )
            elapsed = time.time() - start
            status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
            results.append({"name": gen["name"], "status": status, "time": elapsed})
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            results.append({"name": gen["name"], "status": "TIMEOUT", "time": elapsed})
            print(f"  TIMEOUT after {elapsed:.1f}s")
        except Exception as e:
            elapsed = time.time() - start
            results.append({"name": gen["name"], "status": f"ERROR: {e}", "time": elapsed})

        print()

    total_time = time.time() - total_start

    # Summary
    print("=" * 70)
    print("GENERATION SUMMARY")
    print("=" * 70)
    all_ok = True
    for r in results:
        icon = "OK" if r["status"] == "OK" else "SKIP" if r["status"] == "SKIPPED" else "FAIL"
        print(f"  [{icon}] {r['name']}: {r['status']} ({r['time']:.1f}s)")
        if r["status"] not in ("OK", "SKIPPED"):
            all_ok = False

    print(f"\nTotal time: {total_time:.1f}s")
    print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
