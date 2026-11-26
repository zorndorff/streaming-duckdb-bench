-- jq -r '"\(.id)\t\(.user.screen_name)"'
SELECT (json->>'$.id') || chr(9) || (json->>'$.user.screen_name')
FROM read_ndjson_objects('/dev/stdin');
