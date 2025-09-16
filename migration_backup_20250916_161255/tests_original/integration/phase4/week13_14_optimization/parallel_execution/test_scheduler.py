"""
Test Scheduler - Phase 4 Week 13-14
Intelligent test scheduling and load balancing system for optimized parallel execution

Features:
- Dependency-aware test scheduling
- Resource-based load balancing
- Historical performance optimization
- Dynamic worker allocation
- Intelligent test grouping
"""

import concurrent.futures
import os
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

import psutil


@dataclass
class TestExecutionMetrics:
    """Metrics for test execution performance"""
    test_name: str
    duration: float
    memory_usage: int  # bytes
    cpu_usage: float   # percentage
    success_rate: float  # 0.0-1.0
    resource_requirements: Dict[str, float]
    dependencies: List[str]


@dataclass
class WorkerCapacity:
    """Worker capacity and current load"""
    worker_id: str
    max_cpu_cores: int
    max_memory_mb: int
    current_cpu_load: float
    current_memory_mb: int
    assigned_tests: List[str]
    estimated_completion_time: float


class TestScheduler:
    """Intelligent test scheduler for optimal parallel execution"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "test_performance_history.db"
        self.test_metrics_cache: Dict[str, TestExecutionMetrics] = {}
        self.worker_pool: List[WorkerCapacity] = []
        self.test_dependencies: Dict[str, Set[str]] = {}
        self.resource_pools = {
            'database_connections': 10,
            'temp_directories': 20,
            'network_ports': 50,
            'mock_services': 5
        }
        self._initialize_performance_database()
    
    def _initialize_performance_database(self):
        """Initialize performance tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_performance (
                    test_name TEXT PRIMARY KEY,
                    avg_duration REAL,
                    success_rate REAL,
                    memory_usage INTEGER,
                    cpu_usage REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_count INTEGER DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_dependencies (
                    test_name TEXT,
                    dependency TEXT,
                    dependency_type TEXT,
                    PRIMARY KEY (test_name, dependency)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flaky_test_tracking (
                    test_name TEXT,
                    failure_count INTEGER DEFAULT 0,
                    total_runs INTEGER DEFAULT 0,
                    failure_rate REAL DEFAULT 0.0,
                    last_failure TIMESTAMP,
                    failure_patterns TEXT,
                    remediation_attempts INTEGER DEFAULT 0
                )
            """)
    
    def analyze_test_performance(self, test_files: List[str]) -> Dict[
        str, TestExecutionMetrics]:
        """Analyze historical performance for test scheduling optimization"""
        performance_data = {}
        
        with sqlite3.connect(self.db_path) as conn:
            for test_file in test_files:
                test_name = Path(test_file).stem
                
                cursor = conn.execute("""
                    SELECT avg_duration, success_rate, memory_usage, cpu_usage
                    FROM test_performance 
                    WHERE test_name = ?
                """, (test_name,))
                
                row = cursor.fetchone()
                if row:
                    duration, success_rate, memory_usage, cpu_usage = row
                    
                    # Get dependencies
                    dep_cursor = conn.execute("""
                        SELECT dependency FROM test_dependencies 
                        WHERE test_name = ?
                    """, (test_name,))
                    dependencies = [dep[0] for dep in dep_cursor.fetchall()]
                    
                    performance_data[test_name] = TestExecutionMetrics(
                        test_name=test_name,
                        duration=duration,
                        memory_usage=memory_usage,
                        cpu_usage=cpu_usage,
                        success_rate=success_rate,
                        resource_requirements=self._estimate_resource_requirements(
                            memory_usage, cpu_usage),
                        dependencies=dependencies
                    )
                else:
                    # Default metrics for new tests
                    performance_data[test_name] = TestExecutionMetrics(
                        test_name=test_name,
                        duration=30.0,  # Conservative estimate
                        memory_usage=100 * 1024 * 1024,  # 100MB
                        cpu_usage=25.0,  # 25%
                        success_rate=1.0,
                        resource_requirements={'cpu': 0.25, 'memory': 100},
                        dependencies=[]
                    )
        
        self.test_metrics_cache = performance_data
        return performance_data
    
    def _estimate_resource_requirements(self, memory_bytes: int, cpu_percent: float) -> Dict[str, float]:
        """Estimate resource requirements for scheduling"""
        return {
            'cpu': min(cpu_percent / 100.0, 1.0),  # Normalize to 0-1
            'memory': memory_bytes / (1024 * 1024),  # MB
            'io_intensive': 0.3 if 'file' in str(memory_bytes) else 0.1,
            'network': 0.2 if 'network' in str(memory_bytes) else 0.0
        }
    
    def create_optimal_test_groups(self, test_files: List[str],
                                  max_workers: Optional[int] = None) -> List[List[str]]:
        """Create optimal test groups for parallel execution"""
        if max_workers is None:
            max_workers = max(1, psutil.cpu_count() - 1)
        
        # Analyze performance data
        performance_data = self.analyze_test_performance(test_files)
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(performance_data)
        
        # Perform topological sort for dependency ordering
        execution_order = self._topological_sort(dependency_graph)
        
        # Group tests by resource requirements and dependencies
        test_groups = self._group_tests_by_resources(
            execution_order, performance_data, max_workers)
        
        return test_groups
    
    def _build_dependency_graph(self, performance_data: Dict[
        str, TestExecutionMetrics]) -> Dict[str, Set[str]]:
        """Build test dependency graph"""
        graph = defaultdict(set)
        
        for test_name, metrics in performance_data.items():
            for dependency in metrics.dependencies:
                if dependency in performance_data:
                    graph[dependency].add(test_name)
        
        return dict(graph)
    
    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Perform topological sort for dependency-aware execution order"""
        in_degree = defaultdict(int)
        all_nodes = set()
        
        # Build in-degree map
        for node, neighbors in graph.items():
            all_nodes.add(node)
            for neighbor in neighbors:
                all_nodes.add(neighbor)
                in_degree[neighbor] += 1
        
        # Initialize queue with nodes having no dependencies
        queue = [node for node in all_nodes if in_degree[node] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Update in-degree for neighbors
            for neighbor in graph.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _group_tests_by_resources(self, ordered_tests: List[str],
                                 performance_data: Dict[
                                     str, TestExecutionMetrics],
                                 max_workers: int) -> List[List[str]]:
        """Group tests by resource requirements for optimal execution"""
        test_groups = [[] for _ in range(max_workers)]
        worker_loads = [0.0] * max_workers  # Track estimated completion time
        worker_resources = [{'cpu': 0.0, 'memory': 0.0} for _ in range(max_workers)]
        
        # System capacity
        total_cpu_cores = psutil.cpu_count()
        total_memory_mb = psutil.virtual_memory().total / (1024 * 1024)
        
        cpu_per_worker = total_cpu_cores / max_workers
        memory_per_worker = total_memory_mb / max_workers
        
        for test_name in ordered_tests:
            if test_name not in performance_data:
                continue
                
            metrics = performance_data[test_name]
            
            # Find best worker for this test
            best_worker = self._find_best_worker(
                metrics, worker_loads, worker_resources, 
                cpu_per_worker, memory_per_worker)
            
            # Assign test to worker
            test_groups[best_worker].append(test_name)
            worker_loads[best_worker] += metrics.duration
            worker_resources[best_worker]['cpu'] += metrics.resource_requirements.get('cpu', 0)
            worker_resources[best_worker]['memory'] += metrics.resource_requirements.get('memory', 0)
        
        # Remove empty groups
        return [group for group in test_groups if group]
    
    def _find_best_worker(self, metrics: TestExecutionMetrics, 
                         worker_loads: List[float],
                         worker_resources: List[Dict],
                         cpu_per_worker: float,
                         memory_per_worker: float) -> int:
        """Find the best worker for assigning a test"""
        best_worker = 0
        best_score = float('inf')
        
        for i, (load, resources) in enumerate(zip(worker_loads, worker_resources)):
            # Check resource constraints
            required_cpu = metrics.resource_requirements.get('cpu', 0)
            required_memory = metrics.resource_requirements.get('memory', 0)
            
            if (resources['cpu'] + required_cpu > cpu_per_worker * 0.8 or
                resources['memory'] + required_memory > memory_per_worker * 0.8):
                continue  # Skip overloaded workers
            
            # Calculate assignment score (lower is better)
            # Factor in current load, resource utilization, and success rate
            load_score = load + metrics.duration
            resource_score = (resources['cpu'] + required_cpu) / cpu_per_worker
            reliability_score = 1.0 - metrics.success_rate
            
            total_score = load_score + resource_score * 100 + reliability_score * 50
            
            if total_score < best_score:
                best_score = total_score
                best_worker = i
        
        return best_worker
    
    def update_test_performance_history(self, test_name: str, duration: float,
                                      success: bool, memory_usage: int = 0,
                                      cpu_usage: float = 0.0):
        """Update test performance history for future optimization"""
        with sqlite3.connect(self.db_path) as conn:
            # Check if record exists
            cursor = conn.execute("""
                SELECT avg_duration, success_rate, execution_count 
                FROM test_performance WHERE test_name = ?
            """, (test_name,))
            
            row = cursor.fetchone()
            
            if row:
                # Update existing record with exponential moving average
                old_duration, old_success_rate, execution_count = row
                alpha = 0.1  # Smoothing factor
                
                new_duration = old_duration * (1 - alpha) + duration * alpha
                new_success_rate = old_success_rate * (1 - alpha) + (1.0 if success else 0.0) * alpha
                new_execution_count = execution_count + 1
                
                conn.execute("""
                    UPDATE test_performance 
                    SET avg_duration = ?, success_rate = ?, memory_usage = ?, 
                        cpu_usage = ?, execution_count = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE test_name = ?
                """, (new_duration, new_success_rate, memory_usage, 
                     cpu_usage, new_execution_count, test_name))
            else:
                # Insert new record
                conn.execute("""
                    INSERT INTO test_performance 
                    (test_name, avg_duration, success_rate, memory_usage, cpu_usage)
                    VALUES (?, ?, ?, ?, ?)
                """, (test_name, duration, 1.0 if success else 0.0, 
                     memory_usage, cpu_usage))
    
    def identify_flaky_tests(self, failure_rate_threshold: float = 0.05) -> List[str]:
        """Identify flaky tests based on historical failure patterns"""
        flaky_tests = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT test_name, failure_count, total_runs, failure_rate 
                FROM flaky_test_tracking 
                WHERE failure_rate > ? AND total_runs >= 10
                ORDER BY failure_rate DESC
            """, (failure_rate_threshold,))
            
            flaky_tests = [row[0] for row in cursor.fetchall()]
        
        return flaky_tests
    
    def schedule_optimized_execution(self, test_files: List[str], 
                                   max_workers: int = None,
                                   priority_tests: List[str] = None) -> Dict:
        """Schedule tests for optimized parallel execution"""
        if max_workers is None:
            max_workers = max(1, psutil.cpu_count() - 1)
        
        # Analyze current system resources
        system_resources = self._get_system_resources()
        
        # Create optimal test groups
        test_groups = self.create_optimal_test_groups(test_files, max_workers)
        
        # Prioritize certain tests if specified
        if priority_tests:
            test_groups = self._prioritize_tests(test_groups, priority_tests)
        
        # Identify and handle flaky tests
        flaky_tests = self.identify_flaky_tests()
        
        execution_plan = {
            'timestamp': time.time(),
            'system_resources': system_resources,
            'max_workers': max_workers,
            'test_groups': test_groups,
            'flaky_tests': flaky_tests,
            'estimated_duration': self._estimate_total_duration(test_groups),
            'resource_allocation': self._calculate_resource_allocation(test_groups),
            'optimization_strategy': 'dependency_aware_load_balanced'
        }
        
        return execution_plan
    
    def _get_system_resources(self) -> Dict:
        """Get current system resource availability"""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_total_mb': psutil.virtual_memory().total / (1024 * 1024),
            'memory_available_mb': psutil.virtual_memory().available / (1024 * 1024),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }
    
    def _prioritize_tests(self, test_groups: List[List[str]], 
                         priority_tests: List[str]) -> List[List[str]]:
        """Reorganize test groups to prioritize certain tests"""
        # Move priority tests to front of their respective groups
        for group in test_groups:
            priority_in_group = [test for test in group if test in priority_tests]
            other_tests = [test for test in group if test not in priority_tests]
            group[:] = priority_in_group + other_tests
        
        return test_groups
    
    def _estimate_total_duration(self, test_groups: List[List[str]]) -> float:
        """Estimate total execution duration for parallel execution"""
        group_durations = []
        
        for group in test_groups:
            group_duration = 0.0
            for test_name in group:
                if test_name in self.test_metrics_cache:
                    group_duration += self.test_metrics_cache[test_name].duration
                else:
                    group_duration += 30.0  # Default estimate
            
            group_durations.append(group_duration)
        
        # Parallel execution time is the maximum group duration
        return max(group_durations) if group_durations else 0.0
    
    def _calculate_resource_allocation(self, test_groups: List[List[str]]) -> Dict:
        """Calculate resource allocation for test groups"""
        total_cpu = 0.0
        total_memory = 0.0
        
        for group in test_groups:
            group_cpu = 0.0
            group_memory = 0.0
            
            for test_name in group:
                if test_name in self.test_metrics_cache:
                    metrics = self.test_metrics_cache[test_name]
                    group_cpu += metrics.resource_requirements.get('cpu', 0)
                    group_memory += metrics.resource_requirements.get('memory', 0)
            
            total_cpu = max(total_cpu, group_cpu)  # Peak concurrent CPU
            total_memory = max(total_memory, group_memory)  # Peak concurrent memory
        
        return {
            'peak_cpu_usage': total_cpu,
            'peak_memory_mb': total_memory,
            'resource_efficiency': min(total_cpu, total_memory / 1000) / len(test_groups),
            'parallelization_factor': len(test_groups)
        }


class ParallelTestExecutor:
    """Parallel test execution engine with intelligent scheduling"""
    
    def __init__(self, scheduler: TestScheduler):
        self.scheduler = scheduler
        self.execution_results = {}
        self.worker_stats = {}
        
    def execute_test_groups(self, test_groups: List[List[str]], 
                           base_path: str = None,
                           timeout_per_test: int = 300) -> Dict:
        """Execute test groups in parallel with optimized resource allocation"""
        base_path = base_path or str(Path(__file__).parent.parent.parent)
        
        print(f"🚀 Starting parallel execution of {len(test_groups)} test groups...")
        start_time = time.time()
        
        execution_results = {
            'start_time': start_time,
            'test_groups': len(test_groups),
            'worker_results': {},
            'performance_metrics': {},
            'resource_usage': {},
            'optimization_metrics': {}
        }
        
        # Execute test groups in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(test_groups)) as executor:
            # Submit all test groups
            future_to_group = {
                executor.submit(
                    self._execute_test_group, 
                    f"worker_{i}", group, base_path, timeout_per_test
                ): (i, group)
                for i, group in enumerate(test_groups)
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_group):
                group_id, test_group = future_to_group[future]
                
                try:
                    worker_result = future.result()
                    execution_results['worker_results'][f'worker_{group_id}'] = worker_result
                    
                    # Update performance history
                    self._update_performance_history(worker_result)
                    
                    print(f"✅ Worker {group_id} completed: {worker_result['status']}")
                    
                except Exception as e:
                    print(f"❌ Worker {group_id} failed: {e}")
                    execution_results['worker_results'][f'worker_{group_id}'] = {
                        'status': 'ERROR',
                        'error': str(e),
                        'test_group': test_group
                    }
        
        # Calculate final metrics
        total_time = time.time() - start_time
        execution_results['total_duration'] = total_time
        execution_results['optimization_metrics'] = self._calculate_optimization_metrics(
            execution_results, total_time)
        
        return execution_results
    
    def _execute_test_group(self, worker_id: str, test_group: List[str], 
                           base_path: str, timeout: int) -> Dict:
        """Execute a group of tests in a single worker"""
        worker_start = time.time()
        
        # Track worker resource usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        worker_result = {
            'worker_id': worker_id,
            'test_group': test_group,
            'start_time': worker_start,
            'status': 'UNKNOWN',
            'tests_executed': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_results': {},
            'resource_usage': {},
            'performance_stats': {}
        }
        
        for test_file in test_group:
            test_start = time.time()
            
            try:
                # Execute individual test
                test_result = self._run_single_test(test_file, base_path, timeout)
                
                worker_result['test_results'][test_file] = test_result
                worker_result['tests_executed'] += 1
                
                if test_result.get('success', False):
                    worker_result['tests_passed'] += 1
                else:
                    worker_result['tests_failed'] += 1
                
                # Track individual test performance
                test_duration = time.time() - test_start
                current_memory = process.memory_info().rss
                
                # Update scheduler's performance history
                self.scheduler.update_test_performance_history(
                    test_file, test_duration, test_result.get('success', False),
                    current_memory, process.cpu_percent())
                
            except Exception as e:
                worker_result['test_results'][test_file] = {
                    'success': False,
                    'error': str(e),
                    'duration': time.time() - test_start
                }
                worker_result['tests_failed'] += 1
        
        # Calculate worker statistics
        worker_duration = time.time() - worker_start
        final_memory = process.memory_info().rss
        
        worker_result.update({
            'duration': worker_duration,
            'status': 'SUCCESS' if worker_result['tests_failed'] == 0 else 'PARTIAL',
            'resource_usage': {
                'memory_delta_mb': (final_memory - initial_memory) / (1024 * 1024),
                'peak_cpu_percent': process.cpu_percent(),
                'io_counters': process.io_counters()._asdict()
            }
        })
        
        return worker_result
    
    def _run_single_test(self, test_file: str, base_path: str, timeout: int) -> Dict:
        """Run a single test file with timeout and resource monitoring"""
        import subprocess
        
        test_path = Path(base_path) / test_file
        if not test_path.exists():
            return {'success': False, 'error': f'Test file not found: {test_file}'}
        
        # Prepare pytest command
        cmd = [
            'python', '-m', 'pytest',
            str(test_path),
            '--tb=short',
            '--quiet'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=base_path
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Test execution timed out',
                'timeout': timeout
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_performance_history(self, worker_result: Dict):
        """Update performance history from worker results"""
        for test_file, test_result in worker_result.get('test_results', {}).items():
            duration = test_result.get('duration', 0)
            success = test_result.get('success', False)
            
            self.scheduler.update_test_performance_history(
                test_file, duration, success)
    
    def _calculate_optimization_metrics(self, execution_results: Dict, 
                                      total_time: float) -> Dict:
        """Calculate optimization effectiveness metrics"""
        worker_results = execution_results.get('worker_results', {})
        
        if not worker_results:
            return {}
        
        # Calculate parallel efficiency
        total_worker_time = sum(
            result.get('duration', 0) 
            for result in worker_results.values()
            if isinstance(result.get('duration'), (int, float))
        )
        
        parallel_efficiency = total_worker_time / (total_time * len(worker_results)) if total_time > 0 else 0
        
        # Calculate success metrics
        total_tests = sum(
            result.get('tests_executed', 0) 
            for result in worker_results.values()
        )
        total_passed = sum(
            result.get('tests_passed', 0) 
            for result in worker_results.values()
        )
        
        return {
            'parallel_efficiency': parallel_efficiency,
            'total_tests_executed': total_tests,
            'overall_success_rate': total_passed / max(total_tests, 1),
            'time_savings_estimate': total_worker_time - total_time,
            'speedup_factor': total_worker_time / max(total_time, 1),
            'worker_utilization': len(worker_results)
        }


def create_optimized_test_schedule(test_files: List[str], 
                                  max_workers: int = None) -> Dict:
    """Create an optimized test execution schedule"""
    scheduler = TestScheduler()
    
    # Generate execution plan
    execution_plan = scheduler.schedule_optimized_execution(
        test_files, max_workers)
    
    return execution_plan


if __name__ == "__main__":
    # Example usage for Phase 4 optimization
    import sys
    
    if len(sys.argv) > 1:
        test_files = sys.argv[1:]
    else:
        # Default Phase 3 test files for optimization testing
        test_files = [
            'week9_10_e2e_workflows/test_user_journey_complete.py',
            'week9_10_e2e_workflows/test_application_lifecycle.py',
            'week11_12_performance_security/test_performance_benchmarks.py',
            'week11_12_performance_security/test_security_validation.py'
        ]
    
    print("Phase 4 Test Scheduler - Optimization Analysis")
    print("=" * 50)
    
    execution_plan = create_optimized_test_schedule(test_files)
    
    print(f"Optimal execution plan created:")
    print(f"- Test groups: {len(execution_plan['test_groups'])}")
    print(f"- Estimated duration: {execution_plan['estimated_duration']:.2f}s")
    print(f"- Flaky tests identified: {len(execution_plan['flaky_tests'])}")
    print(f"- Resource efficiency: {execution_plan['resource_allocation']['resource_efficiency']:.2f}")