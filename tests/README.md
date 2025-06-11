# Testing Guide for Richard's File Utilities

This document describes how to run tests and contribute new tests to the RFU project.

## Quick Start

Run all tests with coverage report:
```bash
python run_tests.py --coverage
```

Run tests without GUI tests (useful for CI environments):
```bash
python run_tests.py --no-gui
```

Run tests in parallel for faster execution:
```bash
python run_tests.py --parallel
```

## Test Structure

- `tests/test_utils.py` - Common utilities used across tests
- `tests/test_file_operations.py` - Tests for file organization and renaming
- `tests/test_encryption.py` - Tests for file encryption/decryption
- `tests/test_metadata.py` - Tests for metadata handling
- `tests/test_gui_components.py` - Tests for GUI components
- `tests/test_config.py` - Tests for configuration management
- `tests/test_logging.py` - Tests for logging functionality

## Writing New Tests

### Test Categories

- Unit Tests: Test individual components in isolation
- Integration Tests: Test component interactions
- GUI Tests: Test user interface components
- Acceptance Tests: Test complete user workflows

### Test Markers

Use pytest markers to categorize tests:
```python
@pytest.mark.gui  # For GUI tests
@pytest.mark.slow  # For time-consuming tests
@pytest.mark.integration  # For integration tests
```

### Test Utilities

The `TestUtils` class in `test_utils.py` provides common functionality:
- `get_test_app()` - Get PyQt application instance
- `create_temp_file()` - Create temporary test file
- `create_temp_dir()` - Create temporary test directory
- `cleanup_temp_file()` - Clean up temporary file
- `cleanup_temp_dir()` - Clean up temporary directory

### Best Practices

1. Use meaningful test names that describe the scenario
2. Follow the Arrange-Act-Assert pattern
3. Clean up resources in tearDown
4. Mock external dependencies
5. Keep tests independent
6. Use appropriate assertions
7. Add docstrings to test methods

### Example Test

```python
import unittest
from tests.test_utils import TestUtils

class TestExample(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = TestUtils.create_temp_dir()
        
    def tearDown(self):
        """Clean up after test"""
        TestUtils.cleanup_temp_dir(self.test_dir)
        
    def test_feature(self):
        """Test specific feature"""
        # Arrange
        input_data = "test"
        
        # Act
        result = process_data(input_data)
        
        # Assert
        self.assertEqual(result, expected_output)
```

## Coverage Reports

Coverage reports are generated in HTML format in the `htmlcov` directory. Open `htmlcov/index.html` to view the report.

Key coverage metrics:
- Line coverage: % of code lines executed
- Branch coverage: % of code branches executed
- Missing lines: Lines not covered by tests

## Continuous Integration

Tests are automatically run on:
- Pull request creation
- Push to main branch
- Daily scheduled runs

CI skip markers:
- Add `[skip ci]` to commit message to skip CI
- Use `@pytest.mark.skipif` for environment-specific tests

## Troubleshooting

Common issues and solutions:

1. GUI tests failing in CI:
   - Use `--no-gui` flag
   - Ensure DISPLAY is set in CI environment

2. Tests hanging:
   - Check for infinite loops
   - Verify cleanup in tearDown
   - Use timeouts for long operations

3. Resource cleanup issues:
   - Always use TestUtils cleanup methods
   - Implement proper tearDown methods
   - Use context managers when possible

## Contributing Tests

1. Create new test file in `tests` directory
2. Follow existing test patterns
3. Add to `pytest.ini` if needed
4. Update this documentation
5. Submit pull request