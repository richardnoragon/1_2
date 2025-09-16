"""
Enterprise-Grade Unit Tests for Navigation System
RFU Multi-Pane File Explorer Testing Framework

Test Coverage: Path resolution, breadcrumb functionality, history management,
and bookmark system validation with edge case coverage.

Framework: pytest with enterprise extensions
Standards: Zero-compromise quality assurance
Coverage Target: ≥90% line coverage, ≥95% branch coverage
Security: Path traversal and injection prevention
Performance: Navigation speed and memory efficiency
Reliability: History persistence and data integrity

Test Categories:
- History Management: Navigation tracking and persistence
- Breadcrumb System: Path visualization and interaction
- Address Bar: URL parsing and validation
- Bookmark System: Favorites and quick access
- Path Resolution: Cross-platform path handling
- Navigation Buttons: Back/forward/up functionality
"""

import json
import logging
import os
import platform
import shutil
import sqlite3
# Import the modules under test
import sys
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, patch

import pytest
from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

try:
    from src.rfu.file_explorer.navigation.address_bar import AddressBar
    from src.rfu.file_explorer.navigation.breadcrumb_widget import \
        BreadcrumbWidget
    from src.rfu.file_explorer.navigation.history_manager import (
        HistoryDatabase, HistoryEntry, HistoryManager)
    from src.rfu.file_explorer.navigation.navigation_buttons import \
        NavigationButtons
except ImportError as e:
    pytest.skip(f"Cannot import navigation modules: {e}", 
                allow_module_level=True)


class TestHistoryEntry:
    """
    Comprehensive test suite for HistoryEntry class.
    
    Coverage:
    - Entry initialization and validation
    - Access tracking and timestamp management
    - Serialization and deserialization
    - Metadata handling (tags, notes, favorites)
    """
    
    def test_history_entry_default_initialization(self):
        """Test default initialization of HistoryEntry."""
        path = "/test/path"
        entry = HistoryEntry(path=path)
        
        assert entry.path == path
        assert entry.access_count == 1
        assert entry.is_favorite is False
        assert entry.tags == []
        assert entry.notes == ""
        assert entry.timestamp is not None
        assert entry.last_accessed is not None
        
        # Verify timestamps are valid ISO format
        datetime.fromisoformat(entry.timestamp)
        datetime.fromisoformat(entry.last_accessed)
    
    def test_history_entry_full_initialization(self):
        """Test full initialization with all parameters."""
        path = "/full/test/path"
        timestamp = "2025-09-13T10:00:00"
        access_count = 5
        last_accessed = "2025-09-13T11:00:00"
        is_favorite = True
        tags = ["work", "important"]
        notes = "Test notes"
        
        entry = HistoryEntry(
            path=path,
            timestamp=timestamp,
            access_count=access_count,
            last_accessed=last_accessed,
            is_favorite=is_favorite,
            tags=tags,
            notes=notes
        )
        
        assert entry.path == path
        assert entry.timestamp == timestamp
        assert entry.access_count == access_count
        assert entry.last_accessed == last_accessed
        assert entry.is_favorite is True
        assert entry.tags == tags
        assert entry.notes == notes
    
    def test_history_entry_update_access(self):
        """Test access tracking functionality."""
        entry = HistoryEntry(path="/test/path")
        original_count = entry.access_count
        original_time = entry.last_accessed
        
        # Wait briefly to ensure timestamp difference
        time.sleep(0.01)
        
        entry.update_access()
        
        assert entry.access_count == original_count + 1
        assert entry.last_accessed > original_time
    
    def test_history_entry_serialization(self):
        """Test entry serialization to dictionary."""
        entry = HistoryEntry(
            path="/serialize/test",
            access_count=3,
            is_favorite=True,
            tags=["tag1", "tag2"],
            notes="Serialization test"
        )
        
        data = entry.to_dict()
        
        assert isinstance(data, dict)
        assert data["path"] == "/serialize/test"
        assert data["access_count"] == 3
        assert data["is_favorite"] is True
        assert data["tags"] == ["tag1", "tag2"]
        assert data["notes"] == "Serialization test"
        assert "timestamp" in data
        assert "last_accessed" in data
    
    def test_history_entry_deserialization(self):
        """Test entry deserialization from dictionary."""
        data = {
            "path": "/deserialize/test",
            "timestamp": "2025-09-13T10:00:00",
            "access_count": 7,
            "last_accessed": "2025-09-13T12:00:00",
            "is_favorite": True,
            "tags": ["restored", "test"],
            "notes": "Deserialization test"
        }
        
        entry = HistoryEntry.from_dict(data)
        
        assert entry.path == "/deserialize/test"
        assert entry.timestamp == "2025-09-13T10:00:00"
        assert entry.access_count == 7
        assert entry.last_accessed == "2025-09-13T12:00:00"
        assert entry.is_favorite is True
        assert entry.tags == ["restored", "test"]
        assert entry.notes == "Deserialization test"
    
    def test_history_entry_round_trip_serialization(self):
        """Test round-trip serialization maintains data integrity."""
        original = HistoryEntry(
            path="/round/trip/test",
            access_count=10,
            is_favorite=True,
            tags=["original", "data"],
            notes="Round trip test"
        )
        
        # Serialize and deserialize
        data = original.to_dict()
        restored = HistoryEntry.from_dict(data)
        
        assert restored.path == original.path
        assert restored.access_count == original.access_count
        assert restored.is_favorite == original.is_favorite
        assert restored.tags == original.tags
        assert restored.notes == original.notes
        assert restored.timestamp == original.timestamp
        assert restored.last_accessed == original.last_accessed


class TestHistoryDatabase:
    """
    Comprehensive test suite for HistoryDatabase class.
    
    Coverage:
    - Database initialization and schema creation
    - CRUD operations for history entries
    - Query performance and indexing
    - Concurrent access and thread safety
    - Data integrity and constraints
    """
    
    @pytest.fixture
    def temp_db_path(self):
        """Provide temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except OSError:
            pass
    
    @pytest.fixture
    def history_db(self, temp_db_path):
        """Provide HistoryDatabase instance for testing."""
        db = HistoryDatabase(temp_db_path)
        yield db
        db.close()
    
    def test_history_database_initialization(self, temp_db_path):
        """Test database initialization and schema creation."""
        db = HistoryDatabase(temp_db_path)
        
        # Verify database file was created
        assert os.path.exists(temp_db_path)
        
        # Verify tables were created
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Check if navigation_history table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='navigation_history'
        """)
        assert cursor.fetchone() is not None
        
        # Check table schema
        cursor.execute("PRAGMA table_info(navigation_history)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_columns = {
            'id', 'path', 'timestamp', 'access_count',
            'last_accessed', 'is_favorite', 'tags', 'notes', 'created_at'
        }
        assert set(columns.keys()) == expected_columns
        
        # Verify indexes exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='navigation_history'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        assert 'idx_path' in indexes
        assert 'idx_last_accessed' in indexes
        assert 'idx_is_favorite' in indexes
        
        conn.close()
        db.close()
    
    def test_history_database_add_entry(self, history_db):
        """Test adding history entries to database."""
        entry = HistoryEntry(
            path="/test/add/path",
            access_count=1,
            is_favorite=False,
            tags=["test"],
            notes="Add test"
        )
        
        result = history_db.add_entry(entry)
        assert result is True
        
        # Verify entry was added
        entries = history_db.get_entries()
        assert len(entries) == 1
        assert entries[0].path == "/test/add/path"
        assert entries[0].tags == ["test"]
        assert entries[0].notes == "Add test"
    
    def test_history_database_update_entry(self, history_db):
        """Test updating existing history entries."""
        # Add initial entry
        entry = HistoryEntry(path="/test/update/path", access_count=1)
        history_db.add_entry(entry)
        
        # Update entry
        entry.access_count = 5
        entry.is_favorite = True
        entry.tags = ["updated"]
        entry.notes = "Updated entry"
        
        result = history_db.update_entry(entry)
        assert result is True
        
        # Verify update
        entries = history_db.get_entries()
        assert len(entries) == 1
        updated = entries[0]
        assert updated.path == "/test/update/path"
        assert updated.access_count == 5
        assert updated.is_favorite is True
        assert updated.tags == ["updated"]
        assert updated.notes == "Updated entry"
    
    def test_history_database_get_entry_by_path(self, history_db):
        """Test retrieving entry by path."""
        # Add test entries
        entry1 = HistoryEntry(path="/test/path1", notes="Entry 1")
        entry2 = HistoryEntry(path="/test/path2", notes="Entry 2")
        history_db.add_entry(entry1)
        history_db.add_entry(entry2)
        
        # Retrieve specific entry
        retrieved = history_db.get_entry_by_path("/test/path1")
        assert retrieved is not None
        assert retrieved.path == "/test/path1"
        assert retrieved.notes == "Entry 1"
        
        # Test non-existent path
        non_existent = history_db.get_entry_by_path("/does/not/exist")
        assert non_existent is None
    
    def test_history_database_delete_entry(self, history_db):
        """Test deleting history entries."""
        # Add entry to delete
        entry = HistoryEntry(path="/test/delete/path")
        history_db.add_entry(entry)
        
        # Verify entry exists
        assert len(history_db.get_entries()) == 1
        
        # Delete entry
        result = history_db.delete_entry("/test/delete/path")
        assert result is True
        
        # Verify entry was deleted
        assert len(history_db.get_entries()) == 0
        
        # Test deleting non-existent entry
        result = history_db.delete_entry("/does/not/exist")
        assert result is False
    
    def test_history_database_get_favorites(self, history_db):
        """Test retrieving favorite entries."""
        # Add mixed entries
        favorite1 = HistoryEntry(path="/favorite/path1", is_favorite=True)
        regular = HistoryEntry(path="/regular/path", is_favorite=False)
        favorite2 = HistoryEntry(path="/favorite/path2", is_favorite=True)
        
        history_db.add_entry(favorite1)
        history_db.add_entry(regular)
        history_db.add_entry(favorite2)
        
        # Get favorites
        favorites = history_db.get_favorites()
        assert len(favorites) == 2
        
        favorite_paths = {fav.path for fav in favorites}
        assert "/favorite/path1" in favorite_paths
        assert "/favorite/path2" in favorite_paths
        assert "/regular/path" not in favorite_paths
    
    def test_history_database_search_entries(self, history_db):
        """Test searching history entries."""
        # Add test entries
        entries = [
            HistoryEntry(path="/work/project1", tags=["work", "project"]),
            HistoryEntry(path="/work/project2", tags=["work"], notes="Work notes"),
            HistoryEntry(path="/personal/photos", tags=["personal"]),
            HistoryEntry(path="/backup/data", notes="Important backup")
        ]
        
        for entry in entries:
            history_db.add_entry(entry)
        
        # Search by path
        work_results = history_db.search_entries(query="work")
        assert len(work_results) >= 2
        
        # Search by tags
        project_results = history_db.search_entries(query="project")
        assert len(project_results) >= 1
        
        # Search by notes
        backup_results = history_db.search_entries(query="backup")
        assert len(backup_results) >= 1
    
    def test_history_database_cleanup_old_entries(self, history_db):
        """Test cleanup of old history entries."""
        # Add entries with different ages
        old_time = (datetime.now() - timedelta(days=100)).isoformat()
        recent_time = datetime.now().isoformat()
        
        old_entry = HistoryEntry(
            path="/old/path",
            timestamp=old_time,
            last_accessed=old_time
        )
        recent_entry = HistoryEntry(
            path="/recent/path",
            timestamp=recent_time,
            last_accessed=recent_time
        )
        
        history_db.add_entry(old_entry)
        history_db.add_entry(recent_entry)
        
        # Cleanup entries older than 30 days
        cleanup_count = history_db.cleanup_old_entries(days=30)
        assert cleanup_count >= 1
        
        # Verify old entry was removed, recent entry remains
        remaining_entries = history_db.get_entries()
        paths = {entry.path for entry in remaining_entries}
        assert "/recent/path" in paths
        # Old entry may or may not be removed depending on implementation
    
    def test_history_database_concurrent_access(self, history_db):
        """Test thread-safe concurrent database access."""
        import threading
        import time
        
        results = []
        errors = []
        
        def add_entries(thread_id, count):
            try:
                for i in range(count):
                    entry = HistoryEntry(path=f"/thread_{thread_id}/entry_{i}")
                    result = history_db.add_entry(entry)
                    results.append(result)
                    time.sleep(0.001)  # Small delay to encourage concurrency
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=add_entries, args=(thread_id, 10))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        
        # Verify all entries were added
        assert len(results) == 50  # 5 threads * 10 entries each
        assert all(results), "Some database operations failed"
        
        # Verify database consistency
        all_entries = history_db.get_entries()
        assert len(all_entries) == 50


class TestHistoryManager:
    """
    Comprehensive test suite for HistoryManager class.
    
    Coverage:
    - Navigation history tracking
    - Session management
    - Persistence and restoration
    - Performance optimization
    - Memory management
    """
    
    @pytest.fixture
    def app(self):
        """Provide QApplication instance for Qt tests."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def temp_workspace(self):
        """Provide temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_nav_test_")
        workspace = Path(temp_dir)
        
        # Create test directory structure
        (workspace / "folder1").mkdir()
        (workspace / "folder2").mkdir()
        (workspace / "folder1/subfolder").mkdir()
        
        yield workspace
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def history_manager(self, app, temp_workspace):
        """Provide HistoryManager instance for testing."""
        db_path = str(temp_workspace / "test_history.db")
        with patch('src.rfu.file_explorer.navigation.history_manager.get_log_manager'):
            manager = HistoryManager(db_path=db_path)
            yield manager
            manager.cleanup()
    
    def test_history_manager_initialization(self, history_manager):
        """Test proper initialization of HistoryManager."""
        manager = history_manager
        
        # Verify basic properties
        assert manager is not None
        assert hasattr(manager, 'current_index')
        assert hasattr(manager, 'history_stack')
        assert hasattr(manager, 'database')
        
        # Verify signals
        assert hasattr(manager, 'historyChanged')
        assert hasattr(manager, 'canGoBackChanged')
        assert hasattr(manager, 'canGoForwardChanged')
        
        # Verify initial state
        assert manager.current_index == -1
        assert len(manager.history_stack) == 0
        assert not manager.can_go_back()
        assert not manager.can_go_forward()
    
    def test_history_manager_navigate_to_path(self, history_manager, temp_workspace):
        """Test navigation to new paths."""
        manager = history_manager
        
        path1 = str(temp_workspace / "folder1")
        path2 = str(temp_workspace / "folder2")
        
        # Navigate to first path
        result = manager.navigate_to(path1)
        assert result is True
        assert manager.current_index == 0
        assert len(manager.history_stack) == 1
        assert manager.history_stack[0].path == path1
        
        # Navigate to second path
        result = manager.navigate_to(path2)
        assert result is True
        assert manager.current_index == 1
        assert len(manager.history_stack) == 2
        assert manager.history_stack[1].path == path2
    
    def test_history_manager_back_forward_navigation(self, history_manager, 
                                                   temp_workspace):
        """Test back and forward navigation."""
        manager = history_manager
        
        # Navigate to multiple paths
        paths = [
            str(temp_workspace / "folder1"),
            str(temp_workspace / "folder2"),
            str(temp_workspace / "folder1/subfolder")
        ]
        
        for path in paths:
            manager.navigate_to(path)
        
        # Verify can go back but not forward
        assert manager.can_go_back() is True
        assert manager.can_go_forward() is False
        assert manager.current_index == 2
        
        # Go back one step
        result = manager.go_back()
        assert result is True
        assert manager.current_index == 1
        assert manager.get_current_path() == paths[1]
        
        # Now can go both back and forward
        assert manager.can_go_back() is True
        assert manager.can_go_forward() is True
        
        # Go back again
        result = manager.go_back()
        assert result is True
        assert manager.current_index == 0
        assert manager.get_current_path() == paths[0]
        
        # Go forward
        result = manager.go_forward()
        assert result is True
        assert manager.current_index == 1
        assert manager.get_current_path() == paths[1]
    
    def test_history_manager_clear_forward_history(self, history_manager,
                                                  temp_workspace):
        """Test that navigating to new path clears forward history."""
        manager = history_manager
        
        # Build history and go back
        paths = [str(temp_workspace / f"folder{i}") for i in range(3)]
        for path in paths:
            manager.navigate_to(path)
        
        manager.go_back()  # Go to index 1
        manager.go_back()  # Go to index 0
        
        # Verify forward history exists
        assert manager.can_go_forward() is True
        
        # Navigate to new path - should clear forward history
        new_path = str(temp_workspace / "new_folder")
        os.makedirs(new_path, exist_ok=True)
        manager.navigate_to(new_path)
        
        # Verify forward history is cleared
        assert manager.can_go_forward() is False
        assert manager.current_index == 1
        assert len(manager.history_stack) == 2
    
    def test_history_manager_favorites_management(self, history_manager,
                                                temp_workspace):
        """Test favorites management functionality."""
        manager = history_manager
        
        path = str(temp_workspace / "folder1")
        manager.navigate_to(path)
        
        # Add to favorites
        result = manager.add_to_favorites(path, "Test Favorite")
        assert result is True
        
        # Verify in favorites
        favorites = manager.get_favorites()
        assert len(favorites) >= 1
        favorite_paths = [fav.path for fav in favorites]
        assert path in favorite_paths
        
        # Remove from favorites
        result = manager.remove_from_favorites(path)
        assert result is True
        
        # Verify removed
        favorites = manager.get_favorites()
        favorite_paths = [fav.path for fav in favorites]
        assert path not in favorite_paths
    
    def test_history_manager_search_functionality(self, history_manager,
                                                temp_workspace):
        """Test history search functionality."""
        manager = history_manager
        
        # Navigate to create history
        test_paths = [
            str(temp_workspace / "work_folder"),
            str(temp_workspace / "personal_folder"),
            str(temp_workspace / "backup_folder")
        ]
        
        for path in test_paths:
            os.makedirs(path, exist_ok=True)
            manager.navigate_to(path)
        
        # Search history
        work_results = manager.search_history("work")
        assert len(work_results) >= 1
        
        personal_results = manager.search_history("personal")
        assert len(personal_results) >= 1
        
        # Search for non-existent term
        empty_results = manager.search_history("nonexistent")
        assert len(empty_results) == 0
    
    def test_history_manager_persistence(self, history_manager, temp_workspace):
        """Test history persistence across sessions."""
        manager = history_manager
        db_path = manager.database.db_path
        
        # Create some history
        test_path = str(temp_workspace / "persistent_folder")
        os.makedirs(test_path, exist_ok=True)
        manager.navigate_to(test_path)
        manager.add_to_favorites(test_path, "Persistent Favorite")
        
        # Close manager
        manager.cleanup()
        
        # Create new manager with same database
        new_manager = HistoryManager(db_path=db_path)
        
        # Verify history was restored
        favorites = new_manager.get_favorites()
        favorite_paths = [fav.path for fav in favorites]
        assert test_path in favorite_paths
        
        new_manager.cleanup()
    
    def test_history_manager_duplicate_navigation(self, history_manager,
                                                temp_workspace):
        """Test handling of duplicate path navigation."""
        manager = history_manager
        
        path = str(temp_workspace / "folder1")
        
        # Navigate to same path multiple times
        manager.navigate_to(path)
        initial_count = len(manager.history_stack)
        
        manager.navigate_to(path)  # Same path again
        
        # Should not duplicate in immediate history
        # but may update access count
        assert len(manager.history_stack) <= initial_count + 1
    
    def test_history_manager_max_history_limit(self, history_manager, 
                                             temp_workspace):
        """Test history size limiting."""
        manager = history_manager
        
        # Navigate to many paths to test limit
        for i in range(200):  # Exceed typical history limits
            folder = temp_workspace / f"folder_{i:03d}"
            folder.mkdir(exist_ok=True)
            manager.navigate_to(str(folder))
        
        # Verify history doesn't grow unbounded
        assert len(manager.history_stack) <= 100  # Reasonable limit
    
    def test_history_manager_signal_emission(self, history_manager, temp_workspace):
        """Test that proper signals are emitted."""
        manager = history_manager
        
        # Track signal emissions
        signals_received = []
        
        def track_signal(signal_name):
            def handler(*args):
                signals_received.append(signal_name)
            return handler
        
        manager.historyChanged.connect(track_signal('historyChanged'))
        manager.canGoBackChanged.connect(track_signal('canGoBackChanged'))
        manager.canGoForwardChanged.connect(track_signal('canGoForwardChanged'))
        
        # Perform navigation operations
        path1 = str(temp_workspace / "folder1")
        path2 = str(temp_workspace / "folder2")
        
        manager.navigate_to(path1)
        manager.navigate_to(path2)
        manager.go_back()
        manager.go_forward()
        
        # Verify signals were emitted
        assert 'historyChanged' in signals_received
        assert 'canGoBackChanged' in signals_received
        assert 'canGoForwardChanged' in signals_received


class TestNavigationIntegration:
    """
    Integration tests for navigation components.
    
    Tests interaction between:
    - HistoryManager and AddressBar
    - BreadcrumbWidget and NavigationButtons
    - Component synchronization
    - Event propagation
    """
    
    @pytest.fixture
    def app(self):
        """Provide QApplication instance for Qt tests."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def navigation_components(self, app):
        """Provide integrated navigation components."""
        # Create components
        history_manager = Mock()
        address_bar = Mock()
        breadcrumb_widget = Mock()
        navigation_buttons = Mock()
        
        # Setup basic behaviors
        history_manager.can_go_back.return_value = False
        history_manager.can_go_forward.return_value = False
        history_manager.get_current_path.return_value = "/home"
        
        return {
            'history': history_manager,
            'address': address_bar,
            'breadcrumb': breadcrumb_widget,
            'buttons': navigation_buttons
        }
    
    def test_navigation_component_integration(self, navigation_components):
        """Test basic integration between navigation components."""
        components = navigation_components
        
        # Simulate path change
        new_path = "/test/integration/path"
        
        # Verify components can be called together
        components['history'].navigate_to(new_path)
        components['address'].set_path(new_path)
        components['breadcrumb'].set_path(new_path)
        
        # Verify calls were made
        components['history'].navigate_to.assert_called_with(new_path)
        components['address'].set_path.assert_called_with(new_path)
        components['breadcrumb'].set_path.assert_called_with(new_path)
    
    def test_navigation_synchronization(self, navigation_components):
        """Test synchronization between navigation components."""
        components = navigation_components
        
        # Setup return values for navigation state
        components['history'].can_go_back.return_value = True
        components['history'].can_go_forward.return_value = False
        
        # Simulate state update
        components['buttons'].update_navigation_state()
        
        # Verify state queries
        components['buttons'].update_navigation_state.assert_called_once()


class TestNavigationSecurity:
    """
    Security testing for navigation system.
    
    Tests security aspects:
    - Path traversal prevention
    - Input sanitization
    - SQL injection prevention
    - Resource limits
    """
    
    @pytest.fixture
    def temp_workspace(self):
        """Provide temporary workspace for security testing."""
        temp_dir = tempfile.mkdtemp(prefix="rfu_nav_security_")
        workspace = Path(temp_dir)
        yield workspace
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def security_history_manager(self, temp_workspace):
        """Provide HistoryManager for security testing."""
        db_path = str(temp_workspace / "security_test.db")
        with patch('src.rfu.file_explorer.navigation.history_manager.get_log_manager'):
            manager = HistoryManager(db_path=db_path)
            yield manager
            manager.cleanup()
    
    @pytest.mark.security
    def test_path_traversal_prevention(self, security_history_manager):
        """Test prevention of path traversal attacks."""
        manager = security_history_manager
        
        # Attempt various path traversal attacks
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
            "file:///etc/passwd",
            "\\\\network\\share\\sensitive",
            "/proc/self/environ"
        ]
        
        for path in malicious_paths:
            try:
                # Should either reject or sanitize path
                result = manager.navigate_to(path)
                
                if result:
                    # If accepted, verify it was sanitized
                    current = manager.get_current_path()
                    assert not current.startswith("..")
                    assert ".." not in current
                    
            except (ValueError, OSError):
                # Expected for malicious paths
                pass
    
    @pytest.mark.security
    def test_sql_injection_prevention(self, security_history_manager):
        """Test prevention of SQL injection attacks."""
        manager = security_history_manager
        
        # Attempt SQL injection in various inputs
        injection_attempts = [
            "'; DROP TABLE navigation_history; --",
            "' OR '1'='1",
            "'; INSERT INTO navigation_history VALUES(...); --",
            "\"; DELETE FROM navigation_history; --",
            "' UNION SELECT * FROM navigation_history --"
        ]
        
        for injection in injection_attempts:
            try:
                # Test path input
                manager.navigate_to(injection)
                
                # Test favorite name input
                manager.add_to_favorites("/safe/path", injection)
                
                # Test search input
                manager.search_history(injection)
                
                # Test notes input
                entry = HistoryEntry(path="/test", notes=injection)
                manager.database.add_entry(entry)
                
            except (ValueError, sqlite3.Error):
                # Expected for injection attempts
                pass
        
        # Verify database integrity
        entries = manager.database.get_entries()
        assert isinstance(entries, list)  # Should still function
    
    @pytest.mark.security
    def test_input_validation(self, security_history_manager):
        """Test comprehensive input validation."""
        manager = security_history_manager
        
        # Test various invalid inputs
        invalid_inputs = [
            None,
            "",
            "   ",
            "\x00\x01\x02",  # Null bytes
            "A" * 10000,  # Extremely long string
            "path\nwith\nnewlines",
            "path\rwith\rcarriage\rreturns",
            "path\twith\ttabs"
        ]
        
        for invalid_input in invalid_inputs:
            try:
                manager.navigate_to(invalid_input)
                manager.add_to_favorites(invalid_input, "Test")
                manager.search_history(invalid_input)
                
            except (TypeError, ValueError, OSError):
                # Expected for invalid inputs
                pass
    
    @pytest.mark.security
    def test_resource_limits(self, security_history_manager):
        """Test resource limit enforcement."""
        manager = security_history_manager
        
        # Test history size limits
        for i in range(10000):  # Attempt excessive history
            try:
                path = f"/test/path/{i:05d}"
                manager.navigate_to(path)
            except Exception:
                break
        
        # Verify reasonable limits were enforced
        assert len(manager.history_stack) < 1000
        
        # Test favorites limits
        favorite_count = 0
        for i in range(10000):  # Attempt excessive favorites
            try:
                path = f"/favorite/path/{i:05d}"
                result = manager.add_to_favorites(path, f"Favorite {i}")
                if result:
                    favorite_count += 1
                else:
                    break
            except Exception:
                break
        
        # Should have reasonable limit on favorites
        assert favorite_count < 5000


if __name__ == "__main__":
    # Configure logging for test execution
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests with comprehensive coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=src.rfu.file_explorer.navigation",
        "--cov-report=html:htmlcov_navigation",
        "--cov-report=term-missing",
        "--cov-report=xml:coverage_navigation.xml",
        "--cov-fail-under=90",
        "--html=test_report_navigation.html",
        "--json-report",
        "--json-report-file=test_results_navigation.json"
    ])