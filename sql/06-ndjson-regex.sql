-- jq -r '.text | ascii_downcase | select(test("rt"))'
-- note: lower() is Unicode-aware, ascii_downcase is not; they agree on this data.
SELECT t FROM (
  SELECT lower(json->>'$.text') AS t FROM read_ndjson_objects('/dev/stdin')
) WHERE regexp_matches(t, 'rt');
