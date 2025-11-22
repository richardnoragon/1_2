"""CLI helpers for exporting and importing preference data."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from src.core.preferences.portability import (
    AES_AVAILABLE,
    PreferencePortabilityError,
    export_preferences,
    import_preferences,
)


@click.group()
def cli() -> None:
    """Preference portability tooling."""


@cli.command("export")
@click.option("--user", "user_id", required=True, help="User identifier")
@click.option(
    "--dest",
    "destination",
    type=click.Path(path_type=Path),
    help="Destination directory for the export",
)
@click.option(
    "--category",
    "categories",
    multiple=True,
    help="Restrict export to specific categories",
)
@click.option(
    "--skip-encrypted/--include-encrypted",
    default=False,
    help="Skip rows flagged as encrypted",
)
@click.option(
    "--encrypt",
    is_flag=True,
    default=False,
    help="Encrypt export with an AES passphrase",
)
def export_cmd(
    user_id: str,
    destination: Optional[Path],
    categories: tuple[str, ...],
    skip_encrypted: bool,
    encrypt: bool,
) -> None:
    """Export preferences for a user."""

    if encrypt and not AES_AVAILABLE:
        raise click.ClickException(
            "pyAesCrypt not installed; encryption is unavailable",
        )

    passphrase: Optional[str] = None
    if encrypt:
        passphrase = click.prompt(
            "Passphrase",
            hide_input=True,
            confirmation_prompt=True,
        )

    try:
        path = export_preferences(
            user_id,
            destination=destination,
            categories=categories or None,
            include_encrypted=not skip_encrypted,
            passphrase=passphrase,
        )
    except PreferencePortabilityError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Exported preferences to {path}")


@cli.command("import")
@click.argument("source", type=click.Path(path_type=Path, exists=True))
@click.option(
    "--target-user",
    "target_user_id",
    help="Override export user_id with a new user identifier",
)
@click.option(
    "--allow-overwrite/--skip-existing",
    default=False,
    help="Overwrite existing preferences when collisions occur",
)
@click.option(
    "--decrypt",
    is_flag=True,
    default=False,
    help="Provide passphrase for AES encrypted exports",
)
def import_cmd(
    source: Path,
    target_user_id: Optional[str],
    allow_overwrite: bool,
    decrypt: bool,
) -> None:
    """Import preferences from an export payload."""

    if decrypt and not AES_AVAILABLE:
        raise click.ClickException(
            "pyAesCrypt not installed; decryption is unavailable",
        )

    passphrase: Optional[str] = None
    if decrypt:
        passphrase = click.prompt("Passphrase", hide_input=True)

    try:
        result = import_preferences(
            source,
            passphrase=passphrase,
            target_user_id=target_user_id,
            allow_overwrite=allow_overwrite,
        )
    except PreferencePortabilityError as exc:
        raise click.ClickException(str(exc)) from exc

    message = (
        "Imported {applied} entries (skipped {skipped}) for user {user_id}"
    ).format(**result)
    click.echo(message)


if __name__ == "__main__":
    cli()
