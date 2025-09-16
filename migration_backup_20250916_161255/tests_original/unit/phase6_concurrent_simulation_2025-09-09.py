"""
Phase 6: Concurrent User Simulation Testing
Generated: September 9, 2025

This test simulates multiple concurrent users accessing the SizeAnalyzer simultaneously
to validate memory performance and system stability under multi-user load conditions.
Based on Phase 5 success (4.49 MB/min leak rate with 55.1% safety margin), this test
will validate production readiness under realistic concurrent usage patterns.

**VALIDATION CRITERIA:**
- Memory growth < 10 MB/min under concurrent load
- Successful completion of concurrent operations
- No resource contention issues
- Stable performance across multiple threads
"""

import gc
import json
import os
import sys
import tempfile
import threading
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import SizeAnalyzer
try:
    from src.utilities.analysis.core.size_analyzer_logic import SizeAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Error: Could not import SizeAnalyzer: {e}")
    ANALYZER_AVAILABLE = False


class Phase6ConcurrentUserSimulation:
    """Concurrent user simulation testing suite for Phase 6."""
    
    def __init__(self):
        self.test_results = {}
        self.shared_datasets = {}
        self.lock = threading.Lock()
        self.memory_samples = []
        
    def create_shared_dataset(self, dataset_id: str, size: str = "medium") -> str:
        """Create shared test dataset for concurrent access."""
        test_dir = tempfile.mkdtemp(prefix=f"phase6_concurrent_{dataset_id}_")
        
        if size == "small":
            file_count = 300
            subdir_count = 8
        elif size == "medium":
            file_count = 600
            subdir_count = 15
        else:  # large
            file_count = 1200
            subdir_count = 25
        
        print(f"Creating {size} shared dataset {dataset_id}: {file_count} files...")
        
        # Create main directory files
        for i in range(file_count):
            file_path = os.path.join(test_dir, f"shared_file_{i:05d}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                content_size = 800 + (i % 3000)  # 0.8KB to 3.8KB files
                f.write(f"Shared file {i} - dataset {dataset_id} - timestamp: {datetime.now()}\n")
                f.write("concurrent_test_data_" * (content_size // 20))
        
        # Create subdirectories
        for i in range(subdir_count):
            subdir = os.path.join(test_dir, f"shared_subdir_{i:03d}")
            os.makedirs(subdir, exist_ok=True)
            
            for j in range(25):
                file_path = os.path.join(subdir, f"concurrent_file_{j:03d}.data")
                with open(file_path, 'w', encoding='utf-8') as f:
                    content_size = 400 + (j % 1500)
                    f.write(f"Concurrent access file {i}-{j}\n")
                    f.write("multi_user_content_" * (content_size // 18))
        
        self.shared_datasets[dataset_id] = test_dir
        total_files = file_count + (subdir_count * 25)
        print(f"Created shared dataset {dataset_id} with {total_files} files at: {test_dir}")
        
        return test_dir
    
    def simulate_user_session(self, user_id: int, dataset_path: str, operations_count: int) -> Dict[str, Any]:
        """Simulate a single user session with multiple operations."""
        user_results = {
            'user_id': user_id,
            'operations': [],
            'total_duration': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'avg_operation_time': 0,
            'memory_usage': []
        }
        
        try:
            analyzer = SizeAnalyzer()
            session_start = time.time()
            
            for op_id in range(operations_count):
                operation_start = time.time()
                
                try:
                    # Simulate realistic user behavior with brief pauses
                    time.sleep(0.05 + (user_id * 0.01))  # Staggered start times
                    
                    result = analyzer.analyze_directory(dataset_path)
                    
                    operation_end = time.time()
                    operation_duration = operation_end - operation_start
                    
                    operation_result = {
                        'operation_id': op_id + 1,
                        'success': True,
                        'duration_sec': operation_duration,
                        'files_analyzed': result.get('file_count', 0) if result else 0,
                        'total_size_mb': (result.get('total_size', 0) / 1024 / 1024) if result else 0,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    user_results['successful_operations'] += 1
                    
                except Exception as e:
                    operation_end = time.time()
                    operation_duration = operation_end - operation_start
                    
                    operation_result = {
                        'operation_id': op_id + 1,
                        'success': False,
                        'duration_sec': operation_duration,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    user_results['failed_operations'] += 1
                
                user_results['operations'].append(operation_result)
                
                # Brief pause between operations
                time.sleep(0.1)
            
            session_end = time.time()
            user_results['total_duration'] = session_end - session_start
            
            if user_results['successful_operations'] > 0:
                successful_ops = [op for op in user_results['operations'] if op['success']]
                user_results['avg_operation_time'] = sum(op['duration_sec'] for op in successful_ops) / len(successful_ops)
            
        except Exception as e:
            user_results['session_error'] = str(e)
        
        return user_results
    
    def run_concurrent_simulation(self, 
                                 concurrent_users: int = 5, 
                                 operations_per_user: int = 10,
                                 dataset_size: str = "medium") -> Dict[str, Any]:
        """Run concurrent user simulation test."""
        print("=" * 80)
        print("PHASE 6: CONCURRENT USER SIMULATION")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"Operations per User: {operations_per_user}")
        print(f"Dataset Size: {dataset_size}")
        print("=" * 80)
        
        if not ANALYZER_AVAILABLE:
            return {"error": "SizeAnalyzer not available"}
        
        # Create shared datasets for concurrent access
        datasets = {}
        for i in range(min(3, concurrent_users)):  # Up to 3 shared datasets
            dataset_id = f"dataset_{i+1}"
            datasets[dataset_id] = self.create_shared_dataset(dataset_id, dataset_size)
        
        try:
            # Start memory tracking
            tracemalloc.start()
            baseline_memory = tracemalloc.get_traced_memory()[0]
            test_start_time = time.time()
            
            print(f"\nStarting {concurrent_users} concurrent user sessions...")
            
            # Execute concurrent user sessions
            user_results = []
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                # Submit all user sessions
                future_to_user = {}
                for user_id in range(concurrent_users):
                    # Distribute users across available datasets
                    dataset_key = f"dataset_{(user_id % len(datasets)) + 1}"
                    dataset_path = datasets[dataset_key]
                    
                    future = executor.submit(
                        self.simulate_user_session,
                        user_id + 1,
                        dataset_path,
                        operations_per_user
                    )
                    future_to_user[future] = user_id + 1
                
                # Collect results as they complete
                for future in as_completed(future_to_user):
                    user_id = future_to_user[future]
                    try:
                        result = future.result()
                        user_results.append(result)
                        
                        success_rate = (result['successful_operations'] / 
                                      (result['successful_operations'] + result['failed_operations'])) * 100
                        print(f"User {user_id:2d}: {result['successful_operations']}/{operations_per_user} ops "
                              f"({success_rate:.1f}%), avg: {result['avg_operation_time']:.3f}s")
                        
                    except Exception as e:
                        print(f"User {user_id:2d}: Session failed - {e}")
                        user_results.append({
                            'user_id': user_id,
                            'session_error': str(e),
                            'successful_operations': 0,
                            'failed_operations': operations_per_user
                        })
            
            # Final memory measurement
            final_memory = tracemalloc.get_traced_memory()[0]
            test_end_time = time.time()
            
            tracemalloc.stop()
            
            # Calculate comprehensive statistics
            total_duration_minutes = (test_end_time - test_start_time) / 60
            total_memory_change_mb = (final_memory - baseline_memory) / 1024 / 1024
            memory_leak_rate_mb_per_min = total_memory_change_mb / total_duration_minutes if total_duration_minutes > 0 else 0
            
            # Aggregate user statistics
            total_operations = sum(r['successful_operations'] + r['failed_operations'] for r in user_results)
            total_successful = sum(r['successful_operations'] for r in user_results)
            total_failed = sum(r['failed_operations'] for r in user_results)
            
            successful_user_results = [r for r in user_results if r['successful_operations'] > 0]
            if successful_user_results:
                avg_user_operation_time = sum(r['avg_operation_time'] for r in successful_user_results) / len(successful_user_results)
            else:
                avg_user_operation_time = 0
            
            return {
                'test_configuration': {
                    'concurrent_users': concurrent_users,
                    'operations_per_user': operations_per_user,
                    'dataset_size': dataset_size,
                    'total_duration_minutes': total_duration_minutes,
                    'datasets_used': list(datasets.keys())
                },
                'memory_analysis': {
                    'baseline_memory_mb': baseline_memory / 1024 / 1024,
                    'final_memory_mb': final_memory / 1024 / 1024,
                    'total_memory_change_mb': total_memory_change_mb,
                    'memory_leak_rate_mb_per_min': memory_leak_rate_mb_per_min
                },
                'performance_analysis': {
                    'total_operations': total_operations,
                    'successful_operations': total_successful,
                    'failed_operations': total_failed,
                    'overall_success_rate_percent': (total_successful / total_operations) * 100 if total_operations > 0 else 0,
                    'avg_operation_time_sec': avg_user_operation_time,
                    'concurrent_users_completed': len([r for r in user_results if 'session_error' not in r])
                },
                'threshold_compliance': {
                    'memory_leak_threshold_mb_per_min': 10.0,
                    'actual_leak_rate_mb_per_min': memory_leak_rate_mb_per_min,
                    'threshold_met': memory_leak_rate_mb_per_min < 10.0,
                    'safety_margin_percent': ((10.0 - memory_leak_rate_mb_per_min) / 10.0) * 100 if memory_leak_rate_mb_per_min < 10.0 else None
                },
                'detailed_user_results': user_results
            }
            
        finally:
            # Cleanup shared datasets
            import shutil
            for dataset_path in datasets.values():
                shutil.rmtree(dataset_path, ignore_errors=True)
    
    def generate_concurrent_test_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive Phase 6 concurrent test report."""
        if 'error' in results:
            return f"PHASE 6 TEST FAILED: {results['error']}"
        
        lines = [
            "=" * 100,
            "PHASE 6: CONCURRENT USER SIMULATION - COMPREHENSIVE RESULTS",
            "=" * 100,
            "",
            "TEST CONFIGURATION:",
        ]
        
        config = results['test_configuration']
        lines.extend([
            f"- Concurrent Users: {config['concurrent_users']}",
            f"- Operations per User: {config['operations_per_user']}",
            f"- Dataset Size: {config['dataset_size']}",
            f"- Total Test Duration: {config['total_duration_minutes']:.2f} minutes",
            f"- Datasets Used: {', '.join(config['datasets_used'])}",
            ""
        ])
        
        memory = results['memory_analysis']
        lines.extend([
            "MEMORY ANALYSIS RESULTS:",
            f"- Baseline Memory: {memory['baseline_memory_mb']:.3f} MB",
            f"- Final Memory: {memory['final_memory_mb']:.3f} MB",
            f"- Total Memory Change: {memory['total_memory_change_mb']:.3f} MB",
            f"- Memory Leak Rate (Concurrent): {memory['memory_leak_rate_mb_per_min']:.6f} MB/min",
            ""
        ])
        
        performance = results['performance_analysis']
        lines.extend([
            "CONCURRENT PERFORMANCE ANALYSIS:",
            f"- Total Operations Executed: {performance['total_operations']}",
            f"- Successful Operations: {performance['successful_operations']}",
            f"- Failed Operations: {performance['failed_operations']}",
            f"- Overall Success Rate: {performance['overall_success_rate_percent']:.1f}%",
            f"- Average Operation Time: {performance['avg_operation_time_sec']:.3f} seconds",
            f"- Users Completed Successfully: {performance['concurrent_users_completed']}/{config['concurrent_users']}",
            ""
        ])
        
        threshold = results['threshold_compliance']
        lines.extend([
            "THRESHOLD COMPLIANCE (CONCURRENT LOAD):",
            f"- Required Threshold: < {threshold['memory_leak_threshold_mb_per_min']:.1f} MB/min",
            f"- Actual Leak Rate: {threshold['actual_leak_rate_mb_per_min']:.6f} MB/min",
            f"- Threshold Compliance: {'✓ PASSED' if threshold['threshold_met'] else '✗ FAILED'}",
        ])
        
        if threshold['threshold_met'] and threshold['safety_margin_percent'] is not None:
            lines.append(f"- Safety Margin: {threshold['safety_margin_percent']:.1f}%")
        
        # User performance breakdown
        user_results = results['detailed_user_results']
        successful_users = [u for u in user_results if 'session_error' not in u and u['successful_operations'] > 0]
        
        if successful_users:
            lines.extend([
                "",
                "USER PERFORMANCE BREAKDOWN:",
            ])
            
            for user in successful_users[:10]:  # Show first 10 users
                success_rate = (user['successful_operations'] / 
                              (user['successful_operations'] + user['failed_operations'])) * 100
                lines.append(f"- User {user['user_id']:2d}: {user['successful_operations']} ops, "
                           f"{success_rate:.1f}% success, {user['avg_operation_time']:.3f}s avg")
        
        lines.extend([
            "",
            "CONCURRENT LOAD ASSESSMENT:",
        ])
        
        # Overall assessment
        if threshold['threshold_met'] and performance['overall_success_rate_percent'] >= 95:
            if memory['memory_leak_rate_mb_per_min'] < 2.0:
                assessment = "EXCELLENT - Production Ready for Concurrent Use"
                recommendation = "Safe for high-concurrency production deployment"
            elif memory['memory_leak_rate_mb_per_min'] < 5.0:
                assessment = "GOOD - Production Ready with Concurrent Monitoring"
                recommendation = "Suitable for production with concurrent load monitoring"
            else:
                assessment = "ACCEPTABLE - Production Ready with Concurrent Limits"
                recommendation = "Production ready but monitor concurrent resource usage"
        elif threshold['threshold_met']:
            assessment = "PARTIAL - Requires Concurrent Optimization"
            recommendation = "Memory compliant but concurrent performance needs improvement"
        else:
            assessment = "REQUIRES OPTIMIZATION"
            recommendation = "Concurrent load causes memory threshold violations"
        
        lines.extend([
            f"- Overall Assessment: {assessment}",
            f"- Recommendation: {recommendation}",
            "",
            "=" * 100,
            "END OF PHASE 6 CONCURRENT USER SIMULATION REPORT",
            "=" * 100
        ])
        
        return "\n".join(lines)


def main():
    """Execute Phase 6 concurrent user simulation testing."""
    print("Phase 6: Concurrent User Simulation Testing")
    print("=" * 50)
    
    if not ANALYZER_AVAILABLE:
        print("❌ CRITICAL ERROR: SizeAnalyzer not available for testing")
        return
    
    suite = Phase6ConcurrentUserSimulation()
    
    # Execute concurrent user simulation
    results = suite.run_concurrent_simulation(
        concurrent_users=8,      # Simulate 8 concurrent users
        operations_per_user=12,  # 12 operations per user
        dataset_size="medium"    # Medium-sized datasets
    )
    
    # Generate comprehensive report
    report = suite.generate_concurrent_test_report(results)
    print("\n" + report)
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_file = f"phase6_concurrent_simulation_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # Executive summary for decision making
    if 'threshold_compliance' in results:
        threshold_met = results['threshold_compliance']['threshold_met']
        leak_rate = results['threshold_compliance']['actual_leak_rate_mb_per_min']
        success_rate = results['performance_analysis']['overall_success_rate_percent']
        
        print("\n" + "=" * 70)
        print("PHASE 6 EXECUTIVE SUMMARY:")
        print(f"Concurrent Memory Leak Rate: {leak_rate:.6f} MB/min (Threshold: <10.0 MB/min)")
        print(f"Concurrent Success Rate: {success_rate:.1f}%")
        print(f"Threshold Compliance: {'✅ PASSED' if threshold_met else '❌ FAILED'}")
        
        if threshold_met and success_rate >= 95:
            print("🎉 PHASE 6 RESULT: CONCURRENT PRODUCTION READY")
            print("   SizeAnalyzer handles concurrent users successfully!")
        elif threshold_met:
            print("⚠️  PHASE 6 RESULT: CONCURRENT PERFORMANCE NEEDS ATTENTION")
            print("   Memory compliant but concurrent reliability could improve.")
        else:
            print("❌ PHASE 6 RESULT: CONCURRENT OPTIMIZATION REQUIRED")
            print("   Concurrent load causes memory threshold violations.")
        
        print("=" * 70)
    
    return results


if __name__ == "__main__":
    main()