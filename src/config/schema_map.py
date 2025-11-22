"""Mapping helpers bridging ConfigManager payloads to preference structures."""

from __future__ import annotations

from typing import Any, Dict


def map_config_to_preferences(
    config: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Extract theming and directory preferences from legacy config."""

    result: Dict[str, Dict[str, Any]] = {"theming": {}, "directories": {}}

    if not isinstance(config, dict):
        return {}

    general = config.get("general")
    if isinstance(general, dict):
        theme = general.get("theme")
        if isinstance(theme, str) and theme:
            result["theming"]["theme"] = theme.strip().lower()

        default_directory = general.get("default_directory")
        if isinstance(default_directory, str) and default_directory:
            result["directories"]["default_root"] = default_directory

        recent = general.get("recent_directories")
        if isinstance(recent, list):
            result["directories"]["recent"] = [
                str(item) for item in recent if isinstance(item, str)
            ]

        show_hidden = general.get("show_hidden")
        if isinstance(show_hidden, bool):
            result["directories"]["show_hidden"] = show_hidden
        elif isinstance(show_hidden, (int, str)):
            result["directories"]["show_hidden"] = str(show_hidden).lower() in (
                "true",
                "1",
                "yes",
            )

    return {k: v for k, v in result.items() if v}
