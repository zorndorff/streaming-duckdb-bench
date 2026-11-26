#!/bin/bash
# Downloads simdjson's twitter.json and builds data/full (1 GB NDJSON + ~840 MB document).
# Usage: scripts/make_data.sh [MB] [OUTDIR]   (default 1024 data/full)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
MB=${1:-1024}; OUT=${2:-$ROOT/data/full}
mkdir -p "$ROOT/data"
[ -f "$ROOT/data/twitter.json" ] || curl -fsSL -o "$ROOT/data/twitter.json" \
  https://raw.githubusercontent.com/simdjson/simdjson/master/jsonexamples/twitter.json
python3 -I "$ROOT/scripts/make_data.py" "$ROOT/data/twitter.json" "$OUT" --mb "$MB"
