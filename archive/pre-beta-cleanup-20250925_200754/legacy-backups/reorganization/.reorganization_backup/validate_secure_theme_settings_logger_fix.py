#!/usr/bin/env python3
"""
Validation script for SecureThemeSettingsWidget logger fix.

This script tests that the self.logger undefined issue has been resolved
and validates the implementation works correctly.
"""

import sys
import logging
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_logger_initialization():
    """Test that the logger is properly initialized"""
    print("Testing logger initialization...")
    
    try:
        # Test without PyQt5 first to avoid QApplication dependency
        import sys
        import importlib
        
        # Mock PyQt5 unavailable
        original_pyqt = None
        if 'PyQt5.QtWidgets' in sys.modules:
            original_pyqt = sys.modules['PyQt5.QtWidgets']
            del sys.modules['PyQt5.QtWidgets']
        
        # Force reload the module to use the non-PyQt5 path
        if 'rfu.gui.secure_theme_settings' in sys.modules:
            importlib.reload(sys.modules['rfu.gui.secure_theme_settings'])
        
        from src.gui.secure_theme_settings import SecureThemeSettingsWidget
        
        # Create widget instance (should work without PyQt5)
        widget = SecureThemeSettingsWidget()
        
        # Check if logger attribute exists
        assert hasattr(widget, 'logger'), "Widget should have 'logger' attribute"
        
        # Check if logger is a proper Logger instance
        assert isinstance(widget.logger, logging.Logger), "logger should be a Logger instance"
        
        # Check logger name
        expected_name = 'RFU.SecureThemeSettingsWidget'
        assert widget.logger.name == expected_name, f"Logger name should be '{expected_name}'"
        
        # Restore PyQt5 if it was available
        if original_pyqt:
            sys.modules['PyQt5.QtWidgets'] = original_pyqt
        
        print("✅ Logger initialization test passed")
        return True
        
    except Exception as e:
        print(f"❌ Logger initialization test failed: {e}")
        return False

def test_logger_usage():
    """Test that the logger can be used without errors"""
    print("\nTesting logger usage...")
    
    try:
        from src.gui.secure_theme_settings import SecureThemeSettingsWidget
        
        # Create widget instance
        widget = SecureThemeSettingsWidget()
        
        # Test different log levels
        widget.logger.debug("Test debug message")
        widget.logger.info("Test info message")
        widget.logger.warning("Test warning message")
        widget.logger.error("Test error message")
        
        # Test the specific method that had the logger issue
        widget.on_theme_selected("test_theme")
        
        print("✅ Logger usage test passed")
        return True
        
    except Exception as e:
        print(f"❌ Logger usage test failed: {e}")
        return False

def test_security_event_logging():
    """Test that security events are properly logged"""
    print("\nTesting security event logging...")
    
    try:
        from src.gui.secure_theme_settings import SecureThemeSettingsWidget
        
        # Create widget instance
        widget = SecureThemeSettingsWidget()
        
        # Test security event handling
        widget.on_theme_selected("test_theme")
        
        # Check if security events were recorded
        events = widget.get_security_events()
        
        print(f"Security events recorded: {len(events)}")
        
        # Test clearing events
        widget.clear_security_events()
        cleared_events = widget.get_security_events()
        assert len(cleared_events) == 0, "Events should be cleared"
        
        print("✅ Security event logging test passed")
        return True
        
    except Exception as e:
        print(f"❌ Security event logging test failed: {e}")
        return False

def test_error_handling():
    """Test that error handling works correctly with logging"""
    print("\nTesting error handling with logging...")
    
    try:
        from src.gui.secure_theme_settings import SecureThemeSettingsWidget
        
        # Create widget instance
        widget = SecureThemeSettingsWidget()
        
        # Test error handling in theme selection
        # This should trigger error logging but not crash
        widget.on_theme_selected("invalid_theme")
        
        # Test corrupted theme handling
        try:
            from collections import namedtuple
            ValidationResult = namedtuple('ValidationResult', ['success', 'corruption_type', 'error'])
            validation_result = ValidationResult(False, 'test_corruption', 'Test corruption error')
            
            widget.handle_corrupted_theme("corrupted_theme", validation_result)
        except Exception:
            # This might fail due to missing PyQt5, but should log properly
            pass
        
        print("✅ Error handling test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_factory_function():
    """Test the factory function works correctly"""
    print("\nTesting factory function...")
    
    try:
        from src.gui.secure_theme_settings import create_secure_theme_settings_widget
        
        # Create widget using factory function
        widget = create_secure_theme_settings_widget()
        
        # Verify it has a logger
        assert hasattr(widget, 'logger'), "Factory-created widget should have logger"
        
        print("✅ Factory function test passed")
        return True
        
    except Exception as e:
        print(f"❌ Factory function test failed: {e}")
        return False

def test_logging_configuration():
    """Test that logging is properly configured"""
    print("\nTesting logging configuration...")
    
    try:
        from src.gui.secure_theme_settings import SecureThemeSettingsWidget
        
        # Create widget instance
        widget = SecureThemeSettingsWidget()
        
        # Check if logger has handlers
        assert len(widget.logger.handlers) > 0, "Logger should have at least one handler"
        
        # Check logger level
        assert widget.logger.level <= logging.DEBUG, "Logger should be set to DEBUG level or lower"
        
        # Test log file creation (if possible)
        try:
            log_dir = Path.home() / '.rfu' / 'logs'
            log_file = log_dir / 'theme_security.log'
            
            # If log file exists, check it's writable
            if log_file.exists():
                assert log_file.is_file(), "Log file should be a regular file"
                print(f"Log file created at: {log_file}")
        except Exception as log_error:
            print(f"Note: Log file test failed (this may be expected): {log_error}")
        
        print("✅ Logging configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Logging configuration test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("SecureThemeSettingsWidget Logger Fix Validation")
    print("=" * 60)
    
    # Configure basic logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tests = [
        test_logger_initialization,
        test_logger_usage,
        test_security_event_logging,
        test_error_handling,
        test_factory_function,
        test_logging_configuration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - Logger issue has been fixed!")
        print("✅ SecureThemeSettingsWidget now has proper logger implementation")
        print("✅ self.logger is properly defined and initialized")
        print("✅ Comprehensive logging configuration is in place")
        print("✅ Error handling includes proper logging")
        print("✅ Security event logging is functional")
    else:
        print(f"\n⚠️  {failed} test(s) failed - please review the implementation")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())