# network_analysis

Analysis of a network of configured Raspberry Pi (Pi) chained nodes.

This repo contains a small, reproducible pipeline that parses collected network evidence (ping, iperf3, path traces, packet captures) into auditable CSV tables and figures.

**Author:** @Red-Dog15

## Contents (high level)

- Report: `ELEE1157_Final_Submission.md`
- Refreshed dataset / evidence snapshots: `network-analysis2/` (e.g. `20260310_153321/`, `20260317_142648/`)
- Scripts: `analysis/scripts/`
- Generated outputs: `analysis/output2/`
  - `analysis/output2/csv/` (parsed summaries)
  - `analysis/output2/tables/` (report-ready tables)
  - `analysis/output2/figures/` (plots + Wireshark screenshots)

## Evidence types parsed

- ICMP ping (RTT/loss)
- TCP iperf3 (throughput/retransmissions)
- Path traces (where tooling is available)
- PCAP inventory (deeper protocol inspection may be manual if tshark isn’t available)