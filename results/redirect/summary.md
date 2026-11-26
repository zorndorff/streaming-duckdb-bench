2026-11-25T18:41:18-06:00 INPUT=redirect THREADS=32  
v2.0.0 (Cyanoptera) d54cbbe3df | jq-1.8.2 | hyperfine 2.0.0  
AMD RYZEN AI MAX+ 395 w/ Radeon 8060S x 32 | Linux 7.2.14-200.fc44.x86_64

| # | workload | input | jq | duckdb 1t | duckdb | duckdb vs jq |
|---|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson (1074 MB) | 14.189 s · 0.08 GB/s | 1.421 s · 0.76 GB/s | 0.959 s · 1.12 GB/s | 14.8× |
| 02 | pretty-print (.) | tweets.ndjson (1074 MB) | 15.519 s · 0.07 GB/s | 1.596 s · 0.67 GB/s | 1.091 s · 0.98 GB/s | 14.2× |
| 03 | extract a field | tweets.ndjson (1074 MB) | 6.864 s · 0.16 GB/s | 0.786 s · 1.37 GB/s | 0.192 s · 5.60 GB/s | 35.8× |
| 04 | select and build objects | tweets.ndjson (1074 MB) | 6.878 s · 0.16 GB/s | 0.821 s · 1.31 GB/s | 0.195 s · 5.50 GB/s | 35.2× |
| 05 | string interpolation | tweets.ndjson (1074 MB) | 7.138 s · 0.15 GB/s | 1.149 s · 0.93 GB/s | 0.260 s · 4.13 GB/s | 27.4× |
| 06 | regular expression | tweets.ndjson (1074 MB) | 15.195 s · 0.07 GB/s | 1.552 s · 0.69 GB/s | 0.659 s · 1.63 GB/s | 23.1× |
| 07 | count elements | timeline.json (841 MB) | 6.547 s · 0.13 GB/s | 2.177 s · 0.39 GB/s | 2.175 s · 0.39 GB/s | 3.0× |
| 08 | minify (-c .) | timeline.json (841 MB) | 11.025 s · 0.08 GB/s | 2.579 s · 0.33 GB/s | 2.556 s · 0.33 GB/s | 4.3× |
| 09 | group_by | timeline.json (841 MB) | 6.956 s · 0.12 GB/s | 2.246 s · 0.37 GB/s | 2.245 s · 0.37 GB/s | 3.1× |

Peak RSS (MiB, mean)

| # | workload | input | jq | duckdb 1t | duckdb |
|---|---|---|---|---|---|
| 01 | minify (-c .) | tweets.ndjson | 4 | 1300 | 5180 |
| 02 | pretty-print (.) | tweets.ndjson | 4 | 1647 | 6175 |
| 03 | extract a field | tweets.ndjson | 4 | 181 | 3837 |
| 04 | select and build objects | tweets.ndjson | 4 | 275 | 3877 |
| 05 | string interpolation | tweets.ndjson | 4 | 234 | 5305 |
| 06 | regular expression | tweets.ndjson | 4 | 312 | 5556 |
| 07 | count elements | timeline.json | 3263 | 4298 | 4300 |
| 08 | minify (-c .) | timeline.json | 3358 | 5484 | 5486 |
| 09 | group_by | timeline.json | 3277 | 4302 | 4305 |
