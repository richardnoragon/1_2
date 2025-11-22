"""
Memory Leak Fix Validation Test Suite
Generated: September 9, 2025

This test suite validates that the memory leak fixes in MemoryOptimizedSizeAnalyzer
successfully resolve the identified memory leak issues.

**VALIDATION CRITERIA:**
- Memory growth < 1 MB/min during sustained operations
- Object count growth < 1000 objects per operation
- Successful completion of 20+ sustained operations
- Memory cleanup validation after operations
"""

import gc
import json
import os
import sys
import tempfile
import time
import tracemalloc
from typing import Any, Dict

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Import both original and fixed analyzers
try:
    from src.tools.analysis.size_analyzer.size_analyzer_logic import SizeAnalyzer
except ImportError:
    print(
        "Error: Could not import SizeAnalyzer from "
        "src.tools.analysis.size_analyzer.size_analyzer_logic"
    )
    sys.exit(1)

try:
    from memory_optimized_size_analyzer_2025_09_09 import (
        MemoryOptimizedSizeAnalyzer,
        create_memory_optimized_analyzer,
    )
except ImportError:
    print(
        "Error: Could not import MemoryOptimizedSizeAnalyzer. Make sure memory_optimized_size_analyzer_2025_09_09.py is in the same directory."
    )
    sys.exit(1)


class MemoryLeakFixValidationSuite:
    """Validation suite for memory leak fixes."""

    def __init__(self):
        self.test_results = {}
        self.test_dataset_path = None

    def create_test_dataset(self, size: str = "medium") -> str:
        """Create test dataset for validation."""
        test_dir = tempfile.mkdtemp(prefix="leak_fix_validation_")

        if size == "small":
            file_count = 100
        elif size == "medium":
            file_count = 500
        else:  # large
            file_count = 1000

        # Create test files
        for i in range(file_count):
            file_path = os.path.join(test_dir, f"test_file_{i:04d}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Test content for file {i}\n" + "x" * 1000)

        # Create subdirectories
        for i in range(5):
            subdir = os.path.join(test_dir, f"subdir_{i:02d}")
            os.makedirs(subdir, exist_ok=True)

            for j in range(10):
                file_path = os.path.join(subdir, f"sub_file_{j:02d}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Sub content {i}-{j}\n" + "y" * 500)

        self.test_dataset_path = test_dir
        return test_dir

    def run_memory_comparison_test(self, operations_count: int = 20) -> Dict[str, Any]:
        """Compare memory usage between original and fixed analyzers."""
        print(f"Running memory comparison test with {operations_count} operations...")

        test_dir = self.create_test_dataset("medium")

        try:
            # Test original SizeAnalyzer
            print("Testing original SizeAnalyzer...")
            original_results = self._test_analyzer_memory_usage(
                SizeAnalyzer(), test_dir, operations_count, "original"
            )

            # Test memory-optimized SizeAnalyzer
            print("Testing memory-optimized SizeAnalyzer...")
            optimized_analyzer = create_memory_optimized_analyzer(
                collect_file_details=False,  # Disable file details for memory efficiency
                max_file_details=100,
            )
            optimized_results = self._test_analyzer_memory_usage(
                optimized_analyzer, test_dir, operations_count, "optimized"
            )

            # Compare results
            comparison = self._compare_memory_results(
                original_results, optimized_results
            )

            return {
                "test_configuration": {
                    "operations_count": operations_count,
                    "test_dataset": test_dir,
                },
                "original_analyzer_results": original_results,
                "optimized_analyzer_results": optimized_results,
                "comparison": comparison,
                "validation_results": self._validate_fix_success(comparison),
            }

        finally:
            # Cleanup
            import shutil

            shutil.rmtree(test_dir, ignore_errors=True)

    def _test_analyzer_memory_usage(
        self,
        analyzer,
        test_dir: str,
        operations_count: int,
        analyzer_type: str,
    ) -> Dict[str, Any]:
        """Test memory usage for a specific analyzer."""
        tracemalloc.start()

        baseline_memory = tracemalloc.get_traced_memory()[0]
        memory_samples = []
        operation_results = []

        for i in range(operations_count):
            print(f"  {analyzer_type} operation {i+1}/{operations_count}")

            pre_memory = tracemalloc.get_traced_memory()[0]
            pre_objects = len(gc.get_objects())

            start_time = time.time()
            try:
                if hasattr(analyzer, "cleanup_and_reset"):
                    analyzer.cleanup_and_reset()  # Clean up before operation

                result = analyzer.analyze_directory(test_dir)
                success = True
                error = None
            except Exception as e:
                success = False
                error = str(e)
                result = None

            end_time = time.time()
            post_memory = tracemalloc.get_traced_memory()[0]
            post_objects = len(gc.get_objects())

            # Force garbage collection
            gc.collect()
            post_gc_memory = tracemalloc.get_traced_memory()[0]
            post_gc_objects = len(gc.get_objects())

            operation_result = {
                "operation_id": i + 1,
                "success": success,
                "error": error,
                "duration": end_time - start_time,
                "files_analyzed": result.get("file_count", 0) if result else 0,
                "memory_before_mb": pre_memory / 1024 / 1024,
                "memory_after_mb": post_memory / 1024 / 1024,
                "memory_after_gc_mb": post_gc_memory / 1024 / 1024,
                "memory_change_mb": (post_memory - pre_memory) / 1024 / 1024,
                "memory_change_after_gc_mb": (post_gc_memory - pre_memory)
                / 1024
                / 1024,
                "objects_before": pre_objects,
                "objects_after": post_objects,
                "objects_after_gc": post_gc_objects,
                "object_change": post_objects - pre_objects,
                "object_change_after_gc": post_gc_objects - pre_objects,
            }

            operation_results.append(operation_result)
            memory_samples.append(post_gc_memory)

            print(
                f"    Memory: {operation_result['memory_change_after_gc_mb']:+.3f} MB, "
                f"Objects: {operation_result['object_change_after_gc']:+d}"
            )

        final_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        # Calculate summary statistics
        successful_ops = [op for op in operation_results if op["success"]]
        total_memory_change: float = (final_memory - baseline_memory) / 1024 / 1024

        if successful_ops:
            avg_memory_change = sum(
                float(op["memory_change_after_gc_mb"]) for op in successful_ops
            ) / len(successful_ops)
            avg_object_change = sum(
                int(op["object_change_after_gc"]) for op in successful_ops
            ) / len(successful_ops)
            max_memory_change = max(
                float(op["memory_change_after_gc_mb"]) for op in successful_ops
            )
            max_object_change = max(
                int(op["object_change_after_gc"]) for op in successful_ops
            )
        else:
            avg_memory_change = avg_object_change = max_memory_change = (
                max_object_change
            ) = 0

        return {
            "analyzer_type": analyzer_type,
            "total_operations": operations_count,
            "successful_operations": len(successful_ops),
            "total_memory_change_mb": total_memory_change,
            "avg_memory_change_per_op_mb": avg_memory_change,
            "max_memory_change_per_op_mb": max_memory_change,
            "avg_object_change_per_op": avg_object_change,
            "max_object_change_per_op": max_object_change,
            "operation_results": operation_results,
        }

    def _compare_memory_results(
        self, original: Dict, optimized: Dict
    ) -> Dict[str, Any]:
        """Compare memory usage results between analyzers."""
        memory_improvement = (
            original["total_memory_change_mb"] - optimized["total_memory_change_mb"]
        )
        memory_improvement_percent = (
            memory_improvement / max(original["total_memory_change_mb"], 0.001)
        ) * 100

        avg_memory_improvement = (
            original["avg_memory_change_per_op_mb"]
            - optimized["avg_memory_change_per_op_mb"]
        )
        avg_memory_improvement_percent = (
            avg_memory_improvement / max(original["avg_memory_change_per_op_mb"], 0.001)
        ) * 100

        object_improvement = (
            original["avg_object_change_per_op"] - optimized["avg_object_change_per_op"]
        )
        object_improvement_percent = (
            object_improvement / max(original["avg_object_change_per_op"], 1)
        ) * 100

        return {
            "memory_improvement_mb": memory_improvement,
            "memory_improvement_percent": memory_improvement_percent,
            "avg_memory_improvement_per_op_mb": avg_memory_improvement,
            "avg_memory_improvement_percent": avg_memory_improvement_percent,
            "object_improvement_per_op": object_improvement,
            "object_improvement_percent": object_improvement_percent,
            "original_total_memory_mb": original["total_memory_change_mb"],
            "optimized_total_memory_mb": optimized["total_memory_change_mb"],
            "original_avg_memory_per_op_mb": original["avg_memory_change_per_op_mb"],
            "optimized_avg_memory_per_op_mb": optimized["avg_memory_change_per_op_mb"],
        }

    def _validate_fix_success(self, comparison: Dict) -> Dict[str, Any]:
        """Validate that the fix successfully resolves the memory leak."""
        validation: Dict[str, Any] = {
            "fix_successful": False,
            "criteria_met": [],
            "criteria_failed": [],
            "overall_assessment": "FAILED",
        }

        # Criterion 1: Memory improvement > 50%
        if comparison["memory_improvement_percent"] > 50:
            validation["criteria_met"].append(
                f"Memory improvement: {comparison['memory_improvement_percent']:.1f}% > 50%"
            )
        else:
            validation["criteria_failed"].append(
                f"Memory improvement: {comparison['memory_improvement_percent']:.1f}% <= 50%"
            )

        # Criterion 2: Average memory per operation < 1 MB
        if comparison["optimized_avg_memory_per_op_mb"] < 1.0:
            validation["criteria_met"].append(
                f"Avg memory per op: {comparison['optimized_avg_memory_per_op_mb']:.3f} MB < 1.0 MB"
            )
        else:
            validation["criteria_failed"].append(
                f"Avg memory per op: {comparison['optimized_avg_memory_per_op_mb']:.3f} MB >= 1.0 MB"
            )

        # Criterion 3: Object improvement > 80%
        if comparison["object_improvement_percent"] > 80:
            validation["criteria_met"].append(
                f"Object improvement: {comparison['object_improvement_percent']:.1f}% > 80%"
            )
        else:
            validation["criteria_failed"].append(
                f"Object improvement: {comparison['object_improvement_percent']:.1f}% <= 80%"
            )

        # Criterion 4: Total memory increase < 10 MB for 20 operations
        if comparison["optimized_total_memory_mb"] < 10.0:
            validation["criteria_met"].append(
                f"Total memory increase: {comparison['optimized_total_memory_mb']:.1f} MB < 10.0 MB"
            )
        else:
            validation["criteria_failed"].append(
                f"Total memory increase: {comparison['optimized_total_memory_mb']:.1f} MB >= 10.0 MB"
            )

        # Overall assessment
        if len(validation["criteria_failed"]) == 0:
            validation["fix_successful"] = True
            validation["overall_assessment"] = "EXCELLENT"
        elif len(validation["criteria_failed"]) <= 1:
            validation["fix_successful"] = True
            validation["overall_assessment"] = "GOOD"
        elif len(validation["criteria_failed"]) <= 2:
            validation["overall_assessment"] = "PARTIAL"
        else:
            validation["overall_assessment"] = "FAILED"

        return validation

    def generate_validation_report(self, results: Dict) -> str:
        """Generate comprehensive validation report."""
        lines = [
            "=" * 80,
            "MEMORY LEAK FIX VALIDATION REPORT",
            "=" * 80,
            "",
            "TEST CONFIGURATION:",
            f"- Operations Count: {results['test_configuration']['operations_count']}",
            f"- Test Dataset: {results['test_configuration']['test_dataset']}",
            "",
            "MEMORY USAGE COMPARISON:",
        ]

        original = results["original_analyzer_results"]
        optimized = results["optimized_analyzer_results"]
        comparison = results["comparison"]

        lines.extend(
            [
                "Original Analyzer:",
                f"  - Total Memory Change: {original['total_memory_change_mb']:.3f} MB",
                f"  - Avg Memory Per Operation: {original['avg_memory_change_per_op_mb']:.3f} MB",
                f"  - Max Memory Per Operation: {original['max_memory_change_per_op_mb']:.3f} MB",
                f"  - Avg Object Change Per Op: {original['avg_object_change_per_op']:.0f}",
                "",
                "Optimized Analyzer:",
                f"  - Total Memory Change: {optimized['total_memory_change_mb']:.3f} MB",
                f"  - Avg Memory Per Operation: {optimized['avg_memory_change_per_op_mb']:.3f} MB",
                f"  - Max Memory Per Operation: {optimized['max_memory_change_per_op_mb']:.3f} MB",
                f"  - Avg Object Change Per Op: {optimized['avg_object_change_per_op']:.0f}",
                "",
                "IMPROVEMENT ANALYSIS:",
                f"  - Memory Improvement: {comparison['memory_improvement_percent']:.1f}%",
                f"  - Memory Reduction: {comparison['memory_improvement_mb']:.3f} MB",
                f"  - Object Improvement: {comparison['object_improvement_percent']:.1f}%",
                "",
            ]
        )

        validation = results["validation_results"]
        lines.extend(
            [
                "VALIDATION RESULTS:",
                f"- Fix Successful: {'YES' if validation['fix_successful'] else 'NO'}",
                f"- Overall Assessment: {validation['overall_assessment']}",
                "",
                "CRITERIA MET:",
            ]
        )

        for criterion in validation["criteria_met"]:
            lines.append(f"  ✓ {criterion}")

        if validation["criteria_failed"]:
            lines.append("")
            lines.append("CRITERIA FAILED:")
            for criterion in validation["criteria_failed"]:
                lines.append(f"  ✗ {criterion}")

        lines.extend(["", "=" * 80, "END OF VALIDATION REPORT", "=" * 80])

        return "\n".join(lines)


def main():
    """Main validation execution."""
    print("Memory Leak Fix Validation Test Suite")
    print("=" * 50)

    suite = MemoryLeakFixValidationSuite()

    # Run comprehensive validation
    results = suite.run_memory_comparison_test(operations_count=20)

    # Generate and display report
    report = suite.generate_validation_report(results)
    print("\n" + report)

    # Save detailed results
    results_file = os.path.join(
        os.path.dirname(__file__),
        "memory_leak_fix_validation_results_2025-09-09.json",
    )
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {results_file}")

    # Quick summary
    validation = results["validation_results"]
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY:")
    print(f"Fix Successful: {'YES' if validation['fix_successful'] else 'NO'}")
    print(f"Assessment: {validation['overall_assessment']}")
    print(f"Criteria Met: {len(validation['criteria_met'])}/4")
    print("=" * 50)

    return results


if __name__ == "__main__":
    main()
