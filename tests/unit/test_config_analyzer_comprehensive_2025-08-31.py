#!/usr/bin/env python3
"""
Comprehensive Test Suite for Configuration Analyzer

Tests for config_analyzer.py covering all functionality including:
- Configuration type detection
- Security analysis
- Performance analysis  
- Best practices validation
- Report generation
- Edge cases and error handling
"""

import configparser
import json
import os
# Import the module under test
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.utilities.analysis.config.config_analyzer import (
    ConfigAnalysisResult, ConfigIssue, ConfigType, ConfigurationAnalyzer,
    SecurityLevel, analyze_config_directory, analyze_config_file)


class TestConfigTypeDetection:
    """Test configuration type detection functionality."""
    
    def test_detect_json_by_extension(self):
        """Test JSON detection by file extension."""
        analyzer = ConfigurationAnalyzer()
        assert analyzer.detect_config_type("config.json") == ConfigType.JSON
        
    def test_detect_yaml_by_extension(self):
        """Test YAML detection by file extensions."""
        analyzer = ConfigurationAnalyzer()
        assert analyzer.detect_config_type("config.yaml") == ConfigType.YAML
        assert analyzer.detect_config_type("config.yml") == ConfigType.YAML
        
    def test_detect_ini_by_extension(self):
        """Test INI detection by file extensions."""
        analyzer = ConfigurationAnalyzer()
        assert analyzer.detect_config_type("config.ini") == ConfigType.INI
        assert analyzer.detect_config_type("config.cfg") == ConfigType.INI
        assert analyzer.detect_config_type("config.conf") == ConfigType.INI
        
    def test_detect_xml_by_extension(self):
        """Test XML detection by file extension."""
        analyzer = ConfigurationAnalyzer()
        assert analyzer.detect_config_type("config.xml") == ConfigType.XML
        
    def test_detect_toml_by_extension(self):
        """Test TOML detection by file extension."""
        analyzer = ConfigurationAnalyzer()
        assert analyzer.detect_config_type("config.toml") == ConfigType.TOML
        
    def test_detect_properties_by_extension(self):
        """Test Properties detection by file extensions."""
        analyzer = ConfigurationAnalyzer()
        assert analyzer.detect_config_type("config.properties") == ConfigType.PROPERTIES
        assert analyzer.detect_config_type("config.prop") == ConfigType.PROPERTIES
        
    def test_detect_unknown_extension(self):
        """Test unknown file extension handling."""
        analyzer = ConfigurationAnalyzer()
        assert analyzer.detect_config_type("config.unknown") == ConfigType.UNKNOWN
        
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    @patch("pathlib.Path.exists", return_value=True)
    def test_detect_json_by_content(self, mock_exists, mock_file):
        """Test JSON detection by content analysis."""
        analyzer = ConfigurationAnalyzer()
        result = analyzer.detect_config_type("config.unknown")
        assert result == ConfigType.JSON
        
    @patch("builtins.open", new_callable=mock_open, read_data='key: value\nother: data')
    @patch("pathlib.Path.exists", return_value=True)
    def test_detect_yaml_by_content(self, mock_exists, mock_file):
        """Test YAML detection by content analysis."""
        analyzer = ConfigurationAnalyzer()
        result = analyzer.detect_config_type("config.unknown")
        assert result == ConfigType.YAML
        
    @patch("builtins.open", new_callable=mock_open, read_data='[section]\nkey=value')
    @patch("pathlib.Path.exists", return_value=True)
    def test_detect_ini_by_content(self, mock_exists, mock_file):
        """Test INI detection by content analysis."""
        analyzer = ConfigurationAnalyzer()
        result = analyzer.detect_config_type("config.unknown")
        assert result == ConfigType.INI
        
    @patch("builtins.open", new_callable=mock_open, read_data='<?xml version="1.0"?><root></root>')
    @patch("pathlib.Path.exists", return_value=True)
    def test_detect_xml_by_content(self, mock_exists, mock_file):
        """Test XML detection by content analysis."""
        analyzer = ConfigurationAnalyzer()
        result = analyzer.detect_config_type("config.unknown")
        assert result == ConfigType.XML
        
    @patch("pathlib.Path.exists", return_value=False)
    def test_detect_nonexistent_file(self, mock_exists):
        """Test handling of non-existent files."""
        analyzer = ConfigurationAnalyzer()
        result = analyzer.detect_config_type("nonexistent.json")
        assert result == ConfigType.JSON  # Should detect by extension
        
    @patch("builtins.open", side_effect=OSError("Permission denied"))
    @patch("pathlib.Path.exists", return_value=True)
    def test_detect_permission_error(self, mock_exists, mock_file):
        """Test handling of file permission errors."""
        analyzer = ConfigurationAnalyzer()
        result = analyzer.detect_config_type("protected.json")
        assert result == ConfigType.JSON  # Should fall back to extension


class TestConfigurationParsing:
    """Test configuration parsing functionality."""
    
    def test_parse_json_configuration(self):
        """Test JSON configuration parsing."""
        analyzer = ConfigurationAnalyzer()
        content = '{"database": {"host": "localhost", "port": 5432}}'
        result = analyzer._parse_configuration(content, ConfigType.JSON)
        
        assert result is not None
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == 5432
        
    def test_parse_yaml_configuration(self):
        """Test YAML configuration parsing."""
        analyzer = ConfigurationAnalyzer()
        content = """
        database:
          host: localhost
          port: 5432
        """
        result = analyzer._parse_configuration(content, ConfigType.YAML)
        
        assert result is not None
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == 5432
        
    def test_parse_ini_configuration(self):
        """Test INI configuration parsing."""
        analyzer = ConfigurationAnalyzer()
        content = """
        [database]
        host = localhost
        port = 5432
        """
        result = analyzer._parse_configuration(content, ConfigType.INI)
        
        assert result is not None
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == "5432"  # INI values are strings
        
    def test_parse_properties_configuration(self):
        """Test Properties configuration parsing."""
        analyzer = ConfigurationAnalyzer()
        content = """
        database.host=localhost
        database.port=5432
        # This is a comment
        app.name=MyApp
        """
        result = analyzer._parse_configuration(content, ConfigType.PROPERTIES)
        
        assert result is not None
        assert result["database.host"] == "localhost"
        assert result["database.port"] == "5432"
        assert result["app.name"] == "MyApp"
        assert "# This is a comment" not in result
        
    def test_parse_invalid_json(self):
        """Test handling of invalid JSON."""
        analyzer = ConfigurationAnalyzer()
        content = '{"key": value}'  # Missing quotes around value
        result = analyzer._parse_configuration(content, ConfigType.JSON)
        
        assert result is None
        
    def test_parse_invalid_yaml(self):
        """Test handling of invalid YAML."""
        analyzer = ConfigurationAnalyzer()
        content = """
        key: value
        invalid: [unclosed
        """
        result = analyzer._parse_configuration(content, ConfigType.YAML)
        
        assert result is None
        
    def test_parse_unknown_type(self):
        """Test parsing of unknown configuration type."""
        analyzer = ConfigurationAnalyzer()
        content = "some random content"
        result = analyzer._parse_configuration(content, ConfigType.UNKNOWN)
        
        assert result is not None
        assert result["raw_content"] == content


class TestSecurityAnalysis:
    """Test security analysis functionality."""
    
    def test_detect_password_exposure(self):
        """Test detection of password exposure."""
        analyzer = ConfigurationAnalyzer()
        content = """
        {
            "database": {
                "host": "localhost",
                "password": "secret123"
            }
        }
        """
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = json.loads(content)
        analyzer._analyze_security(content, parsed_config, result)
        
        security_issues = [issue for issue in result.issues if issue.category == "security"]
        assert len(security_issues) > 0
        assert any("password" in issue.message.lower() for issue in security_issues)
        assert result.security_score < 100.0
        
    def test_detect_api_key_exposure(self):
        """Test detection of API key exposure."""
        analyzer = ConfigurationAnalyzer()
        content = """
        api_key: sk-1234567890abcdef
        secret_key: very_secret_key
        """
        
        result = ConfigAnalysisResult(
            file_path="test.yaml",
            config_type=ConfigType.YAML,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = yaml.safe_load(content)
        analyzer._analyze_security(content, parsed_config, result)
        
        security_issues = [issue for issue in result.issues if issue.category == "security"]
        assert len(security_issues) > 0
        assert any("api" in issue.message.lower() or "secret" in issue.message.lower() 
                  for issue in security_issues)
        
    def test_detect_weak_crypto(self):
        """Test detection of weak cryptographic algorithms."""
        analyzer = ConfigurationAnalyzer()
        content = """
        {
            "encryption": {
                "algorithm": "MD5",
                "ssl_version": "SSLv2"
            }
        }
        """
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = json.loads(content)
        analyzer._analyze_security(content, parsed_config, result)
        
        security_issues = [issue for issue in result.issues if issue.category == "security"]
        assert len(security_issues) > 0
        assert any("weak" in issue.message.lower() for issue in security_issues)
        
    def test_detect_debug_settings(self):
        """Test detection of debug/development settings."""
        analyzer = ConfigurationAnalyzer()
        content = """
        debug = true
        development = true
        verbose = true
        """
        
        result = ConfigAnalysisResult(
            file_path="test.ini",
            config_type=ConfigType.INI,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = {"debug": "true", "development": "true", "verbose": "true"}
        analyzer._analyze_security(content, parsed_config, result)
        
        security_issues = [issue for issue in result.issues if issue.category == "security"]
        assert len(security_issues) > 0
        assert any("debug" in issue.message.lower() for issue in security_issues)
        
    def test_no_security_issues(self):
        """Test configuration with no security issues."""
        analyzer = ConfigurationAnalyzer()
        content = """
        {
            "app": {
                "name": "MyApp",
                "version": "1.0.0"
            }
        }
        """
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = json.loads(content)
        analyzer._analyze_security(content, parsed_config, result)
        
        security_issues = [issue for issue in result.issues if issue.category == "security"]
        assert len(security_issues) == 0
        assert result.security_score == 100.0


class TestPerformanceAnalysis:
    """Test performance analysis functionality."""
    
    def test_large_file_detection(self):
        """Test detection of large configuration files."""
        analyzer = ConfigurationAnalyzer()
        content = "x" * (15 * 1024 * 1024)  # 15MB file
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        analyzer._analyze_performance(content, {}, result)
        
        performance_issues = [issue for issue in result.issues if issue.category == "performance"]
        assert len(performance_issues) > 0
        assert any("large" in issue.message.lower() for issue in performance_issues)
        
    def test_deep_nesting_detection(self):
        """Test detection of deeply nested configurations."""
        analyzer = ConfigurationAnalyzer()
        
        # Create deeply nested structure
        nested_config = {"level1": {"level2": {"level3": {"level4": {"level5": {
            "level6": {"level7": {"level8": {"level9": {"level10": {"level11": {
                "deep": "value"
            }}}}}}}}}}}}
        
        content = json.dumps(nested_config)
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        analyzer._analyze_performance(content, nested_config, result)
        
        performance_issues = [issue for issue in result.issues if issue.category == "performance"]
        assert len(performance_issues) > 0
        assert any("nesting" in issue.message.lower() for issue in performance_issues)
        
    def test_long_line_detection(self):
        """Test detection of very long lines."""
        analyzer = ConfigurationAnalyzer()
        long_value = "x" * 15000  # Very long value
        content = f'{{"key": "{long_value}"}}'
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        analyzer._analyze_performance(content, {"key": long_value}, result)
        
        performance_issues = [issue for issue in result.issues if issue.category == "performance"]
        assert len(performance_issues) > 0
        assert any("long line" in issue.message.lower() for issue in performance_issues)
        
    def test_calculate_nesting_depth(self):
        """Test nesting depth calculation."""
        analyzer = ConfigurationAnalyzer()
        
        # Test simple object
        simple_config = {"key": "value"}
        assert analyzer._calculate_nesting_depth(simple_config) == 1
        
        # Test nested object
        nested_config = {"level1": {"level2": {"level3": "value"}}}
        assert analyzer._calculate_nesting_depth(nested_config) == 3
        
        # Test array
        array_config = {"items": [{"nested": "value"}]}
        assert analyzer._calculate_nesting_depth(array_config) == 3
        
        # Test empty object
        empty_config = {}
        assert analyzer._calculate_nesting_depth(empty_config) == 0


class TestBestPracticesAnalysis:
    """Test best practices analysis functionality."""
    
    def test_missing_comments_detection(self):
        """Test detection of missing comments/documentation."""
        analyzer = ConfigurationAnalyzer()
        content = """
        {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        """ * 10  # Make it long enough to trigger the check
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = json.loads(content)
        analyzer._analyze_best_practices(content, parsed_config, result)
        
        doc_issues = [issue for issue in result.issues if issue.category == "documentation"]
        assert len(doc_issues) > 0
        assert any("comment" in issue.message.lower() for issue in doc_issues)
        
    def test_hardcoded_paths_detection(self):
        """Test detection of hardcoded paths and URLs."""
        analyzer = ConfigurationAnalyzer()
        content = """
        {
            "paths": {
                "data": "C:\\\\Users\\\\data",
                "logs": "/var/log/app",
                "backup": "/backup/folder",
                "temp": "C:\\\\temp\\\\folder"
            },
            "urls": {
                "api": "https://api.example.com",
                "web": "http://localhost:8080"
            }
        }
        """
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = json.loads(content)
        analyzer._analyze_best_practices(content, parsed_config, result)
        
        maintainability_issues = [issue for issue in result.issues 
                                 if issue.category == "maintainability"]
        assert len(maintainability_issues) > 0
        assert any("hardcoded" in issue.message.lower() for issue in maintainability_issues)
        
    def test_missing_version_detection(self):
        """Test detection of missing version information."""
        analyzer = ConfigurationAnalyzer()
        content = """
        {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        """
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = json.loads(content)
        analyzer._analyze_best_practices(content, parsed_config, result)
        
        version_issues = [issue for issue in result.issues if issue.category == "versioning"]
        assert len(version_issues) > 0
        assert any("version" in issue.message.lower() for issue in version_issues)
        
    def test_good_practices_no_issues(self):
        """Test configuration with good practices - no issues."""
        analyzer = ConfigurationAnalyzer()
        content = """
        {
            // Configuration for MyApp v1.0.0
            "version": "1.0.0",
            "app": {
                "name": "MyApp"
            }
        }
        """
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = {"version": "1.0.0", "app": {"name": "MyApp"}}
        analyzer._analyze_best_practices(content, parsed_config, result)
        
        # Should have minimal issues due to good practices
        assert len(result.issues) <= 1  # Might have documentation issue for short content


class TestMetricsCalculation:
    """Test metrics calculation functionality."""
    
    def test_basic_metrics_calculation(self):
        """Test calculation of basic file metrics."""
        analyzer = ConfigurationAnalyzer()
        content = """
        {
            "key1": "value1",
            "key2": "value2"
        }
        """
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = json.loads(content)
        analyzer._calculate_metrics(content, parsed_config, result)
        
        assert "total_lines" in result.metrics
        assert "non_empty_lines" in result.metrics
        assert "character_count" in result.metrics
        assert "word_count" in result.metrics
        assert "max_line_length" in result.metrics
        assert "avg_line_length" in result.metrics
        assert "file_hash" in result.metrics
        
        assert result.metrics["character_count"] == len(content)
        assert result.metrics["total_lines"] > 0
        
    def test_nested_structure_metrics(self):
        """Test metrics calculation for nested structures."""
        analyzer = ConfigurationAnalyzer()
        content = """
        {
            "database": {
                "host": "localhost",
                "port": 5432,
                "users": [
                    {"name": "admin", "role": "admin"},
                    {"name": "user", "role": "user"}
                ]
            }
        }
        """
        
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=len(content),
            issues=[],
            metrics={},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.0
        )
        
        parsed_config = json.loads(content)
        analyzer._calculate_metrics(content, parsed_config, result)
        
        assert "total_keys" in result.metrics
        assert "nesting_depth" in result.metrics
        assert "unique_keys" in result.metrics
        
        assert result.metrics["total_keys"] > 0
        assert result.metrics["nesting_depth"] > 1
        
    def test_count_keys_functionality(self):
        """Test key counting functionality."""
        analyzer = ConfigurationAnalyzer()
        
        simple_config = {"key1": "value1", "key2": "value2"}
        assert analyzer._count_keys(simple_config) == 2
        
        nested_config = {
            "level1": {
                "key1": "value1",
                "key2": "value2"
            },
            "level2": "value"
        }
        assert analyzer._count_keys(nested_config) == 4  # level1, level2, key1, key2
        
        array_config = {"items": [{"nested": "value"}]}
        assert analyzer._count_keys(array_config) == 2  # items, nested


class TestFileAnalysis:
    """Test complete file analysis functionality."""
    
    def test_analyze_valid_json_file(self):
        """Test analysis of a valid JSON configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"app": {"name": "test", "version": "1.0"}}, f)
            temp_path = f.name
        
        try:
            analyzer = ConfigurationAnalyzer()
            result = analyzer.analyze_file(temp_path)
            
            assert result.file_path == temp_path
            assert result.config_type == ConfigType.JSON
            assert result.is_valid is True
            assert result.size_bytes > 0
            assert result.analysis_time > 0
            assert isinstance(result.metrics, dict)
            assert isinstance(result.issues, list)
            assert isinstance(result.recommendations, list)
            
        finally:
            os.unlink(temp_path)
            
    def test_analyze_invalid_json_file(self):
        """Test analysis of an invalid JSON configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON
            temp_path = f.name
        
        try:
            analyzer = ConfigurationAnalyzer()
            result = analyzer.analyze_file(temp_path)
            
            assert result.is_valid is False
            assert any(issue.category == "syntax" for issue in result.issues)
            assert result.security_score < 100
            
        finally:
            os.unlink(temp_path)
            
    def test_analyze_nonexistent_file(self):
        """Test analysis of non-existent file."""
        analyzer = ConfigurationAnalyzer()
        
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_file("nonexistent_file.json")
            
    def test_analyze_file_with_security_issues(self):
        """Test analysis of file with security issues."""
        config_data = {
            "database": {
                "host": "localhost",
                "password": "secret123",  # Security issue
                "api_key": "sk-1234567890"  # Security issue
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            analyzer = ConfigurationAnalyzer()
            result = analyzer.analyze_file(temp_path)
            
            assert result.is_valid is True
            security_issues = [issue for issue in result.issues if issue.category == "security"]
            assert len(security_issues) > 0
            assert result.security_score < 100
            
        finally:
            os.unlink(temp_path)


class TestDirectoryAnalysis:
    """Test directory analysis functionality."""
    
    def test_analyze_directory_with_configs(self):
        """Test analysis of directory containing configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test configuration files
            json_file = os.path.join(temp_dir, "app.json")
            yaml_file = os.path.join(temp_dir, "database.yaml")
            ini_file = os.path.join(temp_dir, "settings.ini")
            
            with open(json_file, 'w') as f:
                json.dump({"app": "test"}, f)
                
            with open(yaml_file, 'w') as f:
                yaml.dump({"database": {"host": "localhost"}}, f)
                
            with open(ini_file, 'w') as f:
                f.write("[section]\\nkey=value\\n")
                
            analyzer = ConfigurationAnalyzer()
            results = analyzer.analyze_directory(temp_dir, recursive=False)
            
            assert len(results) == 3
            config_types = {result.config_type for result in results}
            assert ConfigType.JSON in config_types
            assert ConfigType.YAML in config_types
            assert ConfigType.INI in config_types
            
    def test_analyze_directory_recursive(self):
        """Test recursive directory analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create subdirectory with config files
            sub_dir = os.path.join(temp_dir, "subdir")
            os.makedirs(sub_dir)
            
            json_file = os.path.join(temp_dir, "app.json")
            sub_json_file = os.path.join(sub_dir, "sub.json")
            
            with open(json_file, 'w') as f:
                json.dump({"app": "test"}, f)
                
            with open(sub_json_file, 'w') as f:
                json.dump({"sub": "test"}, f)
                
            analyzer = ConfigurationAnalyzer()
            
            # Test recursive
            results_recursive = analyzer.analyze_directory(temp_dir, recursive=True)
            assert len(results_recursive) == 2
            
            # Test non-recursive
            results_non_recursive = analyzer.analyze_directory(temp_dir, recursive=False)
            assert len(results_non_recursive) == 1
            
    def test_analyze_nonexistent_directory(self):
        """Test analysis of non-existent directory."""
        analyzer = ConfigurationAnalyzer()
        results = analyzer.analyze_directory("nonexistent_directory")
        
        assert len(results) == 0
        
    def test_analyze_directory_with_non_config_files(self):
        """Test directory analysis ignoring non-config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create non-config files
            text_file = os.path.join(temp_dir, "readme.txt")
            py_file = os.path.join(temp_dir, "script.py")
            json_file = os.path.join(temp_dir, "config.json")
            
            with open(text_file, 'w') as f:
                f.write("This is a text file")
                
            with open(py_file, 'w') as f:
                f.write("print('Hello, World!')")
                
            with open(json_file, 'w') as f:
                json.dump({"config": "data"}, f)
                
            analyzer = ConfigurationAnalyzer()
            results = analyzer.analyze_directory(temp_dir)
            
            # Should only analyze the JSON file
            assert len(results) == 1
            assert results[0].config_type == ConfigType.JSON


class TestReportGeneration:
    """Test report generation functionality."""
    
    def test_generate_text_report(self):
        """Test generation of text-based report."""
        # Create sample results
        result1 = ConfigAnalysisResult(
            file_path="test1.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=1024,
            issues=[
                ConfigIssue(
                    level=SecurityLevel.HIGH,
                    category="security",
                    message="Password exposure detected",
                    file_path="test1.json",
                    line_number=5,
                    suggestion="Use environment variables"
                )
            ],
            metrics={"total_lines": 10},
            security_score=75.0,
            recommendations=["Improve security"],
            analysis_time=0.1
        )
        
        analyzer = ConfigurationAnalyzer()
        report = analyzer.generate_report([result1], "text")
        
        assert "CONFIGURATION ANALYSIS REPORT" in report
        assert "test1.json" in report
        assert "Password exposure detected" in report
        assert "75.0/100" in report
        assert "Improve security" in report
        
    def test_generate_json_report(self):
        """Test generation of JSON report."""
        result1 = ConfigAnalysisResult(
            file_path="test1.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=1024,
            issues=[],
            metrics={"total_lines": 10},
            security_score=100.0,
            recommendations=[],
            analysis_time=0.1
        )
        
        analyzer = ConfigurationAnalyzer()
        report = analyzer.generate_report([result1], "json")
        
        report_data = json.loads(report)
        assert "metadata" in report_data
        assert "summary" in report_data
        assert "results" in report_data
        assert len(report_data["results"]) == 1
        assert report_data["results"][0]["file_path"] == "test1.json"
        
    def test_generate_html_report(self):
        """Test generation of HTML report."""
        result1 = ConfigAnalysisResult(
            file_path="test1.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=1024,
            issues=[],
            metrics={"total_lines": 10},
            security_score=100.0,
            recommendations=["Great configuration!"],
            analysis_time=0.1
        )
        
        analyzer = ConfigurationAnalyzer()
        report = analyzer.generate_report([result1], "html")
        
        assert "<!DOCTYPE html>" in report
        assert "Configuration Analysis Report" in report
        assert "test1.json" in report
        assert "Great configuration!" in report
        
    def test_generate_report_empty_results(self):
        """Test report generation with empty results."""
        analyzer = ConfigurationAnalyzer()
        
        text_report = analyzer.generate_report([], "text")
        assert "No configuration files analyzed" in text_report
        
        json_report = analyzer.generate_report([], "json")
        report_data = json.loads(json_report)
        assert report_data["summary"]["total_files"] == 0


class TestQuickFunctions:
    """Test quick utility functions."""
    
    def test_analyze_config_file_function(self):
        """Test quick analyze_config_file function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name
        
        try:
            result = analyze_config_file(temp_path)
            assert isinstance(result, ConfigAnalysisResult)
            assert result.file_path == temp_path
            assert result.config_type == ConfigType.JSON
            
        finally:
            os.unlink(temp_path)
            
    def test_analyze_config_directory_function(self):
        """Test quick analyze_config_directory function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = os.path.join(temp_dir, "test.json")
            with open(json_file, 'w') as f:
                json.dump({"test": "data"}, f)
                
            results = analyze_config_directory(temp_dir)
            assert len(results) == 1
            assert isinstance(results[0], ConfigAnalysisResult)


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""
    
    def test_empty_file_analysis(self):
        """Test analysis of empty configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name
        
        try:
            analyzer = ConfigurationAnalyzer()
            result = analyzer.analyze_file(temp_path)
            
            assert result.is_valid is False
            assert result.size_bytes == 0
            
        finally:
            os.unlink(temp_path)
            
    def test_very_large_config_content(self):
        """Test handling of very large configuration content."""
        analyzer = ConfigurationAnalyzer()
        
        # Create large nested structure
        large_config = {}
        for i in range(1000):
            large_config[f"key_{i}"] = f"value_{i}"
        
        content = json.dumps(large_config)
        result = analyzer._parse_configuration(content, ConfigType.JSON)
        
        assert result is not None
        assert len(result) == 1000
        
    def test_unicode_content_handling(self):
        """Test handling of unicode content in configurations."""
        analyzer = ConfigurationAnalyzer()
        content = '{"unicode": "こんにちは世界", "emoji": "🚀🌟"}'
        
        result = analyzer._parse_configuration(content, ConfigType.JSON)
        assert result is not None
        assert result["unicode"] == "こんにちは世界"
        assert result["emoji"] == "🚀🌟"
        
    def test_malformed_yaml_handling(self):
        """Test handling of malformed YAML content."""
        analyzer = ConfigurationAnalyzer()
        content = """
        key1: value1
        key2: [
          - item1
          - item2
        # Missing closing bracket
        """
        
        result = analyzer._parse_configuration(content, ConfigType.YAML)
        assert result is None
        
    def test_custom_logger_initialization(self):
        """Test analyzer initialization with custom logger."""
        import logging
        
        custom_logger = logging.getLogger("test_logger")
        analyzer = ConfigurationAnalyzer(logger=custom_logger)
        
        assert analyzer.logger == custom_logger
        
    def test_recommendations_generation(self):
        """Test recommendation generation based on issues."""
        analyzer = ConfigurationAnalyzer()
        
        # Create result with various issue types
        result = ConfigAnalysisResult(
            file_path="test.json",
            config_type=ConfigType.JSON,
            is_valid=True,
            size_bytes=1024,
            issues=[
                ConfigIssue(SecurityLevel.HIGH, "security", "Security issue", "test.json"),
                ConfigIssue(SecurityLevel.MEDIUM, "performance", "Performance issue", "test.json"),
                ConfigIssue(SecurityLevel.INFO, "documentation", "Documentation issue", "test.json")
            ],
            metrics={"total_lines": 10},
            security_score=60.0,
            recommendations=[],
            analysis_time=0.1
        )
        
        analyzer._generate_recommendations(result)
        
        assert len(result.recommendations) > 0
        assert any("Security" in rec for rec in result.recommendations)
        assert any("Performance" in rec for rec in result.recommendations)
        assert any("Documentation" in rec for rec in result.recommendations)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])