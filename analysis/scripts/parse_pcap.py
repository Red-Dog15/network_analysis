#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from pathlib import Path

from common import discover_files, extract_run_id, write_csv


def tshark_packet_count(pcap: Path):
    tshark_bin = shutil.which("tshark")
    if not tshark_bin:
        return "", "tshark_missing"

    cmd = [tshark_bin, "-r", str(pcap), "-T", "fields", "-e", "frame.number"]
    try:
        result = subprocess.run(cmd, check=False, text=True, capture_output=True, timeout=45)
    except subprocess.TimeoutExpired:
        return "", "tshark_timeout"

    if result.returncode != 0:
        return "", "tshark_error"

    count = 0
    for line in result.stdout.splitlines():
        if line.strip():
            count += 1
    return count, "ok"


def parse_pcap_file(path: Path):
    size = path.stat().st_size
    packet_count, tshark_state = tshark_packet_count(path)

    status = "ok"
    if size == 0:
        status = "empty_capture"
    elif tshark_state != "ok":
        status = tshark_state

    return {
        "run_id": extract_run_id(path),
        "interface": path.stem.replace("capture_", ""),
        "status": status,
        "size_bytes": size,
        "packet_count": packet_count,
        "source_file": str(path),
    }


def main():
    parser = argparse.ArgumentParser(description="Summarize pcap files into CSV.")
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    files = discover_files(args.data_dir, "*/capture_*.pcap")
    rows = [parse_pcap_file(file_path) for file_path in files]

    write_csv(
        args.out_dir / "pcap_summary.csv",
        rows,
        ["run_id", "interface", "status", "size_bytes", "packet_count", "source_file"],
    )

    print(f"Parsed {len(files)} pcap files")


if __name__ == "__main__":
    main()
