"""
Test fixtures for Enhanced Editor unit tests
Created: 2025-08-29

This module provides shared fixtures and utilities for testing the Enhanced Editor.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for the entire test session."""
    if not QT_AVAILABLE:
        pytest.skip("PyQt5 not available")
    
    if QApplication.instance() is None:
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as f:
        f.write("Test content for file operations")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as f:
        f.write("""
def hello_world():
    print("Hello, World!")
    return True

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    hello_world()
""")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_javascript_file():
    """Create a temporary JavaScript file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.js') as f:
        f.write("""
function helloWorld() {
    console.log("Hello, World!");
    return true;
}

class TestClass {
    constructor() {
        this.value = 42;
    }
    
    getValue() {
        return this.value;
    }
}

// Main execution
if (typeof window === 'undefined') {
    helloWorld();
}
""")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_text_content():
    """Provide sample text content for testing."""
    return """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

This is a multi-line text document with various content.
It includes special characters: !@#$%^&*()_+-=[]{}|;:,.<>?
And some Unicode: café, naïve, résumé, 中文, العربية

Numbers: 123456789
Mixed case: CamelCase, snake_case, UPPER_CASE
"""


@pytest.fixture
def sample_python_content():
    """Provide sample Python content for testing."""
    return '''#!/usr/bin/env python3
"""
Sample Python module for testing syntax highlighting and parsing.
"""

import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Person:
    """Represents a person with basic information."""
    name: str
    age: int
    email: Optional[str] = None
    
    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Age cannot be negative")
    
    def greet(self) -> str:
        return f"Hello, my name is {self.name}"

def calculate_average(numbers: List[float]) -> float:
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

def main():
    """Main function demonstrating the module usage."""
    people = [
        Person("Alice", 30, "alice@example.com"),
        Person("Bob", 25),
        Person("Charlie", 35, "charlie@test.org")
    ]
    
    ages = [person.age for person in people]
    avg_age = calculate_average(ages)
    
    print(f"Average age: {avg_age:.1f}")
    
    for person in people:
        print(person.greet())

if __name__ == "__main__":
    main()
'''


@pytest.fixture
def sample_javascript_content():
    """Provide sample JavaScript content for testing."""
    return '''/**
 * Sample JavaScript module for testing syntax highlighting and parsing.
 */

const fs = require('fs');
const path = require('path');

class Person {
    /**
     * Create a new Person instance.
     * @param {string} name - The person's name
     * @param {number} age - The person's age
     * @param {string} email - The person's email (optional)
     */
    constructor(name, age, email = null) {
        this.name = name;
        this.age = age;
        this.email = email;
        
        if (age < 0) {
            throw new Error("Age cannot be negative");
        }
    }
    
    /**
     * Get a greeting message from this person.
     * @returns {string} Greeting message
     */
    greet() {
        return `Hello, my name is ${this.name}`;
    }
}

/**
 * Calculate the average of an array of numbers.
 * @param {number[]} numbers - Array of numbers
 * @returns {number} Average value
 */
function calculateAverage(numbers) {
    if (numbers.length === 0) {
        return 0;
    }
    const sum = numbers.reduce((acc, num) => acc + num, 0);
    return sum / numbers.length;
}

function main() {
    const people = [
        new Person("Alice", 30, "alice@example.com"),
        new Person("Bob", 25),
        new Person("Charlie", 35, "charlie@test.org")
    ];
    
    const ages = people.map(person => person.age);
    const avgAge = calculateAverage(ages);
    
    console.log(`Average age: ${avgAge.toFixed(1)}`);
    
    people.forEach(person => {
        console.log(person.greet());
    });
}

// Run main if this is the entry point
if (require.main === module) {
    main();
}

module.exports = { Person, calculateAverage };
'''


@pytest.fixture
def mock_qsettings():
    """Mock QSettings for testing."""
    with patch('PyQt5.QtCore.QSettings') as mock_settings:
        mock_instance = Mock()
        mock_settings.return_value = mock_instance
        
        # Set up default return values
        mock_instance.value.side_effect = lambda key, default=None, type=None: {
            'font_family': 'Consolas',
            'font_size': 11,
            'tab_width': 4,
            'use_spaces': True,
            'word_wrap': True,
            'line_numbers': True,
            'syntax_highlighting': True,
            'recent_files': []
        }.get(key, default)
        
        yield mock_instance


@pytest.fixture
def mock_file_dialog():
    """Mock file dialogs for testing."""
    with patch('PyQt5.QtWidgets.QFileDialog') as mock_dialog:
        # Set up default return values
        mock_dialog.getOpenFileName.return_value = ("test.py", "")
        mock_dialog.getSaveFileName.return_value = ("test.py", "")
        yield mock_dialog


@pytest.fixture
def mock_message_box():
    """Mock message boxes for testing."""
    with patch('PyQt5.QtWidgets.QMessageBox') as mock_msgbox:
        # Set up default return values
        mock_msgbox.question.return_value = mock_msgbox.Save
        mock_msgbox.information.return_value = mock_msgbox.Ok
        mock_msgbox.warning.return_value = mock_msgbox.Ok
        mock_msgbox.critical.return_value = mock_msgbox.Ok
        yield mock_msgbox


@pytest.fixture
def capture_signals():
    """Utility to capture Qt signals for testing."""
    captured_signals = []
    
    def signal_capture(*args, **kwargs):
        captured_signals.append((args, kwargs))
    
    return signal_capture, captured_signals


@pytest.fixture
def test_workspace(temp_directory):
    """Create a test workspace with sample files."""
    workspace = Path(temp_directory)
    
    # Create directory structure
    (workspace / "src").mkdir()
    (workspace / "tests").mkdir()
    (workspace / "docs").mkdir()
    
    # Create sample files
    files = {
        "src/main.py": "print('Hello from main')",
        "src/utils.py": "def helper(): pass",
        "tests/test_main.py": "def test_something(): assert True",
        "docs/readme.md": "# Project Documentation",
        "config.json": '{"setting": "value"}',
        "script.sh": "#!/bin/bash\necho 'Shell script'",
        "style.css": "body { margin: 0; }"
    }
    
    for file_path, content in files.items():
        full_path = workspace / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    yield workspace