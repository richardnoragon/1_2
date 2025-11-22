"""RFU hub utilities for coordinating centralized integrations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Dict, Optional, Protocol

from src.core.auth.watchdogs import enforce_idle_timeouts
from src.file_validator.models import ValidationResult
from src.gui.notifications.validator_bridge import dispatch_validator_alert
from src.log_manager import get_log_manager

from .config_manager import ValidatorPolicy, resolve_validator_policy


class ValidatorNotifier(Protocol):
    """Protocol describing the validator notification interface."""

    def push(
        self,
        *,
        level: str,
        message: str,
        workflow: str,
        details: dict[str, object],
    ) -> None: ...


_logger = get_log_manager().get_logger("rfu.validator_notifications")
_lock = RLock()
_registered_notifier: Optional[ValidatorNotifier] = None
_idle_watcher_config: Optional["IdleWatcherConfig"] = None
_idle_watcher_last_summary: Optional[Dict[str, Any]] = None
_idle_watcher_observers: set[Callable[[Dict[str, Any]], None]] = set()


@dataclass(frozen=True)
class IdleWatcherConfig:
    database_path: Path
    idle_minutes: int = 10


def configure_idle_timeout_watcher(
    *,
    database_path: str | Path,
    idle_minutes: int = 10,
) -> IdleWatcherConfig:
    path = Path(database_path)
    minutes = max(1, int(idle_minutes))
    config = IdleWatcherConfig(database_path=path, idle_minutes=minutes)
    global _idle_watcher_config
    with _lock:
        _idle_watcher_config = config
    _logger.info(
        "Idle timeout watcher configured (path=%s, idle_minutes=%s)",
        path,
        minutes,
    )
    return config


def get_idle_timeout_watcher_config() -> Optional[IdleWatcherConfig]:
    with _lock:
        return _idle_watcher_config


def has_idle_timeout_watcher() -> bool:
    with _lock:
        return _idle_watcher_config is not None


def register_idle_timeout_observer(callback: Callable[[Dict[str, Any]], None]) -> None:
    with _lock:
        _idle_watcher_observers.add(callback)


def unregister_idle_timeout_observer(
    callback: Callable[[Dict[str, Any]], None],
) -> None:
    with _lock:
        _idle_watcher_observers.discard(callback)


def get_last_idle_timeout_summary() -> Optional[Dict[str, Any]]:
    with _lock:
        return _idle_watcher_last_summary


def run_idle_timeout_watcher(
    *,
    raise_on_missing_config: bool = True,
) -> Dict[str, Any]:
    with _lock:
        config = _idle_watcher_config
    if config is None:
        if raise_on_missing_config:
            raise RuntimeError("Idle timeout watcher has not been configured")
        return {}

    summary = enforce_idle_timeouts(
        database_path=config.database_path,
        idle_minutes=config.idle_minutes,
    )
    observers: list[Callable[[Dict[str, Any]], None]]
    with _lock:
        global _idle_watcher_last_summary
        _idle_watcher_last_summary = summary
        observers = list(_idle_watcher_observers)

    for observer in observers:
        try:
            observer(summary)
        except Exception as exc:  # pragma: no cover - observer safety
            _logger.error("Idle timeout observer failed: %s", exc, exc_info=True)
    return summary


def register_validator_notifier(notifier: ValidatorNotifier) -> None:
    """Register the active GUI notifier for validator events."""
    global _registered_notifier
    with _lock:
        _registered_notifier = notifier
    _logger.debug(
        "Registered validator notifier: %s",
        notifier.__class__.__name__,
    )


def unregister_validator_notifier(
    notifier: Optional[ValidatorNotifier] | None = None,
) -> None:
    """
    Unregister the active GUI notifier if it matches the supplied instance.
    """
    global _registered_notifier
    with _lock:
        if notifier is None or notifier is _registered_notifier:
            _logger.debug("Unregistered validator notifier")
            _registered_notifier = None


def get_validator_notifier() -> Optional[ValidatorNotifier]:
    """Return the currently registered validator notifier, if any."""
    with _lock:
        return _registered_notifier


def dispatch_validator_result(
    validation: ValidationResult,
    *,
    workflow: str | None = None,
    notifier: Optional[ValidatorNotifier] = None,
) -> None:
    """Dispatch a validator result to the GUI notifier if registered."""
    policy = _resolve_policy(workflow)
    effective_workflow = policy.workflow

    if not _should_dispatch(validation, policy):
        _logger.debug(
            "Validator notification suppressed for workflow %s "
            "(notify=%s, action=%s)",
            effective_workflow,
            policy.notify,
            validation.action,
        )
        return

    target = notifier or get_validator_notifier()
    if target is None:
        _log_fallback(validation, effective_workflow, policy)
        return

    try:
        dispatch_validator_alert(
            validation,
            target,
            workflow=effective_workflow,
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        _logger.error(
            "Validator notification dispatch failed for workflow %s: %s",
            effective_workflow,
            exc,
            exc_info=True,
        )
        _log_fallback(validation, effective_workflow, policy)


def _log_fallback(
    validation: ValidationResult,
    workflow: str,
    policy: ValidatorPolicy,
) -> None:
    """Fallback logging used when no GUI notifier has been registered."""
    action = validation.action
    allowed = ", ".join(sorted(validation.allowed_types))
    evidence_preview = "; ".join(validation.detection.evidence[:3])
    message = (
        f"Workflow '{workflow}' validator {action}: {validation.reason} "
        f"(detected={validation.detection.detected_type}, "
        f"confidence={validation.detection.confidence}, "
        f"allowed={allowed or '∅'}, evidence={evidence_preview or 'n/a'}, "
        f"mode={policy.mode}, notify={policy.notify})"
    )
    if action == "reject":
        _logger.warning(message)
    elif action == "warn":
        _logger.info(message)
    else:
        _logger.debug(message)


def _should_dispatch(
    validation: ValidationResult,
    policy: ValidatorPolicy,
) -> bool:
    notify_mode = policy.notify
    action = validation.action
    if notify_mode == "always":
        return True
    if notify_mode == "never":
        return False
    if notify_mode == "on-reject":
        return action == "reject"
    if notify_mode == "on-warn":
        return action == "warn"
    # Default behaviour: notify on any mismatch (warn or reject)
    return action != "accept"


def _resolve_policy(workflow: Optional[str]) -> ValidatorPolicy:
    try:
        return resolve_validator_policy(workflow)
    except Exception as exc:  # pragma: no cover - defensive logging
        fallback = ValidatorPolicy(
            name="default",
            workflow=workflow or "unknown",
            mode="reject",
            allowed_types=(),
            notify="on-mismatch",
        )
        _logger.error(
            "Failed to resolve validator policy for workflow %s: %s",
            workflow,
            exc,
            exc_info=True,
        )
        return fallback
