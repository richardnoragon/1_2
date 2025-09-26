#!/usr/bin/env python3
"""
Simple Test Execution for miner.py Unit Tests
Created: 2025-08-28
Quick verification that the test suite works correctly
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


def simple_test_execution():
    """Execute a simplified version of the tests"""
    print("Simple Test Execution for miner.py")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Setup environment
    test_dir = Path(__file__).parent
    src_path = str(test_dir.parent.parent / "src")
    
    os.environ['PYTHONPATH'] = src_path
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    print(f"Test directory: {test_dir}")
    print(f"Source path: {src_path}")
    print(f"Python executable: {sys.executable}")
    print()
    
    # Build simple pytest command
    pytest_cmd = [
        sys.executable, '-m', 'pytest',
        'test_miner_2025-08-28.py',
        '-v',
        '--tb=short',
        '--maxfail=3',
        '--disable-warnings',
        '-x'  # Stop on first failure
    ]
    
    print("Executing command:")
    print(" ".join(pytest_cmd))
    print()
    
    try:
        # Run the tests
        result = subprocess.run(
            pytest_cmd,
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print("STDOUT:")
        print("-" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("\\nSTDERR:")
            print("-" * 30)
            print(result.stderr)
        
        print("\\n" + "=" * 50)
        if result.returncode == 0:
            print("✓ TESTS EXECUTED SUCCESSFULLY")
        else:
            print(f"✗ TESTS FAILED (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("✗ TESTS TIMED OUT")
        return False
    except Exception as e:
        print(f"✗ TEST EXECUTION FAILED: {e}")
        return False


if __name__ == "__main__":
    success = simple_test_execution()
    print(f"\\nExecution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(0 if success else 1)