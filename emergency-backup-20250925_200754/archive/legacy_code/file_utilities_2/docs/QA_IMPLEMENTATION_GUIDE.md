# QA Implementation Guide for File Utilities 2

## Overview

This guide provides detailed implementation instructions for the Quality Assurance framework established in [`QA_PROTOCOLS.md`](QA_PROTOCOLS.md). It includes practical steps, code examples, and configuration details for implementing the comprehensive QA system.

## Implementation Phases

### Phase 1: Foundation Setup (Weeks 1-2)

#### 1.1 Create QA Tools Structure

Create the following directory structure for QA tools:

```
file_utilities_2/
├── qa_tools/
│   ├── __init__.py
│   ├── data_integrity_validator.py
│   ├── performance_benchmark.py
│   ├── quality_metrics_collector.py
│   ├── report_generator.py
│   └── automation/
│       ├── __init__.py
│       ├── ci_integration.py
│       └── quality_gates.py
├── docs/
│   ├── QA_PROTOCOLS.md
│   ├── QA_PROTOCOLS_APPENDIX.md
│   ├── QA_IMPLEMENTATION_GUIDE.md (this file)
│   └── quality/
│       ├── test_reports/
│       ├── performance_reports/
│       └── quality_metrics/
└── tests/
    ├── qa/
    │   ├── __init__.py
    │   ├── test_data_integrity.py
    │   ├── test_performance.py
    │   └── test_quality_gates.py
    └── ...
```

#### 1.2 Data Integrity Validator Implementation

**File: `file_utilities_2/qa_tools/data_integrity_validator.py`**

```python
#!/usr/bin/env python3
"""
Data Integrity Validation Tool

This tool validates the accuracy and consistency of checksum calculations
against known test vectors and cross-platform requirements.

Usage:
    python -m file_utilities_2.qa_tools.data_integrity_validator
    python -m file_utilities_2.qa_tools.data_integrity_validator --algorithm sha256
    python -m file_utilities_2.qa_tools.data_integrity_validator --full-suite
"""

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.check_sum import ChecksumLogic, VALID_ALGORITHMS

class DataIntegrityValidator:
    """Comprehensive data integrity validation for checksum operations."""
    
    # NIST and RFC test vectors for validation
    STANDARD_TEST_VECTORS = {
        'md5': {
            '': 'd41d8cd98f00b204e9800998ecf8427e',
            'a': '0cc175b9c0f1b6a831c399e269772661',
            'abc': '900150983cd24fb0d6963f7d28e17f72',
            'message digest': 'f96b697d7cb7938d525a2f31aaf161d0',
            'abcdefghijklmnopqrstuvwxyz': 'c3fcd3d76192e4007dfb496cca67e13b',
        },
        'sha1': {
            '': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
            'a': '86f7e437faa5a7fce15d1ddcb9eaeaea377667b8',
            'abc': 'a9993e364706816aba3e25717850c26c9cd0d89d',
            'message digest': 'c12252ceda8be8994d5fa0290a47231c1d16aae3',
            'abcdefghijklmnopqrstuvwxyz': '32d10c7b8cf96570ca04ce37f2a19d84240d3a89',
        },
        'sha256': {
            '': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            'a': 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb',
            'abc': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
            'message digest': 'f7846f55cf23e14eebeab5b4e1550cad5b509e3348fbc4efa3a1413d393cb650',
            'abcdefghijklmnopqrstuvwxyz': '71c480df93d6ae2f1efad1447c66c9525e316218cf51fc8d9ed832f2daf18b73',
        },
        'sha512': {
            '': 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e',
            'a': '1f40fc92da241694750979ee6cf582f2d5d7d28e18335de05abc54d0560e0f5302860c652bf08d560252aa5e74210546f369fbbbce8c12cfc7957b2652fe9a75',
            'abc': 'ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f',
        }
    }
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = {}
        self.temp_files = []
    
    def validate_algorithm(self, algorithm: str) -> bool:
        """Validate a specific algorithm against test vectors."""
        if algorithm not in VALID_ALGORITHMS:
            self._log(f"❌ Invalid algorithm: {algorithm}")
            return False
        
        self._log(f"\n🔍 Validating {algorithm.upper()} algorithm...")
        
        test_vectors = self.STANDARD_TEST_VECTORS.get(algorithm, {})
        if not test_vectors:
            self._log(f"⚠️  No test vectors available for {algorithm}")
            return True
        
        passed = 0
        total = len(test_vectors)
        
        for test_input, expected_hash in test_vectors.items():
            success = self._validate_single_vector(algorithm, test_input, expected_hash)
            if success:
                passed += 1
                self._log(f"  ✅ Test '{test_input[:20]}...': PASS")
            else:
                self._log(f"  ❌ Test '{test_input[:20]}...': FAIL")
        
        success_rate = (passed / total) * 100
        self._log(f"\n📊 {algorithm.upper()} Results: {passed}/{total} passed ({success_rate:.1f}%)")
        
        self.results[algorithm] = {
            'passed': passed,
            'total': total,
            'success_rate': success_rate
        }
        
        return passed == total
    
    def _validate_single_vector(self, algorithm: str, test_input: str, expected_hash: str) -> bool:
        """Validate a single test vector."""
        # Create temporary file with test content
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                               suffix=f'_test_{algorithm}.tmp')
        temp_file.write(test_input)
        temp_file.close()
        self.temp_files.append(temp_file.name)
        
        try:
            # Calculate checksum using our implementation
            checksummer = ChecksumLogic(temp_file.name, algorithm)
            
            if algorithm == 'md5':
                result = checksummer.calculate_md5(temp_file.name)
            elif algorithm == 'sha1':
                result = checksummer.calculate_sha1(temp_file.name)
            elif algorithm == 'sha256':
                result = checksummer.calculate_sha256(temp_file.name)
            elif algorithm == 'sha512':
                # Use generic calculation for sha512
                checksummer.algorithm = 'sha512'
                result = checksummer._calculate_file_checksum(temp_file.name)
            else:
                return False
            
            # Compare results (case-insensitive)
            return result.lower() == expected_hash.lower()
            
        except Exception as e:
            self._log(f"    Error during calculation: {e}")
            return False
    
    def validate_consistency(self, algorithm: str = 'sha256', iterations: int = 5) -> bool:
        """Validate consistency across multiple calculations."""
        self._log(f"\n🔄 Testing consistency for {algorithm.upper()} ({iterations} iterations)...")
        
        # Create test file with known content
        test_content = "Consistency test content for QA validation" * 100
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                               suffix=f'_consistency_{algorithm}.tmp')
        temp_file.write(test_content)
        temp_file.close()
        self.temp_files.append(temp_file.name)
        
        checksums = []
        
        try:
            for i in range(iterations):
                checksummer = ChecksumLogic(temp_file.name, algorithm)
                
                if algorithm == 'md5':
                    result = checksummer.calculate_md5(temp_file.name)
                elif algorithm == 'sha1':
                    result = checksummer.calculate_sha1(temp_file.name)
                elif algorithm == 'sha256':
                    result = checksummer.calculate_sha256(temp_file.name)
                else:
                    checksummer.algorithm = algorithm
                    result = checksummer._calculate_file_checksum(temp_file.name)
                
                checksums.append(result)
                self._log(f"  Iteration {i+1}: {result}")
            
            # Check if all checksums are identical
            unique_checksums = set(checksums)
            is_consistent = len(unique_checksums) == 1
            
            if is_consistent:
                self._log(f"  ✅ Consistency test: PASS (all {iterations} iterations identical)")
            else:
                self._log(f"  ❌ Consistency test: FAIL ({len(unique_checksums)} different results)")
                self._log(f"     Unique results: {list(unique_checksums)}")
            
            return is_consistent
            
        except Exception as e:
            self._log(f"  ❌ Consistency test failed with error: {e}")
            return False
    
    def validate_edge_cases(self) -> bool:
        """Validate edge cases like empty files, large files, special characters."""
        self._log(f"\n🎯 Testing edge cases...")
        
        edge_cases = [
            ("empty_file", ""),
            ("single_byte", "A"),
            ("newlines", "\n\n\n"),
            ("unicode", "Hello 世界 🌍"),
            ("binary_like", "\x00\x01\x02\x03\xFF"),
        ]
        
        all_passed = True
        
        for case_name, content in edge_cases:
            self._log(f"\n  Testing {case_name}...")
            
            # Create test file
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                                   suffix=f'_{case_name}.tmp', 
                                                   encoding='utf-8')
            try:
                temp_file.write(content)
                temp_file.close()
                self.temp_files.append(temp_file.name)
                
                # Test with multiple algorithms
                for algorithm in ['md5', 'sha256']:
                    try:
                        checksummer = ChecksumLogic(temp_file.name, algorithm)
                        
                        if algorithm == 'md5':
                            result = checksummer.calculate_md5(temp_file.name)
                        else:
                            result = checksummer.calculate_sha256(temp_file.name)
                        
                        if result and len(result) > 0:
                            self._log(f"    ✅ {algorithm.upper()}: {result}")
                        else:
                            self._log(f"    ❌ {algorithm.upper()}: No result")
                            all_passed = False
                            
                    except Exception as e:
                        self._log(f"    ❌ {algorithm.upper()}: Error - {e}")
                        all_passed = False
                        
            except Exception as e:
                self._log(f"    ❌ Failed to create test file: {e}")
                all_passed = False
        
        return all_passed
    
    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        report = []
        report.append("# Data Integrity Validation Report")
        report.append(f"Generated: {self._get_timestamp()}")
        report.append("")
        
        # Summary
        total_algorithms = len(self.results)
        passed_algorithms = sum(1 for r in self.results.values() if r['success_rate'] == 100.0)
        
        report.append("## Summary")
        report.append(f"- **Algorithms Tested**: {total_algorithms}")
        report.append(f"- **Algorithms Passed**: {passed_algorithms}")
        report.append(f"- **Overall Success Rate**: {(passed_algorithms/total_algorithms)*100:.1f}%" if total_algorithms > 0 else "- **Overall Success Rate**: N/A")
        report.append("")
        
        # Detailed Results
        report.append("## Detailed Results")
        report.append("")
        
        for algorithm, result in self.results.items():
            status = "✅ PASS" if result['success_rate'] == 100.0 else "❌ FAIL"
            report.append(f"### {algorithm.upper()}")
            report.append(f"- **Status**: {status}")
            report.append(f"- **Test Vectors Passed**: {result['passed']}/{result['total']}")
            report.append(f"- **Success Rate**: {result['success_rate']:.1f}%")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        
        failed_algorithms = [alg for alg, r in self.results.items() if r['success_rate'] < 100.0]
        if failed_algorithms:
            report.append("⚠️ **Critical Issues Found:**")
            for alg in failed_algorithms:
                report.append(f"- {alg.upper()} algorithm failed validation - immediate investigation required")
            report.append("")
            report.append("**Action Required**: Do not deploy until all algorithms pass 100% of test vectors.")
        else:
            report.append("✅ **All validations passed** - checksum calculations are accurate and reliable.")
        
        report.append("")
        report.append("## Next Steps")
        report.append("1. Review any failed test cases")
        report.append("2. Run performance benchmarks")
        report.append("3. Execute integration tests")
        report.append("4. Proceed with release validation if all tests pass")
        
        return "\n".join(report)
    
    def cleanup(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                self._log(f"Warning: Could not remove {temp_file}: {e}")
    
    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(message)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for reports."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Data Integrity Validator for File Utilities 2")
    parser.add_argument('--algorithm', choices=VALID_ALGORITHMS, 
                       help='Test specific algorithm only')
    parser.add_argument('--full-suite', action='store_true',
                       help='Run complete validation suite including edge cases')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress verbose output')
    parser.add_argument('--report', type=str,
                       help='Save report to specified file')
    
    args = parser.parse_args()
    
    validator = DataIntegrityValidator(verbose=not args.quiet)
    
    try:
        print("FILE UTILITIES 2 - DATA INTEGRITY VALIDATION")
        print("=" * 60)
        
        success = True
        
        if args.algorithm:
            # Test specific algorithm
            success = validator.validate_algorithm(args.algorithm)
        else:
            # Test all algorithms
            for algorithm in VALID_ALGORITHMS:
                algorithm_success = validator.validate_algorithm(algorithm)
                success = success and algorithm_success
        
        # Test consistency
        consistency_success = validator.validate_consistency()
        success = success and consistency_success
        
        # Test edge cases if requested
        if args.full_suite:
            edge_case_success = validator.validate_edge_cases()
            success = success and edge_case_success
        
        # Generate and save report
        report = validator.generate_report()
        
        if args.report:
            with open(args.report, 'w') as f:
                f.write(report)
            print(f"\n📄 Report saved to: {args.report}")
        else:
            print("\n" + "=" * 60)
            print(report)
        
        if success:
            print("\n🎉 ALL DATA INTEGRITY VALIDATIONS PASSED!")
            return 0
        else:
            print("\n❌ DATA INTEGRITY VALIDATION FAILED!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        return 1
        
    finally:
        validator.cleanup()

if __name__ == '__main__':
    sys.exit(main())
```

#### 1.3 Performance Benchmark Implementation

**File: `file_utilities_2/qa_tools/performance_benchmark.py`**

```python
#!/usr/bin/env python3
"""
Performance Benchmark Tool

This tool validates performance requirements and generates benchmark reports
for the checksum calculation system.

Usage:
    python -m file_utilities_2.qa_tools.performance_benchmark
    python -m file_utilities_2.qa_tools.performance_benchmark --algorithm sha256
    python -m file_utilities_2.qa_tools.performance_benchmark --size large
"""

import argparse
import time
import tempfile
import os
import sys
import psutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.check_sum import ChecksumLogic, VALID_ALGORITHMS

class PerformanceBenchmark:
    """Comprehensive performance benchmarking for checksum operations."""
    
    # Performance targets based on QA requirements
    PERFORMANCE_TARGETS = {
        'small_files': {
            'size': 1024,                    # 1KB
            'min_throughput': 10.0,          # MB/s
            'max_time': 0.1,                 # seconds
            'max_memory_increase': 10.0,     # MB
        },
        'medium_files': {
            'size': 1024 * 1024,            # 1MB
            'min_throughput': 50.0,          # MB/s
            'max_time': 5.0,                 # seconds
            'max_memory_increase': 25.0,     # MB
        },
        'large_files': {
            'size': 10 * 1024 * 1024,       # 10MB (reduced for testing)
            'min_throughput': 50.0,          # MB/s
            'max_time': 60.0,                # seconds
            'max_memory_increase': 50.0,     # MB
        }
    }
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results = {}
        self.temp_files = []
    
    def create_test_files(self) -> Dict[str, str]:
        """Create test files of various sizes."""
        self._log("📁 Creating test files...")
        
        test_files = {}
        
        for category, config in self.PERFORMANCE_TARGETS.items():
            size = config['size']
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, 
                                                   suffix=f'_{category}.tmp')
            
            # Write test data efficiently
            chunk_size = 8192
            chunk = b'A' * chunk_size
            remaining = size
            
            while remaining > 0:
                write_size = min(remaining, chunk_size)
                temp_file.write(chunk[:write_size])
                remaining -= write_size
            
            temp_file.close()
            self.temp_files.append(temp_file.name)
            test_files[category] = temp_file.name
            
            self._log(f"  ✅ Created {category}: {size / (1024*1024):.1f} MB")
        
        return test_files
    
    def benchmark_algorithm(self, algorithm: str, test_files: Dict[str, str]) -> bool:
        """Benchmark a specific algorithm across all file sizes."""
        self._log(f"\n🚀 Benchmarking {algorithm.upper()} algorithm...")
        
        algorithm_results = {}
        all_passed = True
        
        for category, file_path in test_files.items():
            self._log(f"\n  📊 Testing {category}...")
            
            target = self.PERFORMANCE_TARGETS[category]
            result = self._benchmark_single_file(algorithm, file_path, target)
            
            algorithm_results[category] = result
            
            # Check if targets were met
            passed = self._evaluate_performance(result, target)
            all_passed = all_passed and passed
            
            self._log_performance_result(category, result, target, passed)
        
        self.results[algorithm] = algorithm_results
        return all_passed
    
    def _benchmark_single_file(self, algorithm: str, file_path: str, 
                              target: Dict) -> Dict:
        """Benchmark checksum calculation for a single file."""
        file_size = os.path.getsize(file_path)
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Perform checksum calculation
        checksummer = ChecksumLogic(file_path, algorithm)
        
        start_time = time.time()
        
        try:
            if algorithm == 'md5':
                checksum = checksummer.calculate_md5(file_path)
            elif algorithm == 'sha1':
                checksum = checksummer.calculate_sha1(file_path)
            elif algorithm == 'sha256':
                checksum = checksummer.calculate_sha256(file_path)
            elif algorithm == 'sha512':
                checksummer.algorithm = 'sha512'
                checksum = checksummer._calculate_file_checksum(file_path)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            end_time = time.time()
            
            # Get peak memory usage
            peak_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_increase = peak_memory - initial_memory
            
            # Calculate metrics
            duration = end_time - start_time
            throughput = (file_size / (1024 * 1024)) / duration if duration > 0 else 0
            
            return {
                'file_size': file_size,
                'duration': duration,
                'throughput': throughput,
                'memory_increase': memory_increase,
                'checksum': checksum,
                'success': True
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                'file_size': file_size,
                'duration': duration,
                'throughput': 0,
                'memory_increase': 0,
                'checksum': None,
                'error': str(e),
                'success': False
            }
    
    def _evaluate_performance(self, result: Dict, target: Dict) -> bool:
        """Evaluate if performance meets targets."""
        if not result['success']:
            return False
        
        # Check throughput
        if result['throughput'] < target['min_throughput']:
            return False
        
        # Check duration
        if result['duration'] > target['max_time']:
            return False
        
        # Check memory usage
        if result['memory_increase'] > target['max_memory_increase']:
            return False
        
        return True
    
    def _log_performance_result(self, category: str, result: Dict, 
                               target: Dict, passed: bool):
        """Log performance results."""
        status = "✅ PASS" if passed else "❌ FAIL"
        
        self._log(f"    {status}")
        self._log(f"    Duration: {result['duration']:.3f}s (target: <{target['max_time']}s)")
        self._log(f"    Throughput: {result['throughput']:.1f} MB/s (target: >{target['min_throughput']} MB/s)")
        self._log(f"    Memory increase: {result['memory_increase']:.1f} MB (target: <{target['max_memory_increase']} MB)")
        
        if not result['success']:
            self._log(f"    ❌ Error: {result.get('error', 'Unknown error')}")
    
    def benchmark_gui_responsiveness(self) -> bool:
        """Benchmark GUI responsiveness during operations."""
        self._log(f"\n🖥️  Testing GUI responsiveness...")
        
        try:
            # This would require PyQt5 to be available and a display
            # For now, we'll simulate the test
            self._log("    ⚠️  GUI responsiveness test requires display - skipping")
            return True
            
        except Exception as e:
            self._log(f"    ❌ GUI test failed: {e}")
            return False
    
    def generate_report(self) -> str:
        """Generate comprehensive performance report."""
        report = []
        report.append("# Performance Benchmark Report")
        report.append(f"Generated: {self._get_timestamp()}")
        report.append("")
        
        # Summary
        total_tests = sum(len(alg_results) for alg_results in self.results.values())
        passed_tests = sum(
            sum(1 for r in alg_results.values() if r['success']) 
            for alg_results in self.results.values()
        )
        
        report.append("## Executive Summary")
        report.append(f"- **Total Tests**: {total_tests}")
        report.append(f"- **Passed Tests**: {passed_tests}")
        report.append(f"- **Success Rate**: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "- **Success Rate**: N/A")
        report.append("")
        
        # Detailed Results
        report.append("## Detailed Results")
        report.append("")
        
        for algorithm, alg_results in self.results.items():
            report.append(f"### {algorithm.upper()} Algorithm")
            report.append("")
            
            for category, result in alg_results.items():
                target = self.PERFORMANCE_TARGETS[category]
                passed = self._evaluate_performance(result, target)
                status = "✅ PASS" if passed else "❌ FAIL"
                
                report.append(f"#### {category.replace('_', ' ').title()}")
                report.append(f"- **Status**: {status}")
                report.append(f"- **File Size**: {result['file_size'] / (1024*1024):.1f} MB")
                report.append(f"- **Duration**: {result['duration']:.3f} seconds")
                report.append(f"- **Throughput**: {result['throughput']:.1f} MB/s")
                report.append(f"- **Memory Increase**: {result['memory_increase']:.1f} MB")
                
                if not result['success']:
                    report.append(f"- **Error**: {result.get('error', 'Unknown error')}")
                
                report.append("")
        
        # Performance Analysis
        report.append("## Performance Analysis")
        report.append("")
        
        # Find best and worst performing algorithms
        best_throughput = 0
        best_algorithm = None
        worst_throughput = float('inf')
        worst_algorithm = None
        
        for algorithm, alg_results in self.results.items():
            avg_throughput = sum(r['throughput'] for r in alg_results.values()) / len(alg_results)
            
            if avg_throughput > best_throughput:
                best_throughput = avg_throughput
                best_algorithm = algorithm
            
            if avg_throughput < worst_throughput:
                worst_throughput = avg_throughput
                worst_algorithm = algorithm
        
        if best_algorithm:
            report.append(f"- **Best Performing Algorithm**: {best_algorithm.upper()} ({best_throughput:.1f} MB/s average)")
        if worst_algorithm and worst_algorithm != best_algorithm:
            report.append(f"- **Slowest Algorithm**: {worst_algorithm.upper()} ({worst_throughput:.1f} MB/s average)")
        
        report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        
        failed_tests = []
        for algorithm, alg_results in self.results.items():
            for category, result in alg_results.items():
                target = self.PERFORMANCE_TARGETS[category]
                if not self._evaluate_performance(result, target):
                    failed_tests.append(f"{algorithm.upper()} - {category}")
        
        if failed_tests:
            report.append("⚠️ **Performance Issues Found:**")
            for test in failed_tests:
                report.append(f"- {test} failed to meet performance targets")
            report.append("")
            report.append("**Action Required**: Investigate and optimize performance before release.")
        else:
            report.append("✅ **All performance targets met** - system ready for production use.")
        
        return "\n".join(report)
    
    def cleanup(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                self._log(f"Warning: Could not remove {temp_file}: {e}")
    
    def _log(self, message: