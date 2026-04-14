#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

from common import (
    classify_status,
    discover_files,
    extract_run_id,
    extract_target_from_name,
    mbps_to_float,
    parse_header,
    strip_header,
    write_csv,
)


def find_role_line(text: str, role: str):
    role_line = None
    for line in text.splitlines():
        if line.strip().endswith(role):
            role_line = line
    return role_line


def parse_iperf_line(line: str):
    if not line:
        return "", "", ""
    bitrate_match = re.search(r"([0-9]+(?:\.[0-9]+)?\s*[KMG]bits/sec)", line)
    transfer_match = re.search(r"([0-9]+(?:\.[0-9]+)?\s*[KMG]Bytes)", line)
    retr_match = re.search(r"\s(\d+)\s+\S*\s*sender$", line)
    bitrate = bitrate_match.group(1).replace(" ", "") if bitrate_match else ""
    transfer = transfer_match.group(1).replace(" ", "") if transfer_match else ""
    retransmits = retr_match.group(1) if retr_match else ""
    return transfer, bitrate, retransmits


def parse_iperf_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_header(text)
    command, timestamp = parse_header(text)
    target = extract_target_from_name(path, "iperf_")

    sender_line = find_role_line(text, "sender")
    receiver_line = find_role_line(text, "receiver")

    sender_transfer, sender_rate, sender_retr = parse_iperf_line(sender_line)
    receiver_transfer, receiver_rate, _ = parse_iperf_line(receiver_line)

    ok = bool(sender_rate or receiver_rate)
    status = classify_status(body, text, ok)

    return {
        "run_id": extract_run_id(path),
        "target": target,
        "status": status,
        "command": command,
        "timestamp": timestamp,
        "sender_transfer": sender_transfer,
        "sender_rate": sender_rate,
        "sender_rate_mbps": mbps_to_float(sender_rate) if sender_rate else "",
        "sender_retransmits": int(sender_retr) if sender_retr else "",
        "receiver_transfer": receiver_transfer,
        "receiver_rate": receiver_rate,
        "receiver_rate_mbps": mbps_to_float(receiver_rate) if receiver_rate else "",
        "source_file": str(path),
    }


def main():
    parser = argparse.ArgumentParser(description="Parse iperf3 logs into CSV files.")
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    files = discover_files(args.data_dir, "*/iperf_*.txt")
    rows = [parse_iperf_file(file_path) for file_path in files]

    write_csv(
        args.out_dir / "iperf_summary.csv",
        rows,
        [
            "run_id",
            "target",
            "status",
            "command",
            "timestamp",
            "sender_transfer",
            "sender_rate",
            "sender_rate_mbps",
            "sender_retransmits",
            "receiver_transfer",
            "receiver_rate",
            "receiver_rate_mbps",
            "source_file",
        ],
    )

    print(f"Parsed {len(files)} iperf files")


if __name__ == "__main__":
    main()
