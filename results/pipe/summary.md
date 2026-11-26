2026-11-25T18:39:59-06:00 INPUT=pipe THREADS=32  
v2.0.0 (Cyanoptera) d54cbbe3df | jq-1.8.2 | hyperfine 2.0.0  
AMD RYZEN AI MAX+ 395 w/ Radeon 8060S x 32 | Linux 7.2.14-200.fc44.x86_64

| # | workload | input | jq | duckdb 1t | duckdb | duckdb vs jq |
|---|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson (1074 MB) | 14.335 s · 0.07 GB/s | 1.882 s · 0.57 GB/s | 1.255 s · 0.86 GB/s | 11.4× |
| 02 | pretty-print (.) | tweets.ndjson (1074 MB) | 15.587 s · 0.07 GB/s | 2.043 s · 0.53 GB/s | 1.304 s · 0.82 GB/s | 11.9× |
| 03 | extract a field | tweets.ndjson (1074 MB) | 6.913 s · 0.16 GB/s | 1.238 s · 0.87 GB/s | 0.660 s · 1.63 GB/s | 10.5× |
| 04 | select and build objects | tweets.ndjson (1074 MB) | 6.948 s · 0.15 GB/s | 1.280 s · 0.84 GB/s | 0.659 s · 1.63 GB/s | 10.5× |
| 05 | string interpolation | tweets.ndjson (1074 MB) | 7.105 s · 0.15 GB/s | 1.599 s · 0.67 GB/s | 0.706 s · 1.52 GB/s | 10.1× |
| 06 | regular expression | tweets.ndjson (1074 MB) | 15.231 s · 0.07 GB/s | 1.992 s · 0.54 GB/s | 0.737 s · 1.46 GB/s | 20.7× |
| 07 | count elements | timeline.json (841 MB) | 6.500 s · 0.13 GB/s | 2.431 s · 0.35 GB/s | 2.453 s · 0.34 GB/s | 2.6× |
| 08 | minify (-c .) | timeline.json (841 MB) | 11.026 s · 0.08 GB/s | 2.833 s · 0.30 GB/s | 2.834 s · 0.30 GB/s | 3.9× |
| 09 | group_by | timeline.json (841 MB) | 6.915 s · 0.12 GB/s | 2.531 s · 0.33 GB/s | 2.546 s · 0.33 GB/s | 2.7× |

Peak RSS (MiB, mean)

| # | workload | input | jq | duckdb 1t | duckdb |
|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson | 4 | 2329 | 5978 |
| 02 | pretty-print (.) | tweets.ndjson | 4 | 2668 | 6897 |
| 03 | extract a field | tweets.ndjson | 4 | 1205 | 4857 |
| 04 | select and build objects | tweets.ndjson | 4 | 1299 | 4909 |
| 05 | string interpolation | tweets.ndjson | 4 | 1250 | 6368 |
| 06 | regular expression | tweets.ndjson | 4 | 1346 | 6610 |
| 07 | count elements | timeline.json | 3263 | 5100 | 5102 |
| 08 | minify (-c .) | timeline.json | 3357 | 6285 | 6287 |
| 09 | group_by | timeline.json | 3277 | 5104 | 5106 |
