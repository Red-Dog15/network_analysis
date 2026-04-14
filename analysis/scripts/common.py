#!/usr/bin/env python3
import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def discover_files(data_dir: Path, glob_pattern: str) -> List[Path]:
    return sorted(p for p in data_dir.glob(glob_pattern) if p.is_file())


def extract_run_id(file_path: Path) -> str:
    return file_path.parent.name


def extract_target_from_name(file_path: Path, prefix: str) -> str:
    name = file_path.stem
    if name.startswith(prefix):
        return name[len(prefix) :]
    return "unknown"


def parse_header(text: str) -> Tuple[str, str]:
    cmd = ""
    ts = ""
    for line in text.splitlines()[:6]:
        if line.lower().startswith("command:"):
            cmd = line.split(":", 1)[1].strip()
        elif line.lower().startswith("time:"):
            ts = line.split(":", 1)[1].strip()
    return cmd, ts


def strip_header(text: str) -> str:
    lines = text.splitlines()
    if len(lines) <= 3:
        return ""
    return "\n".join(lines[3:]).strip()


def has_command_not_found(text: str) -> bool:
    return "command not found" in text.lower()


def classify_status(body: str, full_text: str, ok_condition: bool) -> str:
    if ok_condition:
        return "ok"
    if has_command_not_found(full_text):
        return "tool_missing"
    if not body.strip():
        return "missing_output"
    return "command_failed"


def safe_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mbps_to_float(rate_text: str) -> float:
    if not rate_text:
        return float("nan")
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([KMG])bits/sec", rate_text)
    if not match:
        return float("nan")
    value = float(match.group(1))
    unit = match.group(2)
    factor = {"K": 0.001, "M": 1.0, "G": 1000.0}[unit]
    return value * factor
