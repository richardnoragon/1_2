# Size Analyzer Installation and Usage Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Configuration Setup](#configuration-setup)
4. [Basic Usage](#basic-usage)
5. [Advanced Usage](#advanced-usage)
6. [Integration with Hub](#integration-with-hub)
7. [Command Line Usage](#command-line-usage)
8. [Configuration Management](#configuration-management)
9. [Troubleshooting Installation](#troubleshooting-installation)
10. [Verification and Testing](#verification-and-testing)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+) |
| **Python Version** | Python 3.7 or higher |
| **Memory** | 4 GB RAM minimum, 8 GB recommended |
| **Storage** | 100 MB free space for installation |
| **Display** | 1024x768 minimum resolution |

### Recommended Requirements

| Component | Recommendation |
|-----------|----------------|
| **Operating System** | Windows 11, macOS 12+, or Linux (Ubuntu 20.04+) |
| **Python Version** | Python 3.9 or higher |
| **Memory** | 16 GB RAM for large directory analysis |
| **Storage** | 1 GB free space for cache and temporary files |
| **Display** | 1920x1080 or higher resolution |

### Dependencies

#### Required Dependencies
```txt
PyQt5 >= 5.15.0
```

#### Optional Dependencies
```txt
psutil >= 5.8.0          # For performance monitoring
```

#### Development Dependencies
```txt
pytest >= 6.0.0          # For running tests
pytest-qt >= 4.0.0       # For GUI testing
coverage >= 5.0.0        # For test coverage
black >= 21.0.0          # Code formatting
isort >= 5.0.0           # Import sorting
flake8 >= 3.8.0          # Linting
mypy >= 0.800            # Type checking
```

---

## Installation Methods

### Method 1: Package Installation (Recommended)

This is the recommended method for most users who want to use the Size Analyzer as part of the file_utilities_2 package.

#### Step 1: Clone or Download Repository
```bash
# Clone the repository
git clone <repository-url>
cd file_utilities_2

# Or download and extract the ZIP file
# Then navigate to the extracted directory
```

#### Step 2: Install Dependencies
```bash
# Install required dependencies
pip install -r requirements.txt

# For Windows users who encounter PyQt5 installation issues:
pip install --only-binary=all PyQt5

# For Linux users (Ubuntu/Debian):
sudo apt-get install python3-dev python3-pyqt5.qtcore python3-pyqt5.qtgui python3-pyqt5.qtwidgets
pip install -r requirements.txt
```

#### Step 3: Verify Installation
```bash
# Test core functionality
python -c "from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer; print('Core logic: OK')"

# Test GUI functionality
python -c "from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI; print('GUI: OK')"

# Test configuration
python -c "from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig; print('Configuration: OK')"

# Test hub integration
python -c "from file_utilities_2.integration.hub_connector import HubConnector; print('Hub integration: OK')"
```

### Method 2: Development Installation

This method is recommended for developers who want to contribute to the project or modify the code.

#### Step 1: Clone Repository
```bash
git clone <repository-url>
cd file_utilities_2
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### Step 3: Install in Development Mode
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional)
pre-commit install
```

#### Step 4: Run Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=file_utilities_2 tests/

# Run specific test categories
pytest tests/test_size_analyzer_core.py
pytest tests/test_size_analyzer_gui.py
```

### Method 3: Conda Installation

For users who prefer conda package management:

```bash
# Create conda environment
conda create -n size_analyzer python=3.9
conda activate size_analyzer

# Install PyQt5 via conda
conda install pyqt

# Install other dependencies via pip
pip install -r requirements.txt
```

### Method 4: Docker Installation

For containerized deployment:

```bash
# Build Docker image
docker build -t size-analyzer .

# Run container
docker run -it --rm \
  -v /path/to/analyze:/data:ro \
  -v ./results:/app/results \
  size-analyzer
```

---

## Configuration Setup

### Initial Configuration

#### Step 1: Create Configuration Directories
```bash
# Create required directories
mkdir -p cache/size_analyzer
mkdir -p temp/size_analyzer
mkdir -p logs/size_analyzer
mkdir -p file_utilities_2/templates/size_analyzer

# Set appropriate permissions (Linux/macOS)
chmod 755 cache/size_analyzer temp/size_analyzer logs/size_analyzer
```

#### Step 2: Verify Configuration File
Ensure `configuration.json` contains the size_analyzer section:

```json
{
  "size_analyzer": {
    "general": {
      "module_path": "file_utilities_2.gui.size_analyzer_gui",
      "class_name": "SizeAnalyzerGUI",
      "enable_logging": true,
      "log_level": "INFO"
    },
    "analysis": {
      "default_top_files_count": 20,
      "progress_update_interval": 100,
      "include_hidden_files": false,
      "enable_file_type_analysis": true
    },
    "performance": {
      "max_memory_usage_mb": 256,
      "max_cpu_usage_percent": 50,
      "operation_timeout_seconds": 300
    }
  }
}
```

#### Step 3: Set Resource Paths
Verify that resource paths in configuration point to correct locations:

```python
# Verify resource paths
from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig

config = SizeAnalyzerConfig()
issues = config.validate_configuration()

if issues['errors']:
    print("Configuration errors found:")
    for error in issues['errors']:
        print(f"  - {error}")
else:
    print("Configuration is valid")
```

#### Step 4: Create Resource Files
```bash
# Create icon file (if not present)
# Copy or create size_analyzer.png in file_utilities_2/gui/icons/

# Create help file (if not present)
# Copy or create size_analyzer_help.html in file_utilities_2/docs/
```

---

## Basic Usage

### Standalone GUI Application

#### Launch the Application
```python
import sys
from PyQt5.QtWidgets import QApplication
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

# Create application
app = QApplication(sys.argv)

# Create and show window
window = SizeAnalyzerGUI()
window.show()

# Run application
sys.exit(app.exec_())
```

#### Using the GUI

1. **Select Directory**:
   - Click the "Browse" button
   - Navigate to the directory you want to analyze
   - Click "Select Folder"

2. **Start Analysis**:
   - Click "Analyze Directory Size"
   - Monitor progress in the progress bar
   - View real-time status updates

3. **View Results**:
   - Review summary information in the left panel
   - Examine detailed results in the right panel
   - Explore file type statistics and largest files

4. **Export Results**:
   - Click "Export Results"
   - Choose export location and filename
   - Select export format (JSON recommended)

### Core Logic Only

For programmatic usage without GUI:

```python
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

# Create analyzer instance
analyzer = SizeAnalyzer()

# Analyze directory
results = analyzer.analyze_directory("/path/to/directory")

# Display basic results
print(f"Total size: {analyzer.format_size(results['total_size'])}")
print(f"File count: {results['file_count']}")
print(f"Directory count: {results['directory_count']}")

# Display largest files
print("\nLargest files:")
for i, file_info in enumerate(results['largest_files'][:5], 1):
    size = analyzer.format_size(file_info['size'])
    print(f"{i}. {file_info['name']} ({size})")

# Display file type summary
print("\nFile types:")
for ext, stats in sorted(results['file_types'].items(), 
                        key=lambda x: x[1]['total_size'], reverse=True)[:5]:
    count = stats['count']
    size = analyzer.format_size(stats['total_size'])
    print(f"{ext}: {count} files, {size}")

# Export results
analyzer.export_analysis(results, "analysis_results.json")
print("\nResults exported to analysis_results.json")
```

---

## Advanced Usage

### With Progress Tracking

```python
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
from PyQt5.QtCore import QObject, pyqtSlot

class ProgressTracker(QObject):
    def __init__(self):
        super().__init__()
    
    @pyqtSlot(int)
    def on_progress(self, percentage):
        print(f"Progress: {percentage}%")
    
    @pyqtSlot(str)
    def on_status(self, message):
        print(f"Status: {message}")
    
    @pyqtSlot(str, int)
    def on_milestone(self, milestone, percentage):
        print(f"Milestone: {milestone} ({percentage}%)")

# Create analyzer and progress tracker
analyzer = SizeAnalyzer()
tracker = ProgressTracker()

# Connect signals
analyzer.progress_percentage.connect(tracker.on_progress)
analyzer.progress_message.connect(tracker.on_status)
analyzer.milestone_reached.connect(tracker.on_milestone)

# Analyze with progress tracking
results = analyzer.analyze_directory("/large/directory")
```

### With File Filtering

```python
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

analyzer = SizeAnalyzer()

# Analyze only specific file types
results = analyzer.analyze_directory(
    "/path/to/directory",
    top_files_count=20,
    include_extensions=['.py', '.js', '.html', '.css']
)

print(f"Analyzed {results['file_count']} code files")
print(f"Total size: {analyzer.format_size(results['total_size'])}")

# Display file type breakdown
for ext, stats in results['file_types'].items():
    count = stats['count']
    size = analyzer.format_size(stats['total_size'])
    avg_size = analyzer.format_size(stats['average_size'])
    print(f"{ext}: {count} files, {size} total, {avg_size} average")
```

### With Performance Monitoring

```python
import time
import psutil
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

class PerformanceMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_memory = None
    
    def start_monitoring(self):
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
    
    def get_stats(self):
        current_time = time.time()
        current_memory = self.process.memory_info().rss
        
        return {
            'duration': current_time - self.start_time,
            'memory_used': (current_memory - self.start_memory) / 1024 / 1024,  # MB
            'cpu_percent': self.process.cpu_percent()
        }

# Create analyzer and monitor
analyzer = SizeAnalyzer()
monitor = PerformanceMonitor()

# Start monitoring
monitor.start_monitoring()

# Perform analysis
results = analyzer.analyze_directory("/path/to/directory")

# Get performance stats
stats = monitor.get_stats()
print(f"Analysis completed in {stats['duration']:.2f} seconds")
print(f"Memory used: {stats['memory_used']:.2f} MB")
print(f"CPU usage: {stats['cpu_percent']:.1f}%")

# Get analyzer performance metrics
metrics = analyzer.get_performance_metrics()
print(f"Files per second: {metrics['files_per_second']:.2f}")
print(f"Bytes per second: {analyzer.format_size(int(metrics['bytes_per_second']))}/s")
```

### Batch Processing

```python
import os
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

def analyze_multiple_directories(directories):
    """Analyze multiple directories and return combined results."""
    analyzer = SizeAnalyzer()
    all_results = []
    
    for directory in directories:
        if os.path.exists(directory) and os.path.isdir(directory):
            try:
                print(f"Analyzing {directory}...")
                results = analyzer.analyze_directory(directory)
                results['source_directory'] = directory
                all_results.append(results)
                
                # Display summary
                size = analyzer.format_size(results['total_size'])
                print(f"  {results['file_count']} files, {size}")
                
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"  Skipped: {directory} (not found or not a directory)")
    
    return all_results

# Analyze multiple directories
directories = [
    "/home/user/documents",
    "/home/user/downloads",
    "/home/user/pictures",
    "/home/user/videos"
]

results = analyze_multiple_directories(directories)

# Generate summary report
total_files = sum(r['file_count'] for r in results)
total_size = sum(r['total_size'] for r in results)

print(f"\nSummary:")
print(f"Total directories analyzed: {len(results)}")
print(f"Total files: {total_files}")
print(f"Total size: {SizeAnalyzer().format_size(total_size)}")
```

---

## Integration with Hub

### Basic Hub Integration

```python
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
from file_utilities_2.integration.hub_connector import HubConnector

# Create hub connector
hub_connector = HubConnector("Size Analyzer")

# Create GUI with hub integration
gui = SizeAnalyzerGUI(hub_instance=hub_connector)

# Register with hub
success = gui.register_with_hub(hub_connector)
if success:
    print("Successfully registered with hub")
    
    # Report initial status
    gui.report_status_to_hub("ready", {
        "initialization_complete": True,
        "features_available": ["directory_analysis", "export", "progress_tracking"]
    })
else:
    print("Failed to register with hub")

# Show GUI
gui.show()
```

### Hub Resource Coordination

```python
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

# Create GUI instance
gui = SizeAnalyzerGUI(hub_instance=hub_instance)

# Request resources before starting analysis
def start_analysis_with_resources():
    # Define resource requirements
    requirements = {
        "operation": "directory_analysis",
        "priority": "normal",
        "estimated_duration": 300,  # 5 minutes
        "memory_limit_mb": 256,
        "cpu_priority": "normal"
    }
    
    # Request CPU resources
    cpu_granted = gui.request_hub_resources("cpu", requirements)
    
    # Request memory resources
    memory_granted = gui.request_hub_resources("memory", requirements)
    
    if cpu_granted and memory_granted:
        print("Resources granted, starting analysis...")
        gui._start_analysis()
    else:
        print("Resources not available, please try again later")
        gui.show_warning_dialog(
            "Resources Unavailable",
            "System resources are currently busy. Please try again later."
        )

# Connect to button or call directly
start_analysis_with_resources()
```

### Hub Event Broadcasting

```python
from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI

class HubIntegratedAnalyzer(SizeAnalyzerGUI):
    def __init__(self, hub_instance=None):
        super().__init__(hub_instance)
        
        # Connect to analysis completion
        self.analyzer.analysis_complete.connect(self._on_analysis_complete_hub)
    
    def _on_analysis_complete_hub(self, results):
        """Handle analysis completion with hub broadcasting."""
        # Call parent handler
        super()._analysis_complete(results)
        
        # Broadcast completion event to other tools
        event_data = {
            "tool": "Size Analyzer",
            "directory": results.get('path', ''),
            "summary": {
                "file_count": results.get('file_count', 0),
                "total_size": results.get('total_size', 0),
                "largest_file": results.get('largest_files', [{}])[0].get('name', 'N/A') if results.get('largest_files') else 'N/A'
            },
            "completion_time": self.hub_connector.tool_state['last_activity'].isoformat()
        }
        
        self.broadcast_hub_event("analysis_completed", event_data)
        
        # Notify other tools that might be interested
        self.broadcast_hub_event("directory_analyzed", {
            "directory": results.get('path', ''),
            "tool": "Size Analyzer",
            "available_data": ["file_list", "size_statistics", "file_types"]
        })

# Usage
analyzer = HubIntegratedAnalyzer(hub_instance=hub_instance)
analyzer.show()
```

---

## Command Line Usage

### Direct Script Execution

```bash
# Run GUI application
python -m file_utilities_2.gui.size_analyzer_gui

# Run with specific directory (programmatic)
python -c "
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
analyzer = SizeAnalyzer()
results = analyzer.analyze_directory('/path/to/directory')
print(f'Total size: {analyzer.format_size(results[\"total_size\"])}')
print(f'File count: {results[\"file_count\"]}')
"
```

### Batch Analysis Script

Create a script for batch processing:

```python
#!/usr/bin/env python3
"""
Batch Size Analyzer Script
Usage: python batch_analyze.py directory1 directory2 ...
"""

import sys
import json
from pathlib import Path
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer

def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_analyze.py directory1 directory2 ...")
        sys.exit(1)
    
    analyzer = SizeAnalyzer()
    results = {}
    
    for directory in sys.argv[1:]:
        directory_path = Path(directory)
        
        if not directory_path.exists():
            print(f"Error: {directory} does not exist")
            continue
        
        if not directory_path.is_dir():
            print(f"Error: {directory} is not a directory")
            continue
        
        try:
            print(f"Analyzing {directory}...")
            analysis = analyzer.analyze_directory(str(directory_path))
            
            # Store results
            results[directory] = {
                'total_size': analysis['total_size'],
                'total_size_formatted': analyzer.format_size(analysis['total_size']),
                'file_count': analysis['file_count'],
                'directory_count': analysis['directory_count'],
                'largest_files': analysis['largest_files'][:5],  # Top 5
                'file_types': analysis['file_types']
            }
            
            # Print summary
            print(f"  Files: {analysis['file_count']}")
            print(f"  Size: {analyzer.format_size(analysis['total_size'])}")
            print(f"  Directories: {analysis['directory_count']}")
            
        except Exception as e:
            print(f"Error analyzing {directory}: {e}")
            results[directory] = {'error': str(e)}
    
    # Save results to JSON
    output_file = "batch_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
```

Save as `batch_analyze.py` and use:

```bash
# Make executable (Linux/macOS)
chmod +x batch_analyze.py

# Run batch analysis
python batch_analyze.py /home/user/documents /home/user/downloads /home/user/pictures

# Or on Windows
python batch_analyze.py "C:\Users\User\Documents" "C:\Users\User\Downloads"
```

### Shell Integration

#### Bash Function (Linux/macOS)

Add to your `.bashrc` or `.zshrc`:

```bash
# Size Analyzer function
analyze_size() {
    if [ $# -eq 0 ]; then
        echo "Usage: analyze_size <directory>"
        return 1
    fi
    
    python -c "
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
import sys
analyzer = SizeAnalyzer()
try:
    results = analyzer.analyze_directory('$1')
    print(f'Directory: $1')
    print(f'Total size: {analyzer.format_size(results[\"total_size\"])}')
    print(f'Files: {results[\"file_count\"]:,}')
    print(f'Directories: {results[\"directory_count\"]:,}')
    print('\\nLargest files:')
    for i, file_info in enumerate(results['largest_files'][:5], 1):
        size = analyzer.format_size(file_info['size'])
        print(f'  {i}. {file_info[\"name\"]} ({size})')
except Exception as e:
    print(f'Error: {e}')
"
}
```

Usage:
```bash
analyze_size /home/user/documents
analyze_size /var/log
```

#### PowerShell Function (Windows)

Add to your PowerShell profile:

```powershell
function Analyze-Size {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Directory
    )
    
    $pythonCode = @"
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer
analyzer = SizeAnalyzer()
try:
    results = analyzer.analyze_directory('$Directory')
    print(f'Directory: $Directory')
    print(f'Total size: {analyzer.format_size(results["total_size"])}')
    print(f'Files: {results["file_count"]:,}')
    print(f'Directories: {results["directory_count"]:,}')
    print('\nLargest files:')
    for i, file_info in enumerate(results['largest_files'][:5], 1):
        size = analyzer.format_size(file_info['size'])
        print(f'  {i}. {file_info["name"]} ({size})')
except Exception as e:
    print(f'Error: {e}')
"@
    
    python -c $pythonCode
}
```

Usage:
```powershell
Analyze-Size "C:\Users\User\Documents"
Analyze-Size "C:\Program Files"
```

---

## Configuration Management

### Reading Configuration

```python
from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig

# Create configuration manager
config = SizeAnalyzerConfig()

# Get specific settings
top_files_count = config.get_setting('analysis', 'default_top_files_count', 20)
enable_logging = config.get_setting('general', 'enable_logging', True)
memory_limit = config.get_setting('performance', 'max_memory_usage_mb', 256)

print(f"Top files count: {top_files_count}")
print(f"Logging enabled: {enable_logging}")
print(f"Memory limit: {memory_limit} MB")

# Get all settings
all_settings = config.get_all_settings()
print("All settings:", all_settings)
```

### Updating Configuration

```python
from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig

config = SizeAnalyzerConfig()

# Update individual settings
config.set_setting('analysis', 'default_top_files_count', 25)
config.set_setting('performance', 'max_memory_usage_mb', 512)
config.set_setting('ui', 'window_geometry', {
    'width': 1000,
    'height': 700,
    'remember_size': True
})

# Add recent directory
config.add_recent_directory('/home/user/important_files')

# Save window geometry
config.save_window_geometry(1000, 700, 100, 100)

print("Configuration updated successfully")
```

### Configuration Validation

```python
from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig

config = SizeAnalyzerConfig()

# Validate configuration
issues = config.validate_configuration()

print("Configuration validation results:")
if issues['errors']:
    print("Errors:")
    for error in issues['errors']:
        print(f"  - {error}")

if issues['warnings']:
    print("Warnings:")
    for warning in issues['warnings']:
        print(f"  - {warning}")

if issues['info']:
    print("Info:")
    for info in issues['info']:
        print(f"  - {info}")

if not any(issues.values()):
    print("Configuration is valid!")
```

### Export/Import Configuration

```python
from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig

config = SizeAnalyzerConfig()

# Export configuration
export_success = config.export_configuration("my_size_analyzer_config.json")
if export_success:
    print("Configuration exported successfully")

# Import configuration
import_success = config.import_configuration("my_size_analyzer_config.json")
if import_success:
    print("Configuration imported successfully")
```

---

## Troubleshooting Installation

### Common Installation Issues

#### PyQt5 Installation Fails

**Problem**: Error during PyQt5 installation
```
ERROR: Failed building wheel for PyQt5
```

**Solutions**:

1. **Update pip and setuptools**:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Install system dependencies** (Linux):
   ```bash
   sudo apt-get update
   sudo apt-get install python3-dev python3-pyqt5.qtcore python3-pyqt5.qtgui python3-pyqt5.qtwidgets
   ```

3. **Use conda instead of pip**:
   ```bash
   conda install pyqt
   ```

4. **Install pre-compiled wheels**:
   ```bash
   pip install --only-binary=all PyQt5
   ```

#### Import Errors

**Problem**: Module not found errors
```python
ImportError: No module named 'file_utilities_2'
```

**Solutions**:

1. **Verify installation**:
   ```bash
   pip list | grep file-utilities
   python -c "import file_utilities_2; print('OK')"
   ```

2. **Check Python path**:
   ```python
   import sys
   print(sys.path)
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   ```

4. **Check virtual environment**:
   ```bash
   which python
   which pip
   ```

#### Permission Issues

**Problem**: Permission denied errors during installation

**Solutions**:

1. **Use user installation**:
   ```bash
   pip install --user -r requirements.txt
   ```

2. **Fix directory permissions**:
   ```bash
   sudo chown -R $USER:$USER ~/.local/lib/python*/site-packages/
   ```

3. **Use virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

### Platform-Specific Issues

#### Windows Issues

1. **Long path support**:
   ```bash
   # Enable long path support in Windows
   # Run as administrator:
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

2. **Visual C++ redistributable**:
   ```bash
   # Download and install Microsoft Visual C++ Redistributable
   # From: https://aka.ms/vs/16/release/vc_redist.x64.exe
   ```

#### Linux Issues

1. **Missing system libraries**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev libgl1-mesa-glx libglib2.0-0 libxrender1 libxrandr2 libxss1 libgtk-3-0
   
   # CentOS/RHEL
   sudo yum install python3-devel mesa-libGL-devel glib2-devel libXrender-devel libXrandr-devel libXss-devel gtk3-devel
   ```

2. **Display issues**:
   ```bash
   # Set display environment
   export DISPLAY=:0
   xhost +local:
   ```

#### macOS Issues

1. **Xcode command line tools**:
   ```bash
   xcode-select --install
   ```

2. **Homebrew dependencies**:
   ```bash
   brew install python-tk
   ```

---

## Verification and Testing

### Basic Functionality Test

```python
#!/usr/bin/env python3
"""
Size Analyzer Installation Verification Script
"""

import sys
import os
import tempfile
from pathlib import Path

def test_imports():
    """Test all required imports."""
    print("Testing imports...")
    
    try:
        from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer, SizeAnalyzerWorker
        print("  ✓ Core logic imports successful")
    except ImportError as e:
        print(f"  ✗ Core logic import failed: {e}")
        return False
    
    try:
        from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
        print("  ✓ GUI imports successful")
    except ImportError as e:
        print(f"  ✗ GUI import failed: {e}")
        return False
    
    try:
        from file_utilities_2.core.size_analyzer_config import SizeAnalyzerConfig
        print("  ✓ Configuration imports successful")
    except ImportError as e:
        print(f"  ✗ Configuration import failed: {e}")
        return False
    
    try:
        from file_utilities_2.integration.hub_connector import HubConnector
        print("  ✓ Hub integration imports successful")
    except ImportError as e:
        print(f"  ✗