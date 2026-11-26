#!/bin/bash
# Checks that each DuckDB query writes byte-identical output to jq (md5),
# fed the same way as run_bench.sh (INPUT=pipe|redirect), at 1 thread and at default threads.
# Usage: scripts/verify.sh [DATA_DIR]    (default data/full)
set -uo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
source "$ROOT/scripts/workloads.sh"
DATA=$(realpath "${1:-$ROOT/data/full}")
JQ=${JQ:-jq}; DUCKDB=${DUCKDB:-duckdb}
fail=0
for id in "${W_IDS[@]}"; do
  if [ -n "${ONLY:-}" ] && ! echo " $ONLY " | grep -q " $id "; then continue; fi
  file=$DATA/${W_FILE[$id]}; sql=$(sql_for "$id")
  want=$(sh -c "$(feed "$file" "$JQ ${W_JQV[$id]}")" | md5sum | cut -d' ' -f1)
  for t in 1 0; do
    tset=""; [ $t = 1 ] && tset="-cmd 'SET threads=1'"
    got=$(sh -c "$(feed "$file" "$DUCKDB $DUCK_FLAGS $tset -f $sql")" | md5sum | cut -d' ' -f1)
    st=OK; [ "$got" = "$want" ] || { st=DIFF; fail=1; }
    printf '%s %-26s %-14s threads=%-4s %s\n' "$id" "${W_LABEL[$id]}" "${W_FILE[$id]}" "$([ $t = 1 ] && echo 1 || echo all)" "$st"
  done
done
[ "${W_JQV[02]}" != "${W_JQ[02]}" ] && echo "note: 02 is compared against 'jq ${W_JQV[02]}' (json_pretty indents by 4)"
exit $fail
