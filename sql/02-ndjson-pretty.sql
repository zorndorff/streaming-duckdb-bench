-- jq .   (json_pretty indents by 4: byte-identical to `jq --indent 4 .`)
SELECT json_pretty(json) FROM read_ndjson_objects('/dev/stdin');
