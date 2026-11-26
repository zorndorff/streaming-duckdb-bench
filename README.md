# jq vs DuckDB 2.0 CLI: streaming JSON filters (stdin → stdout)

This replicates the benchmark from Lemire's post
[Command-line JSON filtering at 20 GB/s](https://lemire.me/blog/2026/11/25/command-line-json-filtering-at-20-gb-s/)
([his scripts](https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/tree/master/2026/11/sjq)).
It uses the same nine jq workloads and the same inputs, with the DuckDB 2.0 CLI in place of sjq.
Lemire passes the file as an argument. Here every engine reads the input **from stdin** and writes the results to stdout.

## Run

```bash
scripts/make_data.sh                 # data/full: tweets.ndjson (1 GB, 230,138 lines) + timeline.json (840 MB, one doc)
scripts/verify.sh                    # md5: every DuckDB query == jq output, 1 thread and all threads
scripts/run_bench.sh                 # hyperfine -> results/pipe/{NN-engine.json,index.tsv,summary.md}
INPUT=redirect scripts/run_bench.sh  # same, with `cmd < file` instead of `cat file | cmd`
```

For a quick pass, run `scripts/make_data.sh 64 data/small`, then `scripts/run_bench.sh data/small results/smoke`.

You need `jq`, `duckdb` (v2.0), `hyperfine` (2.x) and `python3`.

### Knobs (environment variables)

| var | meaning |
|---|---|
| `INPUT` | `pipe` (default): `cat file \| cmd`, a non-seekable stream. `redirect`: `cmd < file`, where stdin is a seekable file. |
| `THREADS` | threads for the `duckdb` row (default `nproc`). The `duckdb 1t` row always uses `SET threads=1`. |
| `SJQ` | path to an sjq binary. Adds `sjq` and `sjq -P` rows for a direct comparison. |
| `ONLY`, `SKIP_JQ`, `RUNS`, `RUNS_JQ`, `PIN` | same meaning as in Lemire's script. `PIN` is a prefix such as `taskset -c 2` for the 1-thread runs. |
| `JQ`, `DUCKDB`, `HYPERFINE` | binary paths |

## Layout

- `scripts/workloads.sh`: the workload table (id, label, input, jq filter) and the `feed` helper for pipe or redirect.
- `sql/NN-*.sql`: the DuckDB side of each workload. Each file reads `/dev/stdin`.
- `sql/variants/`: alternatives discussed in the write-up. `09-doc-group-by-unnest.sql` is the slow unnest version. `06-ndjson-regex-re2.sql` uses `'(rt)'`, which stops DuckDB from rewriting the regex into `contains()`.
- `scripts/run_bench.sh`, `scripts/verify.sh`, `scripts/summarize.py`: timing, the correctness check, and the GB/s and peak-memory tables. GB/s is input bytes divided by mean wall time, with 1 GB = 10⁹ bytes.
- `scripts/build_post.py` and `post/`: renders the blog post and its inline SVG charts from `results/`.

## How the DuckDB side works

- **NDJSON:** `read_ndjson_objects('/dev/stdin')` returns one raw `JSON` value per line, and the `->>` and `json_*` functions pull out only what the query needs. This is about 5× faster than `read_json(...)` with schema inference or explicit `columns=`, and is the DuckDB counterpart of sjq's "parse only what the filter needs".
- **Single document:** `read_json_objects('/dev/stdin', format='unstructured', maximum_object_size=4000000000)` reads the whole 840 MB document as one value.
- **group_by:** `list_histogram(json_extract_string(json, '$.statuses[*].user.lang'))` aggregates inside the list and never unnests (2.5 s). Two unnest versions went badly:
  - `unnest(from_json(...).statuses)` + `GROUP BY` gives the same output but takes **32 s**, mostly system time, slower than jq. It is kept as `sql/variants/09-doc-group-by-unnest.sql`, with timings in `results/pipe-unnest/`. Our guess, untested, is that every chunk `unnest` emits carries the 840 MB source value.
  - `unnest(json_extract(json,'$.statuses[*]'))` ran out of memory at 100 GiB on a 50 MB document.
- **CLI flags:** the runs use `-no-agent -no-init -list -noheader`. DuckDB 2.0 switches to an "agent" markdown output when `AI_AGENT` is set and stdout isn't a terminal, and `-no-agent` stops that.

## Caveats on equivalence

`verify.sh` checks that the output matches jq byte for byte. Three workloads need qualifying:

- **02 pretty-print:** `json_pretty` indents by 4 spaces. It is byte-identical to `jq --indent 4 .`, not to `jq .`, so it writes more whitespace than jq. The benchmark still times plain `jq .`.
- **01 and 08 minify:** these use `json(json)`, which parses and re-serializes. A bare `SELECT json` would be a passthrough, and only matches because the input is already compact.
- **06 regex:** `lower()` is Unicode-aware, while jq's `ascii_downcase` is not. They give the same result on this data.

At 64 MB, process startup and the `cat` pipe dominate, so quote throughput only from the 1 GB runs.

## Results

The full tables, with peak RSS, are in `results/pipe/summary.md` and `results/redirect/summary.md`.
These numbers come from an AMD Ryzen AI MAX+ 395 (32 threads) running Linux 7.2, jq 1.8.2, DuckDB v2.0.0 and hyperfine 2.0.

| workload | jq | DuckDB 32t, pipe | DuckDB 32t, redirect |
|---|---|---|---|
| extract a field (1 GB NDJSON) | 6.91 s · 0.16 GB/s | 0.66 s · 1.63 GB/s (10.5×) | 0.19 s · 5.60 GB/s (35.8×) |
| regex (1 GB NDJSON) | 15.23 s | 0.74 s (20.7×) | 0.66 s (23.1×) |
| group_by (840 MB document) | 6.92 s | 2.55 s (2.7×) | 2.24 s (3.1×) |

Findings:

- **The pipe is the ceiling.** `cat | cat` moves 6.7 GB/s, but DuckDB reading a non-seekable `/dev/stdin` tops out around 4 threads at about 2.4 GB/s, then slows down. With `< file` it scales to 16 threads. See `results/threads_sweep.txt`.
- **It is not bounded-memory streaming.** jq peaks at 4 MB. DuckDB peaks between 180 MiB and 6.7 GiB, and through a pipe on 1 thread, about the size of the input. `| head -1` still reads everything. `COPY … TO '/dev/stdout'` and `preserve_insertion_order=false` don't change that.
- **Single document:** a 2.6–4.3× win with no thread scaling. Avoid `unnest` on the single huge row: 32 s against 2.5 s.
- **Regex:** DuckDB rewrites `regexp_matches(t,'rt')` to `contains()`. The real-RE2 variant was faster still: 1.07 s on 1 thread and 0.45 s on 32, with a redirect (`results/variants/`).
- Every query is md5-identical to jq in both input modes (`results/verify-redirect.txt`).
