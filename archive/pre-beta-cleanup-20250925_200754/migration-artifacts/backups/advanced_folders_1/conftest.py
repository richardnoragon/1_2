"""
Advanced Folders Testing Configuration - Phase 1 Week 2.

Provides fixtures and utilities for testing the new Advanced Folders
components implemented in Phase 1 Week 2.
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator
from unittest.mock import Mock

import pytest

from src.tools.file_management.advanced_folders_legacy.error_handling.error_handler import (
    ErrorHandler, GracefulDegradation)
# Import our new Phase 1 Week 2 components
from src.tools.file_management.advanced_folders_legacy.models.folder_configuration import (
    DirectoryTarget, FolderConfiguration, PerformanceSettings,
    SecuritySettings)
from src.tools.file_management.advanced_folders_legacy.models.search_parameters import (
    ContentSearchOptions, DateFilter, FileTypeFilter, SearchParameters,
    SizeFilter)
from src.tools.file_management.advanced_folders_legacy.repository.folder_repository import (
    DatabaseConnectionManager, FolderRepository)
from src.tools.file_management.advanced_folders_legacy.validation.validator_framework import \
    ValidationFramework


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for testing."""
    import shutil
    import tempfile
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_db() -> Generator[Path, None, None]:
    """Create temporary SQLite database for testing."""
    temp_db_path = Path(tempfile.mktemp(suffix='.db'))
    try:
        yield temp_db_path
    finally:
        if temp_db_path.exists():
            temp_db_path.unlink()


@pytest.fixture
def mock_logger():
    """Create mock logger for testing."""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def validation_framework():
    """Create ValidationFramework instance for testing."""
    return ValidationFramework()


@pytest.fixture
def error_handler(mock_logger):
    """Create ErrorHandler instance for testing."""
    return ErrorHandler(logger=mock_logger)


@pytest.fixture
def graceful_degradation(error_handler):
    """Create GracefulDegradation instance for testing."""
    return GracefulDegradation(error_handler=error_handler)


@pytest.fixture
def sample_directory_target(temp_dir):
    """Create sample DirectoryTarget for testing."""
    return DirectoryTarget(
        path=temp_dir / "test_folder",
        name="Test Folder",
        description="A test folder configuration"
    )


@pytest.fixture
def sample_performance_settings():
    """Create sample PerformanceSettings for testing."""
    return PerformanceSettings(
        max_search_depth=10,
        timeout_seconds=30,
        max_results=1000,
        enable_caching=True,
        cache_duration_minutes=60
    )


@pytest.fixture
def sample_security_settings():
    """Create sample SecuritySettings for testing."""
    return SecuritySettings(
        restrict_access=True,
        allowed_extensions={".txt", ".pdf", ".docx"},
        blocked_paths={"/system", "/windows"},
        require_confirmation=True
    )


@pytest.fixture
def sample_folder_configuration(
    sample_directory_target,
    sample_performance_settings,
    sample_security_settings
):
    """Create sample FolderConfiguration for testing."""
    return FolderConfiguration(
        name="Test Configuration",
        directory_targets=[sample_directory_target],
        enabled=True,
        description="Test folder configuration",
        performance_settings=sample_performance_settings,
        security_settings=sample_security_settings
    )


@pytest.fixture
def sample_file_type_filter():
    """Create sample FileTypeFilter for testing."""
    return FileTypeFilter(
        include_extensions={".txt", ".pdf"},
        exclude_extensions={".tmp", ".log"},
        include_mime_types={"text/plain", "application/pdf"},
        exclude_mime_types={"application/x-executable"}
    )


@pytest.fixture
def sample_size_filter():
    """Create sample SizeFilter for testing."""
    return SizeFilter(
        min_size_bytes=1024,  # 1KB
        max_size_bytes=1048576  # 1MB
    )


@pytest.fixture
def sample_date_filter():
    """Create sample DateFilter for testing."""
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return DateFilter(
        created_after=base_date,
        created_before=datetime(2024, 12, 31, tzinfo=timezone.utc),
        modified_after=base_date,
        modified_before=datetime(2024, 12, 31, tzinfo=timezone.utc)
    )


@pytest.fixture
def sample_content_search_options():
    """Create sample ContentSearchOptions for testing."""
    return ContentSearchOptions(
        search_text=True,
        search_metadata=True,
        case_sensitive=False,
        use_regex=False,
        encoding="utf-8"
    )


@pytest.fixture
def sample_search_parameters(
    sample_file_type_filter,
    sample_size_filter,
    sample_date_filter,
    sample_content_search_options
):
    """Create sample SearchParameters for testing."""
    return SearchParameters(
        query="test query",
        file_type_filter=sample_file_type_filter,
        size_filter=sample_size_filter,
        date_filter=sample_date_filter,
        content_search_options=sample_content_search_options,
        max_results=100,
        timeout_seconds=30
    )


@pytest.fixture
def db_connection_manager(temp_db):
    """Create DatabaseConnectionManager for testing."""
    return DatabaseConnectionManager(str(temp_db))


@pytest.fixture
def folder_repository(db_connection_manager, validation_framework):
    """Create FolderRepository for testing."""
    return FolderRepository(db_connection_manager, validation_framework)


# Configure pytest with custom markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "database: Database tests")
    config.addinivalue_line("markers", "validation: Validation tests")
    config.addinivalue_line("markers", "error_handling: Error handling tests")