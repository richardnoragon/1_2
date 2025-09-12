"""Advanced Folders Testing Configuration - Phase 1 Week 2."""

import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest

# Import our new Phase 1 Week 2 components
from src.rfu.advanced_folders.models.folder_configuration import (
    FolderConfiguration,
    DirectoryTarget,
    PerformanceSettings,
    SecuritySettings
)
from src.rfu.advanced_folders.models.search_parameters import (
    SearchParameters,
    FileTypeFilter,
    SizeFilter,
    DateFilter,
    ContentSearchOptions
)
from src.rfu.advanced_folders.validation.validator_framework import (
    ValidationFramework
)
from src.rfu.advanced_folders.repository.folder_repository import (
    DatabaseConnectionManager,
    FolderRepository
)
from src.rfu.advanced_folders.error_handling.error_handler import (
    ErrorHandler,
    GracefulDegradation
)


class TestConfig:
    """Testing configuration and constants."""
    
    TEST_DB_NAME = ":memory:"
    TEST_DATA_DIR = Path(__file__).parent / "data"
    TEST_TEMP_DIR = Path(tempfile.gettempdir()) / "advanced_folders_tests"
    
    # Test folder configurations
    SAMPLE_FOLDER_CONFIGS = [
        {
            "name": "Documents",
            "path": "/test/documents",
            "folder_type": FolderType.SMART,
            "auto_organize": True,
            "priority": 1
        },
        {
            "name": "Downloads",
            "path": "/test/downloads",
            "folder_type": FolderType.MONITORED,
            "auto_organize": False,
            "priority": 2
        },
        {
            "name": "Archive",
            "path": "/test/archive",
            "folder_type": FolderType.ARCHIVE,
            "auto_organize": True,
            "priority": 3
        }
    ]
    
    # Test search parameters
    SAMPLE_SEARCH_PARAMS = [
        {
            "folder_config_id": 1,
            "name": "PDF Files",
            "pattern": "*.pdf",
            "case_sensitive": False,
            "include_subdirs": True
        },
        {
            "folder_config_id": 1,
            "name": "Large Files",
            "min_size": 100 * 1024 * 1024,  # 100MB
            "case_sensitive": False,
            "include_subdirs": True
        }
    ]
    
    # Test file metadata
    SAMPLE_FILE_METADATA = [
        {
            "folder_config_id": 1,
            "file_path": "/test/documents/sample.pdf",
            "file_name": "sample.pdf",
            "file_size": 1024 * 1024,  # 1MB
            "file_type": "pdf",
            "checksum": "abcd1234"
        },
        {
            "folder_config_id": 2,
            "file_path": "/test/downloads/archive.zip",
            "file_name": "archive.zip",
            "file_size": 50 * 1024 * 1024,  # 50MB
            "file_type": "zip",
            "checksum": "efgh5678"
        }
    ]


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """Provide test configuration."""
    return TestConfig()


@pytest.fixture
def temp_db() -> Generator[str, None, None]:
    """Create a temporary in-memory database for testing."""
    db_path = ":memory:"
    yield db_path


@pytest.fixture
def db_manager(temp_db: str) -> Generator[AdvancedFoldersDBManager, None, None]:
    """Create a database manager with test database."""
    # Mock the main database manager
    mock_main_db = MagicMock()
    mock_main_db.get_connection.return_value = sqlite3.connect(temp_db)
    
    with patch('src.utilities.advanced_folders.database.database_manager.get_database_manager', 
               return_value=mock_main_db):
        manager = AdvancedFoldersDBManager()
        yield manager


@pytest.fixture
def sample_folder_config() -> FolderConfiguration:
    """Create a sample folder configuration for testing."""
    return FolderConfiguration(
        name="Test Folder",
        path="/test/path",
        folder_type=FolderType.SMART,
        auto_organize=True,
        priority=1,
        description="Test folder configuration"
    )


@pytest.fixture
def sample_search_parameter() -> SearchParameter:
    """Create a sample search parameter for testing."""
    return SearchParameter(
        folder_config_id=1,
        name="Test Search",
        pattern="*.txt",
        case_sensitive=False,
        include_subdirs=True
    )


@pytest.fixture
def sample_file_metadata() -> FileMetadata:
    """Create a sample file metadata for testing."""
    return FileMetadata(
        folder_config_id=1,
        file_path="/test/path/file.txt",
        file_name="file.txt",
        file_size=1024,
        file_type="txt",
        checksum="test_checksum"
    )


@pytest.fixture
def configuration_manager() -> Generator[ConfigurationManager, None, None]:
    """Create a configuration manager for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = Path(f.name)
    
    try:
        manager = ConfigurationManager(config_path)
        yield manager
    finally:
        if config_path.exists():
            config_path.unlink()


@pytest.fixture
def test_data_setup(db_manager: AdvancedFoldersDBManager, 
                   test_config: TestConfig) -> Dict[str, Any]:
    """Set up test data in the database."""
    # Create folder configurations
    folder_ids = []
    for config_data in test_config.SAMPLE_FOLDER_CONFIGS:
        folder_config = FolderConfiguration(**config_data)
        folder_id = db_manager.create_folder_configuration(folder_config)
        folder_ids.append(folder_id)
    
    # Create search parameters
    search_ids = []
    for search_data in test_config.SAMPLE_SEARCH_PARAMS:
        search_param = SearchParameter(**search_data)
        search_id = db_manager.create_search_parameter(search_param)
        search_ids.append(search_id)
    
    # Create file metadata
    metadata_ids = []
    for metadata_data in test_config.SAMPLE_FILE_METADATA:
        file_metadata = FileMetadata(**metadata_data)
        metadata_id = db_manager.insert_file_metadata(file_metadata)
        metadata_ids.append(metadata_id)
    
    return {
        'folder_ids': folder_ids,
        'search_ids': search_ids,
        'metadata_ids': metadata_ids
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", 
        "unit: marks tests as unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", 
        "integration: marks tests as integration tests (slower, database)"
    )
    config.addinivalue_line(
        "markers", 
        "performance: marks tests as performance tests (timing sensitive)"
    )
    config.addinivalue_line(
        "markers", 
        "database: marks tests that require database access"
    )
    config.addinivalue_line(
        "markers", 
        "filesystem: marks tests that require filesystem access"
    )


# Custom assertions
def assert_folder_config_equal(actual: FolderConfiguration, 
                              expected: FolderConfiguration) -> None:
    """Assert that two folder configurations are equal."""
    assert actual.name == expected.name
    assert actual.path == expected.path
    assert actual.folder_type == expected.folder_type
    assert actual.auto_organize == expected.auto_organize
    assert actual.priority == expected.priority
    assert actual.description == expected.description


def assert_search_param_equal(actual: SearchParameter, 
                             expected: SearchParameter) -> None:
    """Assert that two search parameters are equal."""
    assert actual.folder_config_id == expected.folder_config_id
    assert actual.name == expected.name
    assert actual.pattern == expected.pattern
    assert actual.case_sensitive == expected.case_sensitive
    assert actual.include_subdirs == expected.include_subdirs


def assert_file_metadata_equal(actual: FileMetadata, 
                              expected: FileMetadata) -> None:
    """Assert that two file metadata objects are equal."""
    assert actual.folder_config_id == expected.folder_config_id
    assert actual.file_path == expected.file_path
    assert actual.file_name == expected.file_name
    assert actual.file_size == expected.file_size
    assert actual.file_type == expected.file_type
    assert actual.checksum == expected.checksum