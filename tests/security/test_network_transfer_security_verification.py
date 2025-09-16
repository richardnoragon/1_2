#!/usr/bin/env python3
"""
Network Transfer Security Verification Script

This script verifies that the security enhancements in the Network Transfer Tool
are working correctly and that the proper encryption method is being selected.

Date: August 20, 2025
Author: AI Assistant (Security Implementation)
"""

import sys
import os
import importlib.util
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_cryptography_library():
    """Test if cryptography library is available and functioning."""
    print("🔍 Testing cryptography library availability...")
    
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        print("✅ cryptography library is available")
        
        # Test basic AES-GCM functionality
        key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key)
        
        message = b"Test message for AES-GCM verification"
        nonce = os.urandom(12)
        
        encrypted = aesgcm.encrypt(nonce, message, None)
        decrypted = aesgcm.decrypt(nonce, encrypted, None)
        
        if decrypted == message:
            print("✅ AES-GCM encryption/decryption working correctly")
            return True
        else:
            print("❌ AES-GCM test failed - decryption mismatch")
            return False
            
    except ImportError:
        print("❌ cryptography library not available")
        return False
    except Exception as e:
        print(f"❌ cryptography library test failed: {e}")
        return False

def test_network_transfer_security():
    """Test the Network Transfer security implementation."""
    print("\n🔍 Testing Network Transfer security implementation...")
    
    try:
        # Import the SecurityManager class
        from src.tools.network.network_transfer import SecurityManager
        print("✅ SecurityManager imported successfully")
        
        # Create SecurityManager instance
        security_manager = SecurityManager()
        print("✅ SecurityManager instance created")
        
        # Generate session key
        session_key = security_manager.generate_session_key()
        if len(session_key) == 32:  # 256-bit key
            print("✅ Session key generated (256-bit)")
        else:
            print(f"❌ Session key length incorrect: {len(session_key)} bytes")
            return False
        
        # Test encryption method detection
        if hasattr(security_manager, 'aes_gcm') and security_manager.aes_gcm:
            print("✅ AES-GCM encryption method activated")
            encryption_method = "AES-GCM"
        else:
            print("⚠️  Fallback encryption method activated")
            encryption_method = "Enhanced Fallback"
        
        # Test encryption/decryption
        test_message = b"Network Transfer Security Verification Test Message"
        
        encrypted = security_manager.encrypt_message(test_message)
        print(f"✅ Message encrypted using {encryption_method}")
        
        decrypted = security_manager.decrypt_message(encrypted)
        
        if decrypted == test_message:
            print("✅ Message decrypted successfully")
            print(f"✅ End-to-end encryption test passed ({encryption_method})")
        else:
            print("❌ Decryption failed - message mismatch")
            return False
        
        # Test integrity protection
        print("\n🔍 Testing integrity protection...")
        tampered_data = bytearray(encrypted)
        tampered_data[-1] ^= 1  # Flip one bit
        
        try:
            security_manager.decrypt_message(bytes(tampered_data))
            print("❌ Integrity protection failed - tampered data accepted")
            return False
        except ValueError as e:
            if "integrity check failed" in str(e).lower():
                print("✅ Integrity protection working - tampered data rejected")
            else:
                print(f"⚠️  Unexpected error during integrity test: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Network Transfer modules: {e}")
        return False
    except Exception as e:
        print(f"❌ Network Transfer security test failed: {e}")
        return False

def test_path_security():
    """Test the path security implementation."""
    print("\n🔍 Testing path security implementation...")
    
    try:
        from src.tools.network.network_transfer import PathSecurity
        print("✅ PathSecurity class imported successfully")
        
        # Test safe path validation
        test_cases = [
            # Safe paths
            (str(Path.home() / "Documents" / "test.txt"), True, "User Documents"),
            (str(Path.home() / "Downloads" / "file.pdf"), True, "User Downloads"),
            
            # Dangerous paths
            ("../../../etc/passwd", False, "Path traversal attempt"),
            ("C:\\Windows\\System32\\config", False, "System directory"),
            ("/etc/shadow", False, "System file"),
            ("~/.ssh/id_rsa", False, "SSH private key"),
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for test_path, expected_safe, description in test_cases:
            try:
                # Create a temporary instance to test
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Test the path validation
                    is_safe = PathSecurity.is_safe_path(temp_dir, test_path)
                    
                    if is_safe == expected_safe:
                        status = "✅" if expected_safe else "✅"
                        print(f"{status} {description}: {'Safe' if is_safe else 'Blocked'}")
                        passed_tests += 1
                    else:
                        expected_str = "Safe" if expected_safe else "Blocked"
                        actual_str = "Safe" if is_safe else "Blocked"
                        print(f"❌ {description}: Expected {expected_str}, got {actual_str}")
            except Exception as e:
                print(f"❌ {description}: Test error - {e}")
        
        if passed_tests == total_tests:
            print(f"✅ Path security tests passed ({passed_tests}/{total_tests})")
            return True
        else:
            print(f"❌ Path security tests failed ({passed_tests}/{total_tests})")
            return False
        
    except ImportError as e:
        print(f"❌ Failed to import PathSecurity: {e}")
        return False
    except Exception as e:
        print(f"❌ Path security test failed: {e}")
        return False

def test_requirements_compliance():
    """Test that security requirements are properly installed."""
    print("\n🔍 Testing requirements compliance...")
    
    # Check requirements.txt
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        print("✅ requirements.txt found")
        
        with open(requirements_file, 'r') as f:
            requirements_content = f.read()
        
        if "cryptography" in requirements_content:
            print("✅ cryptography library listed in requirements.txt")
            
            # Extract version
            for line in requirements_content.split('\n'):
                if line.strip().startswith('cryptography'):
                    print(f"✅ Requirement: {line.strip()}")
                    break
        else:
            print("❌ cryptography library not found in requirements.txt")
            return False
    else:
        print("❌ requirements.txt not found")
        return False
    
    return True

def generate_security_report():
    """Generate a comprehensive security verification report."""
    print("\n" + "="*60)
    print("📊 NETWORK TRANSFER SECURITY VERIFICATION REPORT")
    print("="*60)
    
    results = {}
    
    # Run all tests
    results['cryptography_library'] = test_cryptography_library()
    results['network_transfer_security'] = test_network_transfer_security()
    results['path_security'] = test_path_security()
    results['requirements_compliance'] = test_requirements_compliance()
    
    # Generate summary
    print("\n📋 VERIFICATION SUMMARY")
    print("-" * 30)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        test_display = test_name.replace('_', ' ').title()
        print(f"{status} {test_display}")
    
    print(f"\nOverall Status: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SECURITY FEATURES VERIFIED SUCCESSFULLY!")
        print("✅ Network Transfer Tool is ready for secure operations")
        return True
    else:
        print("\n⚠️  SOME SECURITY TESTS FAILED")
        print("❌ Please review and address the failed tests")
        return False

def main():
    """Main verification function."""
    print("🛡️  Network Transfer Security Verification")
    print("Date:", "August 20, 2025")
    print("Purpose: Verify security enhancements are working correctly\n")
    
    success = generate_security_report()
    
    print("\n" + "="*60)
    if success:
        print("🔒 SECURITY VERIFICATION COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("🚨 SECURITY VERIFICATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()