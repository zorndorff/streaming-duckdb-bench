#!/bin/bash
# Times jq vs the DuckDB CLI (1 thread and default threads) on JSON streamed
# stdin -> stdout, with hyperfine. Modelled on Lemire's sjq run_bench.sh.
#
# Usage: scripts/run_bench.sh [DATA_DIR] [RESULTS_DIR]
#   defaults: data/full  results/<INPUT>
#
# Environment:
#   JQ, DUCKDB, HYPERFINE   binaries (default: from PATH)
#   SJQ                     optional sjq binary; adds "sjq" and "sjq -P" rows
#   INPUT                   pipe (default) | redirect   -- see feed() in workloads.sh
#   THREADS                 thread count for the "duckdb" row (default: all cores)
#   ONLY                    workload ids to run, e.g. "07 08 09"
#   SKIP_JQ=1               keep existing jq results, time the others only
#   RUNS_JQ, RUNS           hyperfine runs (default 3 for jq, 10 for the others)
#   PIN                     command prefix for single-threaded runs, e.g. "taskset -c 2"
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
source "$ROOT/scripts/workloads.sh"
DATA=$(realpath "${1:-$ROOT/data/full}")
OUT=$(realpath -m "${2:-$ROOT/results/${INPUT:-pipe}}")
JQ=${JQ:-jq}; DUCKDB=${DUCKDB:-duckdb}; HF=${HYPERFINE:-hyperfine}
RUNS_JQ=${RUNS_JQ:-3}; RUNS=${RUNS:-10}; PIN=${PIN:-}
THREADS=${THREADS:-$(nproc)}
mkdir -p "$OUT"

for f in tweets.ndjson timeline.json; do
  [ -f "$DATA/$f" ] || { echo "missing $DATA/$f -- run scripts/make_data.sh" >&2; exit 1; }
done

hf() { # hf NAME OUTJSON RUNS CMD
  "$HF" --shell=default --style basic --warmup 1 --runs "$3" --export-json "$2" -n "$1" "$4"
}

{
  echo "# $(date -Iseconds) INPUT=${INPUT:-pipe} THREADS=$THREADS"
  echo "# $("$DUCKDB" -version 2>&1 | tail -1) | $("$JQ" --version) | $("$HF" --version)"
  echo "# $(lscpu | sed -n 's/^Model name: *//p') x $(nproc) | $(uname -sr)"
} > "$OUT/env.txt"

rm -f "$OUT/index.tsv.new"
for id in "${W_IDS[@]}"; do
  file=$DATA/${W_FILE[$id]}
  printf '%s\t%s\t%s\t%s\n' "$id" "${W_LABEL[$id]}" "${W_FILE[$id]}" "$(stat -c %s "$file")" >> "$OUT/index.tsv.new"
  if [ -n "${ONLY:-}" ] && ! echo " $ONLY " | grep -q " $id "; then continue; fi
  sql=$(sql_for "$id")
  echo "=== $id ${W_LABEL[$id]} (${W_FILE[$id]})"
  if [ "${SKIP_JQ:-}" != 1 ]; then
    hf "jq" "$OUT/$id-jq.json" "$RUNS_JQ" "$(feed "$file" "$PIN $JQ ${W_JQ[$id]}") > /dev/null"
  fi
  hf "duckdb 1t" "$OUT/$id-duckdb1.json" "$RUNS" \
    "$(feed "$file" "$PIN $DUCKDB $DUCK_FLAGS -cmd 'SET threads=1' -f $sql") > /dev/null"
  hf "duckdb" "$OUT/$id-duckdb.json" "$RUNS" \
    "$(feed "$file" "$DUCKDB $DUCK_FLAGS -cmd 'SET threads=$THREADS' -f $sql") > /dev/null"
  if [ -n "${SJQ:-}" ]; then
    hf "sjq" "$OUT/$id-sjq1.json" "$RUNS" "$(feed "$file" "$PIN $SJQ ${W_JQ[$id]}") > /dev/null"
    hf "sjq -P" "$OUT/$id-sjq.json" "$RUNS" "$(feed "$file" "$SJQ -P ${W_JQ[$id]}") > /dev/null"
  fi
done
mv "$OUT/index.tsv.new" "$OUT/index.tsv"
python3 -I "$ROOT/scripts/summarize.py" "$OUT" | tee "$OUT/summary.md"
