"""
Performance Monitoring and Metrics Collection - Phase 4 Week 13-14
Advanced performance monitoring system for test execution optimization

Features:
- Real-time performance metrics collection
- Historical performance tracking and analysis
- Performance regression detection
- Resource usage pattern analysis
- Optimization effectiveness measurement
"""

import json
import sqlite3
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional

import psutil


@dataclass
class PerformanceSnapshot:
    """Single point-in-time performance snapshot"""

    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    io_read_bytes: int
    io_write_bytes: int
    thread_count: int
    test_context: str


@dataclass
class TestPerformanceMetrics:
    """Comprehensive performance metrics for a test execution"""

    test_name: str
    start_time: float
    end_time: float
    duration: float
    cpu_usage_avg: float
    cpu_usage_peak: float
    memory_usage_avg: float
    memory_usage_peak: float
    io_read_total: int
    io_write_total: int
    resource_efficiency_score: float
    performance_grade: str


class PerformanceMonitor:
    """Advanced performance monitoring system"""

    def __init__(self, db_path: str = None, monitoring_interval: float = 0.5):
        self.db_path = db_path or "performance_monitoring.db"
        self.monitoring_interval = monitoring_interval
        self.monitoring_active = False
        self.monitoring_thread = None

        # Performance data storage
        self.current_snapshots = deque(maxlen=1000)
        self.test_metrics_history = {}
        self.performance_baselines = {}

        # Performance thresholds
        self.thresholds = {
            "cpu_high": 80.0,
            "memory_high": 85.0,
            "io_high": 100 * 1024 * 1024,  # 100MB/s
            "duration_warning_multiplier": 1.5,
            "regression_threshold": 0.2,  # 20% performance degradation
        }

        self._initialize_database()
        self._load_performance_baselines()

    def _initialize_database(self):
        """Initialize performance monitoring database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    cpu_percent REAL,
                    memory_mb REAL,
                    memory_percent REAL,
                    io_read_bytes INTEGER,
                    io_write_bytes INTEGER,
                    thread_count INTEGER,
                    test_context TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_performance_metrics (
                    test_name TEXT,
                    execution_timestamp REAL,
                    duration REAL,
                    cpu_usage_avg REAL,
                    cpu_usage_peak REAL,
                    memory_usage_avg REAL,
                    memory_usage_peak REAL,
                    io_read_total INTEGER,
                    io_write_total INTEGER,
                    resource_efficiency_score REAL,
                    performance_grade TEXT,
                    PRIMARY KEY (test_name, execution_timestamp)
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_baselines (
                    test_name TEXT PRIMARY KEY,
                    baseline_duration REAL,
                    baseline_cpu_avg REAL,
                    baseline_memory_avg REAL,
                    baseline_established TIMESTAMP,
                    confidence_level REAL
                )
            """
            )

    def _load_performance_baselines(self):
        """Load established performance baselines"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT test_name, baseline_duration, baseline_cpu_avg, 
                       baseline_memory_avg, confidence_level
                FROM performance_baselines
            """
            )

            for row in cursor.fetchall():
                test_name, duration, cpu_avg, memory_avg, confidence = row
                self.performance_baselines[test_name] = {
                    "duration": duration,
                    "cpu_avg": cpu_avg,
                    "memory_avg": memory_avg,
                    "confidence": confidence,
                }

    def start_monitoring(self, test_context: str = "general"):
        """Start performance monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.current_test_context = test_context

        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()

    def stop_monitoring(self) -> List[PerformanceSnapshot]:
        """Stop performance monitoring and return collected data"""
        if not self.monitoring_active:
            return []

        self.monitoring_active = False

        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)

        snapshots = list(self.current_snapshots)
        return snapshots

    def _monitoring_loop(self):
        """Main monitoring loop"""
        process = psutil.Process()

        while self.monitoring_active:
            try:
                snapshot = self._collect_performance_snapshot(process)
                self.current_snapshots.append(snapshot)
                self._persist_snapshot(snapshot)
                time.sleep(self.monitoring_interval)

            except Exception:
                time.sleep(self.monitoring_interval)

    def _collect_performance_snapshot(self, process) -> PerformanceSnapshot:
        """Collect a single performance snapshot"""
        try:
            io_counters = process.io_counters()
            io_read = io_counters.read_bytes
            io_write = io_counters.write_bytes
        except:
            io_read = io_write = 0

        return PerformanceSnapshot(
            timestamp=time.time(),
            cpu_percent=process.cpu_percent(),
            memory_mb=process.memory_info().rss / (1024 * 1024),
            memory_percent=process.memory_percent(),
            io_read_bytes=io_read,
            io_write_bytes=io_write,
            thread_count=process.num_threads(),
            test_context=getattr(self, "current_test_context", "unknown"),
        )

    def _persist_snapshot(self, snapshot: PerformanceSnapshot):
        """Persist performance snapshot to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO performance_snapshots
                    (timestamp, cpu_percent, memory_mb, memory_percent,
                     io_read_bytes, io_write_bytes, thread_count, test_context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        snapshot.timestamp,
                        snapshot.cpu_percent,
                        snapshot.memory_mb,
                        snapshot.memory_percent,
                        snapshot.io_read_bytes,
                        snapshot.io_write_bytes,
                        snapshot.thread_count,
                        snapshot.test_context,
                    ),
                )
        except Exception:
            pass

    def monitor_test_execution(
        self, test_name: str, test_execution_func: Callable
    ) -> TestPerformanceMetrics:
        """Monitor performance during test execution"""
        self.start_monitoring(test_name)

        start_time = time.time()
        initial_io = self._get_io_counters()

        try:
            test_result = test_execution_func()
        finally:
            snapshots = self.stop_monitoring()

        end_time = time.time()
        final_io = self._get_io_counters()

        metrics = self._calculate_test_metrics(
            test_name, start_time, end_time, snapshots, initial_io, final_io
        )

        self._store_test_metrics(metrics)
        return metrics

    def _get_io_counters(self) -> Dict:
        """Get current I/O counters"""
        try:
            io = psutil.Process().io_counters()
            return {"read_bytes": io.read_bytes, "write_bytes": io.write_bytes}
        except:
            return {"read_bytes": 0, "write_bytes": 0}

    def _calculate_test_metrics(
        self,
        test_name: str,
        start_time: float,
        end_time: float,
        snapshots: List[PerformanceSnapshot],
        initial_io: Dict,
        final_io: Dict,
    ) -> TestPerformanceMetrics:
        """Calculate comprehensive test performance metrics"""
        duration = end_time - start_time

        if not snapshots:
            return TestPerformanceMetrics(
                test_name=test_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                cpu_usage_avg=0,
                cpu_usage_peak=0,
                memory_usage_avg=0,
                memory_usage_peak=0,
                io_read_total=0,
                io_write_total=0,
                resource_efficiency_score=0,
                performance_grade="UNKNOWN",
            )

        test_snapshots = [s for s in snapshots if s.test_context == test_name]
        if not test_snapshots:
            test_snapshots = snapshots

        cpu_values = [s.cpu_percent for s in test_snapshots]
        memory_values = [s.memory_mb for s in test_snapshots]

        cpu_usage_avg = statistics.mean(cpu_values) if cpu_values else 0
        cpu_usage_peak = max(cpu_values) if cpu_values else 0
        memory_usage_avg = (
            statistics.mean(memory_values) if memory_values else 0
        )
        memory_usage_peak = max(memory_values) if memory_values else 0

        io_read_total = final_io["read_bytes"] - initial_io["read_bytes"]
        io_write_total = final_io["write_bytes"] - initial_io["write_bytes"]

        efficiency_score = self._calculate_efficiency_score(
            cpu_usage_avg,
            memory_usage_avg,
            duration,
            io_read_total + io_write_total,
        )

        performance_grade = self._determine_performance_grade(
            duration, cpu_usage_avg, memory_usage_avg, efficiency_score
        )

        return TestPerformanceMetrics(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            cpu_usage_avg=cpu_usage_avg,
            cpu_usage_peak=cpu_usage_peak,
            memory_usage_avg=memory_usage_avg,
            memory_usage_peak=memory_usage_peak,
            io_read_total=io_read_total,
            io_write_total=io_write_total,
            resource_efficiency_score=efficiency_score,
            performance_grade=performance_grade,
        )

    def _calculate_efficiency_score(
        self, cpu_avg: float, memory_avg: float, duration: float, io_total: int
    ) -> float:
        """Calculate resource efficiency score (0-100)"""
        cpu_efficiency = 1.0 - min(cpu_avg / 100.0, 1.0)
        memory_efficiency = 1.0 - min(memory_avg / 2048.0, 1.0)
        duration_efficiency = max(0, 1.0 - (duration / 30.0))
        io_efficiency = max(0, 1.0 - (io_total / (100 * 1024 * 1024)))

        efficiency_score = (
            cpu_efficiency * 0.3
            + memory_efficiency * 0.3
            + duration_efficiency * 0.25
            + io_efficiency * 0.15
        ) * 100

        return min(100.0, max(0.0, efficiency_score))

    def _determine_performance_grade(
        self,
        duration: float,
        cpu_avg: float,
        memory_avg: float,
        efficiency_score: float,
    ) -> str:
        """Determine performance grade based on metrics"""
        if efficiency_score >= 90 and duration < 10:
            return "A+"
        elif efficiency_score >= 80 and duration < 20:
            return "A"
        elif efficiency_score >= 70 and duration < 30:
            return "B+"
        elif efficiency_score >= 60 and duration < 60:
            return "B"
        elif efficiency_score >= 50:
            return "C"
        else:
            return "D"

    def _store_test_metrics(self, metrics: TestPerformanceMetrics):
        """Store test performance metrics in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO test_performance_metrics
                (test_name, execution_timestamp, duration, cpu_usage_avg,
                 cpu_usage_peak, memory_usage_avg, memory_usage_peak,
                 io_read_total, io_write_total, resource_efficiency_score, performance_grade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metrics.test_name,
                    metrics.start_time,
                    metrics.duration,
                    metrics.cpu_usage_avg,
                    metrics.cpu_usage_peak,
                    metrics.memory_usage_avg,
                    metrics.memory_usage_peak,
                    metrics.io_read_total,
                    metrics.io_write_total,
                    metrics.resource_efficiency_score,
                    metrics.performance_grade,
                ),
            )

        if metrics.test_name not in self.test_metrics_history:
            self.test_metrics_history[metrics.test_name] = []

        self.test_metrics_history[metrics.test_name].append(metrics)

    def generate_performance_report(self, time_window_hours: int = 24) -> Dict:
        """Generate comprehensive performance report"""
        cutoff_time = time.time() - (time_window_hours * 3600)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM test_performance_metrics
                WHERE execution_timestamp > ?
                ORDER BY execution_timestamp DESC
            """,
                (cutoff_time,),
            )

            recent_tests = cursor.fetchall()

        report = {
            "report_timestamp": datetime.now().isoformat(),
            "time_window_hours": time_window_hours,
            "total_tests_analyzed": len(recent_tests),
            "performance_summary": self._analyze_performance_summary(
                recent_tests
            ),
            "optimization_recommendations": self._generate_optimization_recommendations(
                recent_tests
            ),
        }

        return report

    def _analyze_performance_summary(self, test_data: List) -> Dict:
        """Analyze performance summary from test data"""
        if not test_data:
            return {"status": "no_data"}

        durations = [row[2] for row in test_data if row[2]]
        cpu_avgs = [row[3] for row in test_data if row[3]]
        memory_avgs = [row[5] for row in test_data if row[5]]
        efficiency_scores = [row[9] for row in test_data if row[9]]

        summary = {}

        if durations:
            summary["duration"] = {
                "avg": statistics.mean(durations),
                "median": statistics.median(durations),
                "min": min(durations),
                "max": max(durations),
            }

        if cpu_avgs:
            summary["cpu_usage"] = {
                "avg": statistics.mean(cpu_avgs),
                "max": max(cpu_avgs),
            }

        if memory_avgs:
            summary["memory_usage"] = {
                "avg": statistics.mean(memory_avgs),
                "max": max(memory_avgs),
            }

        if efficiency_scores:
            summary["efficiency"] = {
                "avg": statistics.mean(efficiency_scores),
                "min": min(efficiency_scores),
            }

        return summary

    def _generate_optimization_recommendations(
        self, test_data: List
    ) -> List[str]:
        """Generate optimization recommendations based on performance data"""
        if not test_data:
            return ["No performance data available for recommendations"]

        recommendations = []

        avg_durations = [row[2] for row in test_data if row[2]]
        avg_cpu = [row[3] for row in test_data if row[3]]
        avg_memory = [row[5] for row in test_data if row[5]]

        if avg_durations and statistics.mean(avg_durations) > 60:
            recommendations.append(
                "Consider implementing more aggressive parallel execution"
            )

        if avg_cpu and statistics.mean(avg_cpu) > 70:
            recommendations.append(
                "High CPU usage detected - consider CPU optimization strategies"
            )

        if avg_memory and statistics.mean(avg_memory) > 1024:
            recommendations.append(
                "High memory usage detected - implement memory pooling"
            )

        if not recommendations:
            recommendations.append(
                "✅ Performance metrics within acceptable ranges"
            )

        return recommendations


def monitor_test_suite_performance(
    test_suite_func: Callable, test_suite_name: str = "test_suite"
) -> Dict:
    """Monitor performance of an entire test suite"""
    monitor = PerformanceMonitor()

    print(f"🚀 Starting performance monitoring for: {test_suite_name}")

    metrics = monitor.monitor_test_execution(test_suite_name, test_suite_func)
    report = monitor.generate_performance_report(time_window_hours=1)

    return {
        "test_metrics": asdict(metrics),
        "performance_report": report,
        "monitoring_summary": {
            "test_name": test_suite_name,
            "performance_grade": metrics.performance_grade,
            "efficiency_score": metrics.resource_efficiency_score,
            "total_duration": metrics.duration,
        },
    }


if __name__ == "__main__":

    def example_test_suite():
        """Example test suite for monitoring demonstration"""
        import time

        print("Running example test operations...")
        time.sleep(2)
        return {"status": "success", "tests_run": 5}

    result = monitor_test_suite_performance(
        example_test_suite, "example_integration_tests"
    )

    print("Performance Monitoring Results:")
    print(
        f"- Performance Grade: {result['monitoring_summary']['performance_grade']}"
    )
    print(
        f"- Efficiency Score: {result['monitoring_summary']['efficiency_score']:.1f}"
    )
    print(f"- Duration: {result['monitoring_summary']['total_duration']:.2f}s")
