#!/usr/bin/env python3
import argparse
import sys
import os
import subprocess
import multiprocessing

def parse_args():
    parser = argparse.ArgumentParser(description='Run RFU test suite')
    parser.add_argument('--no-gui', action='store_true',
                       help='Skip GUI tests')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--parallel', action='store_true',
                       help='Run tests in parallel')
    parser.add_argument('--junit-xml', action='store_true',
                       help='Generate JUnit XML report')
    parser.add_argument('--pattern', type=str,
                       help='Only run tests matching this pattern')
    parser.add_argument('--markers', type=str,
                       help='Only run tests with these markers (comma-separated)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    return parser.parse_args()

def build_pytest_command(args):
    cmd = ['python', '-m', 'pytest']
    
    # Add verbosity
    if args.verbose:
        cmd.append('-v')
    
    # Handle GUI test exclusion
    if args.no_gui:
        cmd.extend(['-m', 'not gui'])
    
    # Handle parallel execution
    if args.parallel:
        cpu_count = multiprocessing.cpu_count()
        cmd.extend(['-n', str(cpu_count)])
    
    # Handle coverage
    if args.coverage:
        cmd.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
    
    # Handle JUnit XML report
    if args.junit_xml:
        cmd.extend(['--junitxml=test-reports/junit.xml'])
    
    # Handle test pattern
    if args.pattern:
        cmd.extend(['-k', args.pattern])
    
    # Handle specific markers
    if args.markers:
        markers = args.markers.split(',')
        marker_expr = ' or '.join(markers)
        cmd.extend(['-m', marker_expr])
    
    return cmd

def setup_environment():
    """Set up the test environment"""
    # Create test-reports directory if it doesn't exist
    os.makedirs('test-reports', exist_ok=True)
    
    # Set up virtual display for Linux GUI tests
    if sys.platform.startswith('linux'):
        try:
            from xvfbwrapper import Xvfb
            vdisplay = Xvfb()
            vdisplay.start()
            return vdisplay
        except ImportError:
            print("Warning: xvfbwrapper not installed. GUI tests may fail on Linux.")
            return None
    return None

def clean_previous_runs():
    """Clean up artifacts from previous test runs"""
    # Clean coverage data
    if os.path.exists('.coverage'):
        os.remove('.coverage')
    
    # Clean HTML coverage report
    if os.path.exists('htmlcov'):
        import shutil
        shutil.rmtree('htmlcov')
    
    # Clean pytest cache
    if os.path.exists('.pytest_cache'):
        import shutil
        shutil.rmtree('.pytest_cache')

def run_tests(args):
    """Run the test suite with the specified options"""
    # Clean up from previous runs
    clean_previous_runs()
    
    # Set up test environment
    vdisplay = setup_environment()
    
    try:
        # Build and run pytest command
        cmd = build_pytest_command(args)
        print(f"Running tests with command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False)
        
        # Handle test results
        if result.returncode == 0:
            print("\nAll tests passed successfully!")
            if args.coverage:
                print("\nCoverage report generated in htmlcov/index.html")
            return 0
        else:
            print(f"\nTests failed with return code: {result.returncode}")
            return result.returncode
            
    finally:
        # Clean up virtual display if used
        if vdisplay:
            vdisplay.stop()

def main():
    args = parse_args()
    try:
        return run_tests(args)
    except KeyboardInterrupt:
        print("\nTest execution cancelled by user")
        return 130
    except Exception as e:
        print(f"\nError running tests: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())