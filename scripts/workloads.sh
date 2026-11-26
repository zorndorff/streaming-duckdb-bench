# Shared workload table, sourced by run_bench.sh and verify.sh.
# Same nine workloads as Lemire's sjq run_bench.sh; the DuckDB side of each is sql/<id>-*.sql.
#   wl ID LABEL FILE JQ_ARGS [JQ_ARGS_FOR_VERIFY]
# JQ_ARGS is a shell string (it is run through sh -c by hyperfine).
W_IDS=(); declare -A W_LABEL W_FILE W_JQ W_JQV
wl() { W_IDS+=("$1"); W_LABEL[$1]=$2; W_FILE[$1]=$3; W_JQ[$1]=$4; W_JQV[$1]=${5:-$4}; }

wl 01 "minify (-c .)"            tweets.ndjson "-c ."
wl 02 "pretty-print (.)"         tweets.ndjson "."  "--indent 4 ."
wl 03 "extract a field"          tweets.ndjson "-r .user.screen_name"
wl 04 "select and build objects" tweets.ndjson "-c 'select(.retweet_count > 100) | {id, user: .user.screen_name}'"
wl 05 "string interpolation"     tweets.ndjson "-r '\"\\(.id)\\t\\(.user.screen_name)\"'"
wl 06 "regular expression"       tweets.ndjson "-r '.text | ascii_downcase | select(test(\"rt\"))'"
wl 07 "count elements"           timeline.json "'.statuses | length'"
wl 08 "minify (-c .)"            timeline.json "-c ."
wl 09 "group_by"                 timeline.json "-c '.statuses | group_by(.user.lang) | map({lang: .[0].user.lang, n: length})'"

sql_for() { ls "$ROOT/sql/$1"-*.sql; }

# Fixed CLI flags: -no-agent so output never switches to agent markdown when
# AI_AGENT is set; -no-init so ~/.duckdbrc can't change settings.
DUCK_FLAGS="-no-agent -no-init -list -noheader"

# INPUT=file: no stdin/stdout at all. DuckDB reads the path and writes with
# COPY ... TO a file (CSV, no quoting/escaping: byte-identical to jq's output);
# jq is given the path and redirected to a file, as Lemire runs it.
# file_sql ID DATAFILE OUTFILE -> writes the COPY version of sql/ID-*.sql to stdout.
file_sql() {
  local q
  q=$(grep -v '^--' "$(sql_for "$1")" | tr '\n' ' ' | sed "s#/dev/stdin#$2#; s/; *\$//")
  printf "COPY (%s) TO '%s' (FORMAT csv, HEADER false, QUOTE '', ESCAPE '', DELIMITER '\\x1f');\n" "$q" "$3"
}

# feed FILE CMD -> a shell string that streams FILE into CMD on stdin.
#   INPUT=pipe      cat FILE | CMD   (non-seekable stdin; the default)
#   INPUT=redirect  CMD < FILE       (stdin is a seekable regular file)
feed() {
  case "${INPUT:-pipe}" in
    pipe) echo "cat $1 | $2" ;;
    redirect) echo "$2 < $1" ;;
    *) echo "feed: INPUT must be pipe or redirect" >&2; exit 2 ;;
  esac
}
