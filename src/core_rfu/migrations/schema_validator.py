"""
Schema Validation System for Database Migrations.

This module validates database schema integrity and migration consistency,
ensuring data integrity throughout the migration process.
"""

import sqlite3
import hashlib
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .migration_base import ValidationResult


class ComparisonResult:
    """Result of schema comparison operation."""

    def __init__(
        self, schemas_match: bool, differences: List[Dict[str, Any]] = None
    ):
        self.schemas_match = schemas_match
        self.differences = differences or []
        self.summary = self._generate_summary()

    def _generate_summary(self) -> str:
        """Generate a summary of the comparison."""
        if self.schemas_match:
            return "Schemas match perfectly"
        else:
            return f"Found {len(self.differences)} differences"


class SchemaValidator:
    """
    Validates database schema integrity and migration consistency.
    """

    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.logger = logging.getLogger("RFU.SchemaValidator")

    def validate_schema_integrity(self) -> ValidationResult:
        """
        Validate current database schema integrity.

        Returns:
            ValidationResult indicating schema integrity status
        """
        try:
            with self.db_manager.get_connection() as conn:
                # Check if all required tables exist
                required_tables = [
                    "migration_history",
                    "migration_locks",
                    "migration_backups",
                    "schema_checksums",
                    "app_settings",
                    "user_preferences",
                ]

                missing_tables = []
                for table in required_tables:
                    cursor = conn.execute(
                        """
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=?
                    """,
                        (table,),
                    )

                    if not cursor.fetchone():
                        missing_tables.append(table)

                if missing_tables:
                    return ValidationResult(
                        success=False,
                        message=f"Missing required tables: {missing_tables}",
                        details={"missing_tables": missing_tables},
                    )

                # Validate foreign key constraints
                cursor = conn.execute("PRAGMA foreign_key_check")
                fk_violations = cursor.fetchall()

                if fk_violations:
                    return ValidationResult(
                        success=False,
                        message=f"Foreign key violations found: {len(fk_violations)}",
                        details={"fk_violations": fk_violations},
                    )

                # Validate table structures
                structure_issues = self._validate_table_structures(conn)
                if structure_issues:
                    return ValidationResult(
                        success=False,
                        message="Table structure validation failed",
                        details={"structure_issues": structure_issues},
                    )

                return ValidationResult(
                    success=True, message="Schema integrity validation passed"
                )

        except Exception as e:
            self.logger.error(f"Schema integrity validation failed: {e}")
            return ValidationResult(
                success=False, message=f"Schema validation error: {e}"
            )

    def validate_migration_consistency(self) -> ValidationResult:
        """
        Validate migration history consistency.

        Returns:
            ValidationResult indicating migration consistency status
        """
        try:
            # Check for duplicate migration versions
            duplicates = self.db_manager.execute_query(
                """
                SELECT version, COUNT(*) as count 
                FROM migration_history 
                GROUP BY version 
                HAVING COUNT(*) > 1
            """
            )

            if duplicates:
                return ValidationResult(
                    success=False,
                    message=f"Duplicate migration versions found: {len(duplicates)}",
                    details={"duplicates": duplicates},
                )

            # Check for broken dependency chains
            applied_migrations = self.db_manager.execute_query(
                """
                SELECT version, dependencies 
                FROM migration_history 
                WHERE status = 'applied'
                ORDER BY applied_at
            """
            )

            applied_versions = [m["version"] for m in applied_migrations]
            dependency_issues = []

            for migration in applied_migrations:
                if migration["dependencies"]:
                    deps = json.loads(migration["dependencies"])
                    for dep in deps:
                        if dep not in applied_versions:
                            dependency_issues.append(
                                {
                                    "migration": migration["version"],
                                    "missing_dependency": dep,
                                }
                            )

            if dependency_issues:
                return ValidationResult(
                    success=False,
                    message="Migration dependency issues found",
                    details={"dependency_issues": dependency_issues},
                )

            # Check migration checksums
            checksum_issues = self._validate_migration_checksums()
            if checksum_issues:
                return ValidationResult(
                    success=False,
                    message="Migration checksum validation failed",
                    details={"checksum_issues": checksum_issues},
                )

            return ValidationResult(
                success=True, message="Migration consistency validation passed"
            )

        except Exception as e:
            self.logger.error(f"Migration consistency validation failed: {e}")
            return ValidationResult(
                success=False, message=f"Migration consistency error: {e}"
            )

    def validate_data_integrity(self) -> ValidationResult:
        """
        Validate data integrity after migrations.

        Returns:
            ValidationResult indicating data integrity status
        """
        try:
            integrity_issues = []

            with self.db_manager.get_connection() as conn:
                # Check for orphaned records
                orphan_issues = self._check_orphaned_records(conn)
                integrity_issues.extend(orphan_issues)

                # Check for data consistency
                consistency_issues = self._check_data_consistency(conn)
                integrity_issues.extend(consistency_issues)

            return self._create_integrity_result(integrity_issues)

        except Exception as e:
            self.logger.error(f"Data integrity validation failed: {e}")
            return ValidationResult(
                success=False, message=f"Data integrity error: {e}"
            )

    def _check_orphaned_records(self, conn) -> List[Dict]:
        """Check for orphaned records in the database."""
        integrity_issues = []

        orphan_checks = [
            # Check for user preferences without valid users
            """
            SELECT COUNT(*) as count FROM user_preferences
            WHERE user_id NOT IN (
                SELECT DISTINCT user_id FROM user_preferences
                WHERE preference_category = 'user_info'
            )
            """,
            # Check for invalid JSON in metadata fields
            """
            SELECT id, metadata FROM file_history
            WHERE metadata IS NOT NULL AND metadata != ''
            """,
        ]

        for i, check_sql in enumerate(orphan_checks):
            cursor = conn.execute(check_sql)

            if i == 0:  # Orphan count check
                result = cursor.fetchone()
                if result and result[0] > 0:
                    integrity_issues.append(
                        {"type": "orphaned_records", "count": result[0]}
                    )

            elif i == 1:  # JSON validation check
                json_issues = self._validate_json_fields(cursor)
                integrity_issues.extend(json_issues)

        return integrity_issues

    def _validate_json_fields(self, cursor) -> List[Dict]:
        """Validate JSON fields in database records."""
        json_issues = []
        results = cursor.fetchall()

        for row in results:
            try:
                json.loads(row[1])
            except json.JSONDecodeError:
                json_issues.append(
                    {
                        "type": "invalid_json",
                        "table": "file_history",
                        "id": row[0],
                    }
                )

        return json_issues

    def _create_integrity_result(
        self, integrity_issues: List[Dict]
    ) -> ValidationResult:
        """Create the final integrity validation result."""
        if integrity_issues:
            return ValidationResult(
                success=False,
                message=(
                    f"Data integrity issues found: " f"{len(integrity_issues)}"
                ),
                details={"integrity_issues": integrity_issues},
            )

        return ValidationResult(
            success=True, message="Data integrity validation passed"
        )

    def generate_schema_checksum(self) -> str:
        """
        Generate checksum for current schema.

        Returns:
            SHA-256 checksum of current schema
        """
        try:
            with self.db_manager.get_connection() as conn:
                # Get schema information
                cursor = conn.execute(
                    """
                    SELECT sql FROM sqlite_master 
                    WHERE type IN ('table', 'index', 'trigger', 'view')
                    AND sql IS NOT NULL
                    ORDER BY name
                """
                )

                schema_parts = [row[0] for row in cursor.fetchall()]
                schema_content = "\n".join(schema_parts)

                # Generate checksum
                return hashlib.sha256(
                    schema_content.encode("utf-8")
                ).hexdigest()

        except Exception as e:
            self.logger.error(f"Failed to generate schema checksum: {e}")
            return ""

    def compare_schemas(
        self, expected_schema: Dict, actual_schema: Dict
    ) -> ComparisonResult:
        """
        Compare expected vs actual schema.

        Args:
            expected_schema: Expected schema structure
            actual_schema: Actual schema structure

        Returns:
            ComparisonResult with comparison details
        """
        differences = []

        # Compare tables
        expected_tables = set(expected_schema.get("tables", {}).keys())
        actual_tables = set(actual_schema.get("tables", {}).keys())

        # Missing tables
        missing_tables = expected_tables - actual_tables
        for table in missing_tables:
            differences.append({"type": "missing_table", "table": table})

        # Extra tables
        extra_tables = actual_tables - expected_tables
        for table in extra_tables:
            differences.append({"type": "extra_table", "table": table})

        # Compare common tables
        common_tables = expected_tables & actual_tables
        for table in common_tables:
            table_diffs = self._compare_table_structure(
                expected_schema["tables"][table],
                actual_schema["tables"][table],
            )
            differences.extend(table_diffs)

        return ComparisonResult(
            schemas_match=len(differences) == 0, differences=differences
        )

    def record_schema_checksum(self, migration_version: str):
        """
        Record schema checksum for a migration version.

        Args:
            migration_version: Migration version to record checksum for
        """
        try:
            with self.db_manager.get_connection() as conn:
                # Get all table names
                cursor = conn.execute(
                    """
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """
                )

                tables = [row[0] for row in cursor.fetchall()]

                for table in tables:
                    # Generate table schema checksum
                    table_checksum = self._generate_table_checksum(conn, table)

                    # Record in schema_checksums table
                    self.db_manager.execute_update(
                        """
                        INSERT OR REPLACE INTO schema_checksums 
                        (migration_version, table_name, schema_checksum, created_at)
                        VALUES (?, ?, ?, ?)
                    """,
                        (
                            migration_version,
                            table,
                            table_checksum,
                            datetime.now().isoformat(),
                        ),
                    )

                self.logger.info(
                    f"Recorded schema checksums for migration {migration_version}"
                )

        except Exception as e:
            self.logger.error(f"Failed to record schema checksum: {e}")

    def _validate_table_structures(
        self, conn: sqlite3.Connection
    ) -> List[Dict[str, Any]]:
        """Validate individual table structures."""
        issues = []

        try:
            # Get all user tables
            cursor = conn.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """
            )

            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                # Check table structure
                pragma_cursor = conn.execute(f"PRAGMA table_info({table})")
                columns = pragma_cursor.fetchall()

                if not columns:
                    issues.append(
                        {"type": "empty_table_structure", "table": table}
                    )

                # Check for required columns based on table type
                if table == "migration_history":
                    required_cols = ["id", "version", "applied_at", "status"]
                    table_cols = [col[1] for col in columns]

                    for req_col in required_cols:
                        if req_col not in table_cols:
                            issues.append(
                                {
                                    "type": "missing_required_column",
                                    "table": table,
                                    "column": req_col,
                                }
                            )

        except Exception as e:
            issues.append({"type": "validation_error", "error": str(e)})

        return issues

    def _validate_migration_checksums(self) -> List[Dict[str, Any]]:
        """Validate migration checksums for integrity."""
        issues = []

        try:
            # Get all applied migrations with checksums
            migrations = self.db_manager.execute_query(
                """
                SELECT version, checksum FROM migration_history 
                WHERE status = 'applied' AND checksum IS NOT NULL
            """
            )

            for migration in migrations:
                # For now, we'll just check if checksum exists and is not empty
                if (
                    not migration["checksum"]
                    or len(migration["checksum"]) != 64
                ):
                    issues.append(
                        {
                            "type": "invalid_checksum",
                            "migration": migration["version"],
                            "checksum": migration["checksum"],
                        }
                    )

        except Exception as e:
            issues.append(
                {"type": "checksum_validation_error", "error": str(e)}
            )

        return issues

    def _check_data_consistency(
        self, conn: sqlite3.Connection
    ) -> List[Dict[str, Any]]:
        """Check for data consistency issues."""
        issues = []

        try:
            # Check for timestamp consistency
            cursor = conn.execute(
                """
                SELECT id FROM migration_history 
                WHERE updated_at < created_at
            """
            )

            invalid_timestamps = cursor.fetchall()
            for row in invalid_timestamps:
                issues.append(
                    {
                        "type": "invalid_timestamp",
                        "table": "migration_history",
                        "id": row[0],
                    }
                )

            # Check for valid enum values
            cursor = conn.execute(
                """
                SELECT id, status FROM migration_history 
                WHERE status NOT IN ('applied', 'rolled_back', 'failed')
            """
            )

            invalid_statuses = cursor.fetchall()
            for row in invalid_statuses:
                issues.append(
                    {
                        "type": "invalid_enum_value",
                        "table": "migration_history",
                        "id": row[0],
                        "field": "status",
                        "value": row[1],
                    }
                )

        except Exception as e:
            issues.append({"type": "consistency_check_error", "error": str(e)})

        return issues

    def _compare_table_structure(
        self, expected: Dict, actual: Dict
    ) -> List[Dict[str, Any]]:
        """Compare structure of individual tables."""
        differences = []

        # Compare columns
        expected_cols = set(expected.get("columns", {}).keys())
        actual_cols = set(actual.get("columns", {}).keys())

        # Missing columns
        missing_cols = expected_cols - actual_cols
        for col in missing_cols:
            differences.append({"type": "missing_column", "column": col})

        # Extra columns
        extra_cols = actual_cols - expected_cols
        for col in extra_cols:
            differences.append({"type": "extra_column", "column": col})

        return differences

    def _generate_table_checksum(
        self, conn: sqlite3.Connection, table_name: str
    ) -> str:
        """Generate checksum for a specific table structure."""
        try:
            # Get table schema
            cursor = conn.execute(
                """
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name=?
            """,
                (table_name,),
            )

            result = cursor.fetchone()
            if result:
                schema_sql = result[0]
                return hashlib.sha256(schema_sql.encode("utf-8")).hexdigest()
            else:
                return ""

        except Exception:
            return ""
