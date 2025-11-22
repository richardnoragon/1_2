# Telemetry Snapshots

This directory stores generated telemetry artifacts for the preferences portability
initiative. The `preferences_portability_summary.py` reporting helper now supports
writing timestamped JSON and Markdown snapshots plus `*_latest` pointers whenever
it runs:

```
powershell
python -m scripts.reporting.preferences_portability_summary `
    --log logs/rfu.log `
    --output-dir reports/telemetry
```

Each execution produces files such as:

- `preferences_portability_summary_YYYYMMDD-HHMMSS.json`
- `preferences_portability_summary_YYYYMMDD-HHMMSS.md`
- `preferences_portability_summary_latest.json`
- `preferences_portability_summary_latest.md`

CI or scheduled jobs should run the command nightly so release reviews can attach the
latest artifacts directly from this folder without re-running the CLI.
