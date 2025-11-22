"""CLI helper for RFU self-registration workflows."""

from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from scripts.admin.cli_types import CommandResult
from src.core.auth.policies import InputValidator
from src.core.auth.services import build_registration_service

_ORIGIN_SURFACE = "cli"
_VALIDATOR = InputValidator()


def register_user_cli(
    *,
    database_path: str | Path,
    username: str,
    password: str,
    metadata: Mapping[str, Any] | None = None,
) -> CommandResult:
    """Submit a pending registration via the CLI surface."""

    try:
        sanitized_username, normalized_password = _VALIDATOR.validate_credentials(
            username,
            password,
        )
    except ValueError as exc:
        return CommandResult(exit_code=1, error=str(exc))

    service = build_registration_service(
        database_path=database_path,
        validator=_VALIDATOR,
        origin_surface=_ORIGIN_SURFACE,
    )
    try:
        payload = service.register_user(
            username=sanitized_username,
            password=normalized_password,
            channel="cli",
            metadata=metadata,
        )
    except Exception as exc:  # pylint: disable=broad-except
        return CommandResult(exit_code=1, error=str(exc))

    return CommandResult(exit_code=0, payload=payload)


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-path", required=True)
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument(
        "--metadata",
        help="Optional JSON metadata payload",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _load_metadata_arg(raw_payload: str) -> Mapping[str, Any]:
    try:
        value = json.loads(raw_payload)
    except Exception as exc:  # pylint: disable=broad-except
        raise ValueError(str(exc)) from exc
    if not isinstance(value, Mapping):
        raise ValueError("metadata must decode to a JSON object")
    return value


def _prompt_for_username() -> str:
    while True:
        username = input("Choose a username: ").strip()
        if username:
            return username
        print("Username is required. Please try again.")


def _prompt_for_password() -> str:
    while True:
        password = getpass.getpass("Choose a password: ")
        if not password:
            print("Password is required. Please try again.")
            continue
        confirmation = getpass.getpass("Confirm password: ")
        if password != confirmation:
            print("Passwords do not match. Please try again.")
            continue
        return password


def _prompt_for_metadata() -> Dict[str, Any] | None:
    print("\nProvide optional context to help administrators approve your request.")
    purpose = input("Reason for requesting access (optional): ").strip()
    preference = input("Preferred workspace layout or tools (optional): ").strip()
    metadata: Dict[str, Any] = {}
    if purpose:
        metadata["purpose"] = purpose
    if preference:
        metadata["preferred_workspace"] = preference
    return metadata or None


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        metadata_payload: Mapping[str, Any] | None = (
            _load_metadata_arg(args.metadata) if args.metadata else None
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    username = args.username or _prompt_for_username()
    password = args.password or _prompt_for_password()
    metadata_payload = metadata_payload or _prompt_for_metadata()

    result = register_user_cli(
        database_path=args.database_path,
        username=username,
        password=password,
        metadata=metadata_payload,
    )
    if result.payload is not None:
        print(json.dumps(result.payload, indent=2))
    if result.error:
        print(result.error, file=sys.stderr)
    return result.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
