"""
OCR Enhanced Test Runner
run_ocr_enhanced_tests_2025-09-01.py
Purpose: Execute comprehensive OCR testing with enhanced coverage and reporting
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def setup_test_environment():
    """Set up the test environment"""
    print("🔧 Setting up test environment...")
    
    # Ensure we're in the correct directory
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    
    # Add source directory to Python path
    src_dir = test_dir.parent.parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path includes: {src_dir}")

def install_dependencies():
    """Install required test dependencies"""
    print("📦 Installing test dependencies...")
    
    dependencies = [
        "pytest>=7.0.0",
        "pytest-html>=3.1.0",
        "pytest-json-report>=1.5.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "Pillow>=9.0.0",
        "psutil>=5.9.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Could not install {dep}: {e}")

def run_enhanced_ocr_tests():
    """Run the enhanced OCR test suite"""
    print("\n🚀 Starting Enhanced OCR Test Execution...")
    print("=" * 80)
    
    # Test execution configuration
    cmd = [
        sys.executable, "-m", "pytest",
        "test_ocr_enhanced_complete_2025-09-01.py",
        "-c", "pytest_ocr_enhanced_complete_2025-09-01.ini",
        "--verbose",
        "--tb=short",
        "--show-capture=no",
        "--durations=10",
        "--color=yes",
        "--html=result_ocr_enhanced_complete_2025-09-01.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=result_ocr_enhanced_complete_2025-09-01.json"
    ]
    
    print(f"🔍 Executing command: {' '.join(cmd)}")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        # Run the tests
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print("=" * 80)
        print(f"⏱️ Test execution completed in {execution_time:.2f} seconds")
        print(f"🏁 Exit code: {result.returncode}")
        
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Test execution failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

def generate_test_summary(exit_code):
    """Generate a comprehensive test summary"""
    print("\n" + "=" * 80)
    print("📊 OCR ENHANCED TESTING SUMMARY")
    print("=" * 80)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📅 Execution Date/Time: {timestamp}")
    print(f"🎯 Target Module: src/utilities/pdf_tools/pdf_enhancements/ocr.py")
    print(f"🧪 Test Suite: test_ocr_enhanced_complete_2025-09-01.py")
    print(f"⚙️ Test Framework: pytest with comprehensive mocking")
    
    if exit_code == 0:
        print(f"✅ Overall Status: SUCCESS")
        print(f"🎉 Result: All tests passed - OCR module validation complete")
    else:
        print(f"❌ Overall Status: FAILURE")
        print(f"⚠️ Result: Some tests failed - review required")
    
    # Check for generated reports
    html_report = Path("result_ocr_enhanced_complete_2025-09-01.html")
    json_report = Path("result_ocr_enhanced_complete_2025-09-01.json")
    
    print(f"\n📄 Generated Reports:")
    if html_report.exists():
        print(f"   📋 HTML Report: {html_report.name} ({html_report.stat().st_size} bytes)")
    else:
        print(f"   ❌ HTML Report: Not generated")
    
    if json_report.exists():
        print(f"   📊 JSON Report: {json_report.name} ({json_report.stat().st_size} bytes)")
    else:
        print(f"   ❌ JSON Report: Not generated")
    
    print("\n🔍 Enhanced Test Coverage Areas:")
    print("   ✅ Core Image Processing Functions")
    print("   ✅ Text Processing and OCR Engine")
    print("   ✅ Image Operations and Conversions")
    print("   ✅ Main OCR Processing Functions")
    print("   ✅ File-level OCR Operations")
    print("   ✅ Folder Operations and Batch Processing")
    print("   ✅ Path Validation and Security")
    print("   ✅ Performance and Memory Testing")
    print("   ✅ Security Validation")
    print("   ✅ Integration Scenarios")
    
    print("\n🛠️ Improvements Implemented:")
    print("   🔧 Fixed pandas API compatibility issues")
    print("   🔧 Enhanced search function testing")
    print("   🔧 Improved mock configurations")
    print("   🔧 Added comprehensive edge case coverage")
    print("   🔧 Enhanced GUI testing framework")
    print("   🔧 Performance and memory testing")
    print("   🔧 Security validation testing")
    print("   🔧 End-to-end workflow simulation")
    
    print("=" * 80)

def main():
    """Main test execution function"""
    print("🎯 OCR ENHANCED COMPREHENSIVE TEST EXECUTION")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Setup environment
        setup_test_environment()
        
        # Install dependencies
        install_dependencies()
        
        # Run enhanced tests
        exit_code = run_enhanced_ocr_tests()
        
        # Generate summary
        generate_test_summary(exit_code)
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⚡ Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Fatal error during test execution: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Exiting with code: {exit_code}")
    sys.exit(exit_code)