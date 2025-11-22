"""Placeholder endpoints for MFA readiness (FR-013)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from src.core.auth.services.mfa_hook_service import (
    MFAFeatureUnavailableError,
    MFAHookService,
)


class MFAPlaceholderController:
    """HTTP-style controller that always returns 501 until MFA ships."""

    def __init__(self, *, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else None
        self.service = MFAHookService(
            db_path=str(self.db_path) if self.db_path else None
        )

    # ------------------------------------------------------------------
    def get_status(self, username: Optional[str] = None) -> Dict[str, Any]:
        try:
            capabilities = self.service.describe_capabilities()
        except MFAFeatureUnavailableError as exc:
            return self._format_response(exc, username=username)
        return {
            "status": "ok",
            "username": username,
            "capabilities": capabilities,
        }

    def post_enroll(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        username = payload.get("username") if isinstance(payload, Mapping) else None
        metadata = payload.get("metadata") if isinstance(payload, Mapping) else None
        try:
            return self.service.enroll_user(username or "", metadata=metadata)
        except MFAFeatureUnavailableError as exc:
            return self._format_response(exc, username=username)

    def post_verify(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        username = payload.get("username") if isinstance(payload, Mapping) else None
        token = payload.get("token") if isinstance(payload, Mapping) else None
        try:
            verified = self.service.verify_challenge(
                username or "",
                token or "",
            )
        except MFAFeatureUnavailableError as exc:
            return self._format_response(exc, username=username)
        return {
            "status": "ok",
            "verified": verified,
            "username": username,
        }

    def post_recovery_codes(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        username = payload.get("username") if isinstance(payload, Mapping) else None
        try:
            codes = self.service.issue_recovery_codes(username or "")
        except MFAFeatureUnavailableError as exc:
            return self._format_response(exc, username=username)
        return {
            "status": "ok",
            "count": len(codes),
            "username": username,
        }

    def delete_mfa(self, username: str) -> Dict[str, Any]:
        try:
            return self.service.disable_mfa(username)
        except MFAFeatureUnavailableError as exc:
            return self._format_response(exc, username=username)

    # ------------------------------------------------------------------
    @staticmethod
    def _format_response(
        error: MFAFeatureUnavailableError,
        *,
        username: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": "not_implemented",
            "status_code": error.status_code,
            "username": username,
            "message": str(error),
            "retry_after": "mfa-rollout",
        }


__all__ = ["MFAPlaceholderController"]
