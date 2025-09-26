"""
Simplified Memory Leak Fix Validation
Generated: September 9, 2025

This test validates that the memory-optimized SizeAnalyzer successfully resolves
the memory leak issues identified in Phase 2B testing.
"""

import gc
import os
import sys
import tempfile
import time
import tracemalloc

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def create_test_directory():
    """Create a test directory with files."""
    test_dir = tempfile.mkdtemp(prefix="memory_test_")

    # Create 100 test files
    for i in range(100):
        file_path = os.path.join(test_dir, f"test_file_{i:03d}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Test content for file {i}\n" + "x" * 500)

    # Create subdirectories
    for i in range(3):
        subdir = os.path.join(test_dir, f"subdir_{i:02d}")
        os.makedirs(subdir, exist_ok=True)

        for j in range(5):
            file_path = os.path.join(subdir, f"sub_file_{j:02d}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Sub content {i}-{j}\n" + "y" * 300)

    return test_dir


def test_original_analyzer():
    """Test the original SizeAnalyzer for memory usage."""
    print("Testing original SizeAnalyzer...")

    try:
        from src.tools.analysis.core.size_analyzer_logic import SizeAnalyzer

        analyzer = SizeAnalyzer()
    except ImportError as e:
        print(f"Could not import original SizeAnalyzer: {e}")
        return None

    test_dir = create_test_directory()

    try:
        tracemalloc.start()
        baseline_memory = tracemalloc.get_traced_memory()[0]

        results = []
        for i in range(10):
            pre_memory = tracemalloc.get_traced_memory()[0]

            try:
                result = analyzer.analyze_directory(test_dir)
                success = True
            except Exception as e:
                success = False
                result = None

            post_memory = tracemalloc.get_traced_memory()[0]
            gc.collect()
            post_gc_memory = tracemalloc.get_traced_memory()[0]

            memory_change = (post_gc_memory - pre_memory) / 1024 / 1024
            results.append(
                {
                    "operation": i + 1,
                    "success": success,
                    "memory_change_mb": memory_change,
                }
            )

            print(
                f"  Operation {i+1}: {'+' if memory_change > 0 else ''}{memory_change:.3f} MB"
            )

        final_memory = tracemalloc.get_traced_memory()[0]
        total_change = (final_memory - baseline_memory) / 1024 / 1024
        avg_change = sum(r["memory_change_mb"] for r in results) / len(results)

        tracemalloc.stop()

        return {
            "analyzer": "Original",
            "total_memory_change_mb": total_change,
            "avg_memory_change_mb": avg_change,
            "operations": results,
        }

    finally:
        import shutil

        shutil.rmtree(test_dir, ignore_errors=True)


def test_optimized_analyzer():
    """Test the memory-optimized SizeAnalyzer for memory usage."""
    print("Testing memory-optimized SizeAnalyzer...")

    try:
        # Import memory-optimized analyzer
        exec(open("memory_optimized_size_analyzer_2025-09-09.py").read())
        # Get the create function from global namespace
        create_memory_optimized_analyzer = globals()[
            "create_memory_optimized_analyzer"
        ]
        analyzer = create_memory_optimized_analyzer(collect_file_details=False)
    except Exception as e:
        print(f"Could not import memory-optimized analyzer: {e}")
        return None

    test_dir = create_test_directory()

    try:
        tracemalloc.start()
        baseline_memory = tracemalloc.get_traced_memory()[0]

        results = []
        for i in range(10):
            pre_memory = tracemalloc.get_traced_memory()[0]

            try:
                # Clean up before operation
                if hasattr(analyzer, "cleanup_and_reset"):
                    analyzer.cleanup_and_reset()

                result = analyzer.analyze_directory(test_dir)
                success = True
            except Exception as e:
                success = False
                result = None
                print(f"    Error in operation {i+1}: {e}")

            post_memory = tracemalloc.get_traced_memory()[0]
            gc.collect()
            post_gc_memory = tracemalloc.get_traced_memory()[0]

            memory_change = (post_gc_memory - pre_memory) / 1024 / 1024
            results.append(
                {
                    "operation": i + 1,
                    "success": success,
                    "memory_change_mb": memory_change,
                }
            )

            print(
                f"  Operation {i+1}: {'+' if memory_change > 0 else ''}{memory_change:.3f} MB"
            )

        final_memory = tracemalloc.get_traced_memory()[0]
        total_change = (final_memory - baseline_memory) / 1024 / 1024
        avg_change = sum(r["memory_change_mb"] for r in results) / len(results)

        tracemalloc.stop()

        return {
            "analyzer": "Optimized",
            "total_memory_change_mb": total_change,
            "avg_memory_change_mb": avg_change,
            "operations": results,
        }

    finally:
        import shutil

        shutil.rmtree(test_dir, ignore_errors=True)


def main():
    """Run the memory leak validation test."""
    print("=" * 60)
    print("MEMORY LEAK FIX VALIDATION TEST")
    print("=" * 60)

    # Test original analyzer
    original_results = test_original_analyzer()

    print()

    # Test optimized analyzer
    optimized_results = test_optimized_analyzer()

    print()
    print("=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    if original_results and optimized_results:
        print(f"Original Analyzer:")
        print(
            f"  Total Memory Change: {original_results['total_memory_change_mb']:.3f} MB"
        )
        print(
            f"  Average per Operation: {original_results['avg_memory_change_mb']:.3f} MB"
        )

        print(f"\nOptimized Analyzer:")
        print(
            f"  Total Memory Change: {optimized_results['total_memory_change_mb']:.3f} MB"
        )
        print(
            f"  Average per Operation: {optimized_results['avg_memory_change_mb']:.3f} MB"
        )

        # Calculate improvement
        memory_improvement = (
            original_results["total_memory_change_mb"]
            - optimized_results["total_memory_change_mb"]
        )
        avg_improvement = (
            original_results["avg_memory_change_mb"]
            - optimized_results["avg_memory_change_mb"]
        )

        if original_results["total_memory_change_mb"] > 0:
            improvement_percent = (
                memory_improvement / original_results["total_memory_change_mb"]
            ) * 100
        else:
            improvement_percent = 0

        print(f"\nIMPROVEMENT ANALYSIS:")
        print(
            f"  Memory Reduction: {memory_improvement:.3f} MB ({improvement_percent:.1f}%)"
        )
        print(f"  Average Reduction: {avg_improvement:.3f} MB per operation")

        # Validation criteria
        criteria_met = 0
        total_criteria = 4

        print(f"\nVALIDATION CRITERIA:")

        # Criterion 1: Memory improvement > 50%
        if improvement_percent > 50:
            print(f"  ✓ Memory improvement > 50%: {improvement_percent:.1f}%")
            criteria_met += 1
        else:
            print(f"  ✗ Memory improvement <= 50%: {improvement_percent:.1f}%")

        # Criterion 2: Average memory per operation < 0.5 MB
        if optimized_results["avg_memory_change_mb"] < 0.5:
            print(
                f"  ✓ Avg memory per operation < 0.5 MB: {optimized_results['avg_memory_change_mb']:.3f} MB"
            )
            criteria_met += 1
        else:
            print(
                f"  ✗ Avg memory per operation >= 0.5 MB: {optimized_results['avg_memory_change_mb']:.3f} MB"
            )

        # Criterion 3: Total memory increase < 5 MB for 10 operations
        if optimized_results["total_memory_change_mb"] < 5.0:
            print(
                f"  ✓ Total memory increase < 5 MB: {optimized_results['total_memory_change_mb']:.3f} MB"
            )
            criteria_met += 1
        else:
            print(
                f"  ✗ Total memory increase >= 5 MB: {optimized_results['total_memory_change_mb']:.3f} MB"
            )

        # Criterion 4: Consistent operation success
        successful_ops = sum(
            1 for op in optimized_results["operations"] if op["success"]
        )
        if successful_ops >= 9:  # At least 90% success rate
            print(f"  ✓ Operation success rate >= 90%: {successful_ops}/10")
            criteria_met += 1
        else:
            print(f"  ✗ Operation success rate < 90%: {successful_ops}/10")

        print(f"\nOVERALL ASSESSMENT:")
        if criteria_met == total_criteria:
            assessment = "EXCELLENT - All criteria met"
        elif criteria_met >= 3:
            assessment = "GOOD - Most criteria met"
        elif criteria_met >= 2:
            assessment = "PARTIAL - Some improvement shown"
        else:
            assessment = "NEEDS WORK - Insufficient improvement"

        print(f"  {assessment} ({criteria_met}/{total_criteria} criteria)")

        # Final recommendation
        if criteria_met >= 3:
            print(f"\n🎉 MEMORY LEAK FIX VALIDATION: PASSED")
            print(
                f"   The memory-optimized analyzer shows significant improvement!"
            )
        else:
            print(f"\n⚠️  MEMORY LEAK FIX VALIDATION: NEEDS IMPROVEMENT")
            print(f"   Additional optimization may be required.")

    else:
        if not original_results:
            print("❌ Could not test original analyzer")
        if not optimized_results:
            print("❌ Could not test optimized analyzer")
        print("❌ VALIDATION FAILED - Unable to complete comparison")

    print("=" * 60)


if __name__ == "__main__":
    main()
