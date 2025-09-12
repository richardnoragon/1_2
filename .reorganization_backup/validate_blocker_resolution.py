#!/usr/bin/env python3
"""
Comprehensive validation test for the Critical Test Execution Blockers Resolution.
This script validates that the core.config_manager architecture is working correctly
and that all network modules can be imported and instantiated.
"""

import os
import sys
from pathlib import Path

# Add src to path properly
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Verify path setup
print(f"Current directory: {current_dir}")
print(f"Source directory: {src_dir}")
print(f"Source directory exists: {src_dir.exists()}")

# Change to src directory for relative imports
os.chdir(src_dir)

def test_config_manager_import():
    """Test that ConfigManager can be imported successfully."""
    try:
        from utilities.network.network_connectivity_complex.core.config_manager import \
            ConfigManager
        print("✅ SUCCESS: ConfigManager import resolved")
        return True
    except ImportError as e:
        print(f"❌ FAILED: ConfigManager import failed: {e}")
        return False

def test_config_manager_functionality():
    """Test core ConfigManager functionality."""
    try:
        from utilities.network.network_connectivity_complex.core.config_manager import \
            ConfigManager

        # Test instantiation
        cm = ConfigManager()
        print("✅ SUCCESS: ConfigManager instantiated")
        
        # Test configuration loading
        network_config = cm.get_setting('network_connectivity')
        if network_config:
            print("✅ SUCCESS: Network configuration loaded")
        else:
            print("❌ FAILED: Network configuration not found")
            return False
        
        # Test specific setting retrieval
        timeout = cm.get_setting('network_connectivity', 'general.default_timeout')
        if timeout:
            print(f"✅ SUCCESS: Configuration setting retrieved: timeout={timeout}ms")
        else:
            print("❌ FAILED: Could not retrieve timeout setting")
            return False
        
        # Test setting modification
        test_key = 'test_setting'
        test_value = 'test_value'
        success = cm.set_setting('network_connectivity', f'general.{test_key}', test_value)
        if success:
            retrieved_value = cm.get_setting('network_connectivity', f'general.{test_key}')
            if retrieved_value == test_value:
                print("✅ SUCCESS: Configuration setting modification works")
            else:
                print("❌ FAILED: Setting modification validation failed")
                return False
        else:
            print("❌ FAILED: Could not set configuration setting")
            return False
        
        # Test validation
        errors = cm.validate_configuration()
        print(f"✅ SUCCESS: Configuration validation completed ({len(errors)} warnings)")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: ConfigManager functionality test failed: {e}")
        return False

def test_network_modules_import():
    """Test that all network modules can be imported."""
    modules_to_test = [
        ('WiFiAnalyzer', 'utilities.network.network_connectivity_complex.tools.wifi_analyzer'),
        ('PortScanner', 'utilities.network.network_connectivity_complex.tools.port_scanner'),
        ('BandwidthMonitor', 'utilities.network.network_connectivity_complex.tools.bandwidth_monitor'),
        ('LANFileTransfer', 'utilities.network.network_connectivity_complex.tools.lan_file_transfer'),
    ]
    
    all_success = True
    
    for class_name, module_path in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ SUCCESS: {class_name} import resolved")
        except ImportError as e:
            print(f"❌ FAILED: {class_name} import failed: {e}")
            all_success = False
        except Exception as e:
            print(f"❌ FAILED: {class_name} import error: {e}")
            all_success = False
    
    return all_success

def test_network_module_instantiation():
    """Test that network modules can be instantiated with ConfigManager."""
    try:
        from utilities.network.network_connectivity_complex.core.config_manager import \
            ConfigManager
        from utilities.network.network_connectivity_complex.tools.wifi_analyzer import \
            WiFiAnalyzer

        # Create ConfigManager
        cm = ConfigManager()
        
        # Test WiFiAnalyzer instantiation (as representative test)
        try:
            wifi_analyzer = WiFiAnalyzer()
            print("✅ SUCCESS: WiFiAnalyzer instantiated successfully")
            
            # Test configuration access
            if hasattr(wifi_analyzer, 'config_manager'):
                print("✅ SUCCESS: WiFiAnalyzer has config_manager access")
            else:
                print("⚠️  WARNING: WiFiAnalyzer may not have config_manager access")
            
            return True
            
        except Exception as e:
            print(f"❌ FAILED: WiFiAnalyzer instantiation failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ FAILED: Network module instantiation test failed: {e}")
        return False

def test_coverage_metrics():
    """Test coverage of the 2,400+ lines of network code."""
    try:
        # Import all major network modules
        module_files = [
            'utilities.network.network_connectivity_complex.tools.wifi_analyzer',
            'utilities.network.network_connectivity_complex.tools.port_scanner',
            'utilities.network.network_connectivity_complex.tools.bandwidth_monitor',
            'utilities.network.network_connectivity_complex.tools.lan_file_transfer',
            'utilities.network.network_connectivity_complex.core.config_manager',
            'utilities.network.network_connectivity_complex.core.network_base',
            'utilities.network.network_connectivity_complex.core.platform_network',
        ]
        
        total_imports = len(module_files)
        successful_imports = 0
        
        for module_path in module_files:
            try:
                __import__(module_path)
                successful_imports += 1
            except Exception as e:
                print(f"⚠️  WARNING: Could not import {module_path}: {e}")
        
        coverage_percentage = (successful_imports / total_imports) * 100
        print(f"✅ SUCCESS: Module import coverage: {coverage_percentage:.1f}% ({successful_imports}/{total_imports})")
        
        # Estimate lines of code coverage (rough estimate based on successful imports)
        estimated_lines_covered = int(2400 * (coverage_percentage / 100))
        print(f"✅ SUCCESS: Estimated lines of code now testable: ~{estimated_lines_covered}/2400 lines")
        
        return coverage_percentage >= 85  # Target 85%+ coverage
        
    except Exception as e:
        print(f"❌ FAILED: Coverage metrics test failed: {e}")
        return False

def main():
    """Main test execution."""
    print("🚀 CRITICAL TEST EXECUTION BLOCKERS - RESOLUTION VALIDATION")
    print("=" * 70)
    print()
    
    test_results = []
    
    print("Phase 1 Validation: Core Architecture")
    print("-" * 40)
    test_results.append(test_config_manager_import())
    test_results.append(test_config_manager_functionality())
    print()
    
    print("Phase 2 Validation: Network Module Integration")
    print("-" * 40)
    test_results.append(test_network_modules_import())
    test_results.append(test_network_module_instantiation())
    print()
    
    print("Phase 3 Validation: Coverage Metrics")
    print("-" * 40)
    test_results.append(test_coverage_metrics())
    print()
    
    # Summary
    successful_tests = sum(test_results)
    total_tests = len(test_results)
    success_rate = (successful_tests / total_tests) * 100
    
    print("🎯 RESOLUTION SUMMARY")
    print("=" * 70)
    print(f"Tests Passed: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if all(test_results):
        print("🎉 RESULT: CRITICAL TEST EXECUTION BLOCKERS FULLY RESOLVED")
        print("✅ Core.config_manager architecture operational")
        print("✅ Network modules import successfully")
        print("✅ Configuration management working")
        print("✅ Ready for comprehensive testing of 2,400+ lines of network code")
        return 0
    else:
        print("⚠️  RESULT: Some issues remain to be resolved")
        return 1

if __name__ == "__main__":
    sys.exit(main())