-- jq '.statuses | length'   (one large document on stdin)
SELECT json_array_length(json, '$.statuses')
FROM read_json_objects('/dev/stdin', format='unstructured', maximum_object_size=4000000000);
