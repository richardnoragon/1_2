#!/usr/bin/env python3
"""Reject UI font/menu and translation metadata regressions.

Exported-document CSS has individually reviewed fingerprints; no UI baseline
waives violations. Static checks do not certify behavioral compliance.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
from collections import Counter
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def findings(root=ROOT):
    result = []
    catalogue_path = root / 'src/rfu/legacy_strings.json'
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8")) if catalogue_path.exists() else {}
    for path in sorted((root / "src/tools").rglob("*.py")):
        source = path.read_text(encoding="utf-8-sig")
        relative = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            result.append((relative, "SYNTAX", exc.msg))
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in {'_ui_bind', '_ui_widget'}:
                    index = 2 if node.func.id == '_ui_bind' else 1
                    if len(node.args) > index and isinstance(node.args[index], ast.Constant):
                        key = node.args[index].value
                        if key not in catalogue:
                            result.append((relative, 'STR', 'Missing catalogue key: ' + str(key)))
                name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                if name in {"QFont", "setPixelSize", "setPointSize"}:
                    result.append((relative, "FNT", ast.dump(node, include_attributes=False)))
                if name in {"addMenu", "QMenu", "QMenuBar"}:
                    result.append((relative, "MEN", ast.dump(node, include_attributes=False)))
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for declaration in re.findall(r"font-(?:size|family)\s*:[^;\n}]+", node.value):
                    result.append((relative, "FNT", declaration.strip()))
    for path in sorted((root / 'src/tools').rglob('*.ui')):
        relative = path.relative_to(root).as_posix()
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            result.append((relative, 'SYNTAX', str(exc)))
            continue
        for prop in tree.iter('property'):
            name = prop.get('name', '')
            if name == 'font':
                result.append((relative, 'FNT', ET.tostring(prop, encoding='unicode')))
            if name == 'styleSheet':
                for declaration in re.findall(r'font-(?:size|family)\s*:[^;\n}]+', prop.findtext('string', '')):
                    result.append((relative, 'FNT', declaration.strip()))
            if name.startswith('rfuLocale_') and prop.findtext('string') not in catalogue:
                result.append((relative, 'STR', 'Missing catalogue key: ' + str(prop.findtext('string'))))
    return result


def counts(items):
    return Counter((path, code, hashlib.sha256(detail.encode()).hexdigest())
                   for path, code, detail in items)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    items = findings()
    current = counts(items)
    rows = [{"path": path, "rule": code, "fingerprint": fingerprint, "count": count}
            for (path, code, fingerprint), count in sorted(current.items())]
    exceptions = json.loads((ROOT / "docs/harmonization2/static-exceptions.json").read_text(encoding="utf-8"))
    allowed = {(row["path"], row["rule"], row["fingerprint"]): row["count"] for row in exceptions["exceptions"]}
    expired = [key for key, count in allowed.items() if current.get(key, 0) != count]
    if expired:
        print("Reviewed document-style exceptions changed; review and update their fingerprints.")
    regressions = [row for row in rows if row["count"] > allowed.get((row["path"], row["rule"], row["fingerprint"]), 0)]
    report = {"existing_findings": sum(current.values()), "regressions": regressions,
              "coverage": "Strict Python/Designer UI font/menu and translation-key checks; fingerprinted document-output CSS is reported separately",
              "document_style_exceptions": sum(allowed.values()), "expired_exceptions": expired,
              "findings": rows}
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for row in regressions:
        print(f"{row['path']}: {row['rule']} increased to {row['count']}")
    print(f"Harmonization: {len(regressions)} UI violations; {sum(allowed.values())} reviewed document-style findings")
    return bool(regressions or expired)


if __name__ == "__main__":
    raise SystemExit(main())
