"""Summarize preference portability export/import activity by day."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

EXPORT_MARKER = "preferences_export_completed"
IMPORT_MARKER = "preferences_import_completed"
TIMESTAMP_SLICE = slice(0, 23)
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S,%f"
DATE_FORMAT = "%Y-%m-%d"
ENTRY_COUNT_RE = re.compile(r"entry_count=(\d+)")
APPLIED_RE = re.compile(r"applied=(\d+)")
SKIPPED_RE = re.compile(r"skipped=(\d+)")


@dataclass
class DailyStats:
    """Aggregate counts for a single calendar day."""

    exports: int = 0
    export_entries: int = 0
    imports: int = 0
    import_entries: int = 0
    import_applied: int = 0
    import_skipped: int = 0

    def as_row(self, date_label: str) -> str:
        return (
            "{date:<12} {exports:>7} {export_entries:>14} {imports:>8} "
            "{import_entries:>14} {import_applied:>15} {import_skipped:>14}"
        ).format(
            date=date_label,
            exports=self.exports,
            export_entries=self.export_entries,
            imports=self.imports,
            import_entries=self.import_entries,
            import_applied=self.import_applied,
            import_skipped=self.import_skipped,
        )


def parse_timestamp(line: str) -> str | None:
    raw = line[TIMESTAMP_SLICE]
    try:
        stamp = datetime.strptime(raw, TIMESTAMP_FORMAT)
    except ValueError:
        return None
    return stamp.strftime(DATE_FORMAT)


def extract_int(pattern: re.Pattern[str], text: str) -> int:
    match = pattern.search(text)
    if not match:
        return 0
    try:
        return int(match.group(1))
    except ValueError:
        return 0


def build_summary(lines: Iterable[str]) -> Dict[str, DailyStats]:
    summary: Dict[str, DailyStats] = defaultdict(DailyStats)
    for line in lines:
        if EXPORT_MARKER not in line and IMPORT_MARKER not in line:
            continue
        date_label = parse_timestamp(line)
        if not date_label:
            continue
        if EXPORT_MARKER in line:
            stats = summary[date_label]
            stats.exports += 1
            stats.export_entries += extract_int(ENTRY_COUNT_RE, line)
        elif IMPORT_MARKER in line:
            stats = summary[date_label]
            stats.imports += 1
            stats.import_entries += extract_int(ENTRY_COUNT_RE, line)
            stats.import_applied += extract_int(APPLIED_RE, line)
            stats.import_skipped += extract_int(SKIPPED_RE, line)
    return summary


def read_log(path: Path) -> Iterable[str]:
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")
    return path.read_text(encoding="utf-8").splitlines()


def summary_rows(summary: Dict[str, DailyStats]) -> List[Dict[str, int | str]]:
    rows: List[Dict[str, int | str]] = []
    for date_label in sorted(summary.keys()):
        stats = summary[date_label]
        rows.append(
            {
                "date": date_label,
                "export_runs": stats.exports,
                "export_entries": stats.export_entries,
                "import_runs": stats.imports,
                "import_entries": stats.import_entries,
                "import_applied": stats.import_applied,
                "import_skipped": stats.import_skipped,
            }
        )
    return rows


def print_table(summary: Dict[str, DailyStats]) -> None:
    header = (
        "Date            Exports   ExportEntries   Imports   "
        "ImportEntries   ImportApplied   ImportSkipped"
    )
    print(header)
    if not summary:
        print("(no preference portability activity found)")
        return
    for date_label in sorted(summary.keys()):
        print(summary[date_label].as_row(date_label))


def render_json(rows: List[Dict[str, int | str]], generated_at: str) -> str:
    payload = {
        "generated_at_utc": generated_at,
        "rows": rows,
    }
    return json.dumps(payload, indent=2)


def render_markdown(rows: List[Dict[str, int | str]], generated_at: str) -> str:
    header = (
        "| Date | Export Runs | Export Entries | Import Runs | "
        "Import Entries | Import Applied | Import Skipped |\n"
        "| --- | --- | --- | --- | --- | --- | --- |"
    )
    if not rows:
        body = "\n| (none) | 0 | 0 | 0 | 0 | 0 | 0 |"
    else:
        body_lines = []
        for row in rows:
            body_lines.append(
                (
                    "| {date} | {export_runs} | {export_entries:,} | {import_runs} | "
                    "{import_entries:,} | {import_applied:,} | {import_skipped:,} |"
                ).format(
                    date=row["date"],
                    export_runs=row["export_runs"],
                    export_entries=row["export_entries"],
                    import_runs=row["import_runs"],
                    import_entries=row["import_entries"],
                    import_applied=row["import_applied"],
                    import_skipped=row["import_skipped"],
                )
            )
        body = "\n" + "\n".join(body_lines)
    footer = f"\n\n_Generated at {generated_at} UTC_"
    return header + body + footer


def write_outputs(
    summary: Dict[str, DailyStats],
    output_dir: Path,
    prefix: str,
    generated_at: str,
) -> Dict[str, Path]:
    rows = summary_rows(summary)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    json_content = render_json(rows, generated_at)
    markdown_content = render_markdown(rows, generated_at)

    timestamped_json = output_dir / f"{prefix}_{timestamp}.json"
    timestamped_md = output_dir / f"{prefix}_{timestamp}.md"
    latest_json = output_dir / f"{prefix}_latest.json"
    latest_md = output_dir / f"{prefix}_latest.md"

    for path, content in (
        (timestamped_json, json_content),
        (timestamped_md, markdown_content),
        (latest_json, json_content),
        (latest_md, markdown_content),
    ):
        path.write_text(content, encoding="utf-8")

    return {
        "timestamped_json": timestamped_json,
        "timestamped_markdown": timestamped_md,
        "latest_json": latest_json,
        "latest_markdown": latest_md,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit daily export/import counts from logs/rfu.log",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("logs") / "rfu.log",
        help="Path to the RFU log file (default: logs/rfu.log)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help=(
            "Directory to store snapshot files (writes JSON/Markdown "
            "timestamped copies and latest pointers)"
        ),
    )
    parser.add_argument(
        "--output-prefix",
        default="preferences_portability_summary",
        help=(
            "Filename prefix for generated artifacts (default: "
            "preferences_portability_summary)"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lines = read_log(args.log)
    summary = build_summary(lines)
    print_table(summary)
    if args.output_dir:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        outputs = write_outputs(
            summary=summary,
            output_dir=args.output_dir,
            prefix=args.output_prefix,
            generated_at=generated_at,
        )
        print()
        print("Snapshot artifacts written:")
        for label, path in outputs.items():
            print(f"  {label}: {path}")


if __name__ == "__main__":
    main()
