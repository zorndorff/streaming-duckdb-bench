#!/usr/bin/env python3
"""Renders the blog post: fills {{chart:NAME}} / {{v:NAME}} placeholders in a
markdown template with inline SVG charts and numbers computed from results/.

Usage: build_post.py TEMPLATE.md OUT.md
Charts follow the PaperMod theme: text/surfaces use its CSS vars (--primary,
--secondary, --border, --theme), series colours switch under body.dark.
"""
import json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
NDJSON_BYTES = 1073745346


def load(mode):
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(RES, mode, "index.tsv"))]
    out = {}
    for rid, label, f, size in rows:
        out[rid] = {"label": label, "file": f, "size": int(size)}
        for key in ("jq", "duckdb1", "duckdb"):
            p = os.path.join(RES, mode, f"{rid}-{key}.json")
            if os.path.exists(p):
                s = json.load(open(p))["results"][0]["summary"]
                out[rid][key] = s["time_wall_clock"]["mean"]
                out[rid][key + "_mem"] = s["memory_peak_resident"]["mean"]
    return out


PIPE, REDIR, UNNEST = load("pipe"), load("redirect"), load("pipe-unnest")
SWEEP = [l.split() for l in open(os.path.join(RES, "threads_sweep.txt")).read().splitlines()[1:]]

STYLE = """<style>
.bv{--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;font:13px/1.35 system-ui,-apple-system,Segoe UI,sans-serif;margin:1.6em 0;color:var(--primary)}
.dark .bv{--s1:#3987e5;--s2:#d95926;--s3:#199e70}
.bv svg{width:100%;height:auto;display:block;overflow:visible}
.bv .t{fill:var(--primary)}.bv .m{fill:var(--secondary)}.bv .g{stroke:var(--border);stroke-width:1}
.bv .cap{color:var(--secondary);font-size:12.5px;margin-top:.4em}
.bv .lg{display:flex;gap:1.1em;flex-wrap:wrap;margin:.2em 0 .5em;font-size:12.5px;color:var(--secondary)}
.bv .lg i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:.35em;vertical-align:-1px}
.bv .tabs{display:flex;gap:.4em;margin-bottom:.4em}
.bv .tabs button{font:inherit;font-size:12.5px;padding:.3em .8em;border-radius:99px;border:1px solid var(--border);background:var(--theme);color:var(--secondary);cursor:pointer}
.bv .tabs button[aria-pressed=true]{background:var(--primary);color:var(--theme);border-color:var(--primary)}
.bv rect.hit:hover+rect,.bv rect:hover{opacity:.82}
.bv-hero{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:1.6em 0}
.bv-hero div{border:1px solid var(--border);border-radius:12px;padding:14px 14px 12px;background:var(--entry)}
.bv-hero b{display:block;font-size:30px;line-height:1.05;letter-spacing:-.02em;color:var(--primary);font-variant-numeric:tabular-nums}
.bv-hero span{display:block;font-size:12.5px;color:var(--secondary);margin-top:6px}
.bv table{font-size:12.5px;font-variant-numeric:tabular-nums}
</style>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gbps(d, rid, key):
    return d[rid]["size"] / d[rid][key] / 1e9


SERIES = [("jq", "jq 1.8.2", "--s1"), ("duckdb1", "DuckDB, 1 thread", "--s2"), ("duckdb", "DuckDB, 32 threads", "--s3")]


def legend(items):
    return '<div class="lg">' + "".join(f'<span><i style="background:var({c})"></i>{esc(n)}</span>' for n, c in items) + "</div>"


def bars_svg(d, xmax):
    """Grouped horizontal bars: GB/s per workload, 3 series, direct value labels."""
    W, L, R = 720, 168, 64
    bh, gap, grp = 9, 2, 14
    ids = sorted(d)
    H = 24 + len(ids) * (3 * bh + 2 * gap + grp)
    sx = lambda v: L + (W - L - R) * v / xmax
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Throughput in GB/s per workload">']
    for t in range(0, int(xmax) + 1):
        x = sx(t)
        o.append(f'<line class="g" x1="{x:.1f}" x2="{x:.1f}" y1="14" y2="{H - 4}"/>'
                 f'<text class="m" x="{x:.1f}" y="10" text-anchor="middle" font-size="11">{t} GB/s</text>')
    y = 24
    for rid in ids:
        r = d[rid]
        doc = " (1 doc)" if r["file"] == "timeline.json" else ""
        o.append(f'<text class="t" x="{L - 10}" y="{y + 1.5 * bh + gap + 4}" text-anchor="end">{esc(r["label"])}{doc}</text>')
        for key, name, col in SERIES:
            v = gbps(d, rid, key)
            w = max(sx(v) - L, 2)
            o.append(f'<rect x="{L}" y="{y}" width="{w:.1f}" height="{bh}" rx="2" fill="var({col})">'
                     f'<title>{esc(name)} · {esc(r["label"])}: {v:.2f} GB/s ({r[key]:.3f} s)</title></rect>')
            o.append(f'<text class="m" x="{L + w + 5:.1f}" y="{y + bh - 1}" font-size="10.5">{v:.2f}</text>')
            y += bh + gap
        y += grp - gap
    o.append("</svg>")
    return "".join(o)


def chart_bars():
    xmax = math.ceil(max(gbps(REDIR, r, "duckdb") for r in REDIR))
    lg = legend([(n, c) for _, n, c in SERIES])
    return f'''<div class="bv" id="bv-bars">
<div class="tabs" role="group" aria-label="input mode">
<button aria-pressed="true" data-m="pipe">pipe: cat file | duckdb</button>
<button aria-pressed="false" data-m="redirect">redirect: duckdb &lt; file</button>
</div>{lg}
<div data-p="pipe">{bars_svg(PIPE, xmax)}</div>
<div data-p="redirect" hidden>{bars_svg(REDIR, xmax)}</div>
<div class="cap">Throughput = input bytes ÷ mean wall time (hyperfine, 3 runs of jq, 10 of DuckDB). Higher is better. Same scale on both tabs.</div>
<script>(function(){{var r=document.getElementById("bv-bars");r.querySelectorAll("button").forEach(function(b){{b.onclick=function(){{r.querySelectorAll("button").forEach(function(x){{x.setAttribute("aria-pressed",x===b)}});r.querySelectorAll("[data-p]").forEach(function(p){{p.hidden=p.dataset.p!==b.dataset.m}})}}}})}})();</script>
</div>'''


def chart_threads():
    W, H, L, R, T, B = 720, 270, 56, 90, 26, 34
    pts = {"pipe": [], "redirect": []}
    for t, mode, secs, kb in SWEEP:
        pts[mode].append((int(t), NDJSON_BYTES / float(secs) / 1e9, int(kb)))
    ymax = 7
    sx = lambda t: L + (W - L - R) * math.log2(t) / 5
    sy = lambda v: T + (H - T - B) * (1 - v / ymax)
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="DuckDB throughput vs threads, pipe vs redirect">']
    for v in range(0, ymax + 1):
        o.append(f'<line class="g" x1="{L}" x2="{W - R}" y1="{sy(v):.1f}" y2="{sy(v):.1f}"/>'
                 f'<text class="m" x="{L - 8}" y="{sy(v) + 4:.1f}" text-anchor="end" font-size="11">{v}</text>')
    for t in (1, 2, 4, 8, 16, 32):
        o.append(f'<text class="m" x="{sx(t):.1f}" y="{H - 14}" text-anchor="middle" font-size="11">{t}</text>')
    o.append(f'<text class="m" x="{(L + W - R) / 2}" y="{H - 1}" text-anchor="middle" font-size="11">threads (SET threads=N)</text>')
    o.append(f'<text class="m" x="{L - 8}" y="{T - 4}" text-anchor="end" font-size="11">GB/s</text>')
    for mode, dash, name in (("redirect", "", "&lt; file"), ("pipe", "6 5", "cat |")):
        p = pts[mode]
        d = " ".join(f"{'M' if i == 0 else 'L'}{sx(t):.1f},{sy(v):.1f}" for i, (t, v, _) in enumerate(p))
        o.append(f'<path d="{d}" fill="none" stroke="var(--s3)" stroke-width="2" stroke-dasharray="{dash}"/>')
        for t, v, kb in p:
            o.append(f'<circle cx="{sx(t):.1f}" cy="{sy(v):.1f}" r="4.5" fill="var(--s3)" stroke="var(--theme)" stroke-width="2">'
                     f'<title>{mode}, {t} threads: {v:.2f} GB/s, peak RSS {kb / 1024:.0f} MiB</title></circle>')
        t, v, _ = p[-1]
        o.append(f'<text class="t" x="{sx(t) + 10:.1f}" y="{sy(v) + 4:.1f}" font-size="12">{name}</text>')
    best = max(pts["pipe"], key=lambda x: x[1])
    o.append(f'<text class="m" x="{sx(best[0]):.1f}" y="{sy(best[1]) - 12:.1f}" text-anchor="middle" font-size="11">pipe peaks at {best[0]} threads</text>')
    o.append("</svg>")
    return ('<div class="bv">' + "".join(o) +
            '<div class="cap">Workload 03 (<code>.user.screen_name</code>) on the 1 GB NDJSON file, best of 3 runs per point. '
            'Solid: stdin redirected from the file. Dashed: stdin is a real pipe.</div></div>')


def chart_unnest():
    W, L, R = 720, 230, 70
    jq = PIPE["09"]["jq"]
    rows = [("jq 1.8.2", jq, "--s1", ""),
            ("DuckDB: unnest + GROUP BY", UNNEST["09"]["duckdb"], "--s3", "url(#bv-hatch)"),
            ("DuckDB: list_histogram", PIPE["09"]["duckdb"], "--s3", "")]
    xmax = 35
    sx = lambda v: L + (W - L - R) * v / xmax
    H = 24 + len(rows) * 30
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="group_by on the 840 MB document: seconds">',
         '<defs><pattern id="bv-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<rect width="6" height="6" fill="var(--s3)"/><line x1="0" y1="0" x2="0" y2="6" stroke="var(--theme)" stroke-width="2.4"/></pattern></defs>']
    for t in range(0, xmax + 1, 5):
        o.append(f'<line class="g" x1="{sx(t):.1f}" x2="{sx(t):.1f}" y1="14" y2="{H - 4}"/>'
                 f'<text class="m" x="{sx(t):.1f}" y="10" text-anchor="middle" font-size="11">{t} s</text>')
    y = 24
    for name, v, col, fill in rows:
        o.append(f'<text class="t" x="{L - 10}" y="{y + 13}" text-anchor="end">{esc(name)}</text>'
                 f'<rect x="{L}" y="{y}" width="{sx(v) - L:.1f}" height="18" rx="3" fill="{fill or f"var({col})"}"><title>{esc(name)}: {v:.2f} s</title></rect>'
                 f'<text class="t" x="{sx(v) + 6:.1f}" y="{y + 13}" font-size="12">{v:.1f} s</text>')
        y += 30
    o.append("</svg>")
    return ('<div class="bv">' + "".join(o) +
            '<div class="cap"><code>.statuses | group_by(.user.lang)</code> on the single 840 MB document, piped in. Lower is better. Same output, byte for byte.</div></div>')


def chart_hero():
    r = REDIR["03"]
    tiles = [
        (f'{gbps(REDIR, "03", "duckdb"):.1f} GB/s', "pull one field out of 1 GB of NDJSON (stdin from file)"),
        (f'{r["jq"] / r["duckdb"]:.1f}×', "faster than jq on that same job"),
        (f'{gbps(PIPE, "03", "duckdb"):.2f} GB/s', "the same query through a real <code>cat |</code> pipe"),
        (f'{PIPE["03"]["duckdb_mem"] / 2**30:.1f} GiB', f'peak memory for that pipe run (jq: {PIPE["03"]["jq_mem"] / 2**20:.0f} MiB)'),
    ]
    return '<div class="bv-hero">' + "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in tiles) + "</div>"


def table():
    h = "| workload | jq | pipe 1t | pipe 32t | pipe vs jq | redirect 1t | redirect 32t | redirect vs jq |\n|---|---|---|---|---|---|---|---|\n"
    for rid in sorted(PIPE):
        p, r = PIPE[rid], REDIR[rid]
        doc = " (doc)" if p["file"] == "timeline.json" else ""
        h += (f'| {p["label"]}{doc} | {p["jq"]:.2f} s | {p["duckdb1"]:.2f} s | {p["duckdb"]:.2f} s | {p["jq"] / p["duckdb"]:.1f}× '
              f'| {r["duckdb1"]:.2f} s | {r["duckdb"]:.2f} s | {r["jq"] / r["duckdb"]:.1f}× |\n')
    return h


def mem_table():
    h = "| workload | jq | DuckDB 1t, pipe | DuckDB 32t, pipe | DuckDB 1t, redirect | DuckDB 32t, redirect |\n|---|---|---|---|---|---|\n"
    mib = lambda b: f"{b / 2**20:,.0f} MiB"
    for rid in ("03", "06", "08"):
        p, r = PIPE[rid], REDIR[rid]
        doc = " (doc)" if p["file"] == "timeline.json" else ""
        h += f'| {rid} {p["label"]}{doc} | {mib(p["jq_mem"])} | {mib(p["duckdb1_mem"])} | {mib(p["duckdb_mem"])} | {mib(r["duckdb1_mem"])} | {mib(r["duckdb_mem"])} |\n'
    return h


def values():
    v = {}
    for rid in PIPE:
        for mode, d in (("pipe", PIPE), ("redir", REDIR)):
            for key in ("jq", "duckdb1", "duckdb"):
                v[f"{mode}.{rid}.{key}.s"] = f"{d[rid][key]:.2f}"
                v[f"{mode}.{rid}.{key}.gbps"] = f"{gbps(d, rid, key):.2f}"
            v[f"{mode}.{rid}.x"] = f"{d[rid]['jq'] / d[rid]['duckdb']:.1f}"
            v[f"{mode}.{rid}.x1"] = f"{d[rid]['jq'] / d[rid]['duckdb1']:.1f}"
    nd = [r for r in PIPE if PIPE[r]["file"] == "tweets.ndjson"]
    x1 = [PIPE[r]["jq"] / PIPE[r]["duckdb1"] for r in nd]
    v["pipe.nd.x1.min"], v["pipe.nd.x1.max"] = f"{min(x1):.1f}", f"{max(x1):.1f}"
    v["unnest.09.s"] = f'{UNNEST["09"]["duckdb"]:.1f}'
    return v


def main():
    src, dst = sys.argv[1], sys.argv[2]
    s = open(src).read()
    charts = {"style": STYLE, "hero": chart_hero(), "bars": chart_bars(), "threads": chart_threads(),
              "unnest": chart_unnest(), "table": table(), "mem": mem_table()}
    vals = values()
    s = re.sub(r"\{\{chart:(\w+)\}\}", lambda m: charts[m.group(1)], s)
    s = re.sub(r"\{\{v:([\w.]+)\}\}", lambda m: vals[m.group(1)], s)
    left = re.findall(r"\{\{[^}]*\}\}", s)
    if left:
        sys.exit(f"unfilled placeholders: {left}")
    open(dst, "w").write(s)


if __name__ == "__main__":
    main()
