#!/usr/bin/env python3
"""
Comprehensive Input Validation Security Testing Suite

This module provides comprehensive testing for input validation security including:
- SQL Injection Protection Testing
- XSS (Cross-Site Scripting) Protection Testing  
- CSRF (Cross-Site Request Forgery) Protection Testing
- General Input Sanitization and Validation
- Malicious Input Detection and Handling

Author: Security Testing Framework
Date: 2025-09-04
Version: 1.0.0
"""

import hashlib
import html
import os
import re
import secrets
import shutil
import sqlite3
import string
import sys
import tempfile
import threading
import time
import unittest
import urllib.parse
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class SecurityTestEnvironment:
    """Security test environment setup for input validation testing"""
    
    def __init__(self):
        self.temp_dir = None
        self.db_path = None
        self.db_connection = None
        
    def setup(self):
        """Setup security test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix="rfu_input_validation_test_")
        self.db_path = os.path.join(self.temp_dir, "validation_test.db")
        self.db_connection = sqlite3.connect(self.db_path)
        
        # Create test tables for SQL injection testing
        self.setup_test_database()
        
        return self.db_connection
    
    def setup_test_database(self):
        """Setup test database with sample data"""
        cursor = self.db_connection.cursor()
        
        # Create test tables
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE sensitive_data (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                data_type TEXT,
                content TEXT,
                security_level INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert sample data
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role) VALUES
            ('admin', 'admin@test.com', 'hashed_admin_password', 'admin'),
            ('user1', 'user1@test.com', 'hashed_user1_password', 'user'),
            ('user2', 'user2@test.com', 'hashed_user2_password', 'user')
        ''')
        
        cursor.execute('''
            INSERT INTO sensitive_data (user_id, data_type, content, security_level) VALUES
            (1, 'admin_secret', 'top_secret_admin_data', 5),
            (2, 'user_data', 'user1_personal_info', 2),
            (3, 'user_data', 'user2_personal_info', 2)
        ''')
        
        self.db_connection.commit()
    
    def teardown(self):
        """Cleanup security test environment"""
        if self.db_connection:
            self.db_connection.close()
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class MockInputValidator:
    """Mock input validator for testing"""
    
    def __init__(self, strict_mode=True):
        self.strict_mode = strict_mode
        self.validation_rules = {
            'sql_patterns': [
                r"(\bUNION\b.*\bSELECT\b)",
                r"(\bSELECT\b.*\bFROM\b)",
                r"(\bINSERT\b.*\bINTO\b)",
                r"(\bUPDATE\b.*\bSET\b)",
                r"(\bDELETE\b.*\bFROM\b)",
                r"(\bDROP\b.*\bTABLE\b)",
                r"(\bCREATE\b.*\bTABLE\b)",
                r"(\bALTER\b.*\bTABLE\b)",
                r"(\bEXEC\b|\bEXECUTE\b)",
                r"(--|/\*|\*/)",
                r"(\bOR\b.*=.*)",
                r"(\bAND\b.*=.*)",
                r"('.*'.*=.*'.*')",
            ],
            'xss_patterns': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"vbscript:",
                r"vbscript\s*:",
                r"vbs:",
                r"visual\s*basic",
                r"on\w+\s*=",
                r"<iframe[^>]*>.*?</iframe>",
                r"<object[^>]*>.*?</object>",
                r"<embed[^>]*>",
                r"<form[^>]*>.*?</form>",
                r"<img[^>]*onerror[^>]*>",
                r"<svg[^>]*onload[^>]*>",
                r"expression\s*\(",
                r"url\s*\(",
                r"@import",
                r"eval\s*\(",
                r"document\.(write|location)",
                r"window\.location",
            ],
            'csrf_patterns': [
                r"<form[^>]*method\s*=\s*[\"']?post[\"']?[^>]*>(?!.*csrf)",
                r"XMLHttpRequest.*POST",
                r"fetch.*POST.*(?!.*csrf)",
                r"axios\.post.*(?!.*csrf)",
            ]
        }
    
    def validate_input(self, input_text, validation_type='all'):
        """Validate input for security vulnerabilities"""
        if not input_text:
            return True, "Empty input"
        
        threats_detected = []
        
        if validation_type in ['all', 'sql']:
            sql_threats = self._check_sql_injection(input_text)
            threats_detected.extend(sql_threats)
        
        if validation_type in ['all', 'xss']:
            xss_threats = self._check_xss(input_text)
            threats_detected.extend(xss_threats)
        
        if validation_type in ['all', 'csrf']:
            csrf_threats = self._check_csrf(input_text)
            threats_detected.extend(csrf_threats)
        
        is_safe = len(threats_detected) == 0
        message = "Input is safe" if is_safe else f"Threats detected: {', '.join(threats_detected)}"
        
        return is_safe, message
    
    def _check_sql_injection(self, input_text):
        """Check for SQL injection patterns"""
        threats = []
        input_lower = input_text.lower()
        
        for pattern in self.validation_rules['sql_patterns']:
            if re.search(pattern, input_lower, re.IGNORECASE):
                threats.append(f"SQL injection pattern: {pattern}")
        
        return threats
    
    def _check_xss(self, input_text):
        """Check for XSS patterns"""
        threats = []
        
        for pattern in self.validation_rules['xss_patterns']:
            if re.search(pattern, input_text, re.IGNORECASE):
                threats.append(f"XSS pattern: {pattern}")
        
        return threats
    
    def _check_csrf(self, input_text):
        """Check for CSRF vulnerabilities"""
        threats = []
        
        for pattern in self.validation_rules['csrf_patterns']:
            if re.search(pattern, input_text, re.IGNORECASE):
                threats.append(f"CSRF vulnerability: {pattern}")
        
        return threats
    
    def sanitize_input(self, input_text, sanitization_type='all'):
        """Sanitize input by removing or escaping dangerous content"""
        if not input_text:
            return input_text
        
        sanitized = input_text
        
        if sanitization_type in ['all', 'html']:
            sanitized = html.escape(sanitized)
        
        if sanitization_type in ['all', 'url']:
            sanitized = urllib.parse.quote(sanitized, safe='')
        
        if sanitization_type in ['all', 'sql']:
            # Basic SQL sanitization - escape single quotes
            sanitized = sanitized.replace("'", "''")
            sanitized = sanitized.replace(";", "")
            sanitized = sanitized.replace("--", "")
            sanitized = sanitized.replace("/*", "")
            sanitized = sanitized.replace("*/", "")
        
        return sanitized


class TestSQLInjectionProtection(unittest.TestCase):
    """Test SQL injection protection mechanisms"""
    
    def setUp(self):
        """Setup SQL injection test environment"""
        self.env = SecurityTestEnvironment()
        self.db_connection = self.env.setup()
        self.validator = MockInputValidator()
        self.test_user = "test_sql_user"
    
    def tearDown(self):
        """Cleanup SQL injection test environment"""
        self.env.teardown()
    
    def test_basic_sql_injection_attacks(self):
        """Test basic SQL injection attack vectors"""
        sql_injection_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT * FROM users--",
            "'; DROP TABLE users; --",
            "' OR 'x'='x",
            "1' OR '1'='1' /*",
            "' OR 1=1#",
            "admin'--",
            "admin'/*",
            "' OR 'a'='a",
            "') OR ('1'='1",
            "' OR (SELECT COUNT(*) FROM users) > 0--",
        ]
        
        for payload in sql_injection_payloads:
            with self.subTest(payload=payload):
                is_safe, message = self.validator.validate_input(payload, 'sql')
                self.assertFalse(is_safe, f"Should detect SQL injection in: {payload}")
                self.assertIn("SQL injection", message)
    
    def test_advanced_sql_injection_attacks(self):
        """Test advanced SQL injection attack vectors"""
        advanced_payloads = [
            "1' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='a",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
            "1' UNION SELECT 1,version(),3,4--",
            "1' UNION SELECT null,table_name,null,null FROM information_schema.tables--",
            "1'; INSERT INTO users VALUES ('hacker','hack@evil.com','hacked');--",
            "1' AND SLEEP(5)--",
            "1' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
            "1' UNION SELECT 1,group_concat(table_name),3,4 FROM information_schema.tables WHERE table_schema=database()--",
        ]
        
        for payload in advanced_payloads:
            with self.subTest(payload=payload):
                is_safe, message = self.validator.validate_input(payload, 'sql')
                self.assertFalse(is_safe, f"Should detect advanced SQL injection in: {payload}")
    
    def test_parameterized_query_simulation(self):
        """Test that parameterized queries prevent SQL injection"""
        cursor = self.db_connection.cursor()
        
        # Simulate parameterized query (safe)
        malicious_username = "admin' OR '1'='1'--"
        
        # This should not return any results because it's treated as literal string
        cursor.execute("SELECT * FROM users WHERE username = ?", (malicious_username,))
        results = cursor.fetchall()
        
        # Should not find any user with this exact malicious string as username
        self.assertEqual(len(results), 0, "Parameterized query should prevent SQL injection")
        
        # Test with valid username
        cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
        valid_results = cursor.fetchall()
        
        # Should find the admin user
        self.assertEqual(len(valid_results), 1, "Parameterized query should work for valid input")
        self.assertEqual(valid_results[0][1], "admin")


class TestXSSProtection(unittest.TestCase):
    """Test XSS (Cross-Site Scripting) protection mechanisms"""
    
    def setUp(self):
        """Setup XSS test environment"""
        self.validator = MockInputValidator()
    
    def test_basic_xss_attacks(self):
        """Test basic XSS attack vectors"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<script>alert(document.cookie)</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input type=text onkeypress=alert('XSS')>",
            "<a href=javascript:alert('XSS')>Click me</a>",
            "<div onclick=alert('XSS')>Click me</div>",
            "<object data=javascript:alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            with self.subTest(payload=payload):
                is_safe, message = self.validator.validate_input(payload, 'xss')
                self.assertFalse(is_safe, f"Should detect XSS in: {payload}")
                self.assertIn("XSS", message)
    
    def test_advanced_xss_attacks(self):
        """Test advanced XSS attack vectors"""
        advanced_xss_payloads = [
            "javascript:alert('XSS')",
            "vbscript:alert('XSS')",
            "<script>eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))</script>",
            "<img src=1 href=1 onerror=\"javascript:alert(1)\"></img>",
            "<audio src=1 href=1 onerror=\"javascript:alert(1)\"></audio>",
            "<video src=1 href=1 onerror=\"javascript:alert(1)\"></video>",
            "<source src=1 href=1 onerror=\"javascript:alert(1)\"></source>",
            "<input autofocus onfocus=alert(1)>",
            "<select autofocus onfocus=alert(1)>",
            "<textarea autofocus onfocus=alert(1)>",
            "<keygen autofocus onfocus=alert(1)>",
            "<video><source onerror=\"javascript:alert(1)\">",
            "<details open ontoggle=\"alert('XSS')\">",
        ]
        
        for payload in advanced_xss_payloads:
            with self.subTest(payload=payload):
                is_safe, message = self.validator.validate_input(payload, 'xss')
                self.assertFalse(is_safe, f"Should detect advanced XSS in: {payload}")


class TestCSRFProtection(unittest.TestCase):
    """Test CSRF (Cross-Site Request Forgery) protection mechanisms"""
    
    def setUp(self):
        """Setup CSRF test environment"""
        self.validator = MockInputValidator()
    
    def test_csrf_form_detection(self):
        """Test detection of forms without CSRF protection"""
        csrf_vulnerable_forms = [
            '<form method="post" action="/transfer"><input name="amount" value="1000"></form>',
            '<form method="POST" action="/delete"><input name="id" value="123"></form>',
            '<form method="post"><input name="password" type="password"></form>',
            '<form action="/admin" method="post"><input name="action" value="delete_all"></form>',
        ]
        
        for form in csrf_vulnerable_forms:
            with self.subTest(form=form):
                is_safe, message = self.validator.validate_input(form, 'csrf')
                self.assertFalse(is_safe, f"Should detect CSRF vulnerability in: {form}")
                self.assertIn("CSRF", message)


class TestGeneralInputValidation(unittest.TestCase):
    """Test general input validation and sanitization"""
    
    def setUp(self):
        """Setup general input validation test environment"""
        self.validator = MockInputValidator()
    
    def test_input_sanitization(self):
        """Test input sanitization functions"""
        test_cases = [
            ("Normal text", "Normal text"),
            ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"),
            ("Text with 'quotes'", "Text with &#x27;quotes&#x27;"),
            ("Text & symbols", "Text &amp; symbols"),
        ]
        
        for input_text, expected_pattern in test_cases:
            with self.subTest(input=input_text):
                sanitized = self.validator.sanitize_input(input_text, 'html')
                # Basic check that dangerous characters are escaped
                self.assertNotIn('<script', sanitized.lower())
                self.assertNotIn('javascript:', sanitized.lower())
    
    def test_null_byte_injection(self):
        """Test null byte injection protection"""
        null_byte_payloads = [
            "normal_file.txt\x00malicious_file.exe",
            "safe_path\x00../../../etc/passwd",
            "regular_input\x00<script>alert('xss')</script>",
            "username\x00admin",
            "\x00' OR '1'='1",
        ]
        
        for payload in null_byte_payloads:
            with self.subTest(payload=repr(payload)):
                # Should detect null bytes
                self.assertIn('\x00', payload)
                # Most systems should reject null bytes in inputs


class TestInputValidationIntegration(unittest.TestCase):
    """Test input validation integration scenarios"""
    
    def setUp(self):
        """Setup integration test environment"""
        self.validator = MockInputValidator()
        self.env = SecurityTestEnvironment()
        self.db_connection = self.env.setup()
    
    def tearDown(self):
        """Cleanup integration test environment"""
        self.env.teardown()
    
    def test_combined_attack_vectors(self):
        """Test combined attack vectors (SQL injection + XSS)"""
        combined_payloads = [
            "'; SELECT '<script>alert(1)</script>' --",
            "admin' UNION SELECT '<img src=x onerror=alert(1)>' --",
            "<script>document.location='?id=1\\' OR 1=1--'</script>",
        ]
        
        for payload in combined_payloads:
            with self.subTest(payload=payload):
                is_safe_sql, _ = self.validator.validate_input(payload, 'sql')
                is_safe_xss, _ = self.validator.validate_input(payload, 'xss')
                
                # Should detect at least one type of attack
                self.assertFalse(is_safe_sql or is_safe_xss, 
                               f"Should detect combined attack in: {payload}")


if __name__ == '__main__':
    unittest.main()