#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

from common import (
    classify_status,
    discover_files,
    extract_run_id,
    extract_target_from_name,
    parse_header,
    strip_header,
    write_csv,
)


def parse_path_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_header(text)
    command, timestamp = parse_header(text)
    target = extract_target_from_name(path, "path_")

    hop_numbers = []
    latencies = []
    for line in text.splitlines():
        hop = re.match(r"^\s*(\d+)\s", line)
        if hop:
            hop_numbers.append(int(hop.group(1)))
        latencies.extend(float(v) for v in re.findall(r"([0-9]+(?:\.[0-9]+)?)\s*ms", line))

    ok = len(hop_numbers) > 0
    status = classify_status(body, text, ok)

    return {
        "run_id": extract_run_id(path),
        "target": target,
        "status": status,
        "command": command,
        "timestamp": timestamp,
        "hop_count": max(hop_numbers) if hop_numbers else "",
        "latency_samples": len(latencies),
        "latency_min_ms": min(latencies) if latencies else "",
        "latency_avg_ms": (sum(latencies) / len(latencies)) if latencies else "",
        "latency_max_ms": max(latencies) if latencies else "",
        "source_file": str(path),
    }


def main():
    parser = argparse.ArgumentParser(description="Parse tracepath/traceroute logs into CSV files.")
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    files = discover_files(args.data_dir, "*/path_*.txt")
    rows = [parse_path_file(file_path) for file_path in files]

    write_csv(
        args.out_dir / "path_summary.csv",
        rows,
        [
            "run_id",
            "target",
            "status",
            "command",
            "timestamp",
            "hop_count",
            "latency_samples",
            "latency_min_ms",
            "latency_avg_ms",
            "latency_max_ms",
            "source_file",
        ],
    )

    print(f"Parsed {len(files)} path files")


if __name__ == "__main__":
    main()
