#!/usr/bin/env python3
"""
Test Database Creation Script
Creates SQLite databases for dev, staging, and prod-like environments
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path


def create_test_database(db_path: str, environment: str):
    """Create a test database with sample schema and data."""

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute(
        """
        CREATE TABLE files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_size INTEGER,
            file_type TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum TEXT,
            environment TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE file_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            metadata_key TEXT NOT NULL,
            metadata_value TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES files (id)
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE processing_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_date TIMESTAMP,
            completed_date TIMESTAMP,
            error_message TEXT,
            environment TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preference_key TEXT NOT NULL,
            preference_value TEXT,
            user_id TEXT DEFAULT 'test_user',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Insert sample data based on environment
    sample_files = [
        (
            f"test_file_1_{environment}.txt",
            f"/test/data/test_file_1_{environment}.txt",
            1024,
            "text",
            environment,
        ),
        (
            f"test_file_2_{environment}.pdf",
            f"/test/data/test_file_2_{environment}.pdf",
            2048,
            "pdf",
            environment,
        ),
        (
            f"test_file_3_{environment}.jpg",
            f"/test/data/test_file_3_{environment}.jpg",
            4096,
            "image",
            environment,
        ),
    ]

    for filename, filepath, size, file_type, env in sample_files:
        cursor.execute(
            """
            INSERT INTO files (filename, filepath, file_size, file_type, environment)
            VALUES (?, ?, ?, ?, ?)
        """,
            (filename, filepath, size, file_type, env),
        )

    # Insert sample metadata
    cursor.execute(
        """
        INSERT INTO file_metadata (file_id, metadata_key, metadata_value)
        VALUES (1, 'author', 'test_user'), (1, 'description', 'Test file for integration testing')
    """
    )

    # Insert sample processing jobs
    sample_jobs = [
        (f"backup_job_{environment}", "completed", environment),
        (f"compression_job_{environment}", "pending", environment),
        (f"validation_job_{environment}", "running", environment),
    ]

    for job_name, status, env in sample_jobs:
        cursor.execute(
            """
            INSERT INTO processing_jobs (job_name, status, environment)
            VALUES (?, ?, ?)
        """,
            (job_name, status, env),
        )

    # Insert sample user preferences
    sample_prefs = [
        ("theme", "dark"),
        ("auto_backup", "true"),
        ("compression_level", "5"),
        ("notification_enabled", "true"),
    ]

    for key, value in sample_prefs:
        cursor.execute(
            """
            INSERT INTO user_preferences (preference_key, preference_value)
            VALUES (?, ?)
        """,
            (key, value),
        )

    # Commit and close
    conn.commit()
    conn.close()

    print(f"✅ Created test database for {environment} environment: {db_path}")


def main():
    """Create test databases for all environments."""

    base_path = Path(__file__).parent.parent
    data_dir = base_path / "data"

    environments = ["dev", "staging", "prod-like"]

    print("🗃️ Creating test databases for integration testing...")

    for env in environments:
        db_path = data_dir / f"test_{env}.db"
        create_test_database(str(db_path), env)

    print(f"\n🎉 All test databases created successfully!")
    print(f"📁 Database location: {data_dir}")


if __name__ == "__main__":
    main()
