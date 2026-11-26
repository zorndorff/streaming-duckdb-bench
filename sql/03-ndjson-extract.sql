-- jq -r .user.screen_name
SELECT json->>'$.user.screen_name' FROM read_ndjson_objects('/dev/stdin');
