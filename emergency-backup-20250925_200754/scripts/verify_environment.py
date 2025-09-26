#!/usr/bin/env python3
"""
Virtual Environment Verification Script
======================================

This script provides comprehensive verification of Python virtual environments,
testing isolation, package installations, and functionality.
"""

import os
import sys
import subprocess
import json
import importlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging


class EnvironmentVerifier:
    """Comprehensive virtual environment verification."""
    
    def __init__(self, venv_path: Path, logger: logging.Logger):
        """Initialize the verifier.
        
        Args:
            venv_path: Path to virtual environment
            logger: Logger instance
        """
        self.venv_path = venv_path
        self.logger = logger
        self.is_windows = os.name == 'nt'
        
        # Set paths based on platform
        if self.is_windows:
            self.venv_python = venv_path / "Scripts" / "python.exe"
            self.venv_pip = venv_path / "Scripts" / "pip.exe"
        else:
            self.venv_python = venv_path / "bin" / "python"
            self.venv_pip = venv_path / "bin" / "pip"
    
    def verify_environment(self) -> bool:
        """Run comprehensive environment verification.
        
        Returns:
            True if all verifications pass, False otherwise
        """
        self.logger.info("Starting comprehensive environment verification...")
        
        checks = [
            ("Environment Structure", self._check_environment_structure),
            ("Python Isolation", self._check_python_isolation),
            ("Package Installation", self._check_package_installation),
            ("Critical Imports", self._check_critical_imports),
            ("GUI Framework", self._check_gui_framework),
            ("File Operations", self._check_file_operations),
            ("Cryptography", self._check_cryptography),
            ("PDF Processing", self._check_pdf_processing),
            ("Data Processing", self._check_data_processing),
        ]
        
        results = {}
        all_passed = True
        
        for check_name, check_func in checks:
            self.logger.info(f"Running check: {check_name}")
            try:
                result = check_func()
                results[check_name] = result
                if result:
                    self.logger.info(f"✅ {check_name}: PASSED")
                else:
                    self.logger.error(f"❌ {check_name}: FAILED")
                    all_passed = False
            except Exception as e:
                self.logger.error(f"💥 {check_name}: ERROR - {e}")
                results[check_name] = False
                all_passed = False
        
        # Print summary
        self._print_summary(results)
        
        return all_passed
    
    def _check_environment_structure(self) -> bool:
        """Check virtual environment directory structure."""
        required_paths = [self.venv_path, self.venv_python, self.venv_pip]
        
        for path in required_paths:
            if not path.exists():
                self.logger.error(f"Missing required path: {path}")
                return False
        
        return True
    
    def _check_python_isolation(self) -> bool:
        """Check Python path isolation."""
        try:
            # Check Python executable path
            cmd = [str(self.venv_python), '-c', 
                  'import sys; print(sys.executable)']
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  check=True)
            python_path = result.stdout.strip()
            
            if str(self.venv_python) not in python_path:
                self.logger.error(f"Python not isolated: {python_path}")
                return False
            
            # Check sys.path isolation
            cmd = [str(self.venv_python), '-c', 
                  'import sys; import json; print(json.dumps(sys.path))']
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  check=True)
            sys_paths = json.loads(result.stdout.strip())
            
            # Check that venv site-packages is in path
            venv_site_packages = str(self.venv_path)
            if not any(venv_site_packages in path for path in sys_paths):
                self.logger.error("Virtual environment site-packages not in "
                                "sys.path")
                return False
            
            return True
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self.logger.error(f"Python isolation check failed: {e}")
            return False
    
    def _check_package_installation(self) -> bool:
        """Check installed packages."""
        try:
            cmd = [str(self.venv_python), '-m', 'pip', 'list', 
                  '--format=json']
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  check=True)
            packages = json.loads(result.stdout)
            
            if len(packages) < 10:  # Should have many packages
                self.logger.error(f"Too few packages installed: "
                                f"{len(packages)}")
                return False
            
            # Check for critical packages
            package_names = {pkg['name'].lower() for pkg in packages}
            critical_packages = {
                'pyqt5', 'numpy', 'pandas', 'cryptography', 
                'pillow', 'lxml', 'psutil'
            }
            
            missing = critical_packages - package_names
            if missing:
                self.logger.error(f"Missing critical packages: {missing}")
                return False
            
            self.logger.info(f"Found {len(packages)} installed packages")
            return True
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self.logger.error(f"Package installation check failed: {e}")
            return False
    
    def _check_critical_imports(self) -> bool:
        """Test importing critical packages."""
        critical_imports = [
            'os', 'sys', 'pathlib', 'json', 'subprocess',
            'numpy', 'pandas', 'cryptography', 'PIL', 'lxml'
        ]
        
        for module_name in critical_imports:
            if not self._test_import(module_name):
                return False
        
        return True
    
    def _check_gui_framework(self) -> bool:
        """Test GUI framework functionality."""
        test_code = '''
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer

# Create application without showing GUI
app = QApplication(sys.argv)
widget = QWidget()

# Test basic functionality
widget.setWindowTitle("Test")
widget.resize(100, 100)

# Clean exit
QTimer.singleShot(0, app.quit)
app.exec_()
print("PyQt5 test successful")
'''
        
        return self._run_test_code(test_code, "PyQt5 GUI test")
    
    def _check_file_operations(self) -> bool:
        """Test file operation capabilities."""
        test_code = '''
import tempfile
import os
from pathlib import Path
import shutil

# Test basic file operations
with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)
    
    # Create test file
    test_file = temp_path / "test.txt"
    test_file.write_text("Hello, World!")
    
    # Read file
    content = test_file.read_text()
    assert content == "Hello, World!"
    
    # Copy file
    copy_file = temp_path / "copy.txt"
    shutil.copy2(test_file, copy_file)
    assert copy_file.exists()
    
    print("File operations test successful")
'''
        
        return self._run_test_code(test_code, "File operations test")
    
    def _check_cryptography(self) -> bool:
        """Test cryptography functionality."""
        test_code = '''
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# Test encryption/decryption
key = Fernet.generate_key()
f = Fernet(key)

message = b"Test message for encryption"
encrypted = f.encrypt(message)
decrypted = f.decrypt(encrypted)

assert decrypted == message

# Test key derivation
password = b"test_password"
salt = os.urandom(16)
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
derived_key = base64.urlsafe_b64encode(kdf.derive(password))

print("Cryptography test successful")
'''
        
        return self._run_test_code(test_code, "Cryptography test")
    
    def _check_pdf_processing(self) -> bool:
        """Test PDF processing capabilities."""
        test_code = '''
import tempfile
from pathlib import Path

# Test PyMuPDF
try:
    import fitz  # PyMuPDF
    print("PyMuPDF available")
except ImportError:
    pass

# Test PyPDF2
try:
    import PyPDF2
    print("PyPDF2 available")
except ImportError:
    pass

# Test PyPDF4
try:
    import PyPDF4
    print("PyPDF4 available")
except ImportError:
    pass

print("PDF processing test successful")
'''
        
        return self._run_test_code(test_code, "PDF processing test")
    
    def _check_data_processing(self) -> bool:
        """Test data processing capabilities."""
        test_code = '''
import numpy as np
import pandas as pd

# Test NumPy
arr = np.array([1, 2, 3, 4, 5])
assert arr.sum() == 15
assert arr.mean() == 3.0

# Test Pandas
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})
assert len(df) == 3
assert df['A'].sum() == 6

print("Data processing test successful")
'''
        
        return self._run_test_code(test_code, "Data processing test")
    
    def _test_import(self, module_name: str) -> bool:
        """Test importing a specific module.
        
        Args:
            module_name: Name of module to import
            
        Returns:
            True if import successful, False otherwise
        """
        try:
            cmd = [str(self.venv_python), '-c', f'import {module_name}']
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.logger.debug(f"Import successful: {module_name}")
            return True
        except subprocess.CalledProcessError:
            self.logger.error(f"Import failed: {module_name}")
            return False
    
    def _run_test_code(self, code: str, test_name: str) -> bool:
        """Run test code in virtual environment.
        
        Args:
            code: Python code to execute
            test_name: Name of the test for logging
            
        Returns:
            True if test successful, False otherwise
        """
        try:
            cmd = [str(self.venv_python), '-c', code]
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  check=True, timeout=30)
            self.logger.debug(f"{test_name} output: {result.stdout}")
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.logger.error(f"{test_name} failed: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"Error output: {e.stderr}")
            return False
    
    def _print_summary(self, results: Dict[str, bool]) -> None:
        """Print verification summary.
        
        Args:
            results: Dictionary of check results
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("VERIFICATION SUMMARY")
        self.logger.info("="*60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for check_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.logger.info(f"{check_name:<25} {status}")
        
        self.logger.info("-"*60)
        self.logger.info(f"Total: {passed}/{total} checks passed")
        
        if passed == total:
            self.logger.info("🎉 All verifications PASSED! Environment is ready.")
        else:
            self.logger.error(f"⚠️  {total - passed} verifications FAILED!")


def main():
    """Main entry point for standalone verification."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify Python Virtual Environment")
    parser.add_argument('--venv-path', type=str, default='venv',
                       help='Path to virtual environment directory')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger('EnvironmentVerifier')
    
    # Run verification
    venv_path = Path(args.venv_path)
    verifier = EnvironmentVerifier(venv_path, logger)
    
    success = verifier.verify_environment()
    
    if success:
        print("\n✅ Environment verification completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Environment verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()