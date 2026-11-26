2026-11-25T19:21:05-06:00 INPUT=pipe THREADS=32  
v2.0.0 (Cyanoptera) d54cbbe3df | jq-1.8.2 | hyperfine 2.0.0  
AMD RYZEN AI MAX+ 395 w/ Radeon 8060S x 32 | Linux 7.2.14-200.fc44.x86_64

| # | workload | input | jq | duckdb 1t | duckdb | duckdb vs jq |
|---|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson (1074 MB) | 14.335 s · 0.07 GB/s | 1.988 s · 0.54 GB/s | 0.736 s · 1.46 GB/s | 19.5× |
| 02 | pretty-print (.) | tweets.ndjson (1074 MB) | 15.587 s · 0.07 GB/s | 1.796 s · 0.60 GB/s | 0.799 s · 1.34 GB/s | 19.5× |
| 03 | extract a field | tweets.ndjson (1074 MB) | 6.913 s · 0.16 GB/s | 1.228 s · 0.87 GB/s | 0.632 s · 1.70 GB/s | 10.9× |
| 04 | select and build objects | tweets.ndjson (1074 MB) | 6.948 s · 0.15 GB/s | 1.258 s · 0.85 GB/s | 0.631 s · 1.70 GB/s | 11.0× |
| 05 | string interpolation | tweets.ndjson (1074 MB) | 7.105 s · 0.15 GB/s | 1.584 s · 0.68 GB/s | 0.676 s · 1.59 GB/s | 10.5× |
| 06 | regular expression | tweets.ndjson (1074 MB) | 15.231 s · 0.07 GB/s | 1.990 s · 0.54 GB/s | 0.694 s · 1.55 GB/s | 22.0× |
| 07 | count elements | timeline.json (841 MB) | 6.500 s · 0.13 GB/s | 2.269 s · 0.37 GB/s | 2.256 s · 0.37 GB/s | 2.9× |
| 08 | minify (-c .) | timeline.json (841 MB) | 11.026 s · 0.08 GB/s | 2.849 s · 0.30 GB/s | 2.774 s · 0.30 GB/s | 4.0× |
| 09 | group_by | timeline.json (841 MB) | 6.915 s · 0.12 GB/s | 2.329 s · 0.36 GB/s | 2.320 s · 0.36 GB/s | 3.0× |

Peak RSS (MiB, mean)

| # | workload | input | jq | duckdb 1t | duckdb |
|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson | 4 | 1209 | 5878 |
| 02 | pretty-print (.) | tweets.ndjson | 4 | 1238 | 6858 |
| 03 | extract a field | tweets.ndjson | 4 | 1201 | 4862 |
| 04 | select and build objects | tweets.ndjson | 4 | 1299 | 4917 |
| 05 | string interpolation | tweets.ndjson | 4 | 1244 | 6320 |
| 06 | regular expression | tweets.ndjson | 4 | 1224 | 5894 |
| 07 | count elements | timeline.json | 3263 | 5100 | 5102 |
| 08 | minify (-c .) | timeline.json | 3357 | 6879 | 6288 |
| 09 | group_by | timeline.json | 3277 | 5105 | 5107 |
