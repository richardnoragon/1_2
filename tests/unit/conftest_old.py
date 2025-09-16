"""""""""#!/usr/bin/env python3#!/usr/bin/env python3

Simple conftest.py for Size Analyzer testing

Created: August 22, 2025Pytest configuration and shared fixtures for Size Analyzer tests

"""

Pytest configuration and shared fixtures for Size Analyzer tests

import sys

import osFile: conftest.py

from pathlib import Path

Target: Size Analyzer comprehensive testing""""""

# Add project root to Python path

project_root = Path(__file__).parent.parent.parentCreated: August 22nd 2025

sys.path.insert(0, str(project_root))

Framework: pytestFile: conftest.py

# Simple test configuration

def pytest_configure(config):"""

    """Configure pytest with basic settings."""

    passTarget: Size Analyzer comprehensive testingPytest configuration and shared fixtures for Size Analyzer testsPytest configuration and shared fixtures for Size Analyzer tests



def pytest_collection_modifyitems(config, items):import os

    """Modify test collection."""

    passimport sysCreated: August 22, 2025

import pytest

import tempfileFramework: pytest

import shutil

from unittest.mock import MagicMock, patch"""

from datetime import datetime

from pathlib import PathFile: conftest.pyFile: conftest.py



# Add project root to Python pathimport os

project_root = Path(__file__).parent.parent.parent

sys.path.insert(0, str(project_root))import sysTarget: Size Analyzer comprehensive testingTarget: Size Analyzer comprehensive testing



import pytest

@pytest.fixture(scope="session")

def test_session_info():import tempfileCreated: 2025-08-22Created: 2025-08-22

    """Provide test session information."""

    return {import shutil

        'start_time': datetime.now(),

        'test_date': 'August 22nd 2025',from unittest.mock import MagicMock, patchFramework: pytestFramework: pytest

        'target_module': 'size_analyzer',

        'framework': 'pytest',from datetime import datetime

        'coverage_threshold': 85

    }from pathlib import Path"""





@pytest.fixture(scope="function") 

def mock_pyqt5_environment():# Add project root to Python pathThis file provides shared test fixtures, setup/teardown methods,

    """Mock PyQt5 environment to avoid GUI dependencies."""

    mock_modules = {project_root = Path(__file__).parent.parent.parent

        'PyQt5': MagicMock(),

        'PyQt5.QtWidgets': MagicMock(),sys.path.insert(0, str(project_root))import osand configuration for all Size Analyzer unit tests.

        'PyQt5.QtCore': MagicMock(),

        'PyQt5.QtGui': MagicMock(),

    }

    import sys"""

    with patch.dict('sys.modules', mock_modules):

        yield mock_modules@pytest.fixture(scope="session")



def test_session_info():import pytest

@pytest.fixture(scope="session", autouse=True)

def test_session_setup_teardown():    """Provide test session information."""

    """Session-level setup and teardown."""

    print("\n" + "="*60)    return {import tempfileimport os

    print("STARTING SIZE ANALYZER COMPREHENSIVE TEST SUITE")

    print("Test Date: August 22nd 2025")        'start_time': datetime.now(),

    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("Target Module: src.utilities.analysis.size_analyzer")        'test_date': 'August 22, 2025',import shutilimport sys

    print("="*60)

            'target_module': 'size_analyzer',

    yield

            'framework': 'pytest',from unittest.mock import MagicMock, patchimport pytest

    print("\n" + "="*60)

    print("SIZE ANALYZER TEST SUITE COMPLETED")        'coverage_threshold': 85

    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("="*60)    }from datetime import datetimeimport tempfile



from pathlib import Pathimport shutil

@pytest.fixture(scope="function")

def mock_pyqt5_environment():from unittest.mock import MagicMock, patch

    """Mock PyQt5 environment to avoid GUI dependencies during testing."""

    mock_modules = {# Add project root to Python pathfrom datetime import datetime

        'PyQt5': MagicMock(),

        'PyQt5.QtWidgets': MagicMock(),project_root = Path(__file__).parent.parent.parentfrom pathlib import Path

        'PyQt5.QtCore': MagicMock(),

        'PyQt5.QtGui': MagicMock(),sys.path.insert(0, str(project_root))

    }

    # Add project root to Python path

    # Mock specific Qt widgets and classes

    mock_qt_widgets = MagicMock()project_root = Path(__file__).parent.parent.parent

    mock_qt_widgets.QMainWindow = MagicMock()

    mock_qt_widgets.QWidget = MagicMock()@pytest.fixture(scope="session")sys.path.insert(0, str(project_root))

    mock_qt_widgets.QVBoxLayout = MagicMock()

    mock_qt_widgets.QHBoxLayout = MagicMock()def test_session_info():

    mock_qt_widgets.QPushButton = MagicMock()

    mock_qt_widgets.QLabel = MagicMock()    """Provide test session information."""

    mock_qt_widgets.QListWidget = MagicMock()

    mock_qt_widgets.QProgressBar = MagicMock()    return {class MockHubInstance:

    mock_qt_widgets.QApplication = MagicMock()

    mock_qt_widgets.QMessageBox = MagicMock()        'start_time': datetime.now(),    """Mock hub instance for testing hub integration."""

    mock_qt_widgets.QFileDialog = MagicMock()

    mock_qt_widgets.QGroupBox = MagicMock()        'test_date': '2025-08-22',    

    

    mock_modules['PyQt5.QtWidgets'] = mock_qt_widgets        'target_module': 'size_analyzer',    def __init__(self):

    

    with patch.dict('sys.modules', mock_modules):        'framework': 'pytest',        self.registered_tools = {}

        yield mock_modules

        'coverage_threshold': 85        self.messages = []



@pytest.fixture(scope="function")    }        self.events = []

def mock_standard_window():

    """Mock StandardWindow for testing without GUI dependencies."""        self.resources = {}

    mock_window = MagicMock()

    mock_window.main_layout = MagicMock()        self.tool_progress = {}

    mock_window.menu_manager = MagicMock()

    mock_window.ensure_menu_bar = MagicMock()@pytest.fixture(scope="function")        

    

    with patch('src.tools.analysis.size_analyzer.StandardWindow', def mock_pyqt5_environment():    def register_tool(self, tool_name: str, connector):

               return_value=mock_window):

        yield mock_window    """Mock PyQt5 environment to avoid GUI dependencies during testing."""        """Register a tool with the mock hub."""



    mock_modules = {        self.registered_tools[tool_name] = connector

@pytest.fixture(scope="function")

def temp_test_directory():        'PyQt5': MagicMock(),        return True

    """Create temporary directory for test file operations."""

    temp_dir = tempfile.mkdtemp(prefix="size_analyzer_test_")        'PyQt5.QtWidgets': MagicMock(),    

    

    # Create sample directory structure for testing        'PyQt5.QtCore': MagicMock(),    def unregister_tool(self, tool_name: str):

    test_structure = {

        'folder1': {        'PyQt5.QtGui': MagicMock(),        """Unregister a tool from the mock hub."""

            'file1.txt': 'Test content for file 1',

            'file2.txt': 'Test content for file 2',    }        if tool_name in self.registered_tools:

            'subfolder1': {

                'file3.txt': 'Test content for file 3'                del self.registered_tools[tool_name]

            }

        },    # Mock specific Qt widgets and classes    

        'folder2': {

            'file4.txt': 'Test content for file 4',    mock_qt_widgets = MagicMock()    def receive_message(self, message):

            'large_file.txt': 'X' * 10000  # Large file for testing

        },    mock_qt_widgets.QMainWindow = MagicMock()        """Receive a message from a tool."""

        'empty_folder': {}

    }    mock_qt_widgets.QWidget = MagicMock()        self.messages.append(message)

    

    def create_structure(base_path, structure):    mock_qt_widgets.QVBoxLayout = MagicMock()    

        for name, content in structure.items():

            if isinstance(content, dict):    mock_qt_widgets.QHBoxLayout = MagicMock()    def broadcast_event(self, tool_name: str, event_type: str, data: Dict[str, Any]):

                # It's a directory

                dir_path = os.path.join(base_path, name)    mock_qt_widgets.QPushButton = MagicMock()        """Broadcast an event to all tools."""

                os.makedirs(dir_path, exist_ok=True)

                create_structure(dir_path, content)    mock_qt_widgets.QLabel = MagicMock()        self.events.append({

            else:

                # It's a file    mock_qt_widgets.QListWidget = MagicMock()            'tool_name': tool_name,

                file_path = os.path.join(base_path, name)

                with open(file_path, 'w', encoding='utf-8') as f:    mock_qt_widgets.QProgressBar = MagicMock()            'event_type': event_type,

                    f.write(content)

        mock_qt_widgets.QApplication = MagicMock()            'data': data

    create_structure(temp_dir, test_structure)

        mock_qt_widgets.QMessageBox = MagicMock()        })

    yield temp_dir

        mock_qt_widgets.QFileDialog = MagicMock()    

    # Cleanup

    shutil.rmtree(temp_dir, ignore_errors=True)    mock_qt_widgets.QGroupBox = MagicMock()    def request_resource(self, tool_name: str, resource_type: str, requirements: Dict[str, Any]) -> bool:



            """Handle resource requests."""

@pytest.fixture(scope="function")

def sample_analysis_data():    mock_modules['PyQt5.QtWidgets'] = mock_qt_widgets        # Always grant resources for testing

    """Provide sample analysis data for testing."""

    return {            self.resources[f"{tool_name}_{resource_type}"] = requirements

        'directories': {

            '/test/folder1': {    with patch.dict('sys.modules', mock_modules):        return True

                'size': 1024,

                'file_count': 3,        yield mock_modules    

                'subdirs': 1

            },    def update_tool_progress(self, tool_name: str, percentage: int, message: str):

            '/test/folder2': {

                'size': 10240,        """Update tool progress."""

                'file_count': 2,

                'subdirs': 0@pytest.fixture(scope="function")        self.tool_progress[tool_name] = {

            }

        },def mock_standard_window():            'percentage': percentage,

        'files': {

            '/test/folder1/file1.txt': 256,    """Mock StandardWindow for testing without GUI dependencies."""            'message': message

            '/test/folder1/file2.txt': 512,

            '/test/folder1/subfolder1/file3.txt': 256,    mock_window = MagicMock()        }

            '/test/folder2/file4.txt': 240,

            '/test/folder2/large_file.txt': 10000    mock_window.main_layout = MagicMock()

        },

        'total_size': 11264,    mock_window.menu_manager = MagicMock()

        'total_files': 5,

        'total_directories': 3    mock_window.ensure_menu_bar = MagicMock()class MockFileSystem:

    }

        """Mock file system for controlled testing."""



@pytest.fixture(scope="function")    with patch('src.tools.analysis.size_analyzer.StandardWindow',     

def test_execution_timer():

    """Track test execution time."""               return_value=mock_window):    def __init__(self):

    start_time = datetime.now()

    yield start_time        yield mock_window        self.files = {}

    end_time = datetime.now()

    execution_time = end_time - start_time        self.directories = set()

    msg = f"\nTest execution time: {execution_time.total_seconds():.3f} s"

    print(msg)        



@pytest.fixture(scope="function")    def add_file(self, path: str, size: int, content: str = None):

@pytest.fixture(scope="session", autouse=True)

def test_session_setup_teardown():def temp_test_directory():        """Add a mock file."""

    """Session-level setup and teardown."""

    print("\n" + "="*60)    """Create temporary directory for test file operations."""        self.files[path] = {

    print("STARTING SIZE ANALYZER COMPREHENSIVE TEST SUITE")

    print("Test Date: August 22, 2025")    temp_dir = tempfile.mkdtemp(prefix="size_analyzer_test_")            'size': size,

    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("Target Module: src.utilities.analysis.size_analyzer")                'content': content or f"Mock content for {path}",

    print("="*60)

        # Create sample directory structure for testing            'modified': 1640995200  # Fixed timestamp

    yield

        test_structure = {        }

    print("\n" + "="*60)

    print("SIZE ANALYZER TEST SUITE COMPLETED")        'folder1': {        # Add parent directories

    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("="*60)            'file1.txt': 'Test content for file 1',        parent = os.path.dirname(path)



            'file2.txt': 'Test content for file 2',        while parent and parent != '/':

@pytest.fixture(scope="function")

def mock_qapplication():            'subfolder1': {            self.directories.add(parent)

    """Mock QApplication for testing main function."""

    mock_app = MagicMock()                'file3.txt': 'Test content for file 3'            parent = os.path.dirname(parent)

    mock_app.exec_.return_value = 0

                }    

    with patch('src.tools.analysis.size_analyzer.QApplication', 

               return_value=mock_app):        },    def add_directory(self, path: str):

        yield mock_app

        'folder2': {        """Add a mock directory."""



# Test markers            'file4.txt': 'Test content for file 4',        self.directories.add(path)

def pytest_configure(config):

    """Configure pytest markers."""            'large_file.txt': 'X' * 10000  # Large file for testing    

    config.addinivalue_line(

        "markers", "unit: mark test as a unit test"        },    def exists(self, path: str) -> bool:

    )

    config.addinivalue_line(        'empty_folder': {}        """Check if path exists."""

        "markers", "integration: mark test as an integration test"

    )    }        return path in self.files or path in self.directories

    config.addinivalue_line(

        "markers", "gui: mark test as a GUI test"        

    )

    config.addinivalue_line(    def create_structure(base_path, structure):    def isfile(self, path: str) -> bool:

        "markers", "mock: mark test as using mocks"

    )        for name, content in structure.items():        """Check if path is a file."""

    config.addinivalue_line(

        "markers", "slow: mark test as slow running"            if isinstance(content, dict):        return path in self.files

    )

                # It's a directory    



def pytest_collection_modifyitems(config, items):                dir_path = os.path.join(base_path, name)    def isdir(self, path: str) -> bool:

    """Modify test collection to add markers automatically."""

    for item in items:                os.makedirs(dir_path, exist_ok=True)        """Check if path is a directory."""

        # Add 'unit' marker to all tests in test_size_analyzer file

        if "test_size_analyzer" in str(item.fspath):                create_structure(dir_path, content)        return path in self.directories

            item.add_marker(pytest.mark.unit)

                    else:    

        # Add 'gui' marker to GUI-related tests

        if "gui" in item.name.lower() or "ui" in item.name.lower():                # It's a file    def getsize(self, path: str) -> int:

            item.add_marker(pytest.mark.gui)

                        file_path = os.path.join(base_path, name)        """Get file size."""

        # Add 'mock' marker to tests using mocks

        if "mock" in item.name.lower():                with open(file_path, 'w', encoding='utf-8') as f:        return self.files.get(path, {}).get('size', 0)

            item.add_marker(pytest.mark.mock)
                    f.write(content)    

        def listdir(self, path: str) -> List[str]:

    create_structure(temp_dir, test_structure)        """List directory contents."""

            contents = []

    yield temp_dir        for file_path in self.files:

                if os.path.dirname(file_path) == path:

    # Cleanup                contents.append(os.path.basename(file_path))

    shutil.rmtree(temp_dir, ignore_errors=True)        for dir_path in self.directories:

            if os.path.dirname(dir_path) == path:

                contents.append(os.path.basename(dir_path))

@pytest.fixture(scope="function")        return contents

def sample_analysis_data():    

    """Provide sample analysis data for testing."""    def walk(self, path: str):

    return {        """Mock os.walk functionality."""

        'directories': {        visited = set()

            '/test/folder1': {        

                'size': 1024,        def _walk(current_path):

                'file_count': 3,            if current_path in visited:

                'subdirs': 1                return

            },            visited.add(current_path)

            '/test/folder2': {            

                'size': 10240,            dirs = []

                'file_count': 2,            files = []

                'subdirs': 0            

            }            # Find direct children

        },            for file_path in self.files:

        'files': {                if os.path.dirname(file_path) == current_path:

            '/test/folder1/file1.txt': 256,                    files.append(os.path.basename(file_path))

            '/test/folder1/file2.txt': 512,            

            '/test/folder1/subfolder1/file3.txt': 256,            for dir_path in self.directories:

            '/test/folder2/file4.txt': 240,                if os.path.dirname(dir_path) == current_path:

            '/test/folder2/large_file.txt': 10000                    dirs.append(os.path.basename(dir_path))

        },            

        'total_size': 11264,            yield current_path, dirs, files

        'total_files': 5,            

        'total_directories': 3            # Recurse into subdirectories

    }            for dir_name in dirs:

                subdir_path = os.path.join(current_path, dir_name)

                yield from _walk(subdir_path)

@pytest.fixture(scope="function")        

def test_execution_timer():        yield from _walk(path)

    """Track test execution time."""

    start_time = datetime.now()

    yield start_time@pytest.fixture(scope="session")

    end_time = datetime.now()def qapp():

    execution_time = end_time - start_time    """Create QApplication instance for GUI testing."""

    print(f"\nTest execution time: {execution_time.total_seconds():.3f} s")    if not QApplication.instance():

        app = QApplication([])

    else:

@pytest.fixture(scope="session", autouse=True)        app = QApplication.instance()

def test_session_setup_teardown():    yield app

    """Session-level setup and teardown."""    # Don't quit the app as it might be used by other tests

    print("\n" + "="*60)

    print("STARTING SIZE ANALYZER COMPREHENSIVE TEST SUITE")

    print(f"Test Date: 2025-08-22")@pytest.fixture

    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")def temp_dir():

    print("Target Module: src.utilities.analysis.size_analyzer")    """Create temporary directory for testing."""

    print("="*60)    temp_path = tempfile.mkdtemp(prefix="size_analyzer_test_")

        yield temp_path

    yield    shutil.rmtree(temp_path, ignore_errors=True)

    

    print("\n" + "="*60)

    print("SIZE ANALYZER TEST SUITE COMPLETED")@pytest.fixture

    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")def test_files(temp_dir):

    print("="*60)    """Create test files with known content and sizes."""

    files = {}

    

@pytest.fixture(scope="function")    # Create various test files

def mock_qapplication():    test_data = {

    """Mock QApplication for testing main function."""        'empty.txt': b'',

    mock_app = MagicMock()        'small.txt': b'Hello, World!' * 10,

    mock_app.exec_.return_value = 0        'medium.txt': b'A' * 1024,  # 1KB

            'large.txt': b'B' * (1024 * 1024),  # 1MB

    with patch('src.tools.analysis.size_analyzer.QApplication',         'binary.bin': bytes(range(256)) * 100,  # Binary file

               return_value=mock_app):        'unicode.txt': 'Hello 世界! 🌍'.encode('utf-8') * 50

        yield mock_app    }

    

    for filename, content in test_data.items():

# Test markers        file_path = os.path.join(temp_dir, filename)

def pytest_configure(config):        with open(file_path, 'wb') as f:

    """Configure pytest markers."""            f.write(content)

    config.addinivalue_line(        

        "markers", "unit: mark test as a unit test"        files[filename] = {

    )            'path': file_path,

    config.addinivalue_line(            'size': len(content),

        "markers", "integration: mark test as an integration test"            'content': content

    )        }

    config.addinivalue_line(    

        "markers", "gui: mark test as a GUI test"    # Create subdirectory with files

    )    subdir = os.path.join(temp_dir, 'subdir')

    config.addinivalue_line(    os.makedirs(subdir)

        "markers", "mock: mark test as using mocks"    

    )    subfile_path = os.path.join(subdir, 'subfile.txt')

    config.addinivalue_line(    subfile_content = b'Subdirectory file content'

        "markers", "slow: mark test as slow running"    with open(subfile_path, 'wb') as f:

    )        f.write(subfile_content)

    

    files['subdir/subfile.txt'] = {

def pytest_collection_modifyitems(config, items):        'path': subfile_path,

    """Modify test collection to add markers automatically."""        'size': len(subfile_content),

    for item in items:        'content': subfile_content

        # Add 'unit' marker to all tests in test_size_analyzer file    }

        if "test_size_analyzer" in str(item.fspath):    

            item.add_marker(pytest.mark.unit)    return files

        

        # Add 'gui' marker to GUI-related tests

        if "gui" in item.name.lower() or "ui" in item.name.lower():@pytest.fixture

            item.add_marker(pytest.mark.gui)def mock_hub():

            """Create mock hub instance for testing."""

        # Add 'mock' marker to tests using mocks    return MockHubInstance()

        if "mock" in item.name.lower():

            item.add_marker(pytest.mark.mock)

@pytest.fixture

def mock_file_system():

def pytest_runtest_setup(item):    """Create mock file system for controlled testing."""

    """Setup before each test run."""    fs = MockFileSystem()

    print(f"\nRunning test: {item.name}")    

    # Add some default test structure

    fs.add_directory('/test')

def pytest_runtest_teardown(item, nextitem):    fs.add_directory('/test/subdir')

    """Teardown after each test run."""    fs.add_file('/test/file1.txt', 100)

    print(f"Completed test: {item.name}")    fs.add_file('/test/file2.txt', 200)
    fs.add_file('/test/subdir/file3.txt', 300)
    
    return fs


@pytest.fixture
def size_analyzer():
    """Create SizeAnalyzer instance for testing."""
    return SizeAnalyzer()


@pytest.fixture
def size_analyzer_with_hub(mock_hub):
    """Create SizeAnalyzer instance with hub integration."""
    analyzer = SizeAnalyzer()
    analyzer.set_hub_connector(mock_hub)
    return analyzer


@pytest.fixture
def size_analyzer_gui(qapp, mock_hub):
    """Create SizeAnalyzerGUI instance for testing."""
    gui = SizeAnalyzerGUI(hub_instance=mock_hub)
    yield gui
    gui.close()


@pytest.fixture
def size_analyzer_config():
    """Create SizeAnalyzerConfig instance for testing."""
    with patch('file_utilities_2.core.size_analyzer_config.ConfigManager'):
        config = SizeAnalyzerConfig()
        return config


@pytest.fixture
def size_analyzer_logger():
    """Create SizeAnalyzerLogger instance for testing."""
    with patch('file_utilities_2.core.size_analyzer_logging.LogManager'):
        logger = SizeAnalyzerLogger()
        return logger


@pytest.fixture
def hub_connector():
    """Create HubConnector instance for testing."""
    return HubConnector("Test Tool")


@pytest.fixture
def mock_progress_callback():
    """Create mock progress callback for testing."""
    callback = Mock()
    callback.call_count = 0
    
    def track_calls(*args, **kwargs):
        callback.call_count += 1
        return callback.return_value
    
    callback.side_effect = track_calls
    return callback


@pytest.fixture
def performance_test_data(temp_dir):
    """Create large test data for performance testing."""
    files = {}
    
    # Create files of various sizes for performance testing
    sizes = {
        'tiny': 1024,           # 1KB
        'small': 10 * 1024,     # 10KB
        'medium': 100 * 1024,   # 100KB
        'large': 1024 * 1024,   # 1MB
        'xlarge': 10 * 1024 * 1024  # 10MB
    }
    
    for name, size in sizes.items():
        file_path = os.path.join(temp_dir, f'{name}_file.dat')
        with open(file_path, 'wb') as f:
            # Write in chunks to avoid memory issues
            chunk_size = min(size, 8192)
            written = 0
            while written < size:
                chunk = b'X' * min(chunk_size, size - written)
                f.write(chunk)
                written += len(chunk)
        
        files[name] = {
            'path': file_path,
            'size': size
        }
    
    return files


@pytest.fixture
def stress_test_structure(temp_dir):
    """Create complex directory structure for stress testing."""
    structure = {
        'root': temp_dir,
        'files': [],
        'directories': []
    }
    
    # Create nested directory structure
    for i in range(5):  # 5 levels deep
        level_dir = os.path.join(temp_dir, *[f'level_{j}' for j in range(i + 1)])
        os.makedirs(level_dir, exist_ok=True)
        structure['directories'].append(level_dir)
        
        # Add files at each level
        for j in range(10):  # 10 files per level
            file_path = os.path.join(level_dir, f'file_{j}.txt')
            content = f'Content for level {i}, file {j}\n' * (j + 1)
            with open(file_path, 'w') as f:
                f.write(content)
            structure['files'].append(file_path)
    
    return structure


@pytest.fixture
def mock_os_operations():
    """Mock OS operations for controlled testing."""
    with patch('os.path.exists') as mock_exists, \
         patch('os.path.isdir') as mock_isdir, \
         patch('os.path.isfile') as mock_isfile, \
         patch('os.path.getsize') as mock_getsize, \
         patch('os.listdir') as mock_listdir, \
         patch('os.walk') as mock_walk, \
         patch('os.stat') as mock_stat:
        
        # Configure default behaviors
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 1024
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        
        # Mock stat result
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024
        mock_stat_result.st_mtime = 1640995200
        mock_stat.return_value = mock_stat_result
        
        # Mock walk result
        mock_walk.return_value = [
            ('/test', ['subdir'], ['file1.txt', 'file2.txt']),
            ('/test/subdir', [], ['file3.txt'])
        ]
        
        yield {
            'exists': mock_exists,
            'isdir': mock_isdir,
            'isfile': mock_isfile,
            'getsize': mock_getsize,
            'listdir': mock_listdir,
            'walk': mock_walk,
            'stat': mock_stat
        }


@pytest.fixture
def analysis_results_sample():
    """Sample analysis results for testing."""
    return {
        'path': '/test/directory',
        'total_size': 1024000,
        'file_count': 100,
        'directory_count': 10,
        'files': [
            {
                'name': 'large_file.txt',
                'path': '/test/directory/large_file.txt',
                'size': 500000,
                'extension': '.txt',
                'modified': 1640995200
            },
            {
                'name': 'medium_file.dat',
                'path': '/test/directory/medium_file.dat',
                'size': 250000,
                'extension': '.dat',
                'modified': 1640995200
            }
        ],
        'file_types': {
            '.txt': {
                'count': 50,
                'total_size': 600000,
                'average_size': 12000
            },
            '.dat': {
                'count': 30,
                'total_size': 300000,
                'average_size': 10000
            },
            '.bin': {
                'count': 20,
                'total_size': 124000,
                'average_size': 6200
            }
        },
        'largest_files': [
            {
                'name': 'huge_file.txt',
                'path': '/test/directory/huge_file.txt',
                'size': 500000,
                'extension': '.txt',
                'modified': 1640995200
            }
        ],
        'directory_tree': {
            'name': 'directory',
            'path': '/test/directory',
            'size': 1024000,
            'children': {}
        },
        'performance_metrics': {
            'start_time': '2024-01-01T00:00:00',
            'end_time': '2024-01-01T00:01:00',
            'files_per_second': 100.0,
            'bytes_per_second': 1024000.0,
            'peak_memory_usage': 50000000
        }
    }


# Test utilities
class TestSignalReceiver(QObject):
    """Test utility for receiving and tracking PyQt signals."""
    
    def __init__(self):
        super().__init__()
        self.signals_received = []
        self.signal_counts = {}
    
    def receive_signal(self, *args, **kwargs):
        """Generic signal receiver."""
        signal_data = {
            'args': args,
            'kwargs': kwargs,
            'timestamp': pytest.approx(1640995200, abs=1000000)  # Flexible timestamp
        }
        self.signals_received.append(signal_data)
        
        # Count signals by type
        signal_type = kwargs.get('signal_type', 'unknown')
        self.signal_counts[signal_type] = self.signal_counts.get(signal_type, 0) + 1
    
    def clear(self):
        """Clear received signals."""
        self.signals_received.clear()
        self.signal_counts.clear()
    
    def get_signal_count(self, signal_type: str = None) -> int:
        """Get count of received signals."""
        if signal_type:
            return self.signal_counts.get(signal_type, 0)
        return len(self.signals_received)


def create_test_directory_structure(base_path: str, structure: Dict[str, Any]):
    """Create a test directory structure from a dictionary specification."""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            # It's a directory
            os.makedirs(path, exist_ok=True)
            create_test_directory_structure(path, content)
        else:
            # It's a file
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(str(content))


def assert_analysis_results_valid(results: Dict[str, Any]):
    """Assert that analysis results have the expected structure and types."""
    required_keys = [
        'path', 'total_size', 'file_count', 'directory_count',
        'files', 'file_types', 'largest_files', 'directory_tree'
    ]
    
    for key in required_keys:
        assert key in results, f"Missing required key: {key}"
    
    assert isinstance(results['total_size'], int)
    assert isinstance(results['file_count'], int)
    assert isinstance(results['directory_count'], int)
    assert isinstance(results['files'], list)
    assert isinstance(results['file_types'], dict)
    assert isinstance(results['largest_files'], list)
    assert isinstance(results['directory_tree'], dict)


def assert_performance_metrics_valid(metrics: Dict[str, Any]):
    """Assert that performance metrics have the expected structure."""
    required_keys = [
        'start_time', 'end_time', 'files_per_second', 'bytes_per_second'
    ]
    
    for key in required_keys:
        assert key in metrics, f"Missing required performance metric: {key}"
    
    assert isinstance(metrics['files_per_second'], (int, float))
    assert isinstance(metrics['bytes_per_second'], (int, float))
    assert metrics['files_per_second'] >= 0
    assert metrics['bytes_per_second'] >= 0