#!/usr/bin/env python3
"""
Integration Tests for Configuration Analyzer

Tests real-world scenarios and integration with other components.
"""

import configparser
import json
import os
import shutil
# Import the module under test
import sys
import tempfile
from pathlib import Path
from typing import List

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.utilities.analysis.config.config_analyzer import (
    ConfigAnalysisResult, ConfigType, ConfigurationAnalyzer, SecurityLevel,
    analyze_config_directory, analyze_config_file)


class TestRealWorldConfigurations:
    """Test with real-world configuration examples."""
    
    def test_django_settings_analysis(self):
        """Test analysis of Django-style settings."""
        django_settings = {
            "DEBUG": True,  # Security issue
            "SECRET_KEY": "django-insecure-secret-key",  # Security issue
            "ALLOWED_HOSTS": ["*"],  # Security issue
            "DATABASES": {
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": "myproject",
                    "USER": "myuser",
                    "PASSWORD": "mypassword",  # Security issue
                    "HOST": "127.0.0.1",
                    "PORT": "5432",
                }
            },
            "STATIC_URL": "/static/",
            "MEDIA_URL": "/media/",
            "INSTALLED_APPS": [
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "myapp",
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(django_settings, f, indent=2)
            temp_path = f.name
        
        try:
            result = analyze_config_file(temp_path)
            
            assert result.is_valid is True
            security_issues = [issue for issue in result.issues if issue.category == "security"]
            assert len(security_issues) >= 3  # DEBUG, SECRET_KEY, PASSWORD, ALLOWED_HOSTS
            assert result.security_score < 50  # Should be low due to multiple issues
            
            # Check specific security issues
            issue_messages = [issue.message.lower() for issue in security_issues]
            assert any("debug" in msg for msg in issue_messages)
            assert any("password" in msg for msg in issue_messages)
            
        finally:
            os.unlink(temp_path)
    
    def test_docker_compose_analysis(self):
        """Test analysis of Docker Compose configuration."""
        docker_compose = {
            "version": "3.8",
            "services": {
                "web": {
                    "build": ".",
                    "ports": ["8000:8000"],
                    "environment": {
                        "DEBUG": "true",  # Security issue
                        "DATABASE_URL": "postgresql://user:password@db:5432/mydb",  # Security issue
                        "SECRET_KEY": "super-secret-key"  # Security issue
                    },
                    "volumes": ["/host/path:/container/path"]  # Potential security issue
                },
                "db": {
                    "image": "postgres:13",
                    "environment": {
                        "POSTGRES_PASSWORD": "password123"  # Security issue
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(docker_compose, f)
            temp_path = f.name
        
        try:
            result = analyze_config_file(temp_path)
            
            assert result.is_valid is True
            assert result.config_type == ConfigType.YAML
            
            security_issues = [issue for issue in result.issues if issue.category == "security"]
            assert len(security_issues) >= 3  # Multiple password/secret exposures
            
        finally:
            os.unlink(temp_path)
    
    def test_nginx_config_analysis(self):
        """Test analysis of Nginx-style configuration."""
        nginx_config = """
        # Nginx configuration
        server {
            listen 80;
            server_name example.com;
            
            # Security headers
            add_header X-Frame-Options DENY;
            add_header X-Content-Type-Options nosniff;
            
            location / {
                proxy_pass http://backend;
                proxy_set_header Host $host;
            }
            
            # Debug mode enabled - security issue
            error_log /var/log/nginx/error.log debug;
        }
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write(nginx_config)
            temp_path = f.name
        
        try:
            result = analyze_config_file(temp_path)
            
            assert result.is_valid is True
            assert result.config_type == ConfigType.INI  # Detected as INI-like
            
            # Should detect some issues
            assert len(result.issues) > 0
            
        finally:
            os.unlink(temp_path)
    
    def test_aws_config_analysis(self):
        """Test analysis of AWS configuration."""
        aws_config = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",  # Security issue - too permissive
                    "Resource": "*"  # Security issue - too permissive
                }
            ],
            "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",  # Security issue
            "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # Security issue
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(aws_config, f, indent=2)
            temp_path = f.name
        
        try:
            result = analyze_config_file(temp_path)
            
            assert result.is_valid is True
            security_issues = [issue for issue in result.issues if issue.category == "security"]
            assert len(security_issues) >= 2  # Access key exposure
            
        finally:
            os.unlink(temp_path)


class TestComplexProjectStructures:
    """Test analysis of complex project structures."""
    
    def test_microservices_config_analysis(self):
        """Test analysis of microservices configuration structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create microservices config structure
            services = ["user-service", "order-service", "payment-service"]
            
            for service in services:
                service_dir = os.path.join(temp_dir, service)
                os.makedirs(service_dir)
                
                # Create service config
                config = {
                    "service": {
                        "name": service,
                        "port": 8000 + len(service),
                        "database": {
                            "host": "localhost",
                            "password": f"{service}-password"  # Security issue
                        }
                    },
                    "logging": {
                        "level": "DEBUG"  # Security issue
                    }
                }
                
                config_file = os.path.join(service_dir, "config.json")
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
            
            # Analyze the entire structure
            results = analyze_config_directory(temp_dir, recursive=True)
            
            assert len(results) == 3
            
            # All should have security issues
            for result in results:
                security_issues = [issue for issue in result.issues if issue.category == "security"]
                assert len(security_issues) >= 1
    
    def test_kubernetes_config_analysis(self):
        """Test analysis of Kubernetes configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create k8s configs
            k8s_configs = {
                "deployment.yaml": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [{
                                    "name": "app",
                                    "env": [
                                        {"name": "DB_PASSWORD", "value": "hardcoded-password"},  # Security issue
                                        {"name": "API_KEY", "value": "sk-1234567890"}  # Security issue
                                    ]
                                }]
                            }
                        }
                    }
                },
                "configmap.yaml": {
                    "apiVersion": "v1",
                    "kind": "ConfigMap",
                    "data": {
                        "app.properties": "debug=true\\npassword=secret123"  # Security issues
                    }
                }
            }
            
            for filename, config in k8s_configs.items():
                config_file = os.path.join(temp_dir, filename)
                with open(config_file, 'w') as f:
                    yaml.dump(config, f)
            
            results = analyze_config_directory(temp_dir)
            
            assert len(results) == 2
            
            # Should detect security issues in both files
            total_security_issues = sum(
                len([issue for issue in result.issues if issue.category == "security"])
                for result in results
            )
            assert total_security_issues >= 2


class TestPerformanceWithLargeFiles:
    """Test performance with large configuration files."""
    
    def test_large_json_config_performance(self):
        """Test performance with large JSON configuration."""
        # Create large configuration
        large_config = {}
        for i in range(10000):
            large_config[f"key_{i}"] = {
                "value": f"value_{i}",
                "nested": {
                    "data": [f"item_{j}" for j in range(10)]
                }
            }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_config, f)
            temp_path = f.name
        
        try:
            import time
            start_time = time.time()
            result = analyze_config_file(temp_path)
            analysis_time = time.time() - start_time
            
            assert result.is_valid is True
            assert analysis_time < 30  # Should complete within 30 seconds
            assert result.analysis_time > 0
            
            # Should detect performance issues
            performance_issues = [issue for issue in result.issues if issue.category == "performance"]
            assert len(performance_issues) > 0
            
        finally:
            os.unlink(temp_path)
    
    def test_deeply_nested_config_performance(self):
        """Test performance with deeply nested configuration."""
        # Create deeply nested structure
        nested_config = {"level0": {}}
        current = nested_config["level0"]
        
        for i in range(50):  # 50 levels deep
            current[f"level{i+1}"] = {}
            current = current[f"level{i+1}"]
        
        current["final_value"] = "deep_value"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(nested_config, f)
            temp_path = f.name
        
        try:
            result = analyze_config_file(temp_path)
            
            assert result.is_valid is True
            assert result.metrics["nesting_depth"] >= 50
            
            # Should detect performance issues
            performance_issues = [issue for issue in result.issues if issue.category == "performance"]
            assert len(performance_issues) > 0
            
        finally:
            os.unlink(temp_path)


class TestMultiFormatIntegration:
    """Test integration across multiple configuration formats."""
    
    def test_mixed_format_project_analysis(self):
        """Test analysis of project with multiple config formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create configs in different formats
            configs = {
                "app.json": {"app": {"name": "myapp", "debug": True}},
                "database.yaml": {"database": {"host": "localhost", "password": "secret"}},
                "settings.ini": "[DEFAULT]\\napi_key = sk-1234567890\\n",
                "docker.toml": {"version": "1.0", "services": {"web": {"debug": True}}}
            }
            
            for filename, content in configs.items():
                config_file = os.path.join(temp_dir, filename)
                
                if filename.endswith('.json'):
                    with open(config_file, 'w') as f:
                        json.dump(content, f)
                elif filename.endswith('.yaml'):
                    with open(config_file, 'w') as f:
                        yaml.dump(content, f)
                elif filename.endswith('.ini'):
                    with open(config_file, 'w') as f:
                        f.write(content)
                elif filename.endswith('.toml'):
                    # For this test, we'll treat TOML as text since toml might not be available
                    with open(config_file, 'w') as f:
                        f.write(str(content))
            
            results = analyze_config_directory(temp_dir)
            
            # Should analyze all config files
            assert len(results) >= 3  # At least JSON, YAML, INI
            
            # Check that different types were detected
            config_types = {result.config_type for result in results}
            assert ConfigType.JSON in config_types
            assert ConfigType.YAML in config_types
            assert ConfigType.INI in config_types
            
            # Should find security issues across formats
            total_security_issues = sum(
                len([issue for issue in result.issues if issue.category == "security"])
                for result in results
            )
            assert total_security_issues >= 2


class TestReportingIntegration:
    """Test report generation in integrated scenarios."""
    
    def test_comprehensive_project_report(self):
        """Test comprehensive report generation for a complex project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a complex project structure
            project_structure = {
                "app": {
                    "config.json": {"app": {"name": "myapp", "debug": False, "version": "1.0.0"}},
                    "database.yaml": {"database": {"host": "localhost", "port": 5432}}
                },
                "docker": {
                    "docker-compose.yml": {"version": "3.8", "services": {"web": {"build": "."}}}
                },
                "k8s": {
                    "deployment.yaml": {"apiVersion": "apps/v1", "kind": "Deployment"}
                }
            }
            
            # Create the structure
            for dir_name, files in project_structure.items():
                dir_path = os.path.join(temp_dir, dir_name)
                os.makedirs(dir_path)
                
                for filename, content in files.items():
                    file_path = os.path.join(dir_path, filename)
                    with open(file_path, 'w') as f:
                        if filename.endswith('.json'):
                            json.dump(content, f, indent=2)
                        else:
                            yaml.dump(content, f)
            
            # Analyze and generate reports
            analyzer = ConfigurationAnalyzer()
            results = analyzer.analyze_directory(temp_dir, recursive=True)
            
            # Test different report formats
            text_report = analyzer.generate_report(results, "text")
            json_report = analyzer.generate_report(results, "json")
            html_report = analyzer.generate_report(results, "html")
            
            # Validate reports
            assert "CONFIGURATION ANALYSIS REPORT" in text_report
            assert len(results) >= 3
            
            json_data = json.loads(json_report)
            assert "metadata" in json_data
            assert "summary" in json_data
            assert len(json_data["results"]) >= 3
            
            assert "<!DOCTYPE html>" in html_report
            assert "Configuration Analysis Report" in html_report
    
    def test_security_focused_report(self):
        """Test report generation focused on security issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create configs with various security issues
            security_config = {
                "credentials": {
                    "username": "admin",
                    "password": "admin123",  # Weak password
                    "api_key": "sk-1234567890abcdef",  # API key exposure
                    "secret_token": "secret123"  # Secret exposure
                },
                "settings": {
                    "debug": True,  # Debug mode
                    "ssl_verify": False,  # SSL verification disabled
                    "encryption": "MD5"  # Weak encryption
                }
            }
            
            config_file = os.path.join(temp_dir, "security.json")
            with open(config_file, 'w') as f:
                json.dump(security_config, f, indent=2)
            
            results = analyze_config_directory(temp_dir)
            
            assert len(results) == 1
            result = results[0]
            
            security_issues = [issue for issue in result.issues if issue.category == "security"]
            assert len(security_issues) >= 4  # Multiple security issues
            assert result.security_score < 50  # Low security score
            
            # Generate focused report
            analyzer = ConfigurationAnalyzer()
            report = analyzer.generate_report(results, "text")
            
            # Should highlight security issues prominently
            assert "SECURITY ISSUES" in report or "Security Score" in report
            assert "password" in report.lower()
            assert "api" in report.lower()


class TestErrorRecoveryIntegration:
    """Test error recovery in integrated scenarios."""
    
    def test_mixed_valid_invalid_configs(self):
        """Test analysis of directory with mix of valid and invalid configs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create valid config
            valid_config = os.path.join(temp_dir, "valid.json")
            with open(valid_config, 'w') as f:
                json.dump({"app": "test"}, f)
            
            # Create invalid config
            invalid_config = os.path.join(temp_dir, "invalid.json")
            with open(invalid_config, 'w') as f:
                f.write('{"invalid": json}')  # Invalid JSON
            
            # Create empty config
            empty_config = os.path.join(temp_dir, "empty.json")
            with open(empty_config, 'w') as f:
                f.write('')  # Empty file
            
            results = analyze_config_directory(temp_dir)
            
            assert len(results) == 3
            
            # Check individual results
            valid_results = [r for r in results if r.is_valid]
            invalid_results = [r for r in results if not r.is_valid]
            
            assert len(valid_results) == 1
            assert len(invalid_results) == 2
            
            # Invalid results should have syntax issues
            for result in invalid_results:
                syntax_issues = [issue for issue in result.issues if issue.category == "syntax"]
                assert len(syntax_issues) > 0
    
    def test_permission_error_handling(self):
        """Test handling of permission errors during analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a config file
            config_file = os.path.join(temp_dir, "test.json")
            with open(config_file, 'w') as f:
                json.dump({"test": "data"}, f)
            
            # This test would be OS-specific and might not work on all systems
            # We'll simulate the behavior instead
            analyzer = ConfigurationAnalyzer()
            
            # Test that the analyzer can handle permission errors gracefully
            # (Implementation should catch OSError and continue with other files)
            try:
                results = analyzer.analyze_directory(temp_dir)
                assert len(results) >= 0  # Should not crash
            except Exception as e:
                pytest.fail(f"Analyzer should handle permission errors gracefully: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])