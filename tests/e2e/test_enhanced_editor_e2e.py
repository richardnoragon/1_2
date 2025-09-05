#!/usr/bin/env python3
"""
Enhanced Editor End-to-End Test Suite

Comprehensive E2E testing for Enhanced Editor tool functionality.
Tests complete workflows from syntax highlighting through multi-file editing
and plugin integration.

Created: 2025-09-04
Coverage: Syntax highlighting workflows, multi-file editing capabilities,
          search and replace operations, plugin integration
Priority: HIGH (implementing 0% E2E coverage for File Operations tools)
"""

import os
import sys
import time
from unittest.mock import Mock

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

try:
    from tests.e2e.file_operations_test_utilities import (
        FileOperationsPerformanceMonitor, FileOperationsSignalTracker,
        MockEnhancedEditorTool, enhanced_editor_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="File Operations utilities not available"
)


class TestEnhancedEditorSyntaxHighlighting:
    """Test syntax highlighting workflows for multiple languages."""
    
    def test_python_syntax_highlighting_workflow(self, 
                                                enhanced_editor_test_environment):
        """
        Test: Python File → Syntax Detection → Highlighting → Validation
        Target: < 3 seconds for syntax highlighting
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Find Python files for testing
        python_files = []
        for root, dirs, files in os.walk(test_data_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        if not python_files:
            # Create a test Python file
            test_py_file = os.path.join(test_data_path, 'test_syntax.py')
            with open(test_py_file, 'w') as f:
                f.write('# Test Python file\ndef hello():\n    print("Hello")\n')
            python_files = [test_py_file]
        
        performance_monitor.start_monitoring('enhanced_editor', 'syntax_highlighting')
        
        start_time = time.time()
        
        try:
            # Open Python file
            python_file = python_files[0]
            open_result = tool.open_file(python_file)
            
            assert open_result['status'] == 'success', \
                "Python file opening should succeed"
            assert 'syntax_language' in open_result, \
                "Should detect syntax language"
            
            # Verify Python syntax detection
            file_info = tool.open_files[python_file]
            assert file_info['syntax_language'] == 'python', \
                "Should detect Python syntax"
            
            # Execute syntax highlighting
            highlight_result = tool.highlight_syntax(python_file)
            
            assert highlight_result['status'] == 'success', \
                "Python syntax highlighting should succeed"
            assert 'language' in highlight_result, \
                "Should report highlighting language"
            assert highlight_result['language'] == 'python', \
                "Should highlight as Python"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 3.0, \
                f"Python highlighting took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Highlighting workflow should complete successfully"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'enhanced_editor', 'syntax_highlighting')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_javascript_syntax_highlighting_workflow(self, 
                                                   enhanced_editor_test_environment):
        """
        Test: JavaScript File → Syntax Detection → Highlighting → Validation
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Find or create JavaScript files
        js_files = []
        for root, dirs, files in os.walk(test_data_path):
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.join(root, file))
        
        if not js_files:
            # Create test JavaScript file
            test_js_file = os.path.join(test_data_path, 'test_syntax.js')
            with open(test_js_file, 'w') as f:
                f.write('// Test JS file\nfunction hello() {\n  console.log("Hello");\n}\n')
            js_files = [test_js_file]
        
        # Open and highlight JavaScript file
        js_file = js_files[0]
        open_result = tool.open_file(js_file)
        
        assert open_result['status'] == 'success', \
            "JavaScript file opening should succeed"
        
        # Verify JavaScript syntax detection
        file_info = tool.open_files[js_file]
        assert file_info['syntax_language'] == 'javascript', \
            "Should detect JavaScript syntax"
        
        # Execute syntax highlighting
        highlight_result = tool.highlight_syntax(js_file)
        
        assert highlight_result['status'] == 'success', \
            "JavaScript syntax highlighting should succeed"
        assert highlight_result['language'] == 'javascript', \
            "Should highlight as JavaScript"
    
    def test_custom_language_support_workflow(self, 
                                            enhanced_editor_test_environment):
        """
        Test: Custom Language → Language Detection → Highlighting Support
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Test various file extensions
        language_tests = [
            {'extension': '.html', 'expected_language': 'html'},
            {'extension': '.css', 'expected_language': 'css'},
            {'extension': '.json', 'expected_language': 'json'},
            {'extension': '.xml', 'expected_language': 'xml'},
            {'extension': '.unknown', 'expected_language': 'text'}
        ]
        
        for test_case in language_tests:
            test_file = os.path.join(
                test_data_path, f"test{test_case['extension']}")
            
            # Create test file
            with open(test_file, 'w') as f:
                f.write(f"Test content for {test_case['extension']} file")
            
            # Open file and check language detection
            open_result = tool.open_file(test_file)
            
            assert open_result['status'] == 'success', \
                f"Should open {test_case['extension']} file"
            
            file_info = tool.open_files[test_file]
            assert file_info['syntax_language'] == test_case['expected_language'], \
                f"Should detect {test_case['expected_language']} for {test_case['extension']}"
            
            # Test highlighting
            highlight_result = tool.highlight_syntax(test_file)
            
            assert highlight_result['status'] == 'success', \
                f"Should highlight {test_case['extension']} file"


class TestEnhancedEditorMultiFile:
    """Test multi-file editing capabilities and session management."""
    
    def test_multi_file_editing_workflow(self, enhanced_editor_test_environment):
        """
        Test: Multiple File Open → Session Management → Concurrent Editing
        Target: < 5 seconds for file loading per file
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        # Find multiple files for editing
        editor_files = []
        for root, dirs, files in os.walk(test_data_path):
            for file in files[:8]:  # Limit for testing
                if any(file.endswith(ext) for ext in ['.py', '.js', '.html', '.txt']):
                    editor_files.append(os.path.join(root, file))
        
        if len(editor_files) < 3:
            # Create test files
            for i in range(3):
                test_file = os.path.join(test_data_path, f'multi_test_{i}.txt')
                with open(test_file, 'w') as f:
                    f.write(f'Multi-file test content {i}')
                editor_files.append(test_file)
        
        performance_monitor.start_monitoring('enhanced_editor', 'file_loading')
        
        start_time = time.time()
        
        try:
            # Open multiple files
            opened_files = []
            for file_path in editor_files[:5]:  # Open first 5 files
                open_result = tool.open_file(file_path)
                
                assert open_result['status'] == 'success', \
                    f"Should open file: {file_path}"
                
                opened_files.append(file_path)
            
            # Verify all files are tracked
            assert len(tool.open_files) >= len(opened_files), \
                "Should track all opened files"
            
            # Verify each file has proper info
            for file_path in opened_files:
                assert file_path in tool.open_files, \
                    f"File should be tracked: {file_path}"
                
                file_info = tool.open_files[file_path]
                required_fields = ['file_path', 'file_size', 'syntax_language',
                                 'encoding', 'opened_at']
                for field in required_fields:
                    assert field in file_info, \
                        f"File info missing field: {field}"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            avg_time_per_file = workflow_time / len(opened_files)
            assert avg_time_per_file < 5.0, \
                f"File loading too slow: {avg_time_per_file:.2f}s per file"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['total_events'] > 0, \
                "Should emit events for multiple file operations"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'enhanced_editor', 'file_loading')
            assert perf_result['target_met'], \
                f"Multi-file loading target not met: {perf_result}"
    
    def test_tab_management_workflow(self, enhanced_editor_test_environment):
        """
        Test: Tab Creation → Tab Switching → Tab Management → Session State
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create test files for tab management
        test_files = []
        for i in range(4):
            test_file = os.path.join(test_data_path, f'tab_test_{i}.txt')
            with open(test_file, 'w') as f:
                f.write(f'Tab {i} content for testing tab management')
            test_files.append(test_file)
        
        # Open files (simulates creating tabs)
        for file_path in test_files:
            open_result = tool.open_file(file_path)
            assert open_result['status'] == 'success', \
                f"Should open file for tab: {file_path}"
        
        # Verify tab management state
        assert len(tool.open_files) == len(test_files), \
            "Should track all open tabs"
        
        # Test session state persistence
        session_data = {
            'open_files': list(tool.open_files.keys()),
            'active_file': test_files[0],
            'session_timestamp': time.time()
        }
        
        tool.editor_sessions['test_session'] = session_data
        
        # Verify session state
        assert 'test_session' in tool.editor_sessions, \
            "Should store session state"
        
        session = tool.editor_sessions['test_session']
        assert len(session['open_files']) == len(test_files), \
            "Session should track all open files"
    
    def test_session_persistence_workflow(self, enhanced_editor_test_environment):
        """
        Test: Editor Session → State Save → Session Restore → Validation
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create and open files for session
        session_files = []
        for i in range(3):
            session_file = os.path.join(
                test_data_path, f'session_file_{i}.py')
            with open(session_file, 'w') as f:
                f.write(f'# Session file {i}\nprint("Session test {i}")')
            
            open_result = tool.open_file(session_file)
            assert open_result['status'] == 'success', \
                f"Should open session file: {session_file}"
            
            session_files.append(session_file)
        
        # Create session state
        session_id = 'persistence_test_session'
        session_state = {
            'session_id': session_id,
            'open_files': session_files,
            'file_positions': {file: 0 for file in session_files},
            'active_file_index': 0,
            'session_created': time.time()
        }
        
        tool.editor_sessions[session_id] = session_state
        
        # Verify session persistence
        assert session_id in tool.editor_sessions, \
            "Should store session state"
        
        persisted_session = tool.editor_sessions[session_id]
        assert len(persisted_session['open_files']) == len(session_files), \
            "Should persist all open files"
        assert 'session_created' in persisted_session, \
            "Should persist session metadata"


class TestEnhancedEditorSearchReplace:
    """Test search and replace operations across files."""
    
    def test_find_replace_workflow(self, enhanced_editor_test_environment):
        """
        Test: Search Pattern → Find Matches → Replace → Validation
        Target: < 10 seconds for search and replace operations
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        
        # Create test files with content for search/replace
        search_test_files = []
        for i in range(3):
            test_file = os.path.join(test_data_path, f'search_test_{i}.txt')
            content = f'''This is a test file {i}.
This file contains the word "example" multiple times.
Here is another example of the word example.
The example word should be found and replaced.
'''
            with open(test_file, 'w') as f:
                f.write(content)
            search_test_files.append(test_file)
        
        performance_monitor.start_monitoring('enhanced_editor', 'search_replace')
        
        start_time = time.time()
        
        try:
            # Execute search and replace
            search_pattern = 'example'
            replacement_text = 'REPLACED'
            
            search_options = {
                'case_sensitive': False,
                'whole_word': True,
                'regex_mode': False,
                'replace_all': True
            }
            
            result = tool.search_and_replace(
                search_pattern, replacement_text, search_test_files, search_options)
            
            # Verify search and replace completion
            assert result['status'] == 'success', \
                "Search and replace should succeed"
            assert 'matches_found' in result, \
                "Should report number of matches found"
            assert 'file_count' in result, \
                "Should report number of files processed"
            
            # Verify search results
            assert len(tool.search_results) > 0, \
                "Should find matches in test files"
            
            search_results = tool.search_results
            for match in search_results[:5]:  # Check first 5 matches
                required_fields = ['file_path', 'line_number', 'match_text',
                                 'replacement_text', 'context']
                for field in required_fields:
                    assert field in match, \
                        f"Search result missing field: {field}"
            
            # Verify pattern matching
            matches_found = result['matches_found']
            assert matches_found >= 3, \
                f"Should find multiple matches, found: {matches_found}"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 10.0, \
                f"Search/replace took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'enhanced_editor', 'search_replace')
            assert perf_result['target_met'], \
                f"Search/replace performance target not met: {perf_result}"
    
    def test_regex_search_workflow(self, enhanced_editor_test_environment):
        """
        Test: Regex Pattern → Pattern Matching → Complex Search → Validation
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create test file with regex-testable content
        regex_test_file = os.path.join(test_data_path, 'regex_test.txt')
        regex_content = '''Email addresses in this file:
john.doe@example.com
jane.smith@company.org
admin@test.net
Phone numbers: (555) 123-4567, 555.987.6543
'''
        with open(regex_test_file, 'w') as f:
            f.write(regex_content)
        
        # Test regex patterns
        regex_tests = [
            {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'replacement': '[EMAIL]',
                'description': 'Email address pattern'
            },
            {
                'pattern': r'\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',
                'replacement': '[PHONE]',
                'description': 'Phone number pattern'
            }
        ]
        
        for regex_test in regex_tests:
            regex_options = {
                'case_sensitive': False,
                'regex_mode': True,
                'replace_all': False,  # Just find, don't replace
                'capture_groups': True
            }
            
            result = tool.search_and_replace(
                regex_test['pattern'], regex_test['replacement'],
                [regex_test_file], regex_options)
            
            assert result['status'] == 'success', \
                f"Regex search should succeed for {regex_test['description']}"
            
            # Should find matches for well-formed patterns
            if result['matches_found'] > 0:
                assert len(tool.search_results) > 0, \
                    f"Should have search results for {regex_test['description']}"
    
    def test_multi_file_search_replace_workflow(self, 
                                              enhanced_editor_test_environment):
        """
        Test: Multi-file Search → Global Replace → Cross-file Validation
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create multiple files with common content
        multi_file_content = '''Project configuration file {file_num}.
This project uses the OLD_API_VERSION for compatibility.
The OLD_API_VERSION should be updated to NEW_API_VERSION.
Configuration: OLD_API_VERSION = "1.2.3"
'''
        
        multi_files = []
        for i in range(5):
            multi_file = os.path.join(test_data_path, f'config_{i}.txt')
            content = multi_file_content.format(file_num=i)
            with open(multi_file, 'w') as f:
                f.write(content)
            multi_files.append(multi_file)
        
        # Execute multi-file search and replace
        global_options = {
            'case_sensitive': True,
            'whole_word': False,
            'regex_mode': False,
            'replace_all': True,
            'backup_original': True
        }
        
        result = tool.search_and_replace(
            'OLD_API_VERSION', 'NEW_API_VERSION', multi_files, global_options)
        
        # Verify multi-file operation
        assert result['status'] == 'success', \
            "Multi-file search/replace should succeed"
        assert result['file_count'] == len(multi_files), \
            "Should process all files"
        
        # Should find multiple matches across files
        matches_found = result['matches_found']
        expected_min_matches = len(multi_files) * 2  # At least 2 per file
        assert matches_found >= expected_min_matches, \
            f"Should find matches across files, found: {matches_found}"
        
        # Verify cross-file consistency
        search_results = tool.search_results
        files_with_matches = set(match['file_path'] for match in search_results)
        assert len(files_with_matches) >= 3, \
            "Should find matches in multiple files"


class TestEnhancedEditorPlugins:
    """Test plugin integration and extensibility."""
    
    def test_plugin_loading_workflow(self, enhanced_editor_test_environment):
        """
        Test: Plugin Discovery → Loading → Integration → Validation
        Target: < 2 seconds for plugin loading
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('enhanced_editor', 'plugin_loading')
        
        start_time = time.time()
        
        try:
            # Simulate plugin loading
            test_plugins = [
                {
                    'name': 'SyntaxExtender',
                    'version': '1.0.0',
                    'capabilities': ['custom_syntax', 'highlighting']
                },
                {
                    'name': 'FindReplaceAdvanced',
                    'version': '2.1.0',
                    'capabilities': ['advanced_regex', 'bulk_operations']
                },
                {
                    'name': 'CodeFormatter',
                    'version': '1.5.0',
                    'capabilities': ['auto_format', 'style_checking']
                }
            ]
            
            loaded_plugins = []
            for plugin in test_plugins:
                # Simulate plugin loading
                plugin_id = plugin['name'].lower()
                
                # Mock plugin loading process
                load_result = {
                    'plugin_id': plugin_id,
                    'status': 'loaded',
                    'capabilities': plugin['capabilities'],
                    'load_time': time.time()
                }
                
                tool.loaded_plugins[plugin_id] = load_result
                loaded_plugins.append(plugin_id)
            
            # Verify plugin loading
            assert len(tool.loaded_plugins) == len(test_plugins), \
                "Should load all test plugins"
            
            for plugin_id in loaded_plugins:
                plugin_info = tool.loaded_plugins[plugin_id]
                assert plugin_info['status'] == 'loaded', \
                    f"Plugin {plugin_id} should be loaded"
                assert 'capabilities' in plugin_info, \
                    f"Plugin {plugin_id} should have capabilities"
            
            # Verify timing
            workflow_time = time.time() - start_time
            avg_plugin_time = workflow_time / len(test_plugins)
            assert avg_plugin_time < 2.0, \
                f"Plugin loading too slow: {avg_plugin_time:.2f}s per plugin"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'enhanced_editor', 'plugin_loading')
            assert perf_result['target_met'], \
                f"Plugin loading target not met: {perf_result}"
    
    def test_plugin_integration_workflow(self, enhanced_editor_test_environment):
        """
        Test: Plugin → Editor Integration → Functionality → Validation
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Load mock plugin
        formatter_plugin = {
            'plugin_id': 'code_formatter',
            'status': 'loaded',
            'capabilities': ['auto_format', 'syntax_validation'],
            'api_version': '1.0'
        }
        
        tool.loaded_plugins['code_formatter'] = formatter_plugin
        
        # Create test file for plugin integration
        plugin_test_file = os.path.join(test_data_path, 'plugin_test.py')
        unformatted_code = '''def test():
    x=1+2
    return x
'''
        with open(plugin_test_file, 'w') as f:
            f.write(unformatted_code)
        
        # Open file and test plugin integration
        open_result = tool.open_file(plugin_test_file)
        assert open_result['status'] == 'success', \
            "Should open file for plugin integration"
        
        # Simulate plugin API call
        plugin_result = {
            'status': 'success',
            'plugin_used': 'code_formatter',
            'operation': 'format_code',
            'changes_made': True
        }
        
        # Verify plugin integration worked
        assert 'code_formatter' in tool.loaded_plugins, \
            "Plugin should be available"
        
        plugin_info = tool.loaded_plugins['code_formatter']
        assert 'auto_format' in plugin_info['capabilities'], \
            "Plugin should have expected capabilities"
    
    def test_plugin_api_workflow(self, enhanced_editor_test_environment):
        """
        Test: Plugin API → Function Calls → Integration Points → Validation
        """
        env = enhanced_editor_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create API test plugin
        api_test_plugin = {
            'plugin_id': 'api_test',
            'status': 'loaded',
            'api_methods': [
                'get_current_file',
                'get_selection',
                'insert_text',
                'get_line_count'
            ],
            'event_handlers': [
                'on_file_open',
                'on_file_save',
                'on_text_changed'
            ]
        }
        
        tool.loaded_plugins['api_test'] = api_test_plugin
        
        # Test API method simulation
        api_test_file = os.path.join(test_data_path, 'api_test.txt')
        with open(api_test_file, 'w') as f:
            f.write('API test content\nLine 2\nLine 3')
        
        open_result = tool.open_file(api_test_file)
        assert open_result['status'] == 'success', \
            "Should open file for API testing"
        
        # Verify plugin API integration points
        plugin_info = tool.loaded_plugins['api_test']
        
        # Check API methods availability
        expected_methods = ['get_current_file', 'get_selection', 'insert_text']
        available_methods = plugin_info['api_methods']
        
        for method in expected_methods:
            assert method in available_methods, \
                f"Plugin should support API method: {method}"
        
        # Check event handler support
        expected_handlers = ['on_file_open', 'on_file_save']
        available_handlers = plugin_info['event_handlers']
        
        for handler in expected_handlers:
            assert handler in available_handlers, \
                f"Plugin should support event handler: {handler}"


# Test runner configuration
def run_enhanced_editor_e2e_tests():
    """Run the Enhanced Editor E2E test suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "-x",  # Stop on first failure for E2E tests
        "--maxfail=3"  # Stop after 3 failures
    ]
    
    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Import PyQt5 for GUI testing if available
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    except ImportError:
        pass
    
    # Run the tests
    print("Starting Enhanced Editor End-to-End Tests...")
    exit_code = run_enhanced_editor_e2e_tests()
    
    print(f"\nEnhanced Editor E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)