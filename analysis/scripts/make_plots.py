#!/usr/bin/env python3
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_ping_plots(csv_dir: Path, fig_dir: Path):
    ping_file = csv_dir / "ping_summary.csv"
    if not ping_file.exists():
        return
    df = pd.read_csv(ping_file)
    df = df[df["status"] == "ok"].copy()
    if df.empty:
        return

    df["rtt_avg_ms"] = pd.to_numeric(df["rtt_avg_ms"], errors="coerce")
    df["packet_loss_pct"] = pd.to_numeric(df["packet_loss_pct"], errors="coerce")

    rtt = df.groupby("target", as_index=False)["rtt_avg_ms"].mean().sort_values("rtt_avg_ms")
    if not rtt.empty:
        plt.figure(figsize=(10, 5))
        plt.bar(rtt["target"], rtt["rtt_avg_ms"])
        plt.title("Average Ping RTT by Target")
        plt.xlabel("Target")
        plt.ylabel("RTT (ms)")
        plt.xticks(rotation=35, ha="right")
        plt.tight_layout()
        plt.savefig(fig_dir / "ping_rtt_avg_by_target.png", dpi=150)
        plt.close()

    loss = df.groupby("target", as_index=False)["packet_loss_pct"].mean().sort_values("packet_loss_pct")
    if not loss.empty:
        plt.figure(figsize=(10, 5))
        plt.bar(loss["target"], loss["packet_loss_pct"])
        plt.title("Packet Loss by Target")
        plt.xlabel("Target")
        plt.ylabel("Packet Loss (%)")
        # Keep a true percentage axis for readability even when all values are zero.
        plt.ylim(0, 100)
        plt.yticks(range(0, 101, 20))
        plt.xticks(rotation=35, ha="right")
        plt.tight_layout()
        plt.savefig(fig_dir / "ping_packet_loss_by_target.png", dpi=150)
        plt.close()


def save_iperf_plot(csv_dir: Path, fig_dir: Path):
    iperf_file = csv_dir / "iperf_summary.csv"
    if not iperf_file.exists():
        return
    df = pd.read_csv(iperf_file)
    df = df[df["status"] == "ok"].copy()
    if df.empty:
        return

    df["receiver_rate_mbps"] = pd.to_numeric(df["receiver_rate_mbps"], errors="coerce")
    agg = (
        df.groupby("target", as_index=False)["receiver_rate_mbps"]
        .mean()
        .sort_values("receiver_rate_mbps", ascending=False)
    )

    if agg.empty:
        return

    plt.figure(figsize=(10, 5))
    plt.bar(agg["target"], agg["receiver_rate_mbps"])
    plt.title("Average Iperf Receiver Throughput by Target")
    plt.xlabel("Target")
    plt.ylabel("Throughput (Mbps)")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(fig_dir / "iperf_receiver_throughput_by_target.png", dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate coursework plots from parsed CSVs.")
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    csv_dir = args.out_dir / "csv"
    fig_dir = args.out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    save_ping_plots(csv_dir, fig_dir)
    save_iperf_plot(csv_dir, fig_dir)

    print("Plot generation complete")


if __name__ == "__main__":
    main()
