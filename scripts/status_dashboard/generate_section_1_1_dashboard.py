#!/usr/bin/env python3
"""Generate Section 1.1 dashboard artifacts from the roadmap."""

from __future__ import annotations

import argparse
import datetime as dt
import html as html_module
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
ROADMAP_PATH = REPO_ROOT / "docs" / "roadmap" / "roadmap_rfu_summary.md"
DASHBOARD_DIR = REPO_ROOT / "reports" / "dashboards"


def _iso_now() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def load_roadmap() -> List[str]:
    if not ROADMAP_PATH.exists():
        raise FileNotFoundError(f"Roadmap file not found: {ROADMAP_PATH}")
    return ROADMAP_PATH.read_text(encoding="utf-8").splitlines()


def extract_top_level_directories(lines: List[str]) -> List[str]:
    directories: List[str] = []
    pattern = re.compile(r"`([^`]+)`")
    for line in lines:
        if line.strip().startswith("- Top-level directories"):
            directories = pattern.findall(line)
            break
    return directories


def extract_section_table(lines: List[str]) -> Tuple[List[str], List[List[str]]]:
    header: List[str] = []
    rows: List[List[str]] = []
    capture = False
    for line in lines:
        if "Section 1.1 Status Tracking" in line:
            capture = True
            continue
        if capture:
            if line.startswith("| Milestone"):
                header = [cell.strip() for cell in line.strip().strip("|").split("|")]
                continue
            if header and line.startswith("| "):
                if set(line.strip()) == {"-", "|", " "}:
                    # Skip markdown separator row
                    continue
                row = [cell.strip() for cell in line.strip().strip("|").split("|")]
                rows.append(row)
            elif header and not line.strip():
                break
    if not header:
        raise ValueError("Unable to locate Section 1.1 status table in roadmap.")
    return header, rows


def create_dashboard_payload(
    header: List[str], rows: List[List[str]], directories: List[str]
) -> Dict[str, Any]:
    return {
        "generated_on": _iso_now(),
        "roadmap_source": str(ROADMAP_PATH.relative_to(REPO_ROOT)),
        "columns": header,
        "milestones": [dict(zip(header, row)) for row in rows],
        "top_level_directories": directories,
    }


def write_html(payload: Dict[str, Any], output_path: Path) -> None:
    columns = [str(col) for col in payload["columns"]]
    milestones: List[Dict[str, Any]] = [
        dict(row) for row in payload["milestones"]  # defensive copy
    ]
    rows_html = "\n".join(
        "<tr>"
        + "".join(
            f"<td>{html_module.escape(str(row.get(col, '')))}</td>" for col in columns
        )
        + "</tr>"
        for row in milestones
    )
    header_row = "".join(f"<th>{html_module.escape(str(col))}</th>" for col in columns)
    directory_list = "".join(
        f"<li>{html_module.escape(str(directory))}</li>"
        for directory in payload["top_level_directories"]
    )
    html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<title>Section 1.1 Status Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; }}
h1 {{ font-size: 1.8rem; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
th, td {{ border: 1px solid #444; padding: 0.5rem; text-align: left; }}
th {{ background-color: #f0f0f0; }}
.footer {{ margin-top: 1.5rem; font-size: 0.9rem; color: #555; }}
</style>
</head>
<body>
<h1>Section 1.1 Status Dashboard</h1>
<p>Generated on {payload['generated_on']} from {payload['roadmap_source']}.</p>
<table>
<thead>
<tr>{header_row}</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
<section>
<h2>Top-Level Directories</h2>
<ul>
{directory_list}
</ul>
</section>
<div class=\"footer\">RFU Enterprise Modernization Dashboard</div>
</body>
</html>
"""
    output_path.write_text(html_content, encoding="utf-8")


def write_json(payload: Dict[str, Any], output_path: Path) -> None:
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Section 1.1 status dashboard artifacts."
    )
    parser.add_argument(
        "--output-html",
        type=Path,
        default=DASHBOARD_DIR / "section_1_1_status_dashboard.html",
        help="HTML output path",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=DASHBOARD_DIR / "section_1_1_status_dashboard.json",
        help="JSON output path",
    )
    parser.add_argument(
        "--inventory-only",
        action="store_true",
        help="Print the top-level directory list and exit",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Regenerate dashboard artifacts (default action)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lines = load_roadmap()
    directories = extract_top_level_directories(lines)

    if args.inventory_only:
        for directory in directories:
            print(directory)
        return

    header, rows = extract_section_table(lines)
    payload = create_dashboard_payload(header, rows, directories)

    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    if args.refresh:
        print("Refresh flag detected; regenerating dashboard artifacts.")
    write_html(payload, args.output_html)
    write_json(payload, args.output_json)
    print(f"Dashboard HTML written to {args.output_html}")
    print(f"Dashboard JSON written to {args.output_json}")


if __name__ == "__main__":
    main()
