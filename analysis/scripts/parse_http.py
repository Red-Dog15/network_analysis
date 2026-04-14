#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

from common import (
    classify_status,
    discover_files,
    extract_run_id,
    parse_header,
    strip_header,
    write_csv,
)


def parse_http_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    body = strip_header(text)
    command, timestamp = parse_header(text)

    target_url = ""
    cmd_match = re.search(r"wget\s+-O\s+/dev/null\s+(\S+)", command)
    if cmd_match:
        target_url = cmd_match.group(1)

    bytes_saved = ""
    speed_text = ""
    speed_mbps = ""

    saved_match = re.search(r"saved\s+\[(\d+)\]", text)
    if saved_match:
        bytes_saved = int(saved_match.group(1))

    speed_match = re.search(r"\(([0-9]+(?:\.[0-9]+)?)\s*([KMG])B/s\)", text)
    if speed_match:
        speed_text = f"{speed_match.group(1)}{speed_match.group(2)}B/s"
        value = float(speed_match.group(1))
        unit = speed_match.group(2)
        if unit == "K":
            speed_mbps = round(value * 8 / 1000, 4)
        elif unit == "M":
            speed_mbps = round(value * 8, 4)
        elif unit == "G":
            speed_mbps = round(value * 8000, 4)

    ok = bool(bytes_saved or speed_text)
    status = classify_status(body, text, ok)

    return {
        "run_id": extract_run_id(path),
        "target_url": target_url,
        "status": status,
        "command": command,
        "timestamp": timestamp,
        "bytes_saved": bytes_saved,
        "transfer_speed": speed_text,
        "transfer_speed_mbps": speed_mbps,
        "source_file": str(path),
    }


def main():
    parser = argparse.ArgumentParser(description="Parse wget logs into CSV files.")
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    files = discover_files(args.data_dir, "*/http_test.txt")
    rows = [parse_http_file(file_path) for file_path in files]

    write_csv(
        args.out_dir / "http_summary.csv",
        rows,
        [
            "run_id",
            "target_url",
            "status",
            "command",
            "timestamp",
            "bytes_saved",
            "transfer_speed",
            "transfer_speed_mbps",
            "source_file",
        ],
    )

    print(f"Parsed {len(files)} http files")


if __name__ == "__main__":
    main()
