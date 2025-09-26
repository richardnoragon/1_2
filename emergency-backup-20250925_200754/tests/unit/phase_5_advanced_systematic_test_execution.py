#!/usr/bin/env python3
"""
Phase 5: Advanced Systematic Test Execution with Comprehensive Failure Protocol

Based on comprehensive_unit_testing_execution_plan.md specifications
Created: September 9, 2025
Status: Enhanced Multi-Stage Execution Framework

Features:
- Multi-stage execution strategy with dependency mapping
- Automated pipeline with quality gates
- Comprehensive failure protocol with root cause analysis
- Real-time monitoring and reporting
- Zero-tolerance for oversimplified patterns
"""

import json
import logging
import os
import subprocess
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

# Ensure proper path configuration
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


class TestStage(Enum):
    """Test execution stages with dependency mapping"""

    IMPORT_VALIDATION = "import_validation"
    CORE_MODULES = "core_modules"
    INTEGRATION = "integration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    SYSTEM = "system"


class FailureCategory(Enum):
    """Enhanced failure categorization for root cause analysis"""

    IMPORT_DEPENDENCY = "import_dependency"
    LOGIC_ALGORITHM = "logic_algorithm"
    PERFORMANCE_RESOURCE = "performance_resource"
    SECURITY_COMPLIANCE = "security_compliance"
    INTEGRATION_COMMUNICATION = "integration_communication"
    ENVIRONMENT_CONFIGURATION = "environment_configuration"
    UNKNOWN = "unknown"


@dataclass
class TestResult:
    """Comprehensive test result tracking"""

    stage: TestStage
    test_name: str
    status: str  # PASSED, FAILED, BLOCKED, SKIPPED
    execution_time: float
    memory_usage: float
    coverage_percentage: Optional[float] = None
    failure_category: Optional[FailureCategory] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    security_issues: Optional[List[str]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.security_issues is None:
            self.security_issues = []
        if self.performance_metrics is None:
            self.performance_metrics = {}


@dataclass
class ExecutionSummary:
    """Comprehensive execution summary with quality gates"""

    total_tests: int
    passed_tests: int
    failed_tests: int
    blocked_tests: int
    skipped_tests: int
    overall_coverage: float
    execution_time: float
    memory_peak: float
    quality_gates_passed: Dict[str, bool]
    failure_breakdown: Dict[FailureCategory, int]
    performance_compliance: float
    security_score: float


class AdvancedTestExecutor:
    """Advanced systematic test execution framework"""

    def __init__(self):
        self.setup_logging()
        self.results: List[TestResult] = []
        self.start_time = datetime.now()
        self.results_dir = Path("tests/unit/results")
        self.results_dir.mkdir(exist_ok=True)

        # Quality gates thresholds (from specification)
        self.quality_gates = {
            "import_success_rate": 1.0,  # 100%
            "unit_test_success_rate": 0.95,  # 95%
            "integration_success_rate": 0.90,  # 90%
            "security_success_rate": 1.0,  # 100%
            "performance_compliance": 0.98,  # 98%
            "system_success_rate": 0.85,  # 85%
            "code_coverage_threshold": 0.85,  # 85%
        }

    def setup_logging(self):
        """Setup comprehensive logging system"""
        log_dir = Path("tests/unit/logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"phase_5_execution_{timestamp}.log"

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)
        msg = "🚀 Phase 5 Advanced Test Execution Framework Initialized"
        self.logger.info(msg)

    def classify_failure(self, error_message: str) -> FailureCategory:
        """AI-powered failure classification using pattern analysis"""
        error_lower = error_message.lower()

        # Import/Dependency patterns
        if any(
            pattern in error_lower
            for pattern in [
                "importerror",
                "modulenotfounderror",
                "no module named",
                "import failed",
                "dependency",
            ]
        ):
            return FailureCategory.IMPORT_DEPENDENCY

        # Security/Compliance patterns
        if any(
            pattern in error_lower
            for pattern in [
                "security",
                "vulnerability",
                "crypto",
                "hash",
                "encrypt",
                "permission",
                "access denied",
                "unauthorized",
            ]
        ):
            return FailureCategory.SECURITY_COMPLIANCE

        # Performance/Resource patterns
        if any(
            pattern in error_lower
            for pattern in [
                "timeout",
                "memory",
                "performance",
                "benchmark",
                "too slow",
                "resource",
                "cpu",
            ]
        ):
            return FailureCategory.PERFORMANCE_RESOURCE

        # Integration/Communication patterns
        if any(
            pattern in error_lower
            for pattern in [
                "connection",
                "network",
                "api",
                "service",
                "communication",
                "protocol",
                "socket",
            ]
        ):
            return FailureCategory.INTEGRATION_COMMUNICATION

        # Environment/Configuration patterns
        if any(
            pattern in error_lower
            for pattern in [
                "config",
                "environment",
                "path",
                "file not found",
                "permission denied",
                "invalid configuration",
            ]
        ):
            return FailureCategory.ENVIRONMENT_CONFIGURATION

        # Logic/Algorithm patterns (default for business logic issues)
        if any(
            pattern in error_lower
            for pattern in [
                "assertion",
                "expected",
                "actual",
                "logic",
                "algorithm",
                "calculation",
                "business",
            ]
        ):
            return FailureCategory.LOGIC_ALGORITHM

        return FailureCategory.UNKNOWN

    def execute_stage(
        self,
        stage: TestStage,
        test_pattern: str,
        additional_args: List[str] = None,
    ) -> List[TestResult]:
        """Execute a single test stage with comprehensive monitoring"""
        self.logger.info(f"🎯 Executing Stage: {stage.value}")

        if additional_args is None:
            additional_args = []

        # Stage-specific configurations
        stage_configs = {
            TestStage.IMPORT_VALIDATION: {
                "pattern": "tests/unit/test_import_system_fixes.py",
                "args": ["-v", "--tb=long", "--import-mode=importlib"],
                "timeout": 60,
            },
            TestStage.CORE_MODULES: {
                "pattern": "tests/unit/test_core_*.py",
                "args": [
                    "-v",
                    "--cov=src/rfu/core",
                    "--cov-report=html:results/core_coverage",
                    "--cov-report=xml:results/coverage.xml",
                    "--cov-fail-under=85",
                    "--cov-branch",
                ],
                "timeout": 300,
            },
            TestStage.INTEGRATION: {
                "pattern": "tests/unit/test_integration_*.py",
                "args": ["-v", "--maxfail=5"],
                "timeout": 600,
            },
            TestStage.SECURITY: {
                "pattern": "tests/unit/test_security_*.py",
                "args": [
                    "-v",
                    "--tb=long",
                    "--log-level=DEBUG",
                    "--capture=no",
                ],
                "timeout": 300,
            },
            TestStage.PERFORMANCE: {
                "pattern": "tests/unit/test_utilities_*.py",
                "args": [
                    "-v",
                    "--benchmark-autosave",
                    f"--benchmark-json=results/utilities_benchmarks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                ],
                "timeout": 900,
            },
            TestStage.SYSTEM: {
                "pattern": "tests/system/",
                "args": ["-v"],
                "timeout": 1200,
            },
        }

        config = stage_configs.get(
            stage,
            {"pattern": test_pattern, "args": additional_args, "timeout": 300},
        )

        # Memory monitoring setup
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()

        try:
            # Build pytest command
            cmd = ["python", "-m", "pytest", config["pattern"]] + config[
                "args"
            ]
            self.logger.info(f"📋 Command: {' '.join(cmd)}")

            # Execute with timeout and monitoring
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config["timeout"],
                cwd=str(Path.cwd()),
                env=dict(os.environ, PYTHONPATH=":".join(sys.path)),
            )

            execution_time = time.time() - start_time
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before

            # Parse pytest output for detailed results
            stage_results = self.parse_pytest_output(
                stage,
                result.stdout,
                result.stderr,
                result.returncode,
                execution_time,
                memory_used,
            )

            self.logger.info(
                f"📊 Stage {stage.value} completed: "
                f"{len([r for r in stage_results if r.status == 'PASSED'])} passed, "
                f"{len([r for r in stage_results if r.status == 'FAILED'])} failed"
            )

            return stage_results

        except subprocess.TimeoutExpired:
            self.logger.error(
                f"⏰ Stage {stage.value} timed out after {config['timeout']} seconds"
            )
            return [
                TestResult(
                    stage=stage,
                    test_name=f"{stage.value}_timeout",
                    status="BLOCKED",
                    execution_time=config["timeout"],
                    memory_usage=0,
                    failure_category=FailureCategory.PERFORMANCE_RESOURCE,
                    error_message=f"Test execution timed out after {config['timeout']} seconds",
                )
            ]

        except Exception as e:
            self.logger.error(
                f"💥 Stage {stage.value} execution failed: {str(e)}"
            )
            return [
                TestResult(
                    stage=stage,
                    test_name=f"{stage.value}_error",
                    status="BLOCKED",
                    execution_time=time.time() - start_time,
                    memory_usage=0,
                    failure_category=self.classify_failure(str(e)),
                    error_message=str(e),
                    stack_trace=traceback.format_exc(),
                )
            ]

    def parse_pytest_output(
        self,
        stage: TestStage,
        stdout: str,
        stderr: str,
        returncode: int,
        execution_time: float,
        memory_used: float,
    ) -> List[TestResult]:
        """Parse pytest output for detailed test results"""
        results = []

        # Basic parsing - in production, this would be more sophisticated
        if returncode == 0:
            # Success case
            test_count = stdout.count("PASSED") + stdout.count("passed")
            if test_count > 0:
                results.append(
                    TestResult(
                        stage=stage,
                        test_name=f"{stage.value}_suite",
                        status="PASSED",
                        execution_time=execution_time,
                        memory_usage=memory_used,
                        coverage_percentage=self.extract_coverage_from_output(
                            stdout
                        ),
                    )
                )
            else:
                # No tests found or executed
                results.append(
                    TestResult(
                        stage=stage,
                        test_name=f"{stage.value}_no_tests",
                        status="SKIPPED",
                        execution_time=execution_time,
                        memory_usage=memory_used,
                        error_message="No tests found or executed",
                    )
                )
        else:
            # Failure case
            error_lines = stderr.split("\n") if stderr else stdout.split("\n")
            error_message = "\n".join(error_lines[-10:])  # Last 10 lines

            results.append(
                TestResult(
                    stage=stage,
                    test_name=f"{stage.value}_failed",
                    status="FAILED",
                    execution_time=execution_time,
                    memory_usage=memory_used,
                    failure_category=self.classify_failure(error_message),
                    error_message=error_message,
                    stack_trace=stderr or stdout,
                )
            )

        return results

    def extract_coverage_from_output(self, output: str) -> Optional[float]:
        """Extract coverage percentage from pytest output"""
        import re

        coverage_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        if coverage_match:
            return float(coverage_match.group(1)) / 100.0
        return None

    def execute_comprehensive_validation(self) -> ExecutionSummary:
        """Execute complete Phase 5 systematic validation"""
        self.logger.info(
            "🚀 Starting Phase 5: Advanced Systematic Test Execution"
        )

        # Define execution stages in dependency order
        execution_plan = [
            (TestStage.IMPORT_VALIDATION, "Import System Validation"),
            (TestStage.CORE_MODULES, "Core Module Tests"),
            (TestStage.INTEGRATION, "Cross-Module Integration Tests"),
            (TestStage.SECURITY, "Security & Vulnerability Tests"),
            (TestStage.PERFORMANCE, "Performance & Load Tests"),
            (TestStage.SYSTEM, "End-to-End System Tests"),
        ]

        total_start_time = time.time()
        peak_memory = 0

        for stage, description in execution_plan:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🎯 Executing: {description}")
            self.logger.info(f"{'='*60}")

            # Monitor system resources
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            peak_memory = max(peak_memory, current_memory)

            stage_results = self.execute_stage(stage, "")
            self.results.extend(stage_results)

            # Check critical failure conditions
            if stage == TestStage.IMPORT_VALIDATION:
                failed_imports = [
                    r for r in stage_results if r.status == "FAILED"
                ]
                if failed_imports:
                    self.logger.critical(
                        "🚨 CRITICAL: Import validation failures detected!"
                    )
                    self.logger.critical(
                        "🚨 Zero-tolerance policy: Stopping execution"
                    )
                    break

            if stage == TestStage.SECURITY:
                failed_security = [
                    r for r in stage_results if r.status == "FAILED"
                ]
                if failed_security:
                    self.logger.critical(
                        "🚨 CRITICAL: Security test failures detected!"
                    )
                    self.logger.critical(
                        "🚨 Zero-compromise policy: Security issues must be resolved"
                    )

        total_execution_time = time.time() - total_start_time

        # Generate comprehensive summary
        summary = self.generate_execution_summary(
            total_execution_time, peak_memory
        )

        # Validate quality gates
        quality_gates_status = self.validate_quality_gates(summary)
        summary.quality_gates_passed = quality_gates_status

        # Generate comprehensive reports
        self.generate_comprehensive_reports(summary)

        return summary

    def generate_execution_summary(
        self, total_time: float, peak_memory: float
    ) -> ExecutionSummary:
        """Generate comprehensive execution summary"""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASSED"])
        failed = len([r for r in self.results if r.status == "FAILED"])
        blocked = len([r for r in self.results if r.status == "BLOCKED"])
        skipped = len([r for r in self.results if r.status == "SKIPPED"])

        # Calculate overall coverage
        coverage_results = [
            r.coverage_percentage
            for r in self.results
            if r.coverage_percentage is not None
        ]
        overall_coverage = (
            sum(coverage_results) / len(coverage_results)
            if coverage_results
            else 0.0
        )

        # Failure breakdown by category
        failure_breakdown = {}
        for category in FailureCategory:
            failure_breakdown[category] = len(
                [r for r in self.results if r.failure_category == category]
            )

        # Performance compliance calculation
        performance_results = [
            r for r in self.results if r.stage == TestStage.PERFORMANCE
        ]
        performance_compliance = 1.0  # Default if no performance tests
        if performance_results:
            passed_perf = len(
                [r for r in performance_results if r.status == "PASSED"]
            )
            performance_compliance = (
                passed_perf / len(performance_results)
                if performance_results
                else 1.0
            )

        # Security score calculation
        security_results = [
            r for r in self.results if r.stage == TestStage.SECURITY
        ]
        security_score = 1.0  # Default if no security tests
        if security_results:
            passed_sec = len(
                [r for r in security_results if r.status == "PASSED"]
            )
            security_score = (
                passed_sec / len(security_results) if security_results else 1.0
            )

        return ExecutionSummary(
            total_tests=total_tests,
            passed_tests=passed,
            failed_tests=failed,
            blocked_tests=blocked,
            skipped_tests=skipped,
            overall_coverage=overall_coverage,
            execution_time=total_time,
            memory_peak=peak_memory,
            quality_gates_passed={},  # Will be populated by validate_quality_gates
            failure_breakdown=failure_breakdown,
            performance_compliance=performance_compliance,
            security_score=security_score,
        )

    def validate_quality_gates(
        self, summary: ExecutionSummary
    ) -> Dict[str, bool]:
        """Validate all quality gates against thresholds"""
        gates = {}

        # Import success rate (zero tolerance)
        import_results = [
            r for r in self.results if r.stage == TestStage.IMPORT_VALIDATION
        ]
        import_success_rate = 1.0
        if import_results:
            passed_imports = len(
                [r for r in import_results if r.status == "PASSED"]
            )
            import_success_rate = passed_imports / len(import_results)
        gates["import_success_rate"] = (
            import_success_rate >= self.quality_gates["import_success_rate"]
        )

        # Unit test success rate
        unit_results = [
            r for r in self.results if r.stage == TestStage.CORE_MODULES
        ]
        unit_success_rate = 1.0
        if unit_results:
            passed_units = len(
                [r for r in unit_results if r.status == "PASSED"]
            )
            unit_success_rate = passed_units / len(unit_results)
        gates["unit_test_success_rate"] = (
            unit_success_rate >= self.quality_gates["unit_test_success_rate"]
        )

        # Integration success rate
        integration_results = [
            r for r in self.results if r.stage == TestStage.INTEGRATION
        ]
        integration_success_rate = 1.0
        if integration_results:
            passed_integration = len(
                [r for r in integration_results if r.status == "PASSED"]
            )
            integration_success_rate = passed_integration / len(
                integration_results
            )
        gates["integration_success_rate"] = (
            integration_success_rate
            >= self.quality_gates["integration_success_rate"]
        )

        # Security success rate (zero compromise)
        gates["security_success_rate"] = (
            summary.security_score
            >= self.quality_gates["security_success_rate"]
        )

        # Performance compliance
        gates["performance_compliance"] = (
            summary.performance_compliance
            >= self.quality_gates["performance_compliance"]
        )

        # System success rate
        system_results = [
            r for r in self.results if r.stage == TestStage.SYSTEM
        ]
        system_success_rate = 1.0
        if system_results:
            passed_system = len(
                [r for r in system_results if r.status == "PASSED"]
            )
            system_success_rate = passed_system / len(system_results)
        gates["system_success_rate"] = (
            system_success_rate >= self.quality_gates["system_success_rate"]
        )

        # Code coverage threshold
        gates["code_coverage_threshold"] = (
            summary.overall_coverage
            >= self.quality_gates["code_coverage_threshold"]
        )

        return gates

    def generate_comprehensive_reports(self, summary: ExecutionSummary):
        """Generate all required comprehensive reports"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # 1. Main execution report
        self.generate_execution_report(summary, timestamp)

        # 2. Failure analysis report
        self.generate_failure_analysis_report(timestamp)

        # 3. Performance benchmark report
        self.generate_performance_report(timestamp)

        # 4. Security assessment report
        self.generate_security_report(timestamp)

        # 5. Coverage analysis report
        self.generate_coverage_report(timestamp)

        # 6. JSON results for programmatic access
        self.generate_json_results(summary, timestamp)

    def generate_execution_report(
        self, summary: ExecutionSummary, timestamp: str
    ):
        """Generate main execution report"""
        report_path = (
            self.results_dir / f"phase_5_execution_report_{timestamp}.md"
        )

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(
                f"""# Phase 5: Advanced Systematic Test Execution Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Execution Framework:** Enhanced Multi-Stage Pipeline  
**Quality Standard:** Zero-Tolerance/Zero-Compromise  

## Executive Summary

### Test Execution Metrics
- **Total Tests Executed:** {summary.total_tests}
- **Passed:** {summary.passed_tests} ({summary.passed_tests/summary.total_tests*100:.1f}%)
- **Failed:** {summary.failed_tests} ({summary.failed_tests/summary.total_tests*100:.1f}%)
- **Blocked:** {summary.blocked_tests} ({summary.blocked_tests/summary.total_tests*100:.1f}%)
- **Skipped:** {summary.skipped_tests} ({summary.skipped_tests/summary.total_tests*100:.1f}%)

### Quality Gate Results
"""
            )

            for gate, passed in summary.quality_gates_passed.items():
                status = "✅ PASSED" if passed else "❌ FAILED"
                f.write(f"- **{gate.replace('_', ' ').title()}:** {status}\n")

            f.write(
                f"""
### Performance Metrics
- **Total Execution Time:** {summary.execution_time:.2f} seconds
- **Peak Memory Usage:** {summary.memory_peak:.2f} MB
- **Overall Code Coverage:** {summary.overall_coverage*100:.1f}%
- **Performance Compliance:** {summary.performance_compliance*100:.1f}%
- **Security Score:** {summary.security_score*100:.1f}%

### Detailed Stage Results

"""
            )

            for stage in TestStage:
                stage_results = [r for r in self.results if r.stage == stage]
                if stage_results:
                    f.write(f"#### {stage.value.replace('_', ' ').title()}\n")
                    f.write(f"- Tests: {len(stage_results)}\n")
                    f.write(
                        f"- Passed: {len([r for r in stage_results if r.status == 'PASSED'])}\n"
                    )
                    f.write(
                        f"- Failed: {len([r for r in stage_results if r.status == 'FAILED'])}\n"
                    )
                    f.write(
                        f"- Blocked: {len([r for r in stage_results if r.status == 'BLOCKED'])}\n\n"
                    )

        self.logger.info(f"📊 Execution report generated: {report_path}")

    def generate_failure_analysis_report(self, timestamp: str):
        """Generate detailed failure analysis report"""
        failed_results = [
            r for r in self.results if r.status in ["FAILED", "BLOCKED"]
        ]

        if not failed_results:
            self.logger.info("🎉 No failures to analyze - all tests passed!")
            return

        report_path = (
            self.results_dir / f"failure_analysis_report_{timestamp}.md"
        )

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(
                f"""# Failure Analysis Report - Phase 5

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Failed/Blocked Tests:** {len(failed_results)}  

## Failure Breakdown by Category

"""
            )

            for category in FailureCategory:
                category_failures = [
                    r for r in failed_results if r.failure_category == category
                ]
                if category_failures:
                    f.write(
                        f"### {category.value.replace('_', ' ').title()} ({len(category_failures)} issues)\n\n"
                    )

                    for result in category_failures:
                        f.write(f"#### {result.test_name}\n")
                        f.write(f"- **Stage:** {result.stage.value}\n")
                        f.write(f"- **Status:** {result.status}\n")
                        f.write(f"- **Error:** {result.error_message}\n")
                        if result.stack_trace:
                            f.write(
                                f"- **Stack Trace:**\n```\n{result.stack_trace[:500]}...\n```\n"
                            )
                        f.write("\n")

        self.logger.info(
            f"📋 Failure analysis report generated: {report_path}"
        )

    def generate_performance_report(self, timestamp: str):
        """Generate performance benchmark report"""
        perf_results = [
            r for r in self.results if r.stage == TestStage.PERFORMANCE
        ]

        report_path = self.results_dir / f"performance_report_{timestamp}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(
                f"""# Performance Benchmark Report - Phase 5

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Performance Tests:** {len(perf_results)}  
**Compliance Rate:** {self.get_summary().performance_compliance*100:.1f}%  

## Performance Metrics Summary

"""
            )

            if perf_results:
                total_time = sum(r.execution_time for r in perf_results)
                avg_memory = sum(r.memory_usage for r in perf_results) / len(
                    perf_results
                )

                f.write(
                    f"- **Total Performance Test Time:** {total_time:.2f} seconds\n"
                )
                f.write(f"- **Average Memory Usage:** {avg_memory:.2f} MB\n")
                f.write(
                    f"- **Benchmark Compliance:** {self.get_summary().performance_compliance*100:.1f}%\n"
                )
            else:
                f.write("- No performance tests executed\n")

        self.logger.info(f"⚡ Performance report generated: {report_path}")

    def generate_security_report(self, timestamp: str):
        """Generate security assessment report"""
        security_results = [
            r for r in self.results if r.stage == TestStage.SECURITY
        ]

        report_path = self.results_dir / f"security_report_{timestamp}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(
                f"""# Security Assessment Report - Phase 5

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Security Tests:** {len(security_results)}  
**Security Score:** {self.get_summary().security_score*100:.1f}%  
**Zero-Compromise Policy:** {'✅ ENFORCED' if self.get_summary().security_score == 1.0 else '❌ VIOLATIONS DETECTED'}

## Security Test Results

"""
            )

            if security_results:
                passed_security = len(
                    [r for r in security_results if r.status == "PASSED"]
                )
                f.write(
                    f"- **Passed Security Tests:** {passed_security}/{len(security_results)}\n"
                )
                f.write(
                    f"- **Security Compliance:** {self.get_summary().security_score*100:.1f}%\n"
                )

                failed_security = [
                    r for r in security_results if r.status == "FAILED"
                ]
                if failed_security:
                    f.write("\n### 🚨 CRITICAL SECURITY ISSUES DETECTED\n\n")
                    for result in failed_security:
                        f.write(
                            f"- **{result.test_name}:** {result.error_message}\n"
                        )
            else:
                f.write("- No security tests executed\n")

        self.logger.info(f"🔒 Security report generated: {report_path}")

    def generate_coverage_report(self, timestamp: str):
        """Generate code coverage analysis report"""
        coverage_results = [
            r for r in self.results if r.coverage_percentage is not None
        ]

        report_path = self.results_dir / f"coverage_report_{timestamp}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(
                f"""# Code Coverage Analysis Report - Phase 5

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Overall Coverage:** {self.get_summary().overall_coverage*100:.1f}%  
**Coverage Threshold:** {self.quality_gates['code_coverage_threshold']*100:.1f}%  
**Status:** {'✅ PASSED' if self.get_summary().overall_coverage >= self.quality_gates['code_coverage_threshold'] else '❌ BELOW THRESHOLD'}

## Coverage by Stage

"""
            )

            for stage in TestStage:
                stage_coverage = [
                    r for r in coverage_results if r.stage == stage
                ]
                if stage_coverage:
                    avg_coverage = sum(
                        r.coverage_percentage for r in stage_coverage
                    ) / len(stage_coverage)
                    f.write(
                        f"- **{stage.value.replace('_', ' ').title()}:** {avg_coverage*100:.1f}%\n"
                    )

        self.logger.info(f"📈 Coverage report generated: {report_path}")

    def generate_json_results(self, summary: ExecutionSummary, timestamp: str):
        """Generate JSON results for programmatic access"""
        json_path = self.results_dir / f"phase_5_results_{timestamp}.json"

        results_data = {
            "execution_summary": asdict(summary),
            "detailed_results": [asdict(result) for result in self.results],
            "quality_gates": self.quality_gates,
            "execution_metadata": {
                "timestamp": timestamp,
                "framework_version": "Phase 5 Advanced",
                "total_execution_time": summary.execution_time,
                "peak_memory": summary.memory_peak,
            },
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results_data, f, indent=2, default=str)

        self.logger.info(f"📋 JSON results generated: {json_path}")

    def get_summary(self) -> ExecutionSummary:
        """Get current execution summary"""
        return self.generate_execution_summary(
            0, 0
        )  # Placeholder for dynamic access


def main():
    """Main execution function for Phase 5 systematic validation"""
    print("🚀 Phase 5: Advanced Systematic Test Execution Framework")
    print("=" * 60)

    executor = AdvancedTestExecutor()

    try:
        summary = executor.execute_comprehensive_validation()

        print("\n🎉 Phase 5 Execution Completed!")
        print(
            f"📊 Results: {summary.passed_tests}/{summary.total_tests} tests passed"
        )
        print(
            f"⚡ Performance: {summary.execution_time:.2f}s, {summary.memory_peak:.2f}MB peak"
        )
        print(f"🔒 Security: {summary.security_score*100:.1f}% compliance")
        print(f"📈 Coverage: {summary.overall_coverage*100:.1f}%")

        # Quality gates summary
        passed_gates = sum(
            1 for passed in summary.quality_gates_passed.values() if passed
        )
        total_gates = len(summary.quality_gates_passed)
        print(f"🎯 Quality Gates: {passed_gates}/{total_gates} passed")

        if passed_gates == total_gates:
            print(
                "✅ ALL QUALITY GATES PASSED - FRAMEWORK VALIDATION SUCCESSFUL!"
            )
            return 0
        else:
            print("❌ QUALITY GATE FAILURES DETECTED - REVIEW REQUIRED")
            return 1

    except Exception as e:
        executor.logger.error(f"💥 Phase 5 execution failed: {str(e)}")
        executor.logger.error(traceback.format_exc())
        return 2


if __name__ == "__main__":
    sys.exit(main())
