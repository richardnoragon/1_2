"""Core RFU package exports for centralized integrations."""

from __future__ import annotations

from .config_manager import (
    ValidatorPolicy,
    list_validator_policies,
    resolve_validator_policy,
    update_validator_profile,
)
def __getattr__(name):
    """Keep typography and strings independent of optional identity services."""
    if name in __all__:
        from importlib import import_module
        value = getattr(import_module(".hub", __name__), name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "ValidatorPolicy",
    "configure_idle_timeout_watcher",
    "dispatch_validator_result",
    "get_idle_timeout_watcher_config",
    "get_last_idle_timeout_summary",
    "get_validator_notifier",
    "has_idle_timeout_watcher",
    "list_validator_policies",
    "register_idle_timeout_observer",
    "register_validator_notifier",
    "resolve_validator_policy",
    "run_idle_timeout_watcher",
    "unregister_idle_timeout_observer",
    "unregister_validator_notifier",
    "update_validator_profile",
]
