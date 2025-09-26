"""
Pytest Configuration for Office Metadata GUI Tests
Generated: 2025-08-29
Target: src/tools/metadata/office_metadata/office_metadata_gui.py

This module provides pytest fixtures and configuration for comprehensive
testing of the Office Metadata GUI components.
"""

import os
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

# Add src to Python path for imports
test_dir = Path(__file__).parent
src_paths = [
    test_dir / ".." / ".." / "src",
    test_dir / ".." / ".." / ".." / "src",
    test_dir / "src",
    Path("src"),
]

for src_path in src_paths:
    if src_path.exists():
        abs_src_path = str(src_path.resolve())
        if abs_src_path not in sys.path:
            sys.path.insert(0, abs_src_path)
        break

# Check PyQt5 availability
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    QApplication = None


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication fixture for GUI tests."""
    if not PYQT5_AVAILABLE:
        pytest.skip("PyQt5 not available")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        app.setQuitOnLastWindowClosed(False)

    # Set platform for headless testing
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    yield app

    # Cleanup
    if app:
        app.quit()


@pytest.fixture
def temp_directory():
    """Create temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    import shutil

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_docx_file(temp_directory):
    """Create a mock DOCX file with complete metadata structure."""
    docx_path = os.path.join(temp_directory, "test_document.docx")

    with zipfile.ZipFile(docx_path, "w") as zip_file:
        # Core properties XML
        core_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                          xmlns:dc="http://purl.org/dc/elements/1.1/"
                          xmlns:dcterms="http://purl.org/dc/terms/">
            <dc:title>Test Document Title</dc:title>
            <dc:creator>Test Author Name</dc:creator>
            <dc:subject>Test Subject Matter</dc:subject>
            <dc:description>Test document description for testing purposes</dc:description>
            <cp:keywords>test, document, metadata, office</cp:keywords>
            <cp:category>Test Category</cp:category>
            <dcterms:created>2025-08-29T10:00:00Z</dcterms:created>
            <dcterms:modified>2025-08-29T12:30:00Z</dcterms:modified>
            <cp:lastModifiedBy>Test Editor Name</cp:lastModifiedBy>
            <cp:revision>5</cp:revision>
            <dc:language>en-US</dc:language>
        </cp:coreProperties>"""

        # App properties XML
        app_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
            <Application>Microsoft Word</Application>
            <AppVersion>16.0000</AppVersion>
            <Company>Test Company Inc.</Company>
            <Manager>Test Manager Name</Manager>
            <TotalTime>240</TotalTime>
            <Pages>10</Pages>
            <Words>2500</Words>
            <Characters>12000</Characters>
            <CharactersWithSpaces>14500</Characters>
            <Lines>125</Lines>
            <Paragraphs>45</Paragraphs>
            <Template>Normal.dotm</Template>
            <ScaleCrop>false</ScaleCrop>
            <DocSecurity>0</DocSecurity>
            <SharedDoc>false</SharedDoc>
        </Properties>"""

        # Custom properties XML
        custom_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties">
            <property name="ProjectCode" pid="2">
                <vt:lpwstr xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">PROJ-2025-001</vt:lpwstr>
            </property>
            <property name="ClientName" pid="3">
                <vt:lpwstr xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">Test Client Corp</vt:lpwstr>
            </property>
            <property name="ReviewStatus" pid="4">
                <vt:lpwstr xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">Draft</vt:lpwstr>
            </property>
        </Properties>"""

        # Write metadata files
        zip_file.writestr("docProps/core.xml", core_xml)
        zip_file.writestr("docProps/app.xml", app_xml)
        zip_file.writestr("docProps/custom.xml", custom_xml)

        # Add minimal document structure
        content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
            <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
            <Default Extension="xml" ContentType="application/xml"/>
            <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
        </Types>"""

        rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
            <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
        </Relationships>"""

        document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:body>
                <w:p>
                    <w:r>
                        <w:t>Test document content</w:t>
                    </w:r>
                </w:p>
            </w:body>
        </w:document>"""

        zip_file.writestr("[Content_Types].xml", content_types_xml)
        zip_file.writestr("_rels/.rels", rels_xml)
        zip_file.writestr("word/document.xml", document_xml)

    yield docx_path


@pytest.fixture
def mock_pdf_file(temp_directory):
    """Create a mock PDF file."""
    pdf_path = os.path.join(temp_directory, "test_document.pdf")

    # Create minimal PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj

xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
203
%%EOF"""

    with open(pdf_path, "wb") as f:
        f.write(pdf_content)

    yield pdf_path


@pytest.fixture
def mock_ole_file(temp_directory):
    """Create a mock OLE/legacy Office file."""
    ole_path = os.path.join(temp_directory, "test_document.doc")

    # Create minimal OLE structure
    ole_content = b"\\xd0\\xcf\\x11\\xe0\\xa1\\xb1\\x1a\\xe1"  # OLE signature
    ole_content += b"Mock OLE document content for testing"

    with open(ole_path, "wb") as f:
        f.write(ole_content)

    yield ole_path


@pytest.fixture
def mock_invalid_file(temp_directory):
    """Create an invalid/unsupported file."""
    invalid_path = os.path.join(temp_directory, "test_file.txt")

    with open(invalid_path, "w", encoding="utf-8") as f:
        f.write("This is a plain text file, not an office document.")

    yield invalid_path


@pytest.fixture
def mock_corrupted_docx(temp_directory):
    """Create a corrupted DOCX file."""
    corrupted_path = os.path.join(temp_directory, "corrupted.docx")

    with open(corrupted_path, "wb") as f:
        f.write(b"This is not a valid ZIP/DOCX file structure")

    yield corrupted_path


@pytest.fixture
def mock_unicode_docx(temp_directory):
    """Create a DOCX file with Unicode metadata."""
    unicode_path = os.path.join(temp_directory, "unicode_test.docx")

    with zipfile.ZipFile(unicode_path, "w") as zip_file:
        # Unicode core properties
        unicode_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                          xmlns:dc="http://purl.org/dc/elements/1.1/">
            <dc:title>测试文档 🌟 Test</dc:title>
            <dc:creator>مؤلف التجربة (Test Author)</dc:creator>
            <dc:subject>Тестовый субъект</dc:subject>
            <dc:description>Document with émojis 🚀 and ñoñó characters</dc:description>
            <cp:keywords>тест, परीक्षण, 테스트, テスト</cp:keywords>
        </cp:coreProperties>""".encode(
            "utf-8"
        )

        zip_file.writestr("docProps/core.xml", unicode_xml)
        zip_file.writestr(
            "[Content_Types].xml", '<?xml version="1.0"?><Types/>'
        )

    yield unicode_path


@pytest.fixture
def sample_metadata():
    """Provide sample metadata for testing."""
    return {
        "file_info": {
            "filename": "test_document.docx",
            "filepath": "/path/to/test_document.docx",
            "size": 45678,
            "size_formatted": "44.6 KB",
            "created": "2025-08-29T08:00:00",
            "modified": "2025-08-29T12:30:00",
            "accessed": "2025-08-29T14:15:00",
            "extension": ".docx",
        },
        "core_properties": {
            "title": "Sample Test Document",
            "creator": "John Doe",
            "subject": "Test Subject",
            "description": "Test description for sample document",
            "keywords": "test, sample, document",
            "category": "Test Category",
            "created": "2025-08-29T08:00:00Z",
            "modified": "2025-08-29T12:30:00Z",
            "lastModifiedBy": "Jane Smith",
            "revision": "3",
            "language": "en-US",
        },
        "app_properties": {
            "Application": "Microsoft Word",
            "AppVersion": "16.0000",
            "Company": "Sample Company",
            "Manager": "Test Manager",
            "TotalTime": "180",
            "Pages": "8",
            "Words": "1500",
            "Characters": "7500",
        },
        "custom_properties": {
            "ProjectCode": "PROJ-2025-TEST",
            "DepartmentCode": "DEPT-001",
            "ReviewStatus": "Final",
        },
        "security_info": {
            "privacy_concerns": [
                "Author name: John Doe",
                "Last modified by: Jane Smith",
                "Company: Sample Company",
            ],
            "sensitive_data": [],
            "recommendations": [
                "Consider removing personal information",
                "Review metadata before sharing",
            ],
        },
    }


@pytest.fixture
def mock_qt_components():
    """Mock Qt components for testing without GUI."""
    if PYQT5_AVAILABLE:
        return None

    # Create mock Qt classes for headless testing
    class MockQWidget:
        def __init__(self):
            self._visible = False
            self._enabled = True

        def setVisible(self, visible):
            self._visible = visible

        def isVisible(self):
            return self._visible

        def setEnabled(self, enabled):
            self._enabled = enabled

        def isEnabled(self):
            return self._enabled

        def close(self):
            pass

    class MockQTableWidget(MockQWidget):
        def __init__(self):
            super().__init__()
            self._rows = 0
            self._columns = 0
            self._items = {}

        def setRowCount(self, rows):
            self._rows = rows

        def rowCount(self):
            return self._rows

        def setColumnCount(self, columns):
            self._columns = columns

        def columnCount(self):
            return self._columns

        def setItem(self, row, column, item):
            self._items[(row, column)] = item

        def item(self, row, column):
            return self._items.get((row, column))

    class MockQTextEdit(MockQWidget):
        def __init__(self):
            super().__init__()
            self._text = ""

        def setText(self, text):
            self._text = text

        def toPlainText(self):
            return self._text

        def clear(self):
            self._text = ""

    return {
        "QWidget": MockQWidget,
        "QTableWidget": MockQTableWidget,
        "QTextEdit": MockQTextEdit,
    }


@pytest.fixture
def test_execution_info():
    """Provide test execution metadata."""
    return {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "target_module": "src/tools/metadata/office_metadata/office_metadata_gui.py",
        "test_suite": "Office Metadata GUI Comprehensive Tests",
        "framework": "pytest + unittest",
        "categories": [
            "Unit Tests",
            "GUI Component Tests",
            "Integration Tests",
            "Edge Case Tests",
            "Security Analysis Tests",
        ],
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest for office metadata GUI tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "gui: mark test as requiring GUI components (PyQt5)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as edge case or error condition test"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Modify test items based on available dependencies."""
    if not PYQT5_AVAILABLE:
        skip_gui = pytest.mark.skip(reason="PyQt5 not available")
        for item in items:
            if "gui" in item.keywords:
                item.add_marker(skip_gui)


def pytest_runtest_setup(item):
    """Setup hook for individual test items."""
    # Skip GUI tests if PyQt5 not available
    if "gui" in item.keywords and not PYQT5_AVAILABLE:
        pytest.skip("PyQt5 not available for GUI tests")


# Test data constants
TEST_CONSTANTS = {
    "SUPPORTED_EXTENSIONS": [
        ".docx",
        ".xlsx",
        ".pptx",
        ".doc",
        ".xls",
        ".ppt",
        ".pdf",
    ],
    "UNSUPPORTED_EXTENSIONS": [".txt", ".rtf", ".odt", ".csv"],
    "CORE_PROPERTY_FIELDS": [
        "title",
        "creator",
        "subject",
        "description",
        "keywords",
        "category",
        "created",
        "modified",
        "lastModifiedBy",
        "revision",
        "language",
    ],
    "APP_PROPERTY_FIELDS": [
        "Application",
        "AppVersion",
        "Company",
        "Manager",
        "TotalTime",
        "Pages",
        "Words",
        "Characters",
        "CharactersWithSpaces",
        "Lines",
        "Paragraphs",
    ],
    "SECURITY_KEYWORDS": [
        "password",
        "secret",
        "confidential",
        "private",
        "sensitive",
    ],
    "FILE_SIZE_UNITS": ["B", "KB", "MB", "GB", "TB"],
}


# Export test constants for use in tests
pytest.TEST_CONSTANTS = TEST_CONSTANTS
