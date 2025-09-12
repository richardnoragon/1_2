# Network Connectivity Testing Suite

This directory contains comprehensive tests for the Network Connectivity toolkit, including unit tests, integration tests, performance tests, GUI tests, and cross-platform compatibility tests.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and shared fixtures
├── test_runner.py             # Custom test runner with reporting
├── README.md                  # This file
├── requirements-test.txt      # Test dependencies
├── .coveragerc               # Coverage configuration
├── unit/                     # Unit tests for individual components
│   ├── __init__.py
│   ├── test_network_base.py
│   ├── test_platform_network.py
│   ├── test_bandwidth_monitor.py
│   ├── test_port_scanner.py
│   ├── test_wifi_analyzer.py
│   ├── test_lan_file_transfer.py
│   ├── test_connection_manager.py
│   ├── test_security_validator.py
│   └── test_performance_analyzer.py
├── integration/              # Integration tests
│   ├── __init__.py
│   ├── test_tool_integration.py
│   ├── test_service_integration.py
│   └── test_rfu_integration.py
├── performance/              # Performance and stress tests
│   ├── __init__.py
│   ├── test_performance.py
│   ├── test_stress.py
│   └── test_memory_leaks.py
├── gui/                      # GUI component tests
│   ├── __init__.py
│   ├── test_gui_components.py
│   ├── test_widgets.py
│   └── test_dialogs.py
├── mocks/                    # Mock objects and test fixtures
│   ├── __init__.py
│   ├── network_mocks.py
│   ├── service_mocks.py
│   └── tool_mocks.py
└── cross_platform/           # Cross-platform compatibility tests
    ├── __init__.py
    ├── test_windows.py
    ├── test_macos.py
    └── test_linux.py
```

## Test Categories

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Location**: `unit/`
- **Coverage**: Core classes, tools, services, and utilities
- **Execution**: Fast, no external dependencies

### Integration Tests
- **Purpose**: Test component interactions and data flow
- **Location**: `integration/`
- **Coverage**: Service integration, tool communication, RFU integration
- **Execution**: Medium speed, may use mock services

### Performance Tests
- **Purpose**: Measure performance and detect regressions
- **Location**: `performance/`
- **Coverage**: Execution time, memory usage, CPU utilization
- **Execution**: Slower, resource monitoring

### Stress Tests
- **Purpose**: Test system behavior under high load
- **Location**: `performance/` (marked with `@pytest.mark.stress`)
- **Coverage**: Concurrent operations, large datasets, extended runtime
- **Execution**: Slow, high resource usage

### GUI Tests
- **Purpose**: Test user interface components
- **Location**: `gui/`
- **Coverage**: Widgets, dialogs, user interactions
- **Execution**: Requires display, PyQt6 dependency

### Cross-Platform Tests
- **Purpose**: Test platform-specific functionality
- **Location**: `cross_platform/`
- **Coverage**: Windows, macOS, Linux specific features
- **Execution**: Platform-dependent

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r tests/requirements-test.txt
```

### Basic Test Execution

Run all tests:
```bash
python -m pytest network_connectivity/tests/
```

Run specific test categories:
```bash
# Unit tests only
python -m pytest network_connectivity/tests/unit/

# Integration tests only
python -m pytest network_connectivity/tests/integration/

# Performance tests only
python -m pytest network_connectivity/tests/performance/ -m performance

# GUI tests only (requires display)
python -m pytest network_connectivity/tests/gui/ -m gui
```

### Using the Custom Test Runner

The custom test runner provides enhanced reporting and test management:

```bash
# Run all tests with detailed reporting
python network_connectivity/tests/test_runner.py --test-type all --verbose

# Run only unit tests
python network_connectivity/tests/test_runner.py --test-type unit

# Run with coverage analysis
python network_connectivity/tests/test_runner.py --coverage

# Run specific test file
python network_connectivity/tests/test_runner.py --specific-test tests/unit/test_bandwidth_monitor.py

# Include stress tests (disabled by default)
python network_connectivity/tests/test_runner.py --test-type all --include-stress

# Save report to file
python network_connectivity/tests/test_runner.py --test-type all --report-file test_report.txt
```

### Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.gui` - GUI tests requiring display
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.stress` - Stress tests (high resource usage)
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.windows` - Windows-specific tests
- `@pytest.mark.macos` - macOS-specific tests
- `@pytest.mark.linux` - Linux-specific tests

Run tests by marker:
```bash
# Run only fast unit tests
python -m pytest -m "unit and not slow"

# Run performance tests but not stress tests
python -m pytest -m "performance and not stress"

# Run platform-specific tests
python -m pytest -m "windows or macos or linux"
```

## Coverage Analysis

### Configuration

Coverage settings are defined in `.coveragerc`:
- Source directories to analyze
- Files to exclude from coverage
- Minimum coverage thresholds
- Report formats (HTML, XML, terminal)

### Running Coverage

Generate coverage report:
```bash
# Run tests with coverage
python -m pytest --cov=network_connectivity --cov-report=html --cov-report=term

# Using custom test runner
python network_connectivity/tests/test_runner.py --coverage
```

View coverage report:
```bash
# Open HTML report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### Coverage Targets

- **Overall Coverage**: ≥ 90%
- **Core Components**: ≥ 95%
- **Tools**: ≥ 90%
- **GUI Components**: ≥ 80%
- **Platform-Specific Code**: ≥ 85%

## Mock Objects and Fixtures

### Network Mocks
- `MockNetworkInterface`: Simulated network interfaces
- `MockNetworkStats`: Simulated network statistics
- `MockPlatformDetector`: Mock platform detection
- `MockNetworkData`: Generated test data
- `MockDeviceDiscovery`: Simulated device discovery

### Service Mocks
- `MockConfigService`: Configuration service simulation
- `MockLoggingService`: Logging service simulation
- `MockNotificationService`: Notification service simulation
- `MockMetricsService`: Metrics service simulation

### Usage Example

```python
from network_connectivity.tests.mocks import MockPlatformDetector

def test_bandwidth_monitor():
    detector = MockPlatformDetector()
    monitor = BandwidthMonitor()
    monitor.platform_detector = detector
    
    interfaces = monitor.get_available_interfaces()
    assert len(interfaces) > 0
```

## Performance Testing

### Performance Metrics

Tests monitor:
- **Execution Time**: Function/operation duration
- **Memory Usage**: RAM consumption during operations
- **CPU Usage**: Processor utilization
- **Resource Cleanup**: Memory leak detection

### Performance Limits

Default performance thresholds:
- Initialization: < 100ms per component
- Data Collection: < 1ms per operation
- Memory Growth: < 50MB per test
- CPU Usage: < 80% during normal operations

### Stress Testing

Stress tests simulate:
- High concurrent operations (10+ threads)
- Large datasets (10,000+ items)
- Extended runtime (60+ seconds)
- Resource exhaustion scenarios

## GUI Testing

### Requirements

GUI tests require:
- PyQt6 installation
- Display environment (X11, Wayland, or Windows display)
- For headless testing: Xvfb (Linux) or similar

### Headless GUI Testing

Run GUI tests without display:
```bash
# Linux with Xvfb
xvfb-run -a python -m pytest network_connectivity/tests/gui/

# Using pytest-qt plugin
python -m pytest network_connectivity/tests/gui/ --qt-no-display
```

### GUI Test Coverage

- Widget initialization and layout
- User interaction simulation (clicks, keyboard input)
- Signal/slot connections
- Data visualization updates
- Dialog functionality

## Cross-Platform Testing

### Platform-Specific Features

Tests verify:
- **Windows**: WMI queries, Windows-specific network APIs
- **macOS**: Core Foundation frameworks, BSD socket extensions
- **Linux**: /proc filesystem, netlink sockets

### Platform Detection

Tests automatically detect platform and run appropriate tests:
```python
@pytest.mark.windows
def test_windows_specific_feature():
    # Only runs on Windows
    pass

@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
def test_macos_feature():
    # Only runs on macOS
    pass
```

## Continuous Integration

### GitHub Actions Integration

Example workflow configuration:
```yaml
name: Network Connectivity Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r tests/requirements-test.txt
    
    - name: Run tests
      run: |
        python network_connectivity/tests/test_runner.py --test-type all --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Test Data Management

### Test Data Generation

Mock objects generate realistic test data:
- Network interface configurations
- Bandwidth monitoring data
- Port scan results
- WiFi network information
- Device discovery results

### Data Cleanup

Tests automatically clean up:
- Temporary files
- Mock data
- Thread resources
- Memory allocations

## Debugging Tests

### Verbose Output

Enable detailed test output:
```bash
python -m pytest -v -s network_connectivity/tests/
```

### Debug Specific Test

Run single test with debugging:
```bash
python -m pytest -v -s network_connectivity/tests/unit/test_bandwidth_monitor.py::TestBandwidthMonitor::test_initialization
```

### Logging During Tests

Enable logging in tests:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing to Tests

### Adding New Tests

1. Choose appropriate test category (unit/integration/performance/gui)
2. Use existing fixtures and mocks when possible
3. Follow naming conventions: `test_<functionality>.py`
4. Add appropriate pytest markers
5. Include docstrings explaining test purpose
6. Ensure tests are deterministic and isolated

### Test Guidelines

- **Isolation**: Tests should not depend on each other
- **Determinism**: Tests should produce consistent results
- **Speed**: Unit tests should be fast (< 1 second each)
- **Clarity**: Test names should clearly describe what is being tested
- **Coverage**: Aim for high code coverage with meaningful tests

### Mock Usage

- Use mocks for external dependencies (network, filesystem, services)
- Create realistic mock data that represents actual usage
- Ensure mocks are properly cleaned up after tests
- Document mock behavior and limitations

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **GUI Test Failures**: Check display environment and PyQt6 installation
3. **Platform Test Skips**: Normal on non-matching platforms
4. **Performance Test Failures**: May indicate performance regressions
5. **Coverage Issues**: Check for untested code paths

### Getting Help

- Check test output for detailed error messages
- Review test logs for debugging information
- Consult mock object documentation
- Verify test environment setup

## Test Metrics and Reporting

The test suite provides comprehensive metrics:
- Test execution time and results
- Code coverage analysis
- Performance benchmarks
- Resource usage statistics
- Cross-platform compatibility status

Reports are generated in multiple formats:
- Terminal output for immediate feedback
- HTML reports for detailed analysis
- JSON/XML for CI/CD integration
- Custom reports via test runner