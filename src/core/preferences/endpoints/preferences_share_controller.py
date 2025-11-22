"""Controller wiring for POST `/preferences/share` contract coverage."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Mapping

from src.core.preferences.services.share_service import ShareService


class PreferencesShareController:
    """Expose share service semantics to contract tests."""

    def __init__(
        self,
        *,
        db_path: str | Path,
        share_service: ShareService | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self._share_service = share_service or ShareService(
            database_path=self.db_path,
            origin_surface="service",
        )

    def post_share(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be a mapping")
        username = payload.get("username")
        purpose = payload.get("purpose")
        anonymize = bool(payload.get("anonymize", True))
        actor_username = payload.get("token_username")
        if not isinstance(username, str) or not username:
            raise ValueError("username is required")
        if not isinstance(purpose, str) or not purpose:
            raise ValueError("purpose is required")

        bundle = self._share_service.export_preferences(
            username=username,
            purpose=purpose,
            actor_username=actor_username,
            additional_actor_candidates=[username],
        )
        if anonymize:
            return self._anonymize_bundle(bundle)
        result = dict(bundle)
        result["anonymized"] = False
        return result

    @staticmethod
    def _anonymize_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
        redacted = deepcopy(bundle)
        redacted["username"] = "redacted"
        redacted.pop("preferences_id", None)
        export_section = redacted.get("export")
        if isinstance(export_section, dict):
            metadata = export_section.get("metadata")
            if isinstance(metadata, dict):
                metadata["shared_by"] = "redacted"
        redacted["anonymized"] = True
        return redacted


__all__ = ["PreferencesShareController"]
