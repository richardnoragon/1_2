#!/usr/bin/env python3
"""
Configuration Analyzer for Richard's File Utilities

This module provides comprehensive configuration analysis capabilities, including
validation, optimization, migration, and security assessment of configuration files.
"""

import configparser
import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml


class ConfigType(Enum):
    """Supported configuration file types."""

    JSON = "json"
    YAML = "yaml"
    INI = "ini"
    XML = "xml"
    TOML = "toml"
    PROPERTIES = "properties"
    UNKNOWN = "unknown"


class SecurityLevel(Enum):
    """Configuration security levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ConfigIssue:
    """Represents a configuration issue or recommendation."""

    level: SecurityLevel
    category: str
    message: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ConfigAnalysisResult:
    """Results of configuration analysis."""

    file_path: str
    config_type: ConfigType
    is_valid: bool
    size_bytes: int
    issues: List[ConfigIssue]
    metrics: Dict[str, Any]
    security_score: float
    recommendations: List[str]
    analysis_time: float


class ConfigurationAnalyzer:
    """
    Advanced configuration file analyzer with security, performance,
    and best practices validation.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the configuration analyzer."""
        self.logger = logger or logging.getLogger(__name__)
        self.supported_extensions = {
            ".json": ConfigType.JSON,
            ".yaml": ConfigType.YAML,
            ".yml": ConfigType.YAML,
            ".ini": ConfigType.INI,
            ".cfg": ConfigType.INI,
            ".conf": ConfigType.INI,
            ".xml": ConfigType.XML,
            ".toml": ConfigType.TOML,
            ".properties": ConfigType.PROPERTIES,
            ".prop": ConfigType.PROPERTIES,
        }

        # Security patterns to detect sensitive information
        self.security_patterns = {
            "password": [
                r'password\s*[=:]\s*["\']?([^"\'\\s]+)',
                r'passwd\s*[=:]\s*["\']?([^"\'\\s]+)',
                r'pwd\s*[=:]\s*["\']?([^"\'\\s]+)',
            ],
            "api_key": [
                r'api[_-]?key\s*[=:]\s*["\']?([^"\'\\s]+)',
                r'apikey\s*[=:]\s*["\']?([^"\'\\s]+)',
                r'secret[_-]?key\s*[=:]\s*["\']?([^"\'\\s]+)',
            ],
            "token": [
                r'token\s*[=:]\s*["\']?([^"\'\\s]+)',
                r'auth[_-]?token\s*[=:]\s*["\']?([^"\'\\s]+)',
                r'access[_-]?token\s*[=:]\s*["\']?([^"\'\\s]+)',
            ],
            "private_key": [
                r'private[_-]?key\s*[=:]\s*["\']?([^"\'\\s]+)',
                r'priv[_-]?key\s*[=:]\s*["\']?([^"\'\\s]+)',
            ],
            "connection_string": [
                r'connection[_-]?string\s*[=:]\s*["\']?([^"\'\\s]+)',
                r'conn[_-]?str\s*[=:]\s*["\']?([^"\'\\s]+)',
                r'database[_-]?url\s*[=:]\s*["\']?([^"\'\\s]+)',
            ],
        }

        # Performance thresholds
        self.performance_thresholds = {
            "max_file_size_mb": 10,
            "max_nesting_depth": 10,
            "max_array_size": 1000,
            "max_string_length": 10000,
        }

    def detect_config_type(self, file_path: str) -> ConfigType:
        """Detect configuration file type based on extension and content."""
        try:
            path = Path(file_path)
            extension = path.suffix.lower()

            # Check by extension first
            if extension in self.supported_extensions:
                return self.supported_extensions[extension]

            # Try to detect by content if extension is unknown
            if path.exists():
                with open(
                    file_path, "r", encoding="utf-8", errors="ignore"
                ) as f:
                    content = f.read(1024)  # Read first 1KB

                # JSON detection
                if content.strip().startswith(("{", "[")):
                    try:
                        json.loads(content[:500])
                        return ConfigType.JSON
                    except:
                        pass

                # YAML detection
                if "---" in content or ":" in content:
                    try:
                        yaml.safe_load(content[:500])
                        return ConfigType.YAML
                    except:
                        pass

                # INI detection
                if "[" in content and "]" in content:
                    return ConfigType.INI

                # XML detection
                if content.strip().startswith("<?xml") or "<" in content:
                    return ConfigType.XML

        except Exception as e:
            self.logger.warning(
                f"Error detecting config type for {file_path}: {e}"
            )

        return ConfigType.UNKNOWN

    def analyze_file(self, file_path: str) -> ConfigAnalysisResult:
        """Perform comprehensive analysis of a configuration file."""
        start_time = time.time()

        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(
                    f"Configuration file not found: {file_path}"
                )

            # Basic file information
            file_size = path.stat().st_size
            config_type = self.detect_config_type(file_path)

            # Initialize analysis result
            result = ConfigAnalysisResult(
                file_path=file_path,
                config_type=config_type,
                is_valid=False,
                size_bytes=file_size,
                issues=[],
                metrics={},
                security_score=100.0,
                recommendations=[],
                analysis_time=0.0,
            )

            # Read and parse configuration
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Validate and parse configuration
            parsed_config = self._parse_configuration(content, config_type)
            result.is_valid = parsed_config is not None

            if not result.is_valid:
                result.issues.append(
                    ConfigIssue(
                        level=SecurityLevel.CRITICAL,
                        category="syntax",
                        message="Configuration file has invalid syntax",
                        file_path=file_path,
                    )
                )
                result.security_score -= 30
            else:
                # Perform detailed analysis
                self._analyze_security(content, parsed_config, result)
                self._analyze_performance(content, parsed_config, result)
                self._analyze_best_practices(content, parsed_config, result)
                self._calculate_metrics(content, parsed_config, result)
                self._generate_recommendations(result)

            result.analysis_time = time.time() - start_time

        except Exception as e:
            self.logger.error(
                f"Error analyzing configuration file {file_path}: {e}"
            )
            result.issues.append(
                ConfigIssue(
                    level=SecurityLevel.CRITICAL,
                    category="error",
                    message=f"Analysis failed: {str(e)}",
                    file_path=file_path,
                )
            )
            result.analysis_time = time.time() - start_time

        return result

    def _parse_configuration(
        self, content: str, config_type: ConfigType
    ) -> Optional[Any]:
        """Parse configuration content based on type."""
        try:
            if config_type == ConfigType.JSON:
                return json.loads(content)
            elif config_type == ConfigType.YAML:
                return yaml.safe_load(content)
            elif config_type == ConfigType.INI:
                parser = configparser.ConfigParser()
                parser.read_string(content)
                return {
                    section: dict(parser[section])
                    for section in parser.sections()
                }
            elif config_type == ConfigType.TOML:
                try:
                    import toml

                    return toml.loads(content)
                except ImportError:
                    self.logger.warning("TOML support requires 'toml' package")
                    return None
            elif config_type == ConfigType.PROPERTIES:
                return self._parse_properties(content)
            else:
                return {"raw_content": content}

        except Exception as e:
            self.logger.warning(
                f"Failed to parse {config_type.value} configuration: {e}"
            )
            return None

    def _parse_properties(self, content: str) -> Dict[str, str]:
        """Parse Java properties file format."""
        properties = {}
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()
        return properties

    def _analyze_security(
        self, content: str, parsed_config: Any, result: ConfigAnalysisResult
    ):
        """Analyze configuration for security issues."""
        content_lower = content.lower()

        # Check for sensitive information exposure
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_lower, re.IGNORECASE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    result.issues.append(
                        ConfigIssue(
                            level=SecurityLevel.HIGH,
                            category="security",
                            message=f"Potential {category.replace('_', ' ')} exposure detected",
                            file_path=result.file_path,
                            line_number=line_num,
                            suggestion=f"Store {category.replace('_', ' ')} in environment variables or secure vault",
                        )
                    )
                    result.security_score -= 15

        # Check for weak encryption settings
        weak_crypto_patterns = [
            r"md5",
            r"sha1(?![\d])",
            r"des",
            r"rc4",
            r"ssl\s*v?[12]",
        ]
        for pattern in weak_crypto_patterns:
            if re.search(pattern, content_lower):
                result.issues.append(
                    ConfigIssue(
                        level=SecurityLevel.HIGH,
                        category="security",
                        message="Weak cryptographic algorithm detected",
                        file_path=result.file_path,
                        suggestion="Use SHA-256 or stronger algorithms",
                    )
                )
                result.security_score -= 10

        # Check for debug/development settings in production
        debug_patterns = [
            r"debug\s*[=:]\s*true",
            r"development\s*[=:]\s*true",
            r"verbose\s*[=:]\s*true",
        ]
        for pattern in debug_patterns:
            if re.search(pattern, content_lower):
                result.issues.append(
                    ConfigIssue(
                        level=SecurityLevel.MEDIUM,
                        category="security",
                        message="Debug/development setting enabled",
                        file_path=result.file_path,
                        suggestion="Disable debug settings in production",
                    )
                )
                result.security_score -= 5

    def _analyze_performance(
        self, content: str, parsed_config: Any, result: ConfigAnalysisResult
    ):
        """Analyze configuration for performance issues."""

        # File size check
        size_mb = result.size_bytes / (1024 * 1024)
        if size_mb > self.performance_thresholds["max_file_size_mb"]:
            result.issues.append(
                ConfigIssue(
                    level=SecurityLevel.MEDIUM,
                    category="performance",
                    message=f"Large configuration file ({size_mb:.1f} MB)",
                    file_path=result.file_path,
                    suggestion="Consider splitting into smaller files",
                )
            )

        # Check nesting depth if JSON/YAML
        if isinstance(parsed_config, dict):
            max_depth = self._calculate_nesting_depth(parsed_config)
            if max_depth > self.performance_thresholds["max_nesting_depth"]:
                result.issues.append(
                    ConfigIssue(
                        level=SecurityLevel.LOW,
                        category="performance",
                        message=f"Deep nesting detected (depth: {max_depth})",
                        file_path=result.file_path,
                        suggestion="Consider flattening deeply nested structures",
                    )
                )

        # Check for very long lines
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > self.performance_thresholds["max_string_length"]:
                result.issues.append(
                    ConfigIssue(
                        level=SecurityLevel.LOW,
                        category="performance",
                        message=f"Very long line detected (line {i})",
                        file_path=result.file_path,
                        line_number=i,
                        suggestion="Break long lines for better readability",
                    )
                )
                break  # Only report first occurrence

    def _analyze_best_practices(
        self, content: str, parsed_config: Any, result: ConfigAnalysisResult
    ):
        """Analyze configuration against best practices."""

        # Check for comments/documentation
        comment_patterns = [r"#", r"//", r"/\*", r"<!--"]
        has_comments = any(
            re.search(pattern, content) for pattern in comment_patterns
        )

        if not has_comments and len(content) > 500:
            result.issues.append(
                ConfigIssue(
                    level=SecurityLevel.INFO,
                    category="documentation",
                    message="Configuration lacks comments or documentation",
                    file_path=result.file_path,
                    suggestion="Add comments to explain configuration options",
                )
            )

        # Check for hardcoded URLs/paths
        hardcoded_patterns = [
            r'[a-zA-Z]:\\\\[^\\s"\']+',  # Windows paths
            r"/[a-zA-Z0-9/_.-]+",  # Unix paths
            r'https?://[^\\s"\']+',  # URLs
            r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",  # IP addresses
        ]

        for pattern in hardcoded_patterns:
            matches = re.finditer(pattern, content)
            count = sum(1 for _ in matches)
            if count > 3:  # More than 3 hardcoded paths/URLs
                result.issues.append(
                    ConfigIssue(
                        level=SecurityLevel.LOW,
                        category="maintainability",
                        message="Multiple hardcoded paths/URLs detected",
                        file_path=result.file_path,
                        suggestion="Use environment variables or relative paths",
                    )
                )
                break

        # Check for version/schema information
        if isinstance(parsed_config, dict):
            version_keys = [
                "version",
                "schema_version",
                "api_version",
                "config_version",
            ]
            has_version = any(
                key in str(parsed_config).lower() for key in version_keys
            )

            if not has_version:
                result.issues.append(
                    ConfigIssue(
                        level=SecurityLevel.INFO,
                        category="versioning",
                        message="Configuration lacks version information",
                        file_path=result.file_path,
                        suggestion="Add version field for better configuration management",
                    )
                )

    def _calculate_nesting_depth(
        self, obj: Any, current_depth: int = 0
    ) -> int:
        """Calculate maximum nesting depth of a configuration object."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(
                self._calculate_nesting_depth(v, current_depth + 1)
                for v in obj.values()
            )
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(
                self._calculate_nesting_depth(item, current_depth + 1)
                for item in obj
            )
        else:
            return current_depth

    def _calculate_metrics(
        self, content: str, parsed_config: Any, result: ConfigAnalysisResult
    ):
        """Calculate various metrics for the configuration."""
        lines = content.split("\n")

        result.metrics = {
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": len(
                [
                    line
                    for line in lines
                    if line.strip().startswith(("#", "//", "/*"))
                ]
            ),
            "character_count": len(content),
            "word_count": len(content.split()),
            "max_line_length": (
                max(len(line) for line in lines) if lines else 0
            ),
            "avg_line_length": (
                sum(len(line) for line in lines) / len(lines) if lines else 0
            ),
            "file_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
        }

        if isinstance(parsed_config, dict):
            result.metrics.update(
                {
                    "total_keys": self._count_keys(parsed_config),
                    "nesting_depth": self._calculate_nesting_depth(
                        parsed_config
                    ),
                    "unique_keys": len(set(self._get_all_keys(parsed_config))),
                }
            )

    def _count_keys(self, obj: Any) -> int:
        """Count total number of keys in a nested structure."""
        if isinstance(obj, dict):
            return len(obj) + sum(self._count_keys(v) for v in obj.values())
        elif isinstance(obj, list):
            return sum(self._count_keys(item) for item in obj)
        return 0

    def _get_all_keys(
        self, obj: Any, keys: Optional[List[str]] = None
    ) -> List[str]:
        """Get all keys from a nested structure."""
        if keys is None:
            keys = []

        if isinstance(obj, dict):
            keys.extend(obj.keys())
            for v in obj.values():
                self._get_all_keys(v, keys)
        elif isinstance(obj, list):
            for item in obj:
                self._get_all_keys(item, keys)

        return keys

    def _generate_recommendations(self, result: ConfigAnalysisResult):
        """Generate recommendations based on analysis results."""

        # Security recommendations
        security_issues = [
            issue for issue in result.issues if issue.category == "security"
        ]
        if security_issues:
            result.recommendations.append(
                "🔒 Security: Review and secure sensitive information in configuration"
            )

        # Performance recommendations
        performance_issues = [
            issue for issue in result.issues if issue.category == "performance"
        ]
        if performance_issues:
            result.recommendations.append(
                "⚡ Performance: Optimize configuration for better loading times"
            )

        # Documentation recommendations
        doc_issues = [
            issue
            for issue in result.issues
            if issue.category == "documentation"
        ]
        if doc_issues:
            result.recommendations.append(
                "📚 Documentation: Add comments and documentation to configuration"
            )

        # General recommendations based on metrics
        if result.metrics.get("total_lines", 0) > 1000:
            result.recommendations.append(
                "📄 Structure: Consider splitting large configuration into modules"
            )

        if result.security_score < 70:
            result.recommendations.append(
                "🛡️ Security Score: Critical security improvements needed"
            )
        elif result.security_score < 85:
            result.recommendations.append(
                "🔐 Security Score: Some security improvements recommended"
            )

    def analyze_directory(
        self, directory_path: str, recursive: bool = True
    ) -> List[ConfigAnalysisResult]:
        """Analyze all configuration files in a directory."""
        results = []
        path = Path(directory_path)

        if not path.exists() or not path.is_dir():
            self.logger.error(f"Directory not found: {directory_path}")
            return results

        # Find configuration files
        pattern = "**/*" if recursive else "*"
        for file_path in path.glob(pattern):
            if file_path.is_file():
                config_type = self.detect_config_type(str(file_path))
                if config_type != ConfigType.UNKNOWN:
                    try:
                        result = self.analyze_file(str(file_path))
                        results.append(result)
                    except Exception as e:
                        self.logger.error(
                            f"Failed to analyze {file_path}: {e}"
                        )

        return results

    def generate_report(
        self, results: List[ConfigAnalysisResult], format_type: str = "text"
    ) -> str:
        """Generate analysis report in specified format."""
        if format_type.lower() == "json":
            return self._generate_json_report(results)
        elif format_type.lower() == "html":
            return self._generate_html_report(results)
        else:
            return self._generate_text_report(results)

    def _generate_text_report(
        self, results: List[ConfigAnalysisResult]
    ) -> str:
        """Generate text-based analysis report."""
        if not results:
            return "No configuration files analyzed."

        report = []
        report.append("=" * 80)
        report.append("CONFIGURATION ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Total files analyzed: {len(results)}")
        report.append(
            f"Analysis timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report.append("")

        # Summary statistics
        valid_configs = [r for r in results if r.is_valid]
        total_issues = sum(len(r.issues) for r in results)
        avg_security_score = sum(r.security_score for r in results) / len(
            results
        )

        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(
            f"Valid configurations: {len(valid_configs)}/{len(results)}"
        )
        report.append(f"Total issues found: {total_issues}")
        report.append(f"Average security score: {avg_security_score:.1f}/100")
        report.append("")

        # Detailed results
        for result in results:
            report.append(f"FILE: {result.file_path}")
            report.append(f"Type: {result.config_type.value}")
            report.append(f"Valid: {result.is_valid}")
            report.append(f"Size: {result.size_bytes:,} bytes")
            report.append(f"Security Score: {result.security_score:.1f}/100")
            report.append(f"Issues: {len(result.issues)}")

            if result.issues:
                report.append("\nISSUES:")
                for issue in result.issues:
                    prefix = (
                        "⚠️"
                        if issue.level
                        in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]
                        else "ℹ️"
                    )
                    line_info = (
                        f" (line {issue.line_number})"
                        if issue.line_number
                        else ""
                    )
                    report.append(
                        f"  {prefix} [{issue.level.value.upper()}] {issue.message}{line_info}"
                    )
                    if issue.suggestion:
                        report.append(f"      Suggestion: {issue.suggestion}")

            if result.recommendations:
                report.append("\nRECOMMENDATIONS:")
                for rec in result.recommendations:
                    report.append(f"  • {rec}")

            report.append("-" * 80)

        return "\n".join(report)

    def _generate_json_report(
        self, results: List[ConfigAnalysisResult]
    ) -> str:
        """Generate JSON analysis report."""
        report_data = {
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_files": len(results),
                "analyzer_version": "1.0.0",
            },
            "summary": {
                "valid_configurations": len(
                    [r for r in results if r.is_valid]
                ),
                "total_issues": sum(len(r.issues) for r in results),
                "average_security_score": (
                    sum(r.security_score for r in results) / len(results)
                    if results
                    else 0
                ),
            },
            "results": [],
        }

        for result in results:
            result_data = {
                "file_path": result.file_path,
                "config_type": result.config_type.value,
                "is_valid": result.is_valid,
                "size_bytes": result.size_bytes,
                "security_score": result.security_score,
                "analysis_time": result.analysis_time,
                "metrics": result.metrics,
                "issues": [
                    {
                        "level": issue.level.value,
                        "category": issue.category,
                        "message": issue.message,
                        "line_number": issue.line_number,
                        "suggestion": issue.suggestion,
                    }
                    for issue in result.issues
                ],
                "recommendations": result.recommendations,
            }
            report_data["results"].append(result_data)

        return json.dumps(report_data, indent=2)

    def _generate_html_report(
        self, results: List[ConfigAnalysisResult]
    ) -> str:
        """Generate HTML analysis report."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Configuration Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
                .summary { background: #e8f4fd; padding: 15px; margin: 20px 0; border-radius: 5px; }
                .file-result { border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 5px; }
                .issues { background: #fff2e8; padding: 10px; margin: 10px 0; border-radius: 3px; }
                .recommendations { background: #e8f5e8; padding: 10px; margin: 10px 0; border-radius: 3px; }
                .critical { color: #d32f2f; }
                .high { color: #f57c00; }
                .medium { color: #fbc02d; }
                .low { color: #388e3c; }
                .info { color: #1976d2; }
            </style>
        </head>
        <body>
        """

        html += f"""
        <div class="header">
            <h1>Configuration Analysis Report</h1>
            <p><strong>Generated:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Files Analyzed:</strong> {len(results)}</p>
        </div>
        """

        if results:
            valid_configs = len([r for r in results if r.is_valid])
            total_issues = sum(len(r.issues) for r in results)
            avg_security_score = sum(r.security_score for r in results) / len(
                results
            )

            html += f"""
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Valid Configurations:</strong> {valid_configs}/{len(results)}</p>
                <p><strong>Total Issues:</strong> {total_issues}</p>
                <p><strong>Average Security Score:</strong> {avg_security_score:.1f}/100</p>
            </div>
            """

            for result in results:
                html += f"""
                <div class="file-result">
                    <h3>{result.file_path}</h3>
                    <p><strong>Type:</strong> {result.config_type.value}</p>
                    <p><strong>Valid:</strong> {result.is_valid}</p>
                    <p><strong>Size:</strong> {result.size_bytes:,} bytes</p>
                    <p><strong>Security Score:</strong> {result.security_score:.1f}/100</p>
                """

                if result.issues:
                    html += '<div class="issues"><h4>Issues:</h4><ul>'
                    for issue in result.issues:
                        line_info = (
                            f" (line {issue.line_number})"
                            if issue.line_number
                            else ""
                        )
                        html += f'<li class="{issue.level.value}">[{issue.level.value.upper()}] {issue.message}{line_info}'
                        if issue.suggestion:
                            html += (
                                f"<br><em>Suggestion: {issue.suggestion}</em>"
                            )
                        html += "</li>"
                    html += "</ul></div>"

                if result.recommendations:
                    html += '<div class="recommendations"><h4>Recommendations:</h4><ul>'
                    for rec in result.recommendations:
                        html += f"<li>{rec}</li>"
                    html += "</ul></div>"

                html += "</div>"

        html += """
        </body>
        </html>
        """

        return html


# For backward compatibility and easy imports
import time


def analyze_config_file(file_path: str) -> ConfigAnalysisResult:
    """Quick function to analyze a single configuration file."""
    analyzer = ConfigurationAnalyzer()
    return analyzer.analyze_file(file_path)


def analyze_config_directory(
    directory_path: str, recursive: bool = True
) -> List[ConfigAnalysisResult]:
    """Quick function to analyze all configuration files in a directory."""
    analyzer = ConfigurationAnalyzer()
    return analyzer.analyze_directory(directory_path, recursive)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python config_analyzer.py <file_or_directory> [output_format]"
        )
        print("Output formats: text (default), json, html")
        sys.exit(1)

    target_path = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "text"

    analyzer = ConfigurationAnalyzer()

    if os.path.isfile(target_path):
        results = [analyzer.analyze_file(target_path)]
    elif os.path.isdir(target_path):
        results = analyzer.analyze_directory(target_path)
    else:
        print(f"Error: {target_path} is not a valid file or directory")
        sys.exit(1)

    report = analyzer.generate_report(results, output_format)
    print(report)
