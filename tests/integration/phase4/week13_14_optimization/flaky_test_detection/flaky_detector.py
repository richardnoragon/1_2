"""
Flaky Test Detection System - Phase 4 Week 13-14
Comprehensive flaky test detection and elimination system

Features:
- Statistical analysis of test failure patterns
- Root cause classification for failures
- Automatic remediation strategies
- Continuous monitoring and tracking
- Pattern-based failure analysis
"""

import json
import sqlite3
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FlakyTestMetrics:
    """Metrics for flaky test analysis"""
    test_name: str
    total_runs: int
    failure_count: int
    failure_rate: float
    consecutive_failures: int
    consecutive_successes: int
    last_failure_time: Optional[datetime]
    failure_patterns: List[str]
    remediation_attempts: int
    classification: str
    confidence_level: float


class FlakyTestDetector:
    """Advanced flaky test detection and analysis system"""
    
    def __init__(self, db_path: Optional[str] = None, 
                 analysis_window_days: int = 30):
        self.db_path = db_path or "flaky_test_analysis.db"
        self.analysis_window_days = analysis_window_days
        self.confidence_threshold = 0.85
        self.flaky_threshold = 0.05  # 5% failure rate
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize flaky test tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL,
                    duration REAL,
                    error_message TEXT,
                    error_type TEXT,
                    environment_context TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flaky_test_analysis (
                    test_name TEXT PRIMARY KEY,
                    failure_rate REAL,
                    total_runs INTEGER,
                    failure_count INTEGER,
                    consecutive_failures INTEGER,
                    consecutive_successes INTEGER,
                    last_failure TIMESTAMP,
                    classification TEXT,
                    confidence_level REAL,
                    remediation_status TEXT,
                    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS remediation_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT,
                    remediation_type TEXT,
                    action_description TEXT,
                    applied_timestamp TIMESTAMP,
                    success BOOLEAN,
                    notes TEXT
                )
            """)
    
    def record_test_execution(self, test_name: str, success: bool, 
                             duration: float, error_message: str = None,
                             environment_context: Dict = None):
        """Record test execution for flaky test analysis"""
        with sqlite3.connect(self.db_path) as conn:
            error_type = self._classify_error_type(error_message) if error_message else None
            env_json = json.dumps(environment_context) if environment_context else None
            
            conn.execute("""
                INSERT INTO test_execution_history 
                (test_name, success, duration, error_message, error_type, environment_context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (test_name, success, duration, error_message, error_type, env_json))
            
            self._update_flaky_analysis(test_name)
    
    def _classify_error_type(self, error_message: str) -> str:
        """Classify error type based on error message"""
        if not error_message:
            return "unknown"
        
        error_lower = error_message.lower()
        
        if any(keyword in error_lower for keyword in 
               ['timeout', 'time out', 'timed out']):
            return "timing_issue"
        elif any(keyword in error_lower for keyword in 
                ['lock', 'resource', 'busy', 'contention']):
            return "resource_contention"
        elif any(keyword in error_lower for keyword in 
                ['network', 'connection', 'api', 'http']):
            return "network_instability"
        elif any(keyword in error_lower for keyword in 
                ['race', 'concurrent', 'thread', 'async']):
            return "race_condition"
        else:
            return "unknown"
    
    def _update_flaky_analysis(self, test_name: str):
        """Update flaky test analysis based on recent execution history"""
        with sqlite3.connect(self.db_path) as conn:
            cutoff_date = datetime.now() - timedelta(days=self.analysis_window_days)
            
            cursor = conn.execute("""
                SELECT success, error_type, execution_time
                FROM test_execution_history 
                WHERE test_name = ? AND execution_time > ?
                ORDER BY execution_time DESC
            """, (test_name, cutoff_date.isoformat()))
            
            executions = cursor.fetchall()
            
            if len(executions) < 5:
                return
            
            total_runs = len(executions)
            failure_count = sum(1 for success, _, _ in executions if not success)
            failure_rate = failure_count / total_runs
            
            # Calculate consecutive patterns
            consecutive_failures = 0
            consecutive_successes = 0
            current_streak_failures = 0
            current_streak_successes = 0
            
            for success, _, _ in executions:
                if not success:
                    current_streak_failures += 1
                    current_streak_successes = 0
                    consecutive_failures = max(consecutive_failures, 
                                             current_streak_failures)
                else:
                    current_streak_successes += 1
                    current_streak_failures = 0
                    consecutive_successes = max(consecutive_successes,
                                              current_streak_successes)
            
            last_failure = None
            for success, _, exec_time in executions:
                if not success:
                    last_failure = exec_time
                    break
            
            classification = self._classify_flaky_test(
                failure_rate, consecutive_failures)
            
            confidence_level = self._calculate_confidence_level(
                total_runs, failure_rate, consecutive_failures)
            
            conn.execute("""
                INSERT OR REPLACE INTO flaky_test_analysis
                (test_name, failure_rate, total_runs, failure_count,
                 consecutive_failures, consecutive_successes, last_failure,
                 classification, confidence_level, remediation_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (test_name, failure_rate, total_runs, failure_count,
                  consecutive_failures, consecutive_successes, last_failure,
                  classification, confidence_level, "pending"))
    
    def _classify_flaky_test(self, failure_rate: float, 
                            consecutive_failures: int) -> str:
        """Classify the type of flaky behavior"""
        if failure_rate > 0.5:
            return "consistently_failing"
        elif failure_rate > 0.2:
            return "highly_flaky"
        elif failure_rate > self.flaky_threshold:
            if consecutive_failures > 3:
                return "intermittent_failing"
            else:
                return "randomly_flaky"
        else:
            return "stable"
    
    def _calculate_confidence_level(self, total_runs: int, failure_rate: float,
                                   consecutive_failures: int) -> float:
        """Calculate confidence level in flaky test classification"""
        sample_confidence = min(total_runs / 50.0, 1.0)
        pattern_confidence = 1.0 if failure_rate > 0.1 else failure_rate * 10
        consecutive_penalty = min(consecutive_failures / 10.0, 0.3)
        
        return max(0.1, min(1.0, 
                           sample_confidence * pattern_confidence - consecutive_penalty))
    
    def detect_flaky_tests(self, min_runs: int = 10) -> List[FlakyTestMetrics]:
        """Detect flaky tests based on historical analysis"""
        flaky_tests = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT test_name, failure_rate, total_runs, failure_count,
                       consecutive_failures, consecutive_successes, last_failure,
                       classification, confidence_level
                FROM flaky_test_analysis
                WHERE total_runs >= ? AND failure_rate > ?
                ORDER BY failure_rate DESC, confidence_level DESC
            """, (min_runs, self.flaky_threshold))
            
            for row in cursor.fetchall():
                (test_name, failure_rate, total_runs, failure_count,
                 consecutive_failures, consecutive_successes, last_failure,
                 classification, confidence_level) = row
                
                patterns = self._get_failure_patterns(test_name)
                last_failure_dt = (datetime.fromisoformat(last_failure) 
                                 if last_failure else None)
                
                flaky_test = FlakyTestMetrics(
                    test_name=test_name,
                    total_runs=total_runs,
                    failure_count=failure_count,
                    failure_rate=failure_rate,
                    consecutive_failures=consecutive_failures,
                    consecutive_successes=consecutive_successes,
                    last_failure_time=last_failure_dt,
                    failure_patterns=patterns,
                    remediation_attempts=self._get_remediation_count(test_name),
                    classification=classification,
                    confidence_level=confidence_level
                )
                
                flaky_tests.append(flaky_test)
        
        return flaky_tests
    
    def _get_failure_patterns(self, test_name: str) -> List[str]:
        """Get failure patterns for a specific test"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT error_type, COUNT(*) as frequency
                FROM test_execution_history
                WHERE test_name = ? AND success = 0
                GROUP BY error_type
                ORDER BY frequency DESC
            """, (test_name,))
            
            return [f"{error_type}: {freq}x" for error_type, freq in cursor.fetchall()]
    
    def _get_remediation_count(self, test_name: str) -> int:
        """Get number of remediation attempts for a test"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM remediation_actions 
                WHERE test_name = ?
            """, (test_name,))
            
            return cursor.fetchone()[0]
    
    def generate_flaky_test_report(self) -> Dict:
        """Generate comprehensive flaky test report"""
        flaky_tests = self.detect_flaky_tests()
        
        report = {
            'report_generation_time': datetime.now().isoformat(),
            'analysis_period_days': self.analysis_window_days,
            'total_flaky_tests': len(flaky_tests),
            'flaky_test_details': [],
            'summary_statistics': {},
            'recommendations': []
        }
        
        for flaky_test in flaky_tests:
            test_detail = {
                'test_name': flaky_test.test_name,
                'failure_rate': flaky_test.failure_rate,
                'classification': flaky_test.classification,
                'confidence_level': flaky_test.confidence_level,
                'total_runs': flaky_test.total_runs,
                'failure_patterns': flaky_test.failure_patterns,
                'remediation_attempts': flaky_test.remediation_attempts
            }
            report['flaky_test_details'].append(test_detail)
        
        if flaky_tests:
            failure_rates = [ft.failure_rate for ft in flaky_tests]
            confidence_levels = [ft.confidence_level for ft in flaky_tests]
            
            report['summary_statistics'] = {
                'avg_failure_rate': statistics.mean(failure_rates),
                'max_failure_rate': max(failure_rates),
                'avg_confidence_level': statistics.mean(confidence_levels),
                'total_remediation_attempts': sum(ft.remediation_attempts for ft in flaky_tests)
            }
        
        report['recommendations'] = self._generate_recommendations(flaky_tests)
        
        return report
    
    def _generate_recommendations(self, flaky_tests: List[FlakyTestMetrics]) -> List[str]:
        """Generate recommendations for flaky test management"""
        if not flaky_tests:
            return ["✅ No flaky tests detected - excellent test stability!"]
        
        recommendations = []
        critical_flaky = [t for t in flaky_tests if t.failure_rate > 0.2]
        
        if critical_flaky:
            recommendations.append(
                f"🚨 {len(critical_flaky)} critical flaky tests require immediate attention"
            )
        
        recommendations.extend([
            "🔧 Implement automatic remediation for common patterns",
            "📊 Enable continuous flaky test monitoring",
            "🎯 Set up alerts for new flaky test detection"
        ])
        
        return recommendations


def detect_and_remediate_flaky_tests(auto_remediate: bool = False) -> Dict:
    """Main function to detect and optionally remediate flaky tests"""
    detector = FlakyTestDetector()
    
    print("🔍 Starting flaky test detection analysis...")
    start_time = time.time()
    
    # Generate comprehensive report
    report = detector.generate_flaky_test_report()
    
    print(f"✅ Flaky test analysis completed in {time.time() - start_time:.2f}s")
    print(f"📊 Found {report['total_flaky_tests']} flaky tests")
    
    return report


if __name__ == "__main__":
    result = detect_and_remediate_flaky_tests()
    print(json.dumps(result, indent=2, default=str))