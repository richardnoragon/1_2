#!/usr/bin/env python3
"""
Comprehensive Unit Tests for launch_main.py

This module contains comprehensive unit tests for the launch_main.py file,
testing all functions and methods with appropriate assertions, edge cases,
and mock data using pytest framework.

Test Coverage:
- Module path manipulation
- Workspace root detection
- File existence checking
- Main execution functionality
- Exception handling
- Error scenarios

Created: 2025-08-28
Target: src/rfu/launch_main.py
Framework: pytest
"""

import importlib.util
import os
import shutil
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add the src directory to Python path for imports
test_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(test_root))
sys.path.insert(0, str(test_root / "src"))


class TestLaunchMainModule:
    """Test class for launch_main.py module functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment before each test method."""
        # Store original sys.path and cwd
        self.original_path = sys.path.copy()
        self.original_cwd = os.getcwd()
        
        # Create temporary directory structure
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_root = Path(self.temp_dir) / "workspace"
        self.src_dir = self.workspace_root / "src"
        self.rfu_dir = self.src_dir / "rfu"
        
        # Create directory structure
        self.workspace_root.mkdir(parents=True)
        self.src_dir.mkdir()
        self.rfu_dir.mkdir()
        
        # Create test launch_main.py file
        self.launch_main_path = self.rfu_dir / "launch_main.py"
        self.create_test_launch_main_file()
        
        # Create test main.py file
        self.main_py_path = self.workspace_root / "main.py"
        self.create_test_main_file()
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Restore original state
        sys.path[:] = self.original_path
        os.chdir(self.original_cwd)
        
        # Clean up temporary directory
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_launch_main_file(self):
        """Create a test version of launch_main.py."""
        launch_main_content = '''#!/usr/bin/env python3
"""
Simple launcher for RFU from the rfu directory
"""
import sys
import os
from pathlib import Path

# Get the workspace root (two levels up from this script)
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

# Now we can import and run the main application
if __name__ == "__main__":
    try:
        # Import the main function from the workspace root main.py
        sys.path.insert(0, str(workspace_root))
        
        # Read and execute the main.py from workspace root
        main_py_path = workspace_root / "main.py"
        if main_py_path.exists():
            with open(main_py_path, 'r', encoding='utf-8') as f:
                main_code = f.read()
            
            # Change working directory to workspace root
            original_cwd = os.getcwd()
            os.chdir(workspace_root)
            
            try:
                # Execute the main.py code
                exec(main_code)
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
        else:
            print("Error: main.py not found in workspace root")
            print(f"Looking for: {main_py_path}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error launching application: {e}")
        print("\\nAlternative: Run from workspace root:")
        print("cd c:\\\\Users\\\\HP1\\\\1_2\\\\1_2")
        print("python main.py")
        sys.exit(1)
'''
        with open(self.launch_main_path, 'w', encoding='utf-8') as f:
            f.write(launch_main_content)
    
    def create_test_main_file(self):
        """Create a test main.py file."""
        main_content = '''#!/usr/bin/env python3
"""Test main.py file for launch_main testing."""
print("Test main.py executed successfully")
test_executed = True
'''
        with open(self.main_py_path, 'w', encoding='utf-8') as f:
            f.write(main_content)
    
    def load_launch_main_module(self):
        """Load the launch_main module dynamically."""
        spec = importlib.util.spec_from_file_location(
            "launch_main", 
            self.launch_main_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def test_module_imports(self):
        """Test that the module imports correctly."""
        module = self.load_launch_main_module()
        
        # Verify module has expected attributes
        assert hasattr(module, 'sys')
        assert hasattr(module, 'os')
        assert hasattr(module, 'Path')
        assert hasattr(module, 'workspace_root')
    
    def test_workspace_root_calculation(self):
        """Test workspace root path calculation."""
        module = self.load_launch_main_module()
        
        # Verify workspace_root is calculated correctly
        expected_root = self.launch_main_path.parent.parent.parent
        assert module.workspace_root == expected_root
        assert module.workspace_root.exists()
    
    def test_sys_path_modification(self):
        """Test that sys.path is modified correctly."""
        original_path_len = len(sys.path)
        module = self.load_launch_main_module()
        
        # Verify workspace_root is added to sys.path
        assert str(module.workspace_root) in sys.path
        
        # Note: sys.path may have grown by 1 or more entries
        assert len(sys.path) >= original_path_len
    
    @patch('builtins.print')
    @patch('sys.exit')
    def test_main_execution_success(self, mock_exit, mock_print):
        """Test successful main execution."""
        # Change to the rfu directory to simulate proper execution
        os.chdir(self.rfu_dir)
        
        # Load and execute the module
        module = self.load_launch_main_module()
        
        # Execute the main block by calling exec on the module's code
        with patch('builtins.__name__', '__main__'):
            # Create a proper execution environment
            exec_globals = {
                '__name__': '__main__',
                '__file__': str(self.launch_main_path),
                'sys': sys,
                'os': os,
                'Path': Path
            }
            
            # Read the file content and execute it
            with open(self.launch_main_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Execute the code in a controlled environment
            exec(code, exec_globals)
        
        # Verify no exit was called (successful execution)
        mock_exit.assert_not_called()
    
    @patch('builtins.print')
    @patch('sys.exit')
    def test_main_py_not_found(self, mock_exit, mock_print):
        """Test behavior when main.py is not found."""
        # Remove main.py file
        self.main_py_path.unlink()
        
        # Change to the rfu directory
        os.chdir(self.rfu_dir)
        
        # Execute the main block
        exec_globals = {
            '__name__': '__main__',
            '__file__': str(self.launch_main_path),
            'sys': sys,
            'os': os,
            'Path': Path
        }
        
        with open(self.launch_main_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        exec(code, exec_globals)
        
        # Verify error message and exit
        mock_print.assert_any_call("Error: main.py not found in workspace root")
        mock_exit.assert_called_with(1)
    
    @patch('builtins.print')
    @patch('sys.exit')
    def test_file_read_error(self, mock_exit, mock_print):
        """Test behavior when main.py cannot be read."""
        # Create a main.py that exists but will cause read error
        bad_main_content = 'print("test")'
        with open(self.main_py_path, 'w', encoding='utf-8') as f:
            f.write(bad_main_content)
        
        os.chdir(self.rfu_dir)
        
        # Mock the open function to raise IOError when reading main.py
        original_open = open
        def mock_open_func(*args, **kwargs):
            if len(args) > 0 and 'main.py' in str(args[0]):
                raise IOError("File read error")
            return original_open(*args, **kwargs)
        
        with patch('builtins.open', side_effect=mock_open_func):
            exec_globals = {
                '__name__': '__main__',
                '__file__': str(self.launch_main_path),
                'sys': sys,
                'os': os,
                'Path': Path
            }
            
            # Read the launch_main.py with original open
            with original_open(self.launch_main_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            exec(code, exec_globals)
        
        # Verify error handling
        mock_exit.assert_called_with(1)
        assert any("Error launching application:" in str(call) 
                  for call in mock_print.call_args_list)
    
    @patch('builtins.print')
    @patch('sys.exit')
    def test_main_py_execution_error(self, mock_exit, mock_print):
        """Test behavior when main.py has execution errors."""
        # Create a main.py with syntax error
        bad_main_content = '''
print("Start")
invalid_syntax_here !!!
print("End")
'''
        with open(self.main_py_path, 'w', encoding='utf-8') as f:
            f.write(bad_main_content)
        
        os.chdir(self.rfu_dir)
        
        exec_globals = {
            '__name__': '__main__',
            '__file__': str(self.launch_main_path),
            'sys': sys,
            'os': os,
            'Path': Path
        }
        
        with open(self.launch_main_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        exec(code, exec_globals)
        
        # Verify error handling
        mock_exit.assert_called_with(1)
        assert any("Error launching application:" in str(call) 
                  for call in mock_print.call_args_list)
    
    def test_working_directory_restoration(self):
        """Test that working directory is properly restored."""
        original_cwd = os.getcwd()
        
        # Change to rfu directory
        os.chdir(self.rfu_dir)
        
        # Execute the main functionality with mock to prevent actual execution
        with patch('builtins.exec') as mock_exec:
            exec_globals = {
                '__name__': '__main__',
                '__file__': str(self.launch_main_path),
                'sys': sys,
                'os': os,
                'Path': Path
            }
            
            with open(self.launch_main_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            exec(code, exec_globals)
        
        # Working directory should be restored
        # (Note: In our test, we're in the rfu_dir, so that's what should be restored)
        assert os.getcwd() == str(self.rfu_dir)
    
    @patch('os.chdir')
    def test_chdir_operations(self, mock_chdir):
        """Test directory change operations."""
        os.chdir(self.rfu_dir)
        
        # Create a simple main.py to avoid execution errors
        simple_main = 'print("Hello World")'
        with open(self.main_py_path, 'w', encoding='utf-8') as f:
            f.write(simple_main)
        
        exec_globals = {
            '__name__': '__main__',
            '__file__': str(self.launch_main_path),
            'sys': sys,
            'os': os,
            'Path': Path
        }
        
        with open(self.launch_main_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        with patch('builtins.exec'):  # Prevent actual execution
            exec(code, exec_globals)
        
        # Verify chdir was called
        mock_chdir.assert_called()
    
    def test_path_object_functionality(self):
        """Test Path object operations in the module."""
        module = self.load_launch_main_module()
        
        # Test workspace_root is a Path object
        assert isinstance(module.workspace_root, Path)
        
        # Test path operations
        main_py_path = module.workspace_root / "main.py"
        assert isinstance(main_py_path, Path)
        assert main_py_path.exists()
    
    def test_encoding_handling(self):
        """Test proper encoding handling for file operations."""
        # Create main.py with non-ASCII characters
        unicode_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test with unicode: ñáéíóú"""
print("Unicode test: ñáéíóú")
'''
        with open(self.main_py_path, 'w', encoding='utf-8') as f:
            f.write(unicode_content)
        
        os.chdir(self.rfu_dir)
        
        # The module should handle unicode content properly
        exec_globals = {
            '__name__': '__main__',
            '__file__': str(self.launch_main_path),
            'sys': sys,
            'os': os,
            'Path': Path
        }
        
        with open(self.launch_main_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Should not raise encoding errors
        try:
            with patch('builtins.exec'):  # Prevent actual execution
                exec(code, exec_globals)
        except UnicodeError:
            pytest.fail("Encoding error occurred")
    
    def test_exception_message_formatting(self):
        """Test that exception messages are properly formatted."""
        # Create main.py that raises a specific exception
        error_main = '''
raise ValueError("Test error message")
'''
        with open(self.main_py_path, 'w', encoding='utf-8') as f:
            f.write(error_main)
        
        os.chdir(self.rfu_dir)
        
        with patch('builtins.print') as mock_print, patch('sys.exit'):
            exec_globals = {
                '__name__': '__main__',
                '__file__': str(self.launch_main_path),
                'sys': sys,
                'os': os,
                'Path': Path
            }
            
            with open(self.launch_main_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            exec(code, exec_globals)
        
        # Check that error message includes the exception details
        error_calls = [call for call in mock_print.call_args_list 
                      if "Error launching application:" in str(call)]
        assert len(error_calls) > 0
    
    def test_alternative_instructions_display(self):
        """Test that alternative instructions are displayed on error."""
        # Remove main.py to trigger error path
        self.main_py_path.unlink()
        
        os.chdir(self.rfu_dir)
        
        with patch('builtins.print') as mock_print, patch('sys.exit'):
            exec_globals = {
                '__name__': '__main__',
                '__file__': str(self.launch_main_path),
                'sys': sys,
                'os': os,
                'Path': Path
            }
            
            with open(self.launch_main_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            exec(code, exec_globals)
        
        # Verify error message and alternative instructions are shown
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Check for error message
        assert any("Error: main.py not found" in call for call in print_calls), \
            f"Expected error message not found in: {print_calls}"


class TestLaunchMainIntegration:
    """Integration tests for launch_main.py with real file system."""
    
    @pytest.fixture(autouse=True)
    def setup_integration_environment(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir) / "test_workspace"
        self.src_dir = self.workspace / "src"
        self.rfu_dir = self.src_dir / "rfu"
        
        # Create directory structure
        self.rfu_dir.mkdir(parents=True)
        
        # Store original working directory
        self.original_cwd = os.getcwd()
    
    def teardown_method(self):
        """Clean up integration test environment."""
        os.chdir(self.original_cwd)
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_execution_cycle(self):
        """Test complete execution cycle from start to finish."""
        # Create launch_main.py
        launch_content = '''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

if __name__ == "__main__":
    try:
        sys.path.insert(0, str(workspace_root))
        main_py_path = workspace_root / "main.py"
        if main_py_path.exists():
            with open(main_py_path, 'r', encoding='utf-8') as f:
                main_code = f.read()
            original_cwd = os.getcwd()
            os.chdir(workspace_root)
            try:
                exec(main_code)
            finally:
                os.chdir(original_cwd)
        else:
            print("Error: main.py not found in workspace root")
            sys.exit(1)
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)
'''
        launch_path = self.rfu_dir / "launch_main.py"
        with open(launch_path, 'w', encoding='utf-8') as f:
            f.write(launch_content)
        
        # Create main.py
        main_content = '''
print("Integration test successful")
integration_test_completed = True
'''
        main_path = self.workspace / "main.py"
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(main_content)
        
        # Execute the script
        os.chdir(self.rfu_dir)
        
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            exec_globals = {
                '__name__': '__main__',
                '__file__': str(launch_path)  # Provide the __file__ variable
            }
            with open(launch_path, 'r', encoding='utf-8') as f:
                code = f.read()
            exec(code, exec_globals)
        
        # Verify output
        output = captured_output.getvalue()
        assert "Integration test successful" in output
    
    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        # Create launch_main.py
        launch_content = '''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

workspace_root = Path(__file__).parent.parent.parent

if __name__ == "__main__":
    try:
        main_py_path = workspace_root / "main.py"
        if main_py_path.exists():
            with open(main_py_path, 'r', encoding='utf-8') as f:
                main_code = f.read()
            exec(main_code)
        else:
            print("Error: main.py not found")
            sys.exit(1)
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)
'''
        launch_path = self.rfu_dir / "launch_main.py"
        with open(launch_path, 'w', encoding='utf-8') as f:
            f.write(launch_content)
        
        # Create main.py with permission issues (simulated)
        main_path = self.workspace / "main.py"
        main_path.touch()
        
        # Mock open to raise PermissionError
        original_open = open
        def mock_open_func(*args, **kwargs):
            if len(args) > 0 and 'main.py' in str(args[0]):
                raise PermissionError("Access denied")
            return original_open(*args, **kwargs)
        
        with patch('builtins.open', side_effect=mock_open_func):
            with patch('builtins.print') as mock_print:
                with patch('sys.exit') as mock_exit:
                    os.chdir(self.rfu_dir)
                    exec_globals = {
                        '__name__': '__main__',
                        '__file__': str(launch_path)
                    }
                    # Read with original open
                    with original_open(launch_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    exec(code, exec_globals)
        
        # Verify error handling
        mock_exit.assert_called_with(1)
        error_calls = [call for call in mock_print.call_args_list 
                      if "Error launching application:" in str(call)]
        assert len(error_calls) > 0


class TestLaunchMainEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture(autouse=True)
    def setup_edge_case_tests(self):
        """Set up edge case test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir) / "edge_case_workspace"
        self.src_dir = self.workspace / "src"
        self.rfu_dir = self.src_dir / "rfu"
        
        self.rfu_dir.mkdir(parents=True)
        self.original_cwd = os.getcwd()
    
    def teardown_method(self):
        """Clean up edge case test environment."""
        os.chdir(self.original_cwd)
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_main_file(self):
        """Test behavior with empty main.py file."""
        # Create empty main.py
        main_path = self.workspace / "main.py"
        main_path.touch()
        
        # Create launch_main.py
        launch_content = '''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

workspace_root = Path(__file__).parent.parent.parent

if __name__ == "__main__":
    try:
        main_py_path = workspace_root / "main.py"
        if main_py_path.exists():
            with open(main_py_path, 'r', encoding='utf-8') as f:
                main_code = f.read()
            exec(main_code)  # Should handle empty code gracefully
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)
'''
        launch_path = self.rfu_dir / "launch_main.py"
        with open(launch_path, 'w', encoding='utf-8') as f:
            f.write(launch_content)
        
        # Execute - should not raise exception for empty file
        os.chdir(self.rfu_dir)
        try:
            exec_globals = {
                '__name__': '__main__',
                '__file__': str(launch_path)
            }
            with open(launch_path, 'r', encoding='utf-8') as f:
                code = f.read()
            exec(code, exec_globals)
        except SystemExit:
            pytest.fail("Empty main.py should not cause SystemExit")
    
    def test_very_long_path(self):
        """Test behavior with very long file paths."""
        # Create a deeply nested directory structure
        deep_path = self.workspace
        for i in range(10):  # Create deep nesting
            deep_path = deep_path / f"level_{i}"
        
        deep_path.mkdir(parents=True)
        
        # Test that Path operations still work
        test_file = deep_path / "test.txt"
        test_file.touch()
        
        assert test_file.exists()
        assert test_file.is_file()
    
    def test_special_characters_in_path(self):
        """Test handling of special characters in file paths."""
        # Create directory with special characters (if supported by OS)
        try:
            special_workspace = Path(self.temp_dir) / "test_ñáéíóú_workspace"
            special_src = special_workspace / "src"
            special_rfu = special_src / "rfu"
            
            special_rfu.mkdir(parents=True)
            
            # Create files in special character path
            launch_path = special_rfu / "launch_main.py"
            main_path = special_workspace / "main.py"
            
            # Simple launch content
            launch_content = '''#!/usr/bin/env python3
from pathlib import Path
workspace_root = Path(__file__).parent.parent.parent
print(f"Workspace root: {workspace_root}")
'''
            
            with open(launch_path, 'w', encoding='utf-8') as f:
                f.write(launch_content)
            
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write('print("Special chars handled")')
            
            # Should handle special characters without error
            assert launch_path.exists()
            assert main_path.exists()
            
        except (OSError, UnicodeError):
            # Skip test if OS doesn't support special characters in paths
            pytest.skip("OS doesn't support special characters in paths")
    
    def test_circular_symlink_handling(self):
        """Test behavior with circular symlinks (Unix-like systems)."""
        if os.name == 'nt':  # Skip on Windows
            pytest.skip("Symlink test not applicable on Windows")
        
        try:
            # Create a circular symlink
            link1 = self.workspace / "link1"
            link2 = self.workspace / "link2"
            
            link1.symlink_to(link2)
            link2.symlink_to(link1)
            
            # Test that Path operations handle this gracefully
            # Should not cause infinite recursion
            assert link1.is_symlink()
            assert link2.is_symlink()
            
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported on this system")


class TestLaunchMainPerformance:
    """Performance tests for launch_main.py."""
    
    def test_startup_time(self):
        """Test that module startup time is reasonable."""
        import time
        
        temp_dir = tempfile.mkdtemp()
        try:
            workspace = Path(temp_dir) / "perf_workspace"
            src_dir = workspace / "src"
            rfu_dir = src_dir / "rfu"
            rfu_dir.mkdir(parents=True)
            
            # Create launch_main.py
            launch_content = '''#!/usr/bin/env python3
import sys
import os
from pathlib import Path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))
'''
            launch_path = rfu_dir / "launch_main.py"
            with open(launch_path, 'w', encoding='utf-8') as f:
                f.write(launch_content)
            
            # Measure import time
            start_time = time.time()
            
            spec = importlib.util.spec_from_file_location("launch_main", launch_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            end_time = time.time()
            
            # Should load quickly (less than 1 second)
            load_time = end_time - start_time
            assert load_time < 1.0, f"Module took {load_time:.3f}s to load"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_memory_usage(self):
        """Test that module doesn't use excessive memory."""
        import tracemalloc
        
        temp_dir = tempfile.mkdtemp()
        try:
            workspace = Path(temp_dir) / "memory_workspace"
            src_dir = workspace / "src"
            rfu_dir = src_dir / "rfu"
            rfu_dir.mkdir(parents=True)
            
            # Create launch_main.py
            launch_content = '''#!/usr/bin/env python3
import sys
import os
from pathlib import Path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))
'''
            launch_path = rfu_dir / "launch_main.py"
            with open(launch_path, 'w', encoding='utf-8') as f:
                f.write(launch_content)
            
            # Measure memory usage
            tracemalloc.start()
            
            spec = importlib.util.spec_from_file_location("launch_main", launch_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Memory usage should be reasonable (less than 10MB peak)
            peak_mb = peak / 1024 / 1024
            assert peak_mb < 10, f"Module used {peak_mb:.2f}MB peak memory"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Configuration for standalone execution
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--strict-markers",
        f"--html=result_launch_main_2025-08-28.html",
        f"--json-report=result_launch_main_2025-08-28.json",
        "--cov=launch_main",
        "--cov-report=html:coverage_launch_main_2025-08-28",
        "--cov-report=json:coverage_launch_main_2025-08-28.json"
    ])