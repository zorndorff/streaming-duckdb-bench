-- jq -c 'select(.retweet_count > 100) | {id, user: .user.screen_name}'
SELECT json_object('id', json->'$.id', 'user', json->>'$.user.screen_name')
FROM read_ndjson_objects('/dev/stdin')
WHERE (json->>'$.retweet_count')::BIGINT > 100;
