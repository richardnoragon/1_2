#!/usr/bin/env python3
"""
Enterprise Test Runner Script
Phase 4: Testing & QA (Week 10) - Automated Test Execution

This script provides a command-line interface for running enterprise-grade
tests with comprehensive reporting and CI/CD integration.
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.phase4_enterprise_testing.enterprise_test_executor import \
    EnterpriseTestExecutor


def main():
    """Main entry point for test execution."""
    parser = argparse.ArgumentParser(
        description="Enterprise Test Runner for Advanced Folders System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                           # Run all test suites
  python run_tests.py --suite unit              # Run unit tests only
  python run_tests.py --suite security          # Run security tests only
  python run_tests.py --ci-cd                   # CI/CD integration mode
  python run_tests.py --coverage                # Generate coverage report
  python run_tests.py --performance             # Run performance tests
        """
    )
    
    # Test suite selection
    parser.add_argument(
        "--suite", 
        choices=['unit', 'integration', 'performance', 'security', 'all'],
        default='all',
        help="Test suite to run (default: all)"
    )
    
    # Output configuration
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="test_reports",
        help="Output directory for test reports (default: test_reports)"
    )
    
    # Execution modes
    parser.add_argument(
        "--ci-cd", 
        action="store_true",
        help="Run in CI/CD integration mode"
    )
    
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate detailed coverage reports"
    )
    
    parser.add_argument(
        "--performance", 
        action="store_true",
        help="Include performance benchmarking"
    )
    
    parser.add_argument(
        "--security", 
        action="store_true",
        help="Include comprehensive security testing"
    )
    
    parser.add_argument(
        "--parallel", 
        action="store_true",
        help="Run test suites in parallel (when supported)"
    )
    
    # Verbosity and reporting
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--quiet", "-q", 
        action="store_true",
        help="Quiet output (errors only)"
    )
    
    parser.add_argument(
        "--html-report", 
        action="store_true",
        help="Generate HTML reports"
    )
    
    parser.add_argument(
        "--json-report", 
        action="store_true",
        help="Generate JSON reports"
    )
    
    # Quality gates
    parser.add_argument(
        "--fail-under", 
        type=float, 
        default=90.0,
        help="Minimum coverage percentage required (default: 90.0)"
    )
    
    parser.add_argument(
        "--max-failures", 
        type=int, 
        default=0,
        help="Maximum allowed test failures (default: 0)"
    )
    
    args = parser.parse_args()
    
    # Initialize test executor
    output_dir = Path(args.output_dir).resolve()
    executor = EnterpriseTestExecutor(project_root, output_dir)
    
    print("🚀 Advanced Folders System - Enterprise Test Runner")
    print("=" * 60)
    print(f"Project Root: {project_root}")
    print(f"Output Directory: {output_dir}")
    print(f"Test Suite: {args.suite}")
    
    try:
        if args.ci_cd:
            print("\n🔧 Running in CI/CD Integration Mode...")
            success = executor.run_ci_cd_integration()
            exit_code = 0 if success else 1
            
        elif args.suite == 'all':
            print("\n🧪 Running All Test Suites...")
            results = executor.execute_all_test_suites(parallel=args.parallel)
            
            # Check quality gates
            summary = results['summary']
            exit_code = 0
            
            # Coverage check
            if summary.get('success_rate', 0) < args.fail_under:
                print(f"❌ Coverage below threshold: {summary.get('success_rate', 0):.1f}% < {args.fail_under}%")
                exit_code = 1
            
            # Failure check
            if summary.get('total_failed', 0) > args.max_failures:
                print(f"❌ Too many failures: {summary.get('total_failed', 0)} > {args.max_failures}")
                exit_code = 1
            
            # Overall status check
            if summary.get('overall_status') != 'passed':
                print(f"❌ Overall test status: {summary.get('overall_status')}")
                exit_code = 1
            
            if exit_code == 0:
                print("✅ All quality gates passed!")
            
        else:
            print(f"\n🧪 Running {args.suite.title()} Test Suite...")
            
            if not executor.validate_test_environment():
                print("❌ Environment validation failed")
                sys.exit(1)
            
            result = executor.execute_test_suite(args.suite)
            
            # Determine exit code based on results
            if result['status'] == 'passed':
                exit_code = 0
                print(f"✅ {args.suite.title()} tests passed!")
            else:
                exit_code = 1
                print(f"❌ {args.suite.title()} tests failed: {result['status']}")
        
        # Final reporting
        if args.verbose or not args.quiet:
            print(f"\n📊 Test execution completed with exit code: {exit_code}")
            print(f"📁 Reports available in: {output_dir}")
            
            if output_dir.exists():
                reports = list(output_dir.glob("*.html")) + list(output_dir.glob("*.json"))
                if reports:
                    print("📋 Generated reports:")
                    for report in sorted(reports):
                        print(f"   - {report.name}")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()