from __future__ import annotations

import importlib
import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

apply_identity_schema = importlib.import_module(
    "tests.integration.identity.utils"
).apply_identity_schema


def main() -> None:
    db_path = Path("temp/schema_guard_test.sqlite3")
    if db_path.exists():
        db_path.unlink()

    apply_identity_schema(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='rfu_schema_version'"
        )
        table_exists = cursor.fetchone() is not None

        rows = conn.execute(
            "SELECT version, applied_at, description FROM rfu_schema_version"
        ).fetchall()

        print("schema_table_exists=", table_exists)
        print("schema_version_rows=", rows)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
