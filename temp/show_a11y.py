import json

data = json.load(open("temp/a11y_baseline.json"))
SKIP = [
    "advanced_folders",
    "synchronization_backup",
    "system_cleanup",
    "test",
    "__pycache__",
    "scripts",
    "core",
    "gui/themes",
    "rfu/ui_",
]
out = []
for filepath, viols in sorted(data["violations_by_file"].items()):
    fp = filepath.replace("\\", "/")
    if any(s in fp for s in SKIP):
        continue
    if "src/tools" in fp:
        out.append("{} ({}):".format(fp, len(viols)))
        for v in viols:
            out.append(
                "  {}: {} = {}".format(v["line"], v["variable"], v["widget_type"])
            )
print("\n".join(out))
