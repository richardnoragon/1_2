"""TH-4b headless smoke test — verifies the ThemeManager callback mechanism."""

import sys

sys.path.insert(0, ".")

import src.gui.themes as _tm
from src.gui.themes import ThemeManager, apply_theme, token

# Register mock callback
calls = []


def mock_cb(variant):
    calls.append(variant)


ThemeManager.add_theme_changed_callback(mock_cb)

# --- dark round-trip ---
apply_theme("dark")
assert _tm._active_variant == "dark", f"Expected dark, got {_tm._active_variant}"
dark_surface = token("surface")
assert dark_surface == "#2C3E50", f"token('surface') wrong in dark: {dark_surface}"
assert calls and calls[-1] == "dark", f"callback not called with dark; calls={calls}"

# --- light round-trip ---
apply_theme("light")
assert _tm._active_variant == "light", f"Expected light, got {_tm._active_variant}"
light_surface = token("surface")
assert light_surface == "#F5F5F5", f"token('surface') wrong in light: {light_surface}"
assert calls and calls[-1] == "light", f"callback not called with light; calls={calls}"

ThemeManager.remove_theme_changed_callback(mock_cb)

print("TH-4b PASS: apply_theme() fires callbacks and token() resolves correctly.")
print(f"  callback sequence: {calls}")
print(f"  dark surface={dark_surface}  light surface={light_surface}")
