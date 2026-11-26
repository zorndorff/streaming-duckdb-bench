#!/usr/bin/env python3
"""Markdown table of mean time and GB/s (input bytes / mean, 1 GB = 1e9 B) per workload.
Usage: summarize.py RESULTS_DIR"""
import json, os, sys

out = sys.argv[1]
engines = [("jq", "jq"), ("duckdb1", "duckdb 1t"), ("duckdb", "duckdb"), ("sjq1", "sjq"), ("sjq", "sjq -P")]
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(out, "index.tsv"))]
present = [e for e in engines if any(os.path.exists(os.path.join(out, f"{r[0]}-{e[0]}.json")) for r in rows)]

def stat(rid, key, what="time"):
    p = os.path.join(out, f"{rid}-{key}.json")
    if not os.path.exists(p):
        return None
    r = json.load(open(p))["results"][0]
    if "summary" in r:  # hyperfine 2.x
        k = "time_wall_clock" if what == "time" else "memory_peak_resident"
        return r["summary"][k]["mean"]
    return r["mean"] if what == "time" else None  # hyperfine 1.x: no memory


def mean(rid, key):
    return stat(rid, key)

env = os.path.join(out, "env.txt")
if os.path.exists(env):
    print(open(env).read().replace("# ", "").strip().replace("\n", "  \n"), end="\n\n")
print("| # | workload | input | " + " | ".join(n for _, n in present) + " | duckdb vs jq |")
print("|---|---|---|" + "---|" * len(present) + "---|")
for rid, label, f, size in rows:
    size = int(size)
    cells, ts = [], {}
    for key, _ in present:
        t = mean(rid, key)
        ts[key] = t
        cells.append("–" if t is None else f"{t:.3f} s · {size / t / 1e9:.2f} GB/s")
    sp = f"{ts['jq'] / ts['duckdb']:.1f}×" if ts.get("jq") and ts.get("duckdb") else "–"
    print(f"| {rid} | {label} | {f} ({size / 1e6:.0f} MB) | " + " | ".join(cells) + f" | {sp} |")

print("\nPeak RSS (MiB, mean)\n")
print("| # | workload | input | " + " | ".join(n for _, n in present) + " |")
print("|---|---|---|" + "---|" * len(present))
for rid, label, f, size in rows:
    m = [stat(rid, k, "mem") for k, _ in present]
    print(f"| {rid} | {label} | {f} | " + " | ".join("–" if v is None else f"{v / 2**20:.0f}" for v in m) + " |")
