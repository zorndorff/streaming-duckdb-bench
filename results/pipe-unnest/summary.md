2026-11-25T18:39:59-06:00 INPUT=pipe THREADS=32  
v2.0.0 (Cyanoptera) d54cbbe3df | jq-1.8.2 | hyperfine 2.0.0  
AMD RYZEN AI MAX+ 395 w/ Radeon 8060S x 32 | Linux 7.2.14-200.fc44.x86_64

| # | workload | input | jq | duckdb 1t | duckdb | duckdb vs jq |
|---|---|---|---|---|---|---|
| 09 | group_by | timeline.json (841 MB) | 6.915 s · 0.12 GB/s | 32.285 s · 0.03 GB/s | 32.090 s · 0.03 GB/s | 0.2× |

Peak RSS (MiB, mean)

| # | workload | input | jq | duckdb 1t | duckdb |
|---|---|---|---|---|---|
| 09 | group_by | timeline.json | 3277 | 6713 | 6713 |
