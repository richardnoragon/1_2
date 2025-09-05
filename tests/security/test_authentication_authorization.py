#!/usr/bin/env python3
"""
Authentication and Authorization Security Testing Suite

This module provides comprehensive testing for authentication and authorization
security including:
- User Authentication Testing
- Session Management Security
- Role-Based Access Control (RBAC) Testing
- Permission and Privilege Escalation Testing
- Multi-Factor Authentication Testing
- Password Security and Policy Testing

Author: Security Testing Framework
Date: 2025-09-04
Version: 1.0.0
"""

import base64
import hashlib
import os
import secrets
import shutil
import sqlite3
import string
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class MockAuthenticationManager:
    """Mock authentication manager for testing"""
    
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.failed_attempts = {}
        self.lockout_threshold = 5
        self.lockout_duration = 300  # 5 minutes
        self.session_timeout = 3600  # 1 hour
        self.password_policies = {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special_chars': True,
            'max_age_days': 90,
            'prevent_reuse_count': 5
        }
    
    def create_user(self, username, password, role='user', email=None):
        """Create a new user with authentication data"""
        if username in self.users:
            return False, "User already exists"
        
        # Validate password policy
        is_valid, policy_message = self._validate_password_policy(password)
        if not is_valid:
            return False, f"Password policy violation: {policy_message}"
        
        password_hash = self._hash_password(password)
        
        self.users[username] = {
            'username': username,
            'password_hash': password_hash,
            'role': role,
            'email': email,
            'created_at': datetime.now(),
            'last_login': None,
            'password_changed_at': datetime.now(),
            'is_locked': False,
            'lockout_until': None,
            'password_history': [password_hash],
            'mfa_enabled': False,
            'mfa_secret': None
        }
        
        return True, "User created successfully"
    
    def authenticate_user(self, username, password, mfa_token=None):
        """Authenticate user with username and password"""
        if username not in self.users:
            return False, "Invalid credentials", None
        
        user = self.users[username]
        
        # Check if account is locked
        if self._is_account_locked(username):
            return False, "Account is locked", None
        
        # Verify password
        if not self._verify_password(password, user['password_hash']):
            self._record_failed_attempt(username)
            return False, "Invalid credentials", None
        
        # Check MFA if enabled
        if user['mfa_enabled']:
            if not mfa_token or not self._verify_mfa_token(username, mfa_token):
                return False, "Invalid MFA token", None
        
        # Create session
        session_id = self._create_session(username)
        user['last_login'] = datetime.now()
        self._clear_failed_attempts(username)
        
        return True, "Authentication successful", session_id
    
    def validate_session(self, session_id):
        """Validate user session"""
        if session_id not in self.sessions:
            return False, "Invalid session", None
        
        session = self.sessions[session_id]
        
        # Check session timeout
        if datetime.now() > session['expires_at']:
            self._invalidate_session(session_id)
            return False, "Session expired", None
        
        # Update session activity
        session['last_activity'] = datetime.now()
        
        return True, "Session valid", session['username']
    
    def check_permission(self, username, resource, action):
        """Check if user has permission for resource/action"""
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        role = user['role']
        
        # Define role-based permissions
        permissions = {
            'admin': {
                'users': ['create', 'read', 'update', 'delete'],
                'system': ['read', 'write', 'admin'],
                'files': ['read', 'write', 'delete'],
                'security': ['read', 'write', 'admin']
            },
            'power_user': {
                'users': ['read'],
                'system': ['read'],
                'files': ['read', 'write'],
                'security': ['read']
            },
            'user': {
                'files': ['read'],
                'security': []
            },
            'guest': {
                'files': [],
                'security': []
            }
        }
        
        role_permissions = permissions.get(role, {})
        resource_permissions = role_permissions.get(resource, [])
        
        has_permission = action in resource_permissions
        return has_permission, f"Permission {'granted' if has_permission else 'denied'}"
    
    def _hash_password(self, password):
        """Hash password using secure method"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                           password.encode('utf-8'), 
                                           salt.encode('utf-8'), 
                                           100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            salt, hash_hex = stored_hash.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256',
                                               password.encode('utf-8'),
                                               salt.encode('utf-8'),
                                               100000)
            return password_hash.hex() == hash_hex
        except:
            return False
    
    def _validate_password_policy(self, password):
        """Validate password against security policy"""
        policy = self.password_policies
        
        if len(password) < policy['min_length']:
            return False, f"Password must be at least {policy['min_length']} characters"
        
        if policy['require_uppercase'] and not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letters"
        
        if policy['require_lowercase'] and not any(c.islower() for c in password):
            return False, "Password must contain lowercase letters"
        
        if policy['require_numbers'] and not any(c.isdigit() for c in password):
            return False, "Password must contain numbers"
        
        if policy['require_special_chars'] and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            return False, "Password must contain special characters"
        
        return True, "Password meets policy requirements"
    
    def _create_session(self, username):
        """Create new user session"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=self.session_timeout)
        
        self.sessions[session_id] = {
            'username': username,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'expires_at': expires_at
        }
        
        return session_id
    
    def _invalidate_session(self, session_id):
        """Invalidate user session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def _is_account_locked(self, username):
        """Check if account is locked due to failed attempts"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        if user['is_locked'] and user['lockout_until']:
            if datetime.now() < user['lockout_until']:
                return True
            else:
                # Unlock account after lockout period
                user['is_locked'] = False
                user['lockout_until'] = None
        
        return False
    
    def _record_failed_attempt(self, username):
        """Record failed authentication attempt"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(datetime.now())
        
        # Check if lockout threshold exceeded
        recent_attempts = [
            attempt for attempt in self.failed_attempts[username]
            if datetime.now() - attempt < timedelta(minutes=15)
        ]
        
        if len(recent_attempts) >= self.lockout_threshold:
            if username in self.users:
                self.users[username]['is_locked'] = True
                self.users[username]['lockout_until'] = datetime.now() + timedelta(seconds=self.lockout_duration)
    
    def _clear_failed_attempts(self, username):
        """Clear failed attempts after successful login"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
    
    def _verify_mfa_token(self, username, token):
        """Verify MFA token (mock implementation)"""
        # In real implementation, this would verify TOTP/HOTP tokens
        return token == "123456"  # Mock token for testing


class TestUserAuthentication(unittest.TestCase):
    """Test user authentication mechanisms"""
    
    def setUp(self):
        """Setup authentication test environment"""
        self.auth_manager = MockAuthenticationManager()
        
        # Create test users
        self.auth_manager.create_user("admin", "AdminPass123!", "admin", "admin@test.com")
        self.auth_manager.create_user("user1", "UserPass123!", "user", "user1@test.com")
        self.auth_manager.create_user("guest", "GuestPass123!", "guest", "guest@test.com")
    
    def test_valid_user_authentication(self):
        """Test valid user authentication"""
        success, message, session_id = self.auth_manager.authenticate_user("admin", "AdminPass123!")
        
        self.assertTrue(success, "Valid credentials should authenticate successfully")
        self.assertEqual(message, "Authentication successful")
        self.assertIsNotNone(session_id, "Session ID should be provided")
    
    def test_invalid_username_authentication(self):
        """Test authentication with invalid username"""
        success, message, session_id = self.auth_manager.authenticate_user("nonexistent", "password")
        
        self.assertFalse(success, "Invalid username should fail authentication")
        self.assertEqual(message, "Invalid credentials")
        self.assertIsNone(session_id, "No session should be created")
    
    def test_invalid_password_authentication(self):
        """Test authentication with invalid password"""
        success, message, session_id = self.auth_manager.authenticate_user("admin", "wrongpassword")
        
        self.assertFalse(success, "Invalid password should fail authentication")
        self.assertEqual(message, "Invalid credentials")
        self.assertIsNone(session_id, "No session should be created")
    
    def test_account_lockout_after_failed_attempts(self):
        """Test account lockout after multiple failed attempts"""
        username = "user1"
        
        # Make multiple failed attempts
        for i in range(5):
            success, message, session_id = self.auth_manager.authenticate_user(username, "wrongpassword")
            self.assertFalse(success, f"Failed attempt {i+1} should fail")
        
        # Next attempt should show account locked
        success, message, session_id = self.auth_manager.authenticate_user(username, "wrongpassword")
        self.assertFalse(success, "Account should be locked")
        self.assertEqual(message, "Account is locked")
        
        # Even correct password should fail when locked
        success, message, session_id = self.auth_manager.authenticate_user(username, "UserPass123!")
        self.assertFalse(success, "Correct password should still fail when locked")
    
    def test_password_policy_enforcement(self):
        """Test password policy enforcement"""
        weak_passwords = [
            ("short", "Password must be at least 8 characters"),
            ("lowercase", "Password must contain uppercase letters"),
            ("UPPERCASE", "Password must contain lowercase letters"),
            ("NoNumbers!", "Password must contain numbers"),
            ("NoSpecial123", "Password must contain special characters"),
        ]
        
        for password, expected_error in weak_passwords:
            with self.subTest(password=password):
                success, message = self.auth_manager.create_user(f"test_{password}", password)
                self.assertFalse(success, f"Weak password should be rejected: {password}")
                self.assertIn(expected_error, message)


class TestSessionManagement(unittest.TestCase):
    """Test session management security"""
    
    def setUp(self):
        """Setup session management test environment"""
        self.auth_manager = MockAuthenticationManager()
        self.auth_manager.create_user("testuser", "TestPass123!", "user")
    
    def test_valid_session_validation(self):
        """Test valid session validation"""
        # Authenticate and get session
        success, message, session_id = self.auth_manager.authenticate_user("testuser", "TestPass123!")
        self.assertTrue(success)
        
        # Validate session
        valid, message, username = self.auth_manager.validate_session(session_id)
        self.assertTrue(valid, "Valid session should be accepted")
        self.assertEqual(username, "testuser")
    
    def test_invalid_session_validation(self):
        """Test invalid session validation"""
        fake_session_id = "invalid_session_id"
        
        valid, message, username = self.auth_manager.validate_session(fake_session_id)
        self.assertFalse(valid, "Invalid session should be rejected")
        self.assertEqual(message, "Invalid session")
        self.assertIsNone(username)
    
    def test_session_timeout(self):
        """Test session timeout functionality"""
        # Set short timeout for testing
        self.auth_manager.session_timeout = 1  # 1 second
        
        # Authenticate and get session
        success, message, session_id = self.auth_manager.authenticate_user("testuser", "TestPass123!")
        self.assertTrue(success)
        
        # Wait for session to expire
        time.sleep(2)
        
        # Validate expired session
        valid, message, username = self.auth_manager.validate_session(session_id)
        self.assertFalse(valid, "Expired session should be invalid")
        self.assertEqual(message, "Session expired")
    
    def test_session_invalidation(self):
        """Test manual session invalidation"""
        # Authenticate and get session
        success, message, session_id = self.auth_manager.authenticate_user("testuser", "TestPass123!")
        self.assertTrue(success)
        
        # Invalidate session
        self.auth_manager._invalidate_session(session_id)
        
        # Validate invalidated session
        valid, message, username = self.auth_manager.validate_session(session_id)
        self.assertFalse(valid, "Invalidated session should be rejected")


class TestRoleBasedAccessControl(unittest.TestCase):
    """Test Role-Based Access Control (RBAC)"""
    
    def setUp(self):
        """Setup RBAC test environment"""
        self.auth_manager = MockAuthenticationManager()
        
        # Create users with different roles
        self.auth_manager.create_user("admin", "AdminPass123!", "admin")
        self.auth_manager.create_user("power_user", "PowerPass123!", "power_user")
        self.auth_manager.create_user("regular_user", "UserPass123!", "user")
        self.auth_manager.create_user("guest_user", "GuestPass123!", "guest")
    
    def test_admin_permissions(self):
        """Test admin role permissions"""
        admin_permissions = [
            ("users", "create", True),
            ("users", "delete", True),
            ("system", "admin", True),
            ("files", "delete", True),
            ("security", "admin", True),
        ]
        
        for resource, action, expected in admin_permissions:
            with self.subTest(resource=resource, action=action):
                has_permission, message = self.auth_manager.check_permission("admin", resource, action)
                self.assertEqual(has_permission, expected, 
                               f"Admin should {'have' if expected else 'not have'} {action} access to {resource}")
    
    def test_power_user_permissions(self):
        """Test power user role permissions"""
        power_user_permissions = [
            ("users", "read", True),
            ("users", "delete", False),
            ("system", "read", True),
            ("system", "admin", False),
            ("files", "write", True),
            ("files", "delete", False),
            ("security", "read", True),
            ("security", "admin", False),
        ]
        
        for resource, action, expected in power_user_permissions:
            with self.subTest(resource=resource, action=action):
                has_permission, message = self.auth_manager.check_permission("power_user", resource, action)
                self.assertEqual(has_permission, expected,
                               f"Power user should {'have' if expected else 'not have'} {action} access to {resource}")
    
    def test_regular_user_permissions(self):
        """Test regular user role permissions"""
        user_permissions = [
            ("users", "read", False),
            ("users", "create", False),
            ("system", "read", False),
            ("files", "read", True),
            ("files", "write", False),
            ("security", "read", False),
        ]
        
        for resource, action, expected in user_permissions:
            with self.subTest(resource=resource, action=action):
                has_permission, message = self.auth_manager.check_permission("regular_user", resource, action)
                self.assertEqual(has_permission, expected,
                               f"Regular user should {'have' if expected else 'not have'} {action} access to {resource}")
    
    def test_guest_permissions(self):
        """Test guest role permissions"""
        guest_permissions = [
            ("users", "read", False),
            ("system", "read", False),
            ("files", "read", False),
            ("security", "read", False),
        ]
        
        for resource, action, expected in guest_permissions:
            with self.subTest(resource=resource, action=action):
                has_permission, message = self.auth_manager.check_permission("guest_user", resource, action)
                self.assertEqual(has_permission, expected,
                               f"Guest should {'have' if expected else 'not have'} {action} access to {resource}")
    
    def test_privilege_escalation_prevention(self):
        """Test prevention of privilege escalation"""
        # Regular user should not be able to access admin functions
        admin_only_permissions = [
            ("users", "create"),
            ("users", "delete"),
            ("system", "admin"),
            ("security", "admin"),
        ]
        
        for resource, action in admin_only_permissions:
            with self.subTest(resource=resource, action=action):
                has_permission, message = self.auth_manager.check_permission("regular_user", resource, action)
                self.assertFalse(has_permission, 
                               f"Regular user should not have {action} access to {resource}")


class TestMultiFactorAuthentication(unittest.TestCase):
    """Test Multi-Factor Authentication (MFA)"""
    
    def setUp(self):
        """Setup MFA test environment"""
        self.auth_manager = MockAuthenticationManager()
        self.auth_manager.create_user("mfa_user", "MfaPass123!", "user")
        
        # Enable MFA for test user
        self.auth_manager.users["mfa_user"]["mfa_enabled"] = True
        self.auth_manager.users["mfa_user"]["mfa_secret"] = "test_secret"
    
    def test_mfa_required_authentication(self):
        """Test authentication requires MFA when enabled"""
        # Try authentication without MFA token
        success, message, session_id = self.auth_manager.authenticate_user("mfa_user", "MfaPass123!")
        self.assertFalse(success, "Authentication should fail without MFA token")
        self.assertEqual(message, "Invalid MFA token")
    
    def test_mfa_successful_authentication(self):
        """Test successful authentication with MFA"""
        # Authenticate with valid MFA token
        success, message, session_id = self.auth_manager.authenticate_user("mfa_user", "MfaPass123!", "123456")
        self.assertTrue(success, "Authentication should succeed with valid MFA token")
        self.assertEqual(message, "Authentication successful")
        self.assertIsNotNone(session_id)
    
    def test_mfa_invalid_token(self):
        """Test authentication with invalid MFA token"""
        # Authenticate with invalid MFA token
        success, message, session_id = self.auth_manager.authenticate_user("mfa_user", "MfaPass123!", "000000")
        self.assertFalse(success, "Authentication should fail with invalid MFA token")
        self.assertEqual(message, "Invalid MFA token")


class TestConcurrentAuthentication(unittest.TestCase):
    """Test concurrent authentication scenarios"""
    
    def setUp(self):
        """Setup concurrent authentication test environment"""
        self.auth_manager = MockAuthenticationManager()
        self.auth_manager.create_user("concurrent_user", "ConcurrentPass123!", "user")
        self.results = []
        self.lock = threading.Lock()
    
    def test_concurrent_login_attempts(self):
        """Test multiple concurrent login attempts"""
        
        def login_attempt(attempt_id):
            try:
                success, message, session_id = self.auth_manager.authenticate_user(
                    "concurrent_user", "ConcurrentPass123!"
                )
                with self.lock:
                    self.results.append((attempt_id, success, session_id))
            except Exception as e:
                with self.lock:
                    self.results.append((attempt_id, False, str(e)))
        
        # Start multiple concurrent authentication attempts
        threads = []
        for i in range(5):
            thread = threading.Thread(target=login_attempt, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All attempts should succeed (no race conditions)
        successful_attempts = [result for result in self.results if result[1] is True]
        self.assertEqual(len(successful_attempts), 5, 
                        "All concurrent authentication attempts should succeed")
        
        # All session IDs should be unique
        session_ids = [result[2] for result in successful_attempts]
        unique_sessions = set(session_ids)
        self.assertEqual(len(unique_sessions), 5, 
                        "All sessions should have unique IDs")


if __name__ == '__main__':
    unittest.main()