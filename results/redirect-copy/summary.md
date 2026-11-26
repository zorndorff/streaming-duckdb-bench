2026-11-25T19:28:20-06:00 INPUT=redirect THREADS=32  
v2.0.0 (Cyanoptera) d54cbbe3df | jq-1.8.2 | hyperfine 2.0.0  
AMD RYZEN AI MAX+ 395 w/ Radeon 8060S x 32 | Linux 7.2.14-200.fc44.x86_64

| # | workload | input | jq | duckdb 1t | duckdb | duckdb vs jq |
|---|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson (1074 MB) | 14.189 s · 0.08 GB/s | 1.564 s · 0.69 GB/s | 0.318 s · 3.38 GB/s | 44.7× |
| 02 | pretty-print (.) | tweets.ndjson (1074 MB) | 15.519 s · 0.07 GB/s | 1.365 s · 0.79 GB/s | 0.361 s · 2.97 GB/s | 42.9× |
| 03 | extract a field | tweets.ndjson (1074 MB) | 6.864 s · 0.16 GB/s | 0.797 s · 1.35 GB/s | 0.196 s · 5.47 GB/s | 35.0× |
| 04 | select and build objects | tweets.ndjson (1074 MB) | 6.878 s · 0.16 GB/s | 0.837 s · 1.28 GB/s | 0.200 s · 5.36 GB/s | 34.3× |
| 05 | string interpolation | tweets.ndjson (1074 MB) | 7.138 s · 0.15 GB/s | 1.157 s · 0.93 GB/s | 0.261 s · 4.12 GB/s | 27.4× |
| 06 | regular expression | tweets.ndjson (1074 MB) | 15.195 s · 0.07 GB/s | 1.576 s · 0.68 GB/s | 0.268 s · 4.00 GB/s | 56.6× |
| 07 | count elements | timeline.json (841 MB) | 6.547 s · 0.13 GB/s | 2.008 s · 0.42 GB/s | 2.067 s · 0.41 GB/s | 3.2× |
| 08 | minify (-c .) | timeline.json (841 MB) | 11.025 s · 0.08 GB/s | 2.639 s · 0.32 GB/s | 2.520 s · 0.33 GB/s | 4.4× |
| 09 | group_by | timeline.json (841 MB) | 6.956 s · 0.12 GB/s | 2.094 s · 0.40 GB/s | 2.101 s · 0.40 GB/s | 3.3× |

Peak RSS (MiB, mean)

| # | workload | input | jq | duckdb 1t | duckdb |
|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson | 4 | 202 | 4820 |
| 02 | pretty-print (.) | tweets.ndjson | 4 | 227 | 5344 |
| 03 | extract a field | tweets.ndjson | 4 | 182 | 3833 |
| 04 | select and build objects | tweets.ndjson | 4 | 275 | 3882 |
| 05 | string interpolation | tweets.ndjson | 4 | 233 | 5267 |
| 06 | regular expression | tweets.ndjson | 4 | 229 | 4916 |
| 07 | count elements | timeline.json | 3263 | 4299 | 4301 |
| 08 | minify (-c .) | timeline.json | 3358 | 6077 | 5487 |
| 09 | group_by | timeline.json | 3277 | 4303 | 4305 |
