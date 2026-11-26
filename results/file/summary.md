2026-11-25T19:08:03-06:00 INPUT=file THREADS=32  
v2.0.0 (Cyanoptera) d54cbbe3df | jq-1.8.2 | hyperfine 2.0.0  
AMD RYZEN AI MAX+ 395 w/ Radeon 8060S x 32 | Linux 7.2.14-200.fc44.x86_64

| # | workload | input | jq | duckdb 1t | duckdb | duckdb vs jq |
|---|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson (1074 MB) | 14.806 s · 0.07 GB/s | 1.687 s · 0.64 GB/s | 0.506 s · 2.12 GB/s | 29.2× |
| 02 | pretty-print (.) | tweets.ndjson (1074 MB) | 16.303 s · 0.07 GB/s | 1.556 s · 0.69 GB/s | 0.638 s · 1.68 GB/s | 25.5× |
| 03 | extract a field | tweets.ndjson (1074 MB) | 7.016 s · 0.15 GB/s | 0.792 s · 1.36 GB/s | 0.194 s · 5.53 GB/s | 36.1× |
| 04 | select and build objects | tweets.ndjson (1074 MB) | 6.900 s · 0.16 GB/s | 0.821 s · 1.31 GB/s | 0.196 s · 5.49 GB/s | 35.3× |
| 05 | string interpolation | tweets.ndjson (1074 MB) | 7.031 s · 0.15 GB/s | 1.153 s · 0.93 GB/s | 0.260 s · 4.13 GB/s | 27.0× |
| 06 | regular expression | tweets.ndjson (1074 MB) | 15.244 s · 0.07 GB/s | 1.565 s · 0.69 GB/s | 0.275 s · 3.90 GB/s | 55.3× |
| 07 | count elements | timeline.json (841 MB) | 6.435 s · 0.13 GB/s | 2.023 s · 0.42 GB/s | 2.008 s · 0.42 GB/s | 3.2× |
| 08 | minify (-c .) | timeline.json (841 MB) | 11.196 s · 0.08 GB/s | 2.739 s · 0.31 GB/s | 2.623 s · 0.32 GB/s | 4.3× |
| 09 | group_by | timeline.json (841 MB) | 6.766 s · 0.12 GB/s | 2.067 s · 0.41 GB/s | 2.058 s · 0.41 GB/s | 3.3× |

Peak RSS (MiB, mean)

| # | workload | input | jq | duckdb 1t | duckdb |
|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson | 4 | 200 | 5012 |
| 02 | pretty-print (.) | tweets.ndjson | 4 | 228 | 5608 |
| 03 | extract a field | tweets.ndjson | 4 | 182 | 3834 |
| 04 | select and build objects | tweets.ndjson | 4 | 276 | 3871 |
| 05 | string interpolation | tweets.ndjson | 4 | 233 | 5264 |
| 06 | regular expression | tweets.ndjson | 4 | 229 | 4921 |
| 07 | count elements | timeline.json | 3263 | 4299 | 4301 |
| 08 | minify (-c .) | timeline.json | 3357 | 6077 | 5487 |
| 09 | group_by | timeline.json | 3277 | 4303 | 4305 |
