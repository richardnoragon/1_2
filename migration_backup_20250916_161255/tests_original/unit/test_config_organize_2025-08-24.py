"""Configuration file for organize.py unit tests.

This module provides configuration constants and utilities for testing.
"""

import os
from datetime import datetime
from pathlib import Path

# Test configuration constants
TEST_DATE = "2025-08-24"
TARGET_MODULE = "organize.py"
TEST_MODULE = f"test_organize_{TEST_DATE}.py"

# File naming patterns
RESULT_PREFIX = "result_organize"
COVERAGE_PREFIX = "result_organize_coverage"

# Output file names
HTML_REPORT = f"{RESULT_PREFIX}_{TEST_DATE}.html"
JSON_REPORT = f"{RESULT_PREFIX}_{TEST_DATE}.json"
JUNIT_XML = f"{RESULT_PREFIX}_{TEST_DATE}_junit.xml"
COVERAGE_JSON = f"{COVERAGE_PREFIX}_{TEST_DATE}.json"
COVERAGE_HTML = f"{COVERAGE_PREFIX}_{TEST_DATE}"
SUMMARY_JSON = f"{RESULT_PREFIX}_{TEST_DATE}_summary.json"

# Test paths
TEST_DIR = Path("C:/Users/HP1/1_2/1_2/tests/unit")
PROJECT_ROOT = Path("C:/Users/HP1/1_2/1_2")

# Test categories covered
TEST_CATEGORIES = [
    "OrganizeRule dataclass functionality",
    "OrganizeWindow class methods",
    "File organization operations", 
    "UI component interactions",
    "Error handling and edge cases",
    "Rules management dialogs",
    "File pattern matching",
    "Directory operations",
    "Memory and performance tests"
]

# Expected test coverage areas
COVERAGE_AREAS = [
    "OrganizeRule.__init__",
    "OrganizeWindow.__init__",
    "OrganizeWindow._load_directory",
    "OrganizeWindow._organize_files",
    "OrganizeWindow._organize_single_file",
    "OrganizeWindow._move_file_to_destination",
    "OrganizeWindow._get_file_list",
    "OrganizeWindow._update_file_list",
    "OrganizeWindow._undo_last_organization",
    "RulesDialog.__init__",
    "RuleEditDialog.__init__",
    "main function"
]

def get_test_timestamp():
    """Get current timestamp for test execution."""
    return datetime.now().isoformat()

def get_test_session_info():
    """Get comprehensive test session information."""
    return {
        "execution_timestamp": get_test_timestamp(),
        "test_date": TEST_DATE,
        "target_module": TARGET_MODULE,
        "test_file": TEST_MODULE,
        "test_directory": str(TEST_DIR),
        "project_root": str(PROJECT_ROOT),
        "test_categories": TEST_CATEGORIES,
        "expected_coverage_areas": COVERAGE_AREAS,
        "output_files": {
            "html_report": HTML_REPORT,
            "json_report": JSON_REPORT,
            "junit_xml": JUNIT_XML,
            "coverage_json": COVERAGE_JSON,
            "coverage_html": COVERAGE_HTML,
            "summary": SUMMARY_JSON
        }
    }