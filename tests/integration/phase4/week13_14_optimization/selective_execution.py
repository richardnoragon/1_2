"""
Selective Test Execution System - Phase 4 Week 13-14
Intelligent test selection based on code changes and impact analysis

Features:
- Git-based change detection
- Impact analysis for test selection
- Dependency mapping between code and tests
- Smart test filtering and prioritization
- Change-driven test execution optimization
"""

import json
import os
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import git


@dataclass
class CodeChange:
    """Represents a code change for impact analysis"""

    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    lines_added: int
    lines_deleted: int
    impact_score: float


@dataclass
class TestImpactAnalysis:
    """Analysis of how code changes impact specific tests"""

    test_file: str
    impact_score: float
    impact_reasons: List[str]
    priority: str  # 'high', 'medium', 'low'
    should_run: bool


class SelectiveTestExecutor:
    """Intelligent selective test execution system"""

    def __init__(self, base_path: str = None, repo_path: str = None):
        self.base_path = (
            Path(base_path)
            if base_path
            else Path(__file__).parent.parent.parent
        )
        self.repo_path = (
            Path(repo_path) if repo_path else self.base_path.parent.parent
        )

        # Test-to-code mapping database
        self.test_mappings = {}
        self.dependency_graph = defaultdict(set)
        self.impact_cache = {}

        # Configure impact scoring weights
        self.impact_weights = {
            "direct_import": 0.9,
            "indirect_dependency": 0.6,
            "file_pattern_match": 0.7,
            "test_category_match": 0.5,
            "recent_changes": 0.3,
            "historical_failures": 0.4,
        }

        self._initialize_test_mappings()

    def _initialize_test_mappings(self):
        """Initialize mappings between tests and source code"""
        # Phase 2 test mappings
        self.test_mappings.update(
            {
                "test_database_integration.py": {
                    "source_patterns": [
                        "src/rfu/core/",
                        "src/utilities/*/core/",
                    ],
                    "dependencies": ["sqlite3", "database"],
                    "categories": ["database", "core"],
                },
                "test_file_operations_integration.py": {
                    "source_patterns": [
                        "src/utilities/file_operations/",
                        "src/rfu/core/file_ops/",
                    ],
                    "dependencies": ["file_ops", "utilities"],
                    "categories": ["file_operations", "utilities"],
                },
                "test_gui_integration.py": {
                    "source_patterns": ["src/rfu/gui/", "gui/"],
                    "dependencies": ["tkinter", "gui"],
                    "categories": ["gui", "interface"],
                },
                "test_external_service_integration.py": {
                    "source_patterns": [
                        "src/utilities/network/",
                        "src/utilities/*/network/",
                    ],
                    "dependencies": ["network", "api"],
                    "categories": ["network", "external"],
                },
            }
        )

        # Phase 3 test mappings
        self.test_mappings.update(
            {
                "test_user_journey_complete.py": {
                    "source_patterns": ["src/rfu/", "src/utilities/", "gui/"],
                    "dependencies": ["hub", "tools", "workflow"],
                    "categories": ["e2e", "workflow", "integration"],
                },
                "test_application_lifecycle.py": {
                    "source_patterns": ["src/rfu/hub/", "src/rfu/core/"],
                    "dependencies": ["hub", "lifecycle"],
                    "categories": ["lifecycle", "startup"],
                },
                "test_performance_benchmarks.py": {
                    "source_patterns": ["src/rfu/", "src/utilities/"],
                    "dependencies": ["performance", "benchmarks"],
                    "categories": ["performance", "benchmarks"],
                },
                "test_security_validation.py": {
                    "source_patterns": [
                        "src/utilities/security/",
                        "src/rfu/core/",
                    ],
                    "dependencies": ["security", "encryption"],
                    "categories": ["security", "validation"],
                },
            }
        )

    def detect_code_changes(
        self, base_commit: str = "HEAD~1", target_commit: str = "HEAD"
    ) -> List[CodeChange]:
        """Detect code changes between commits"""
        try:
            repo = git.Repo(self.repo_path)

            # Get diff between commits
            diff = repo.commit(base_commit).diff(repo.commit(target_commit))

            changes = []

            for diff_item in diff:
                # Determine change type
                if diff_item.new_file:
                    change_type = "added"
                elif diff_item.deleted_file:
                    change_type = "deleted"
                else:
                    change_type = "modified"

                # Get file path
                file_path = diff_item.a_path or diff_item.b_path

                # Calculate change metrics
                lines_added = (
                    diff_item.diff.count("\n+") if diff_item.diff else 0
                )
                lines_deleted = (
                    diff_item.diff.count("\n-") if diff_item.diff else 0
                )

                # Calculate initial impact score
                impact_score = self._calculate_change_impact_score(
                    file_path, change_type, lines_added, lines_deleted
                )

                change = CodeChange(
                    file_path=file_path,
                    change_type=change_type,
                    lines_added=lines_added,
                    lines_deleted=lines_deleted,
                    impact_score=impact_score,
                )

                changes.append(change)

            return changes

        except Exception as e:
            print(f"⚠️ Git change detection failed: {e}")
            return self._fallback_change_detection()

    def _calculate_change_impact_score(
        self,
        file_path: str,
        change_type: str,
        lines_added: int,
        lines_deleted: int,
    ) -> float:
        """Calculate impact score for a code change"""
        base_score = 0.5

        # File type impact
        if file_path.endswith(".py"):
            base_score += 0.3
        elif file_path.endswith((".yaml", ".yml", ".json")):
            base_score += 0.2
        elif file_path.endswith(".md"):
            base_score += 0.1

        # Change type impact
        if change_type == "added":
            base_score += 0.2
        elif change_type == "deleted":
            base_score += 0.4
        elif change_type == "modified":
            base_score += 0.3

        # Change size impact
        total_changes = lines_added + lines_deleted
        if total_changes > 100:
            base_score += 0.3
        elif total_changes > 50:
            base_score += 0.2
        elif total_changes > 10:
            base_score += 0.1

        # Critical path impact
        critical_patterns = ["core/", "hub/", "main.py", "__init__.py"]
        if any(pattern in file_path for pattern in critical_patterns):
            base_score += 0.4

        return min(1.0, base_score)

    def _fallback_change_detection(self) -> List[CodeChange]:
        """Fallback change detection when Git is not available"""
        print("Using fallback change detection (recent file modifications)")

        changes = []
        current_time = time.time()

        # Look for recently modified Python files
        for root, dirs, files in os.walk(self.repo_path / "src"):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    try:
                        mod_time = file_path.stat().st_mtime
                        if (
                            current_time - mod_time < 86400
                        ):  # Modified in last 24 hours
                            relative_path = str(
                                file_path.relative_to(self.repo_path)
                            )

                            change = CodeChange(
                                file_path=relative_path,
                                change_type="modified",
                                lines_added=10,  # Estimate
                                lines_deleted=5,  # Estimate
                                impact_score=0.5,
                            )
                            changes.append(change)
                    except Exception:
                        continue

        return changes

    def analyze_test_impact(
        self, changes: List[CodeChange]
    ) -> List[TestImpactAnalysis]:
        """Analyze which tests should run based on code changes"""
        impact_analyses = []

        # Get all available test files
        all_test_files = list(self.test_mappings.keys())

        for test_file in all_test_files:
            impact_analysis = self._calculate_test_impact(test_file, changes)
            impact_analyses.append(impact_analysis)

        # Sort by impact score (highest first)
        impact_analyses.sort(key=lambda x: x.impact_score, reverse=True)

        return impact_analyses

    def _calculate_test_impact(
        self, test_file: str, changes: List[CodeChange]
    ) -> TestImpactAnalysis:
        """Calculate impact score for a specific test based on changes"""
        test_config = self.test_mappings.get(test_file, {})

        total_impact = 0.0
        impact_reasons = []

        for change in changes:
            change_impact = 0.0

            # Check direct pattern matches
            source_patterns = test_config.get("source_patterns", [])
            for pattern in source_patterns:
                if pattern in change.file_path:
                    change_impact += (
                        change.impact_score
                        * self.impact_weights["direct_import"]
                    )
                    impact_reasons.append(f"Direct pattern match: {pattern}")
                    break

            # Check dependency matches
            dependencies = test_config.get("dependencies", [])
            for dependency in dependencies:
                if dependency.lower() in change.file_path.lower():
                    change_impact += (
                        change.impact_score
                        * self.impact_weights["indirect_dependency"]
                    )
                    impact_reasons.append(f"Dependency match: {dependency}")

            # Check category matches
            categories = test_config.get("categories", [])
            for category in categories:
                if category.lower() in change.file_path.lower():
                    change_impact += (
                        change.impact_score
                        * self.impact_weights["test_category_match"]
                    )
                    impact_reasons.append(f"Category match: {category}")

            total_impact += change_impact

        # Normalize impact score
        normalized_impact = min(1.0, total_impact)

        # Determine priority and execution decision
        if normalized_impact >= 0.7:
            priority = "high"
            should_run = True
        elif normalized_impact >= 0.4:
            priority = "medium"
            should_run = True
        elif normalized_impact >= 0.1:
            priority = "low"
            should_run = False  # Skip low-impact tests for efficiency
        else:
            priority = "minimal"
            should_run = False

        return TestImpactAnalysis(
            test_file=test_file,
            impact_score=normalized_impact,
            impact_reasons=impact_reasons,
            priority=priority,
            should_run=should_run,
        )

    def select_tests_for_execution(
        self,
        base_commit: str = "HEAD~1",
        target_commit: str = "HEAD",
        force_critical: bool = True,
    ) -> Dict:
        """Select tests for execution based on code changes"""
        print("🔍 Analyzing code changes for selective test execution...")

        start_time = time.time()

        # Detect changes
        changes = self.detect_code_changes(base_commit, target_commit)

        # Analyze test impact
        impact_analyses = self.analyze_test_impact(changes)

        # Filter tests to run
        tests_to_run = [
            analysis.test_file
            for analysis in impact_analyses
            if analysis.should_run
        ]

        # Always include critical tests if requested
        if force_critical:
            critical_tests = [
                "test_user_journey_complete.py",
                "test_application_lifecycle.py",
            ]
            for critical_test in critical_tests:
                if critical_test not in tests_to_run:
                    tests_to_run.append(critical_test)

        analysis_time = time.time() - start_time

        selection_result = {
            "analysis_timestamp": datetime.now().isoformat(),
            "base_commit": base_commit,
            "target_commit": target_commit,
            "total_changes": len(changes),
            "total_available_tests": len(impact_analyses),
            "tests_selected": len(tests_to_run),
            "selection_ratio": len(tests_to_run)
            / max(len(impact_analyses), 1),
            "analysis_duration": analysis_time,
            "code_changes": [
                {
                    "file_path": change.file_path,
                    "change_type": change.change_type,
                    "impact_score": change.impact_score,
                    "lines_changed": change.lines_added + change.lines_deleted,
                }
                for change in changes
            ],
            "test_impact_analysis": [
                {
                    "test_file": analysis.test_file,
                    "impact_score": analysis.impact_score,
                    "priority": analysis.priority,
                    "should_run": analysis.should_run,
                    "impact_reasons": analysis.impact_reasons,
                }
                for analysis in impact_analyses
            ],
            "selected_tests": tests_to_run,
            "optimization_metrics": {
                "tests_skipped": len(impact_analyses) - len(tests_to_run),
                "estimated_time_savings": self._estimate_time_savings(
                    len(impact_analyses) - len(tests_to_run)
                ),
                "selection_efficiency": len(tests_to_run)
                / max(len(impact_analyses), 1),
            },
        }

        return selection_result

    def _estimate_time_savings(self, tests_skipped: int) -> float:
        """Estimate time savings from skipping tests"""
        # Assume average test execution time of 30 seconds
        avg_test_time = 30.0
        return tests_skipped * avg_test_time

    def create_test_dependency_mapping(self) -> Dict:
        """Create comprehensive test-to-code dependency mapping"""
        print("🔗 Creating test dependency mapping...")

        mapping_start = time.time()
        dependency_mapping = {
            "creation_timestamp": datetime.now().isoformat(),
            "mappings": {},
            "statistics": {},
            "coverage_analysis": {},
        }

        for test_file, config in self.test_mappings.items():
            # Analyze test file to extract actual imports and dependencies
            test_path = self._find_test_file_path(test_file)

            if test_path and test_path.exists():
                actual_dependencies = self._analyze_test_dependencies(
                    test_path
                )

                # Combine configured and actual dependencies
                combined_mapping = {
                    "configured_patterns": config.get("source_patterns", []),
                    "configured_dependencies": config.get("dependencies", []),
                    "configured_categories": config.get("categories", []),
                    "actual_imports": actual_dependencies.get("imports", []),
                    "actual_file_references": actual_dependencies.get(
                        "file_refs", []
                    ),
                    "dependency_confidence": self._calculate_dependency_confidence(
                        config, actual_dependencies
                    ),
                }

                dependency_mapping["mappings"][test_file] = combined_mapping

        # Calculate mapping statistics
        total_mappings = len(dependency_mapping["mappings"])
        high_confidence = sum(
            1
            for mapping in dependency_mapping["mappings"].values()
            if mapping["dependency_confidence"] > 0.7
        )

        dependency_mapping["statistics"] = {
            "total_test_files": total_mappings,
            "high_confidence_mappings": high_confidence,
            "mapping_confidence_avg": sum(
                mapping["dependency_confidence"]
                for mapping in dependency_mapping["mappings"].values()
            )
            / max(total_mappings, 1),
            "analysis_duration": time.time() - mapping_start,
        }

        return dependency_mapping

    def _find_test_file_path(self, test_file: str) -> Optional[Path]:
        """Find the actual path to a test file"""
        # Search in phase directories
        search_paths = [
            self.base_path / "phase2" / "week5_6_component_tests",
            self.base_path / "phase2" / "week7_8_cross_component_tests",
            self.base_path / "phase3" / "week9_10_e2e_workflows",
            self.base_path / "phase3" / "week11_12_performance_security",
        ]

        for search_path in search_paths:
            test_path = search_path / test_file
            if test_path.exists():
                return test_path

        return None

    def _analyze_test_dependencies(self, test_path: Path) -> Dict:
        """Analyze actual dependencies in a test file"""
        try:
            with open(test_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract imports
            imports = []
            file_references = []

            for line in content.split("\n"):
                line_stripped = line.strip()

                # Import statements
                if line_stripped.startswith(("import ", "from ")):
                    imports.append(line_stripped)

                # File path references
                if any(
                    pattern in line_stripped
                    for pattern in ["src/", "gui/", "core/", "utilities/"]
                ):
                    file_references.append(line_stripped)

            return {
                "imports": imports,
                "file_refs": file_references,
                "total_lines": len(content.split("\n")),
                "import_count": len(imports),
            }

        except Exception:
            return {
                "imports": [],
                "file_refs": [],
                "total_lines": 0,
                "import_count": 0,
            }

    def _calculate_dependency_confidence(
        self, config: Dict, actual_deps: Dict
    ) -> float:
        """Calculate confidence level in dependency mapping"""
        confidence = 0.5  # Base confidence

        # Boost confidence if actual imports match configured patterns
        actual_imports = actual_deps.get("imports", [])
        configured_deps = config.get("dependencies", [])

        import_matches = sum(
            1
            for dep in configured_deps
            if any(dep.lower() in imp.lower() for imp in actual_imports)
        )

        if configured_deps:
            import_confidence = import_matches / len(configured_deps)
            confidence += import_confidence * 0.3

        # File reference confidence
        file_refs = actual_deps.get("file_refs", [])
        source_patterns = config.get("source_patterns", [])

        pattern_matches = sum(
            1
            for pattern in source_patterns
            if any(pattern in ref for ref in file_refs)
        )

        if source_patterns:
            pattern_confidence = pattern_matches / len(source_patterns)
            confidence += pattern_confidence * 0.2

        return min(1.0, confidence)

    def generate_selective_execution_plan(
        self,
        base_commit: str = "HEAD~1",
        optimization_target: str = "balanced",
    ) -> Dict:
        """Generate optimized selective execution plan"""
        print("📋 Generating selective execution plan...")

        # Get test selection
        selection_result = self.select_tests_for_execution(base_commit)

        # Apply optimization target
        if optimization_target == "aggressive":
            # Only run high priority tests
            filtered_tests = [
                analysis["test_file"]
                for analysis in selection_result["test_impact_analysis"]
                if analysis["priority"] == "high"
            ]
        elif optimization_target == "conservative":
            # Run high and medium priority tests
            filtered_tests = [
                analysis["test_file"]
                for analysis in selection_result["test_impact_analysis"]
                if analysis["priority"] in ["high", "medium"]
            ]
        else:  # balanced
            filtered_tests = selection_result["selected_tests"]

        execution_plan = {
            "plan_timestamp": datetime.now().isoformat(),
            "optimization_target": optimization_target,
            "base_commit": base_commit,
            "selection_analysis": selection_result,
            "filtered_test_files": filtered_tests,
            "execution_strategy": "selective_optimized",
            "estimated_execution_time": len(filtered_tests)
            * 30,  # 30s per test
            "optimization_summary": {
                "total_available_tests": selection_result[
                    "total_available_tests"
                ],
                "tests_after_selection": len(filtered_tests),
                "reduction_percentage": (
                    (
                        selection_result["total_available_tests"]
                        - len(filtered_tests)
                    )
                    / max(selection_result["total_available_tests"], 1)
                )
                * 100,
                "estimated_time_savings": selection_result[
                    "optimization_metrics"
                ]["estimated_time_savings"],
            },
        }

        return execution_plan

    def execute_selective_tests(self, execution_plan: Dict) -> Dict:
        """Execute tests based on selective execution plan"""
        test_files = execution_plan["filtered_test_files"]

        if not test_files:
            return {
                "status": "NO_TESTS_SELECTED",
                "message": "No tests selected for execution based on code changes",
                "execution_time": 0,
            }

        print(f"🚀 Executing {len(test_files)} selected tests...")

        execution_start = time.time()
        results = {
            "execution_type": "selective",
            "plan_used": execution_plan,
            "test_results": {},
            "execution_summary": {
                "total_tests": len(test_files),
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
            },
        }

        # Execute each selected test
        for test_file in test_files:
            test_result = self._execute_single_test(test_file)
            results["test_results"][test_file] = test_result

            if test_result.get("success", False):
                results["execution_summary"]["passed_tests"] += 1
            else:
                results["execution_summary"]["failed_tests"] += 1

        execution_time = time.time() - execution_start
        results["execution_summary"]["total_execution_time"] = execution_time

        # Calculate effectiveness metrics
        results["effectiveness_metrics"] = {
            "execution_time": execution_time,
            "time_per_test": execution_time / max(len(test_files), 1),
            "success_rate": (
                results["execution_summary"]["passed_tests"]
                / max(len(test_files), 1)
            ),
            "optimization_effective": execution_time
            < execution_plan["estimated_execution_time"],
        }

        print(f"✅ Selective execution completed in {execution_time:.2f}s")
        print(
            f"📊 Success rate: {results['effectiveness_metrics']['success_rate']:.1%}"
        )

        return results

    def _execute_single_test(self, test_file: str) -> Dict:
        """Execute a single test file"""
        test_path = self._find_test_file_path(test_file)

        if not test_path or not test_path.exists():
            return {
                "success": False,
                "error": f"Test file not found: {test_file}",
                "duration": 0,
            }

        try:
            start_time = time.time()

            cmd = [
                "python",
                "-m",
                "pytest",
                str(test_path),
                "--tb=short",
                "--quiet",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(self.base_path.parent),
            )

            duration = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "duration": duration,
                "stdout": result.stdout[:500],  # Truncate output
                "stderr": result.stderr[:500],  # Truncate errors
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test execution timed out",
                "duration": 300,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "duration": 0}


def run_selective_test_execution(
    base_commit: str = "HEAD~1",
    optimization_target: str = "balanced",
    force_critical: bool = True,
) -> Dict:
    """Main function for selective test execution"""
    executor = SelectiveTestExecutor()

    print("🎯 Starting selective test execution analysis...")

    # Generate execution plan
    execution_plan = executor.generate_selective_execution_plan(
        base_commit, optimization_target
    )

    print(f"📋 Execution plan generated:")
    print(
        f"  - Total available tests: {execution_plan['optimization_summary']['total_available_tests']}"
    )
    print(
        f"  - Tests selected: {execution_plan['optimization_summary']['tests_after_selection']}"
    )
    print(
        f"  - Reduction: {execution_plan['optimization_summary']['reduction_percentage']:.1f}%"
    )
    print(
        f"  - Estimated time savings: {execution_plan['optimization_summary']['estimated_time_savings']:.0f}s"
    )

    # Execute selective tests
    execution_result = executor.execute_selective_tests(execution_plan)

    return {
        "selective_execution_plan": execution_plan,
        "execution_results": execution_result,
        "summary": {
            "optimization_effective": execution_result[
                "effectiveness_metrics"
            ]["optimization_effective"],
            "time_savings_achieved": execution_plan["optimization_summary"][
                "estimated_time_savings"
            ],
            "success_rate": execution_result["effectiveness_metrics"][
                "success_rate"
            ],
        },
    }


if __name__ == "__main__":
    # Example usage for selective test execution
    result = run_selective_test_execution(
        base_commit="HEAD~1", optimization_target="balanced"
    )

    print("\nSelective Test Execution Results:")
    print(
        f"- Optimization Effective: {result['summary']['optimization_effective']}"
    )
    print(f"- Time Savings: {result['summary']['time_savings_achieved']:.0f}s")
    print(f"- Success Rate: {result['summary']['success_rate']:.1%}")
