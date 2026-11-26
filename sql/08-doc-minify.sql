-- jq -c .   (one large document on stdin)
SELECT json(json)
FROM read_json_objects('/dev/stdin', format='unstructured', maximum_object_size=4000000000);
