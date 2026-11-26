-- jq -c .   (json() re-parses and re-serializes; bare `SELECT json` would be a passthrough)
SELECT json(json) FROM read_ndjson_objects('/dev/stdin');
