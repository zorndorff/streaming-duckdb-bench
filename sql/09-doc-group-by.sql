-- jq -c '.statuses | group_by(.user.lang) | map({lang: .[0].user.lang, n: length})'
-- Aggregates inside the list (list_histogram) instead of unnest + GROUP BY.
-- The unnest version (sql/variants/09-doc-group-by-unnest.sql) takes ~32 s, mostly
-- system time; see results/pipe-unnest/.
SELECT to_json(list_transform(
         list_sort(map_entries(list_histogram(json_extract_string(json, '$.statuses[*].user.lang')))),
         lambda e: {'lang': e.key, 'n': e.value}))
FROM read_json_objects('/dev/stdin', format='unstructured', maximum_object_size=4000000000);
