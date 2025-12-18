"""Specialized configuration helpers for RFU validator integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Tuple

from src.config.config_manager import get_config_manager
from src.file_validator.utils import canonicalise_allowed_types

_ALLOWED_MODES = {"reject", "warn", "auto"}
_DEFAULT_MODE = "reject"

_NOTIFY_ALIASES = {
    "always": "always",
    "on-mismatch": "on-mismatch",
    "mismatch": "on-mismatch",
    "on-reject": "on-reject",
    "reject-only": "on-reject",
    "on-warn": "on-warn",
    "warn-only": "on-warn",
    "never": "never",
    "none": "never",
    "disabled": "never",
}
_DEFAULT_NOTIFY = "on-mismatch"
_WORKFLOW_SECTION = "validator_workflows"


def _resolve_workflow_override(
    workflow_map: Any, workflow: Optional[str]
) -> Tuple[Optional[str], Dict[str, Any]]:
    if not workflow or not isinstance(workflow_map, dict):
        return None, {}

    mapping = workflow_map.get(workflow)
    if isinstance(mapping, str):
        return str(mapping), {}
    if isinstance(mapping, dict):
        mapped_profile = mapping.get("profile") or mapping.get("inherit")
        overrides = {
            key: value
            for key, value in mapping.items()
            if key not in {"profile", "inherit"}
        }
        if mapped_profile is None:
            return None, overrides
        return str(mapped_profile), overrides

    return None, {}


@dataclass(frozen=True)
class ValidatorPolicy:
    """Resolved validator policy details for a workflow."""

    name: str
    workflow: str
    mode: str
    allowed_types: Tuple[str, ...]
    notify: str

    def allowed_set(self) -> set[str]:
        """Return allowed types as a set for membership checks."""

        return set(self.allowed_types)

    def as_kwargs(self) -> Dict[str, Any]:
        """Return dictionary representation for logging or telemetry."""

        return {
            "name": self.name,
            "workflow": self.workflow,
            "mode": self.mode,
            "allowed_types": list(self.allowed_types),
            "notify": self.notify,
        }


def list_validator_policies() -> list[str]:
    """Return available validator profile names."""

    manager = get_config_manager()
    profiles = manager.get_section("validator_profiles")
    if not isinstance(profiles, dict):
        return ["default"]
    names = set(profiles.keys())
    names.add("default")
    return sorted(names)


def resolve_validator_policy(
    workflow: Optional[str] = None,
    *,
    profile: Optional[str] = None,
) -> ValidatorPolicy:
    """Resolve the effective validator policy for a workflow or profile."""

    manager = get_config_manager()
    profiles = manager.get_section("validator_profiles")
    if not isinstance(profiles, dict):
        profiles = {}

    workflow_map = manager.get_section(_WORKFLOW_SECTION)

    target_name = profile or workflow or "default"
    mapped_name, inline_overrides = _resolve_workflow_override(
        workflow_map, workflow
    )
    if mapped_name:
        target_name = mapped_name

    if target_name not in profiles and target_name != "default":
        target_name = "default"

    merged = _resolve_profile_dict(profiles, target_name)
    if inline_overrides:
        merged.update(inline_overrides)
    resolved_workflow = (
        (workflow or merged.get("workflow"))
        or merged.get("name")
        or target_name
        or "default"
    )
    resolved_mode = _normalise_mode(merged.get("mode"))
    resolved_notify = _normalise_notify(merged.get("notify"))
    allowed = _normalise_allowed_types(merged.get("allowed_types"))

    return ValidatorPolicy(
        name=merged.get("name", target_name),
        workflow=str(resolved_workflow),
        mode=resolved_mode,
        allowed_types=allowed,
        notify=resolved_notify,
    )


def update_validator_profile(
    name: str,
    updates: Dict[str, Any],
    *,
    persist: bool = True,
) -> ValidatorPolicy:
    """Create or update a validator profile and optionally persist it."""

    manager = get_config_manager()
    profiles = manager.get_section("validator_profiles")
    if not isinstance(profiles, dict):
        profiles = {}

    current: Dict[str, Any] = dict(profiles.get(name, {}))
    current.update(updates)
    current.pop("name", None)
    profiles[name] = current

    if persist:
        manager.set_section("validator_profiles", profiles)

    return resolve_validator_policy(profile=name)


def _resolve_profile_dict(
    profiles: Dict[str, Dict[str, Any]],
    name: str,
    visited: Optional[set[str]] = None,
) -> Dict[str, Any]:
    visited = visited or set()
    if name in visited:
        raise ValueError(
            f"Circular validator profile inheritance detected for '{name}'"
        )
    visited.add(name)

    if name == "default":
        data = profiles.get("default", {})
    else:
        data = profiles.get(name, {})
    if not isinstance(data, dict):
        data = {}

    inherit = data.get("inherit")
    if inherit:
        parent = _resolve_profile_dict(profiles, str(inherit), visited)
    else:
        parent = {}

    merged: Dict[str, Any] = dict(parent)
    merged.update({k: v for k, v in data.items() if k != "inherit"})
    merged.setdefault("name", name)

    return merged


def _normalise_allowed_types(allowed: Any) -> Tuple[str, ...]:
    if allowed is None:
        return ()
    if isinstance(allowed, str):
        iterable: Iterable[str] = [allowed]
    elif isinstance(allowed, Iterable):
        iterable = allowed  # type: ignore[assignment]
    else:
        iterable = []
    canonical = canonicalise_allowed_types(iterable)
    return tuple(sorted(canonical))


def _normalise_mode(mode: Optional[str]) -> str:
    if not mode:
        return _DEFAULT_MODE
    value = str(mode).lower().strip()
    if value not in _ALLOWED_MODES:
        return _DEFAULT_MODE
    return value


def _normalise_notify(notify: Optional[str]) -> str:
    if not notify:
        return _DEFAULT_NOTIFY
    key = str(notify).lower().strip()
    return _NOTIFY_ALIASES.get(key, _DEFAULT_NOTIFY)


__all__ = [
    "ValidatorPolicy",
    "list_validator_policies",
    "resolve_validator_policy",
    "update_validator_profile",
]
