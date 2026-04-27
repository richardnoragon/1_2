import pathlib
import re

p = pathlib.Path("src/tools/file_management/advanced_catalog/color_coding_engine.py")
t = p.read_text(encoding="utf-8")
# Move comma from after noqa comment to before noqa comment
# Before: color_hex="#XXXX"  # noqa: TH-1  ...,
# After:  color_hex="#XXXX",  # noqa: TH-1  ...
n = re.sub(r'(color_hex="#[0-9A-Fa-f]{3,6}")(\s+# noqa: TH-1[^\n]*?),\n', r"\1,\2\n", t)
fixes = t.count("colour,") - n.count("colour,")
p.write_text(n, encoding="utf-8")
print(f"color_coding_engine.py: {fixes} commas moved before noqa comment")
