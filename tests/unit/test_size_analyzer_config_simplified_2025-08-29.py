"""
Simplified Test Runner for size_analyzer_config.py

This script runs basic tests without complex reporting infrastructure.
Created: 2025-08-29
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_basic_imports():
    """Test that we can import the module."""
    try:
        # Try multiple import paths
        import_paths = [
            'src.tools.analysis.config.size_analyzer_config',
            'utilities.analysis.config.size_analyzer_config'
        ]
        
        module = None
        for path in import_paths:
            try:
                module = __import__(path, fromlist=['SizeAnalyzerConfig', 'get_config_manager', 'get_log_manager'])
                break
            except ImportError:
                continue
        
        if module is None:
            # Try direct file import
            import importlib.util
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'analysis', 'config', 'size_analyzer_config.py')
            if os.path.exists(file_path):
                spec = importlib.util.spec_from_file_location("size_analyzer_config", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                print(f"✗ Module file not found at: {file_path}")
                return False
        
        # Verify required components exist
        assert hasattr(module, 'SizeAnalyzerConfig')
        assert hasattr(module, 'get_config_manager')
        assert hasattr(module, 'get_log_manager')
        
        print("✓ Successfully imported size_analyzer_config module")
        return True
    except Exception as e:
        print(f"✗ Failed to import module: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of SizeAnalyzerConfig."""
    try:
        # Import the module
        import importlib.util
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'analysis', 'config', 'size_analyzer_config.py')
        spec = importlib.util.spec_from_file_location("size_analyzer_config", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        SizeAnalyzerConfig = module.SizeAnalyzerConfig
        
        from unittest.mock import Mock

        # Create mock config manager
        mock_cm = Mock()
        mock_cm.config = {}
        mock_cm.save_config = Mock()
        
        # Test initialization
        config = SizeAnalyzerConfig(config_manager=mock_cm)
        assert config.config_manager == mock_cm
        assert config.section_name == 'size_analyzer'
        print("✓ SizeAnalyzerConfig initialization works")
        
        # Test setting/getting values
        result = config.set_setting('general', 'test_key', 'test_value')
        assert result is True
        
        value = config.get_setting('general', 'test_key')
        assert value == 'test_value'
        print("✓ Setting and getting values works")
        
        # Test defaults structure
        defaults = config.defaults
        expected_sections = ['general', 'analysis', 'export', 'ui', 'performance', 'resources', 'hub_integration', 'logging']
        for section in expected_sections:
            assert section in defaults
        print("✓ Defaults structure is correct")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_helper_functions():
    """Test helper functions."""
    try:
        # Import the module
        import importlib.util
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'utilities', 'analysis', 'config', 'size_analyzer_config.py')
        spec = importlib.util.spec_from_file_location("size_analyzer_config", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        get_config_manager = module.get_config_manager
        get_log_manager = module.get_log_manager
        
        from unittest.mock import Mock, patch

        # Test get_config_manager
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock()
            mock_module.ConfigManager = Mock()
            mock_import.return_value = mock_module
            
            result = get_config_manager()
            assert result is not None
        
        # Test get_config_manager with import error
        with patch('builtins.__import__', side_effect=ImportError()):
            result = get_config_manager()
            assert result is None
        
        print("✓ Helper functions work correctly")
        return True
    except Exception as e:
        print(f"✗ Helper functions test failed: {e}")
        return False

def create_test_report():
    """Create a simple test report."""
    timestamp = datetime.now()
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)
    
    # Run tests
    tests = [
        ('Import Test', test_basic_imports),
        ('Basic Functionality Test', test_basic_functionality),
        ('Helper Functions Test', test_helper_functions)
    ]
    
    test_results = []
    passed = 0
    total = len(tests)
    
    print("Running simplified tests for size_analyzer_config.py...")
    print("=" * 60)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            success = test_func()
            if success:
                passed += 1
                status = "PASSED"
            else:
                status = "FAILED"
        except Exception as e:
            print(f"✗ {test_name} threw exception: {e}")
            status = "ERROR"
        
        test_results.append({
            'test_name': test_name,
            'status': status,
            'timestamp': timestamp.isoformat()
        })
        print(f"Status: {status}")
    
    # Generate report
    report = {
        'execution_timestamp': timestamp.isoformat(),
        'tests_run': total,
        'tests_passed': passed,
        'tests_failed': total - passed,
        'success_rate': (passed / total * 100) if total > 0 else 0,
        'test_details': test_results,
        'summary': f"Executed {total} tests, {passed} passed, {total - passed} failed"
    }
    
    # Save report
    date_str = timestamp.strftime('%Y-%m-%d')
    report_file = results_dir / f'result_size_analyzer_config_simplified_{date_str}.json'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("TEST EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed / total * 100:.1f}%")
    print(f"Report saved to: {report_file}")
    
    return passed == total

if __name__ == '__main__':
    success = create_test_report()
    sys.exit(0 if success else 1)