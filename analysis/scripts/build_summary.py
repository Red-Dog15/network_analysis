#!/usr/bin/env python3
import argparse
from collections import Counter
from pathlib import Path

from common import load_csv, write_csv


def main():
    parser = argparse.ArgumentParser(description="Build merged and quality summary tables.")
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    csv_dir = args.out_dir / "csv"
    table_dir = args.out_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)

    ping = load_csv(csv_dir / "ping_summary.csv")
    iperf = load_csv(csv_dir / "iperf_summary.csv")
    path = load_csv(csv_dir / "path_summary.csv")
    http = load_csv(csv_dir / "http_summary.csv")
    pcap = load_csv(csv_dir / "pcap_summary.csv")

    merged_rows = []
    for row in ping:
        merged_rows.append(
            {
                "run_id": row.get("run_id", ""),
                "target": row.get("target", ""),
                "test_type": "ping",
                "status": row.get("status", ""),
                "metric_1": row.get("rtt_avg_ms", ""),
                "metric_2": row.get("packet_loss_pct", ""),
                "source_file": row.get("source_file", ""),
            }
        )

    for row in iperf:
        merged_rows.append(
            {
                "run_id": row.get("run_id", ""),
                "target": row.get("target", ""),
                "test_type": "iperf",
                "status": row.get("status", ""),
                "metric_1": row.get("receiver_rate_mbps", ""),
                "metric_2": row.get("sender_retransmits", ""),
                "source_file": row.get("source_file", ""),
            }
        )

    for row in path:
        merged_rows.append(
            {
                "run_id": row.get("run_id", ""),
                "target": row.get("target", ""),
                "test_type": "path",
                "status": row.get("status", ""),
                "metric_1": row.get("hop_count", ""),
                "metric_2": row.get("latency_avg_ms", ""),
                "source_file": row.get("source_file", ""),
            }
        )

    for row in http:
        merged_rows.append(
            {
                "run_id": row.get("run_id", ""),
                "target": row.get("target_url", ""),
                "test_type": "http",
                "status": row.get("status", ""),
                "metric_1": row.get("transfer_speed_mbps", ""),
                "metric_2": row.get("bytes_saved", ""),
                "source_file": row.get("source_file", ""),
            }
        )

    for row in pcap:
        merged_rows.append(
            {
                "run_id": row.get("run_id", ""),
                "target": row.get("interface", ""),
                "test_type": "pcap",
                "status": row.get("status", ""),
                "metric_1": row.get("packet_count", ""),
                "metric_2": row.get("size_bytes", ""),
                "source_file": row.get("source_file", ""),
            }
        )

    write_csv(
        csv_dir / "analysis_summary.csv",
        merged_rows,
        ["run_id", "target", "test_type", "status", "metric_1", "metric_2", "source_file"],
    )

    status_counter = Counter(row.get("status", "unknown") for row in merged_rows)
    quality_rows = [{"status": k, "count": v} for k, v in sorted(status_counter.items())]

    write_csv(table_dir / "data_quality.csv", quality_rows, ["status", "count"])

    print("Built analysis_summary.csv and data_quality.csv")


if __name__ == "__main__":
    main()
