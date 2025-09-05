"""
Phase 3 Integration Tests Runner
Comprehensive test execution runner for RFU Phase 3 Advanced Testing

Features:
- Executes both Week 9-10 E2E Workflow Tests and Week 11-12 Performance/Security Tests
- Generates detailed reports and performance metrics
- Provides comprehensive benchmarking and security validation
- Supports selective test execution
- Creates detailed summaries with compliance reporting
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Test categories and their corresponding files
WEEK_9_10_TESTS = {
    'user_journey_complete': 'week9_10_e2e_workflows/test_user_journey_complete.py',
    'application_lifecycle': 'week9_10_e2e_workflows/test_application_lifecycle.py',
    'multi_component_operations': 'week9_10_e2e_workflows/test_multi_component_operations.py'
}

WEEK_11_12_TESTS = {
    'performance_benchmarks': 'week11_12_performance_security/test_performance_benchmarks.py',
    'security_validation': 'week11_12_performance_security/test_security_validation.py',
    'load_testing_integration': 'week11_12_performance_security/test_load_testing_integration.py',
    'vulnerability_scanning': 'week11_12_performance_security/test_vulnerability_scanning.py'
}

ALL_TESTS = {**WEEK_9_10_TESTS, **WEEK_11_12_TESTS}


class Phase3TestRunner:
    """Comprehensive test runner for Phase 3 advanced testing"""
    
    def __init__(self, base_path=None):
        self.base_path = base_path or Path(__file__).parent
        self.results = {
            'execution_summary': {
                'start_time': None,
                'end_time': None,
                'total_duration': 0,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'error_tests': 0
            },
            'test_categories': {},
            'performance_metrics': {},
            'security_metrics': {},
            'detailed_results': {},
            'recommendations': [],
            'compliance_status': {}
        }
        
    def run_tests(self, test_categories=None, verbose=False, 
                  generate_html=True, skip_slow=False):
        """Run specified test categories or all tests"""
        print("=" * 70)
        print("RFU Phase 3 Advanced Testing - End-to-End & Performance/Security")
        print("=" * 70)
        
        # Determine which tests to run
        if test_categories:
            tests_to_run = {k: v for k, v in ALL_TESTS.items() 
                           if k in test_categories}
        else:
            tests_to_run = ALL_TESTS
        
        print(f"Running {len(tests_to_run)} test categories...")
        print()
        
        self.results['execution_summary']['start_time'] = datetime.now().isoformat()
        start_time = time.time()
        
        # Execute each test category
        for category, test_file in tests_to_run.items():
            print(f"Executing {category}...")
            test_result = self._run_single_test(category, test_file, verbose, skip_slow)
            self.results['test_categories'][category] = test_result
            
            # Update summary statistics
            self._update_summary_stats(test_result)
            
            print(f"  Result: {test_result['status']}")
            if test_result['status'] == 'FAILED':
                print(f"  Failures: {test_result['failures']}")
            print()
        
        # Calculate final metrics
        end_time = time.time()
        self.results['execution_summary']['end_time'] = datetime.now().isoformat()
        self.results['execution_summary']['total_duration'] = end_time - start_time
        
        # Generate comprehensive analysis
        self._generate_performance_metrics()
        self._generate_security_metrics()
        self._generate_compliance_status()
        self._generate_recommendations()
        
        # Output results
        self._print_summary()
        
        if generate_html:
            self._generate_html_report()
        
        return self.results
    
    def _run_single_test(self, category, test_file, verbose, skip_slow):
        """Run a single test file and collect results"""
        test_path = self.base_path / test_file
        
        if not test_path.exists():
            return {
                'status': 'ERROR',
                'message': f'Test file not found: {test_file}',
                'duration': 0,
                'tests_run': 0,
                'failures': 0,
                'errors': 0,
                'skipped': 0
            }
        
        # Prepare pytest command
        cmd = [
            sys.executable, '-m', 'pytest',
            str(test_path),
            '--tb=short',
            '--json-report',
            '--json-report-file=' + str(self.base_path / f'{category}_results.json')
        ]
        
        if verbose:
            cmd.append('--verbose')
        else:
            cmd.append('--quiet')
        
        if skip_slow:
            cmd.extend(['-m', 'not slow'])
        
        start_time = time.time()
        
        try:
            # Execute pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.base_path)
            )
            
            duration = time.time() - start_time
            
            # Parse JSON results if available
            json_file = self.base_path / f'{category}_results.json'
            test_details = self._parse_json_results(json_file)
            
            # Clean up JSON file
            if json_file.exists():
                os.unlink(json_file)
            
            # Determine status
            status = 'PASSED' if result.returncode == 0 else 'FAILED'
            
            return {
                'status': status,
                'duration': duration,
                'tests_run': test_details.get('total', 0),
                'failures': test_details.get('failed', 0),
                'errors': test_details.get('error', 0),
                'skipped': test_details.get('skipped', 0),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'details': test_details
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': str(e),
                'duration': time.time() - start_time,
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0
            }
    
    def _parse_json_results(self, json_file):
        """Parse pytest JSON results if available"""
        try:
            if json_file.exists():
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                summary = data.get('summary', {})
                return {
                    'total': summary.get('total', 0),
                    'passed': summary.get('passed', 0),
                    'failed': summary.get('failed', 0),
                    'error': summary.get('error', 0),
                    'skipped': summary.get('skipped', 0),
                    'tests': data.get('tests', [])
                }
        except Exception:
            pass
        
        return {'total': 0, 'passed': 0, 'failed': 0, 'error': 0, 'skipped': 0}
    
    def _update_summary_stats(self, test_result):
        """Update summary statistics"""
        summary = self.results['execution_summary']
        
        summary['total_tests'] += test_result.get('tests_run', 0)
        summary['failed_tests'] += test_result.get('failures', 0)
        summary['error_tests'] += test_result.get('errors', 0)
        summary['skipped_tests'] += test_result.get('skipped', 0)
        
        # Calculate passed tests
        tests_run = test_result.get('tests_run', 0)
        failures = test_result.get('failures', 0)
        errors = test_result.get('errors', 0)
        skipped = test_result.get('skipped', 0)
        
        summary['passed_tests'] += max(0, tests_run - failures - errors - skipped)
    
    def _generate_performance_metrics(self):
        """Generate performance metrics from test results"""
        metrics = {
            'total_execution_time': self.results['execution_summary']['total_duration'],
            'average_test_time': 0,
            'slowest_categories': [],
            'fastest_categories': [],
            'category_performance': {}
        }
        
        # Calculate category performance
        category_times = []
        for category, result in self.results['test_categories'].items():
            duration = result.get('duration', 0)
            tests_count = result.get('tests_run', 0)
            
            metrics['category_performance'][category] = {
                'duration': duration,
                'tests_count': tests_count,
                'avg_test_time': duration / max(1, tests_count)
            }
            
            category_times.append((category, duration))
        
        # Sort by duration
        category_times.sort(key=lambda x: x[1])
        
        if category_times:
            metrics['fastest_categories'] = category_times[:2]
            metrics['slowest_categories'] = category_times[-2:]
            
            total_tests = sum(r.get('tests_run', 0) 
                            for r in self.results['test_categories'].values())
            if total_tests > 0:
                metrics['average_test_time'] = (
                    metrics['total_execution_time'] / total_tests)
        
        self.results['performance_metrics'] = metrics
    
    def _generate_security_metrics(self):
        """Generate security metrics from test results"""
        security_metrics = {
            'security_categories_tested': 0,
            'security_tests_passed': 0,
            'vulnerability_scans_completed': 0,
            'security_score': 0,
            'compliance_level': 'UNKNOWN'
        }
        
        # Analyze security test results
        security_categories = ['security_validation', 'vulnerability_scanning']
        
        for category in security_categories:
            if category in self.results['test_categories']:
                result = self.results['test_categories'][category]
                security_metrics['security_categories_tested'] += 1
                
                if result['status'] == 'PASSED':
                    security_metrics['security_tests_passed'] += result.get('tests_run', 0)
                    if 'vulnerability' in category:
                        security_metrics['vulnerability_scans_completed'] += 1
        
        # Calculate security score
        total_security_tests = sum(
            self.results['test_categories'][cat].get('tests_run', 0)
            for cat in security_categories
            if cat in self.results['test_categories']
        )
        
        if total_security_tests > 0:
            security_metrics['security_score'] = (
                security_metrics['security_tests_passed'] / total_security_tests) * 100
        
        # Determine compliance level
        if security_metrics['security_score'] >= 95:
            security_metrics['compliance_level'] = 'EXCELLENT'
        elif security_metrics['security_score'] >= 85:
            security_metrics['compliance_level'] = 'GOOD'
        else:
            security_metrics['compliance_level'] = 'NEEDS_IMPROVEMENT'
        
        self.results['security_metrics'] = security_metrics
    
    def _generate_compliance_status(self):
        """Generate Phase 3 compliance status"""
        compliance = {
            'overall_status': 'UNKNOWN',
            'phase3_requirements_met': False,
            'end_to_end_workflows_validated': False,
            'performance_benchmarks_met': False,
            'security_validation_passed': False,
            'compliance_percentage': 0
        }
        
        # Check Week 9-10 requirements
        week9_10_passed = all(
            self.results['test_categories'].get(category, {}).get('status') == 'PASSED'
            for category in WEEK_9_10_TESTS.keys()
            if category in self.results['test_categories']
        )
        
        # Check Week 11-12 requirements
        week11_12_passed = all(
            self.results['test_categories'].get(category, {}).get('status') == 'PASSED'
            for category in WEEK_11_12_TESTS.keys()
            if category in self.results['test_categories']
        )
        
        compliance['end_to_end_workflows_validated'] = week9_10_passed
        compliance['performance_benchmarks_met'] = week11_12_passed
        compliance['security_validation_passed'] = week11_12_passed
        compliance['phase3_requirements_met'] = week9_10_passed and week11_12_passed
        
        # Calculate compliance percentage
        compliance_factors = [
            compliance['end_to_end_workflows_validated'],
            compliance['performance_benchmarks_met'],
            compliance['security_validation_passed']
        ]
        
        compliance['compliance_percentage'] = (
            sum(compliance_factors) / len(compliance_factors)) * 100
        
        # Determine overall status
        if compliance['compliance_percentage'] >= 100:
            compliance['overall_status'] = 'FULLY_COMPLIANT'
        elif compliance['compliance_percentage'] >= 75:
            compliance['overall_status'] = 'MOSTLY_COMPLIANT'
        else:
            compliance['overall_status'] = 'NON_COMPLIANT'
        
        self.results['compliance_status'] = compliance
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for failures
        failed_categories = [
            cat for cat, result in self.results['test_categories'].items()
            if result.get('status') == 'FAILED'
        ]
        
        if failed_categories:
            recommendations.append({
                'type': 'CRITICAL',
                'priority': 'HIGH',
                'message': f"Address failing test categories: {', '.join(failed_categories)}",
                'action_items': [
                    'Review test failure details',
                    'Fix underlying issues',
                    'Re-run failed tests',
                    'Update test documentation if needed'
                ]
            })
        
        # Performance recommendations
        perf_metrics = self.results.get('performance_metrics', {})
        if perf_metrics.get('total_execution_time', 0) > 300:  # 5 minutes
            recommendations.append({
                'type': 'PERFORMANCE',
                'priority': 'MEDIUM',
                'message': 'Test execution time exceeds recommended duration',
                'action_items': [
                    'Optimize slow test scenarios',
                    'Implement parallel test execution',
                    'Review test data sizes'
                ]
            })
        
        # Security recommendations
        security_metrics = self.results.get('security_metrics', {})
        if security_metrics.get('security_score', 0) < 90:
            recommendations.append({
                'type': 'SECURITY',
                'priority': 'HIGH',
                'message': 'Security validation score below recommended threshold',
                'action_items': [
                    'Review failed security tests',
                    'Enhance security controls',
                    'Update security configurations'
                ]
            })
        
        # Success recommendations
        if not failed_categories:
            recommendations.append({
                'type': 'SUCCESS',
                'priority': 'INFO',
                'message': 'All Phase 3 advanced tests passed - system ready for production'
            })
        
        self.results['recommendations'] = recommendations
    
    def _print_summary(self):
        """Print comprehensive test execution summary"""
        print("=" * 70)
        print("PHASE 3 ADVANCED TESTING SUMMARY")
        print("=" * 70)
        
        summary = self.results['execution_summary']
        
        print(f"Total Duration: {summary['total_duration']:.2f} seconds")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Errors: {summary['error_tests']}")
        print(f"Skipped: {summary['skipped_tests']}")
        
        # Calculate success rate
        if summary['total_tests'] > 0:
            success_rate = (summary['passed_tests'] / summary['total_tests']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print()
        print("Category Results:")
        print("-" * 50)
        
        for category, result in self.results['test_categories'].items():
            status = result.get('status', 'UNKNOWN')
            duration = result.get('duration', 0)
            tests_run = result.get('tests_run', 0)
            
            print(f"{category:35} {status:8} ({tests_run:2d} tests, {duration:5.2f}s)")
        
        # Security Summary
        print()
        print("Security Summary:")
        print("-" * 50)
        security_metrics = self.results.get('security_metrics', {})
        print(f"Security Score: {security_metrics.get('security_score', 0):.1f}%")
        print(f"Compliance Level: {security_metrics.get('compliance_level', 'UNKNOWN')}")
        
        # Compliance Status
        print()
        print("Phase 3 Compliance Status:")
        print("-" * 50)
        compliance = self.results.get('compliance_status', {})
        print(f"Overall Status: {compliance.get('overall_status', 'UNKNOWN')}")
        print(f"Compliance: {compliance.get('compliance_percentage', 0):.1f}%")
        
        print()
        print("Recommendations:")
        print("-" * 50)
        
        for rec in self.results['recommendations']:
            rec_type = rec['type']
            priority = rec['priority']
            message = rec['message']
            print(f"[{rec_type}] ({priority}) {message}")
        
        print()
    
    def _generate_html_report(self):
        """Generate comprehensive HTML report"""
        report_file = self.base_path / 'phase3_test_report.html'
        
        html_content = self._create_html_report()
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report generated: {report_file}")
    
    def _create_html_report(self):
        """Create comprehensive HTML report content"""
        summary = self.results['execution_summary']
        compliance = self.results.get('compliance_status', {})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>RFU Phase 3 Advanced Testing Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
        .metric h3 {{ margin: 0; color: #495057; }}
        .metric .number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .compliance {{ margin: 20px 0; padding: 15px; border-radius: 5px; }}
        .compliance-excellent {{ background-color: #d4edda; }}
        .compliance-good {{ background-color: #d1ecf1; }}
        .compliance-poor {{ background-color: #f8d7da; }}
        .category {{ margin: 15px 0; padding: 15px; border: 1px solid #dee2e6; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>RFU Phase 3 Advanced Testing Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Duration:</strong> {summary['total_duration']:.2f} seconds</p>
        <p><strong>Phase:</strong> Week 9-12 End-to-End & Performance/Security</p>
    </div>

    <div class="compliance">
        <h2>Phase 3 Compliance Status</h2>
        <p><strong>Overall:</strong> {compliance.get('overall_status', 'UNKNOWN')}</p>
        <p><strong>Compliance:</strong> {compliance.get('compliance_percentage', 0):.1f}%</p>
    </div>

    <div class="summary">
        <div class="metric">
            <h3>Total Tests</h3>
            <div class="number">{summary['total_tests']}</div>
        </div>
        <div class="metric">
            <h3>Passed</h3>
            <div class="number passed">{summary['passed_tests']}</div>
        </div>
        <div class="metric">
            <h3>Failed</h3>
            <div class="number failed">{summary['failed_tests']}</div>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <div class="number">
                {(summary['passed_tests'] / max(1, summary['total_tests']) * 100):.1f}%
            </div>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def save_results(self, filename=None):
        """Save results to JSON file"""
        if filename is None:
            filename = f"phase3_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        results_file = self.base_path / filename
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"Results saved to: {results_file}")
        return results_file


def main():
    """Main entry point for the Phase 3 test runner"""
    parser = argparse.ArgumentParser(
        description='RFU Phase 3 Advanced Integration Test Runner')
    
    parser.add_argument(
        '--categories', 
        nargs='*', 
        choices=list(ALL_TESTS.keys()) + ['week9-10', 'week11-12'],
        help='Specific test categories to run (default: all)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--no-html',
        action='store_true',
        help='Skip HTML report generation'
    )
    
    parser.add_argument(
        '--skip-slow',
        action='store_true',
        help='Skip slow-running tests'
    )
    
    parser.add_argument(
        '--save-results',
        help='Save results to specified JSON file'
    )
    
    args = parser.parse_args()
    
    # Handle special category groups
    test_categories = None
    if args.categories:
        if 'week9-10' in args.categories:
            test_categories = list(WEEK_9_10_TESTS.keys())
        elif 'week11-12' in args.categories:
            test_categories = list(WEEK_11_12_TESTS.keys())
        else:
            test_categories = args.categories
    
    # Create and run test runner
    runner = Phase3TestRunner()
    
    try:
        results = runner.run_tests(
            test_categories=test_categories,
            verbose=args.verbose,
            generate_html=not args.no_html,
            skip_slow=args.skip_slow
        )
        
        # Save results if requested
        if args.save_results:
            runner.save_results(args.save_results)
        
        # Exit with appropriate code
        failed_tests = results['execution_summary']['failed_tests']
        error_tests = results['execution_summary']['error_tests']
        
        if failed_tests > 0 or error_tests > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()