#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


def run_step(script: Path, data_dir: Path, out_dir: Path):
    cmd = [sys.executable, str(script), "--data-dir", str(data_dir), "--out-dir", str(out_dir / "csv")]
    if script.name in {"build_summary.py", "make_plots.py"}:
        cmd = [sys.executable, str(script), "--out-dir", str(out_dir)]

    result = subprocess.run(cmd, check=False, text=True, capture_output=True)
    print(f"[{script.name}] exit={result.returncode}")
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())

    if result.returncode != 0:
        raise RuntimeError(f"Step failed: {script.name}")


def main():
    parser = argparse.ArgumentParser(description="Run the full network-analysis parsing pipeline.")
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent

    steps = [
        scripts_dir / "parse_ping.py",
        scripts_dir / "parse_iperf.py",
        scripts_dir / "parse_path.py",
        scripts_dir / "parse_http.py",
        scripts_dir / "parse_pcap.py",
        scripts_dir / "build_summary.py",
        scripts_dir / "make_plots.py",
    ]

    for step in steps:
        run_step(step, args.data_dir, args.out_dir)

    print("All steps completed successfully")


if __name__ == "__main__":
    main()
