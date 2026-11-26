-- The first, slow version of workload 09 (kept to reproduce the "unnest trap").
-- Same output as sql/09-doc-group-by.sql, but unnest + GROUP BY on the single
-- 840 MB row: ~32 s vs ~2.5 s, most of it system time. Our guess (untested):
-- each chunk unnest emits drags the huge source value along.
SELECT to_json(list({'lang': lang, 'n': n} ORDER BY lang))
FROM (
  SELECT s.user.lang AS lang, count(*) AS n
  FROM (
    SELECT unnest(from_json(json, '{"statuses":[{"user":{"lang":"VARCHAR"}}]}').statuses) AS s
    FROM read_json_objects('/dev/stdin', format='unstructured', maximum_object_size=4000000000)
  )
  GROUP BY ALL
);
