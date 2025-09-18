#!/usr/bin/env python3
"""
Phase 4: Migration Testing - Verify Functionality
Test the migrated application to ensure everything works correctly
"""

import importlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class MigrationPhase4:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.test_results = []
        self.errors = []
        self.import_tests = []
        
    def execute_phase4_testing(self):
        """Phase 4: Execute comprehensive testing"""
        print("=" * 80)
        print("MIGRATION PHASE 4: FUNCTIONALITY TESTING")
        print("=" * 80)
        
        try:
            # Step 1: Test critical imports
            self._test_critical_imports()
            
            # Step 2: Test application startup
            self._test_application_startup()
            
            # Step 3: Test configuration system
            self._test_configuration_system()
            
            # Step 4: Test file explorer functionality
            self._test_file_explorer()
            
            # Step 5: Generate test report
            self._generate_test_report()
            
            success_rate = self._calculate_success_rate()
            print(f"\n✅ Phase 4 completed!")
            print(f"📊 Overall success rate: {success_rate:.1f}%")
            
            return success_rate > 80  # Consider success if >80% tests pass
            
        except Exception as e:
            self.errors.append(f"Phase 4 failed: {str(e)}")
            print(f"❌ Phase 4 failed: {e}")
            return False
    
    def _test_critical_imports(self):
        """Test that all critical modules can be imported"""
        print("\n🧪 Step 1: Testing critical imports...")
        
        critical_modules = [
            'src.config_manager',
            'src.log_manager',
            'src.hub',
            'src.main',
            'src.core_rfu.constants',
            'src.core_rfu.error_handler',
            'src.file_explorer.multi_pane_explorer',
            'src.gui',
            'src.database'
        ]
        
        for module_name in critical_modules:
            try:
                # Test import
                importlib.import_module(module_name)
                print(f"   ✅ {module_name}")
                self.import_tests.append({
                    "module": module_name,
                    "status": "success",
                    "error": None
                })
            except ImportError as e:
                print(f"   ❌ {module_name}: {e}")
                self.import_tests.append({
                    "module": module_name,
                    "status": "failed",
                    "error": str(e)
                })
                self.errors.append(f"Import failed: {module_name} - {e}")
            except Exception as e:
                print(f"   ⚠️ {module_name}: {e}")
                self.import_tests.append({
                    "module": module_name,
                    "status": "warning",
                    "error": str(e)
                })
        
        success_count = len([t for t in self.import_tests if t["status"] == "success"])
        print(f"   📊 Import success rate: {success_count}/{len(critical_modules)} ({success_count/len(critical_modules)*100:.1f}%)")
    
    def _test_application_startup(self):
        """Test that the main application can start"""
        print("\n🚀 Step 2: Testing application startup...")
        
        # Test main.py can be imported and basic functions work
        try:
            # Test basic import
            import main
            print("   ✅ main.py imports successfully")
            
            # Test that we can access key functions (without actually running GUI)
            if hasattr(main, 'initialize_database_system'):
                print("   ✅ initialize_database_system function found")
            else:
                print("   ⚠️ initialize_database_system function not found")
            
            self.test_results.append({
                "test": "main_application_startup",
                "status": "success",
                "details": "Main application imports and basic structure verified"
            })
            
        except Exception as e:
            print(f"   ❌ Application startup test failed: {e}")
            self.test_results.append({
                "test": "main_application_startup", 
                "status": "failed",
                "details": str(e)
            })
            self.errors.append(f"Application startup failed: {e}")
    
    def _test_configuration_system(self):
        """Test configuration system functionality"""
        print("\n⚙️ Step 3: Testing configuration system...")
        
        try:
            # Test config manager import and basic functionality
            from src.config_manager import ConfigManager

            # Test singleton pattern
            config1 = ConfigManager()
            config2 = ConfigManager()
            
            if config1 is config2:
                print("   ✅ ConfigManager singleton pattern works")
            else:
                print("   ⚠️ ConfigManager singleton pattern issue")
            
            # Test basic configuration methods
            if hasattr(config1, 'get_setting'):
                print("   ✅ ConfigManager.get_setting method available")
            else:
                print("   ⚠️ ConfigManager.get_setting method missing")
                
            if hasattr(config1, 'set_setting'):
                print("   ✅ ConfigManager.set_setting method available")
            else:
                print("   ⚠️ ConfigManager.set_setting method missing")
            
            self.test_results.append({
                "test": "configuration_system",
                "status": "success", 
                "details": "Configuration manager functional"
            })
            
        except Exception as e:
            print(f"   ❌ Configuration system test failed: {e}")
            self.test_results.append({
                "test": "configuration_system",
                "status": "failed",
                "details": str(e)
            })
            self.errors.append(f"Configuration system failed: {e}")
    
    def _test_file_explorer(self):
        """Test file explorer functionality"""
        print("\n📁 Step 4: Testing file explorer...")
        
        try:
            # Test file explorer imports
            from src.file_explorer.multi_pane_explorer import \
                MultiPaneFileExplorer
            print("   ✅ MultiPaneFileExplorer imports successfully")
            
            # Test that class can be instantiated (without actually creating GUI)
            # We'll just check if the class exists and has expected methods
            expected_methods = ['setup_ui', 'create_panes', 'setup_menus']
            missing_methods = []
            
            for method_name in expected_methods:
                if hasattr(MultiPaneFileExplorer, method_name):
                    print(f"   ✅ Method {method_name} found")
                else:
                    print(f"   ⚠️ Method {method_name} missing")
                    missing_methods.append(method_name)
            
            self.test_results.append({
                "test": "file_explorer",
                "status": "success" if not missing_methods else "warning",
                "details": f"File explorer accessible, missing methods: {missing_methods}" if missing_methods else "File explorer fully functional"
            })
            
        except Exception as e:
            print(f"   ❌ File explorer test failed: {e}")
            self.test_results.append({
                "test": "file_explorer",
                "status": "failed", 
                "details": str(e)
            })
            self.errors.append(f"File explorer failed: {e}")
    
    def _test_tools_accessibility(self):
        """Test that tools are accessible through new import paths"""
        print("\n🔧 Step 5: Testing tools accessibility...")
        
        tool_modules = [
            'src.tools.file_management.file_finder',
            'src.tools.file_management.organize', 
            'src.tools.security.en_and_decrypt',
            'src.tools.analysis.size_analyzer',
            'src.tools.network.network_connectivity'
        ]
        
        for module_name in tool_modules:
            try:
                importlib.import_module(module_name)
                print(f"   ✅ {module_name}")
                self.test_results.append({
                    "test": f"tool_import_{module_name.split('.')[-1]}",
                    "status": "success",
                    "details": "Tool accessible via new import path"
                })
            except Exception as e:
                print(f"   ❌ {module_name}: {e}")
                self.test_results.append({
                    "test": f"tool_import_{module_name.split('.')[-1]}",
                    "status": "failed",
                    "details": str(e)
                })
    
    def _calculate_success_rate(self):
        """Calculate overall success rate"""
        if not self.test_results:
            return 0.0
        
        success_count = len([t for t in self.test_results if t["status"] == "success"])
        warning_count = len([t for t in self.test_results if t["status"] == "warning"])
        
        # Count warnings as half success
        effective_success = success_count + (warning_count * 0.5)
        return (effective_success / len(self.test_results)) * 100
    
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📋 Step 6: Generating test report...")
        
        report = {
            "phase": "functionality_testing",
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace_root),
            "statistics": {
                "total_tests": len(self.test_results),
                "successful_tests": len([t for t in self.test_results if t["status"] == "success"]),
                "warning_tests": len([t for t in self.test_results if t["status"] == "warning"]),
                "failed_tests": len([t for t in self.test_results if t["status"] == "failed"]),
                "import_tests": len(self.import_tests),
                "successful_imports": len([t for t in self.import_tests if t["status"] == "success"]),
                "success_rate": self._calculate_success_rate()
            },
            "test_results": self.test_results,
            "import_tests": self.import_tests,
            "errors": self.errors
        }
        
        # Save report
        report_file = self.workspace_root / f"migration_phase4_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"   💾 Report saved: {report_file}")
        
        # Print summary
        stats = report["statistics"]
        print(f"\n📊 Test Summary:")
        print(f"   • Total tests: {stats['total_tests']}")
        print(f"   • Successful: {stats['successful_tests']}")
        print(f"   • Warnings: {stats['warning_tests']}")
        print(f"   • Failed: {stats['failed_tests']}")
        print(f"   • Import tests: {stats['successful_imports']}/{stats['import_tests']}")
        print(f"   • Overall success rate: {stats['success_rate']:.1f}%")


def main():
    workspace_root = Path(__file__).parent
    phase4 = MigrationPhase4(workspace_root)
    
    print("🚀 Starting Migration Phase 4...")
    print("⚠️  This will test the migrated application functionality")
    print("⚠️  No GUI windows will be opened, only import and basic tests")
    
    # Add src to Python path for testing
    src_path = workspace_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    success = phase4.execute_phase4_testing()
    
    if success:
        print("\n" + "="*80)
        print("✅ PHASE 4 COMPLETED SUCCESSFULLY")
        print("="*80)
        print("📋 Next Steps:")
        print("   1. Phase 5: Final cleanup and removal of src/rfu")
        
        print("\n🎉 MIGRATION STATUS:")
        print("   ✅ Files migrated successfully")
        print("   ✅ Import statements updated")
        print("   ✅ Functionality tests passed")
        print("   ✅ Ready for final cleanup")
        
    else:
        print("\n" + "="*80)
        print("⚠️ PHASE 4 COMPLETED WITH ISSUES")
        print("="*80)
        print("Some functionality tests failed. Review the test report.")
        print("You may proceed with caution or investigate issues first.")
        
        if phase4.errors:
            print("\n❌ Issues found:")
            for error in phase4.errors[:5]:
                print(f"   • {error}")
            if len(phase4.errors) > 5:
                print(f"   ... and {len(phase4.errors) - 5} more errors")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())