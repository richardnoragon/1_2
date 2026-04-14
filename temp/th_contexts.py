"""Show violation contexts for key tool files."""

import json
import os

with open("results/compliance/theming_baseline.json") as f:
    data = json.load(f)

target = "advanced_folders"
print(f"=== {target} violations ===")
for v in data["violations"]:
    fp = v["file"].replace(os.getcwd() + os.sep, "").replace(os.sep, "/")
    if target in fp:
        print(f"  [{v['line']:4d}] {v['match']:12s}  {v['source'].strip()[:100]}")

target = "system_cleanup"
print(f"\n=== {target} violations ===")
for v in data["violations"]:
    fp = v["file"].replace(os.getcwd() + os.sep, "").replace(os.sep, "/")
    if target in fp and "privacy" not in fp:
        print(f"  [{v['line']:4d}] {v['match']:12s}  {v['source'].strip()[:100]}")
