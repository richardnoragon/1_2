# Preference Portability Performance Benchmarks

_Run date: 2025-11-14 · Script: `python -m scripts.perf.preferences_portability_benchmark`_

## Dataset & Environment

- Synthetic dataset of 10,000 preference entries distributed across 50 categories (mixed string, numeric, boolean, and JSON payloads).
- Benchmark executed on the local Windows development workstation inside `.venv312` (Python 3.12) using a temporary SQLite database instance.
- Export artifacts were written to a temporary directory; the JSON payload measured below was not persisted in the repository.

## Timing Results

| Metric            | Value                       |
| ----------------- | --------------------------- |
| Seed duration     | 2.843 s                     |
| Export duration   | 0.433 s                     |
| Import duration   | 44.714 s                    |
| Export throughput | 23,079 entries/s            |
| Import throughput | 224 entries/s               |
| Export size       | 2,531,797 bytes (~2.41 MiB) |

## Observations

- Export performance remains strong at ~0.43 seconds for 10k entries, largely due to batched reads and a single JSON serialization pass.
- Import throughput (~224 entries/s) is bottlenecked by per-row upserts plus audit trigger execution; batching or wrapping the import loop in an explicit transaction could improve latency significantly.
- Creating a fresh `DatabaseManager` instance for the benchmark triggers the preference bootstrap, which currently copies the existing config file into `config/rfu_config_backup_*.json`; consider providing a flag to suppress bootstrap side effects during synthetic runs.

## Next Steps

1. Evaluate options for batching import writes (e.g., prepared inserts within a transaction scope) to improve throughput before release.
2. Provide a benchmark mode or environment toggle that prevents config backups when running against ephemeral databases.
3. Re-run the benchmark after any import optimizations to quantify gains and update this report accordingly.
