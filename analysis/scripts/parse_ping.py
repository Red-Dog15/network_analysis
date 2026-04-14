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


def parse_ping_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_header(text)
    command, timestamp = parse_header(text)
    target = extract_target_from_name(path, "ping_")

    packet_match = re.search(
        r"(\d+) packets transmitted,\s*(\d+) received,\s*([0-9.]+)% packet loss",
        text,
    )
    rtt_match = re.search(
        r"rtt min/avg/max/mdev = ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+) ms",
        text,
    )

    sample_rows = []
    for line in text.splitlines():
        sample = re.search(
            r"icmp_seq=(\d+).*ttl=(\d+).*time=([0-9.]+) ms",
            line,
        )
        if sample:
            sample_rows.append(
                {
                    "run_id": extract_run_id(path),
                    "target": target,
                    "icmp_seq": int(sample.group(1)),
                    "ttl": int(sample.group(2)),
                    "rtt_ms": float(sample.group(3)),
                    "source_file": str(path),
                }
            )

    ok = packet_match is not None and rtt_match is not None
    status = classify_status(body, text, ok)

    row = {
        "run_id": extract_run_id(path),
        "target": target,
        "status": status,
        "command": command,
        "timestamp": timestamp,
        "tx_packets": int(packet_match.group(1)) if packet_match else "",
        "rx_packets": int(packet_match.group(2)) if packet_match else "",
        "packet_loss_pct": float(packet_match.group(3)) if packet_match else "",
        "rtt_min_ms": float(rtt_match.group(1)) if rtt_match else "",
        "rtt_avg_ms": float(rtt_match.group(2)) if rtt_match else "",
        "rtt_max_ms": float(rtt_match.group(3)) if rtt_match else "",
        "rtt_mdev_ms": float(rtt_match.group(4)) if rtt_match else "",
        "samples_count": len(sample_rows),
        "source_file": str(path),
    }
    return row, sample_rows


def main():
    parser = argparse.ArgumentParser(description="Parse ping logs into CSV files.")
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    files = discover_files(args.data_dir, "*/ping_*.txt")
    summary_rows = []
    sample_rows = []

    for file_path in files:
        summary, samples = parse_ping_file(file_path)
        summary_rows.append(summary)
        sample_rows.extend(samples)

    write_csv(
        args.out_dir / "ping_summary.csv",
        summary_rows,
        [
            "run_id",
            "target",
            "status",
            "command",
            "timestamp",
            "tx_packets",
            "rx_packets",
            "packet_loss_pct",
            "rtt_min_ms",
            "rtt_avg_ms",
            "rtt_max_ms",
            "rtt_mdev_ms",
            "samples_count",
            "source_file",
        ],
    )

    write_csv(
        args.out_dir / "ping_samples.csv",
        sample_rows,
        ["run_id", "target", "icmp_seq", "ttl", "rtt_ms", "source_file"],
    )

    print(f"Parsed {len(files)} ping files")


if __name__ == "__main__":
    main()
