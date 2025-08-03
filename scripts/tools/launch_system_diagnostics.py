#!/usr/bin/env python3
"""
System Diagnostics Launcher Script

This script provides multiple ways to launch the System Diagnostics tool:
1. GUI mode (default)
2. Command-line mode
3. Test mode
4. Diagnostic mode

Usage:
    python launch_system_diagnostics.py [options]

Options:
    --gui           Launch GUI mode (default)
    --cli           Launch command-line mode
    --test          Run diagnostic tests
    --check         Check system dependencies
    --help          Show this help message
"""

import sys
import os
import argparse
from typing import Optional

def check_dependencies():
    """Check and report system dependencies."""
    print("System Diagnostics - Dependency Check")
    print("=" * 50)
    
    dependencies = {
        'PyQt5': 'GUI framework for the main interface',
        'psutil': 'System and process monitoring',
        'matplotlib': 'Charts and visualizations',
        'numpy': 'Numerical computations for analysis'
    }
    
    available = []
    missing = []
    
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            available.append((dep, description))
            print(f"✓ {dep:<12} - {description}")
        except ImportError:
            missing.append((dep, description))
            print(f"✗ {dep:<12} - {description} (MISSING)")
    
    print(f"\nSummary: {len(available)}/{len(dependencies)} dependencies available")
    
    if missing:
        print("\nTo install missing dependencies:")
        for dep, _ in missing:
            print(f"  pip install {dep}")
    
    return len(missing) == 0

def launch_gui_mode(hub_integration: bool = False):
    """Launch the GUI mode."""
    try:
        print("Launching System Diagnostics GUI...")
        
        # Check PyQt5 availability
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            print("Error: PyQt5 is required for GUI mode.")
            print("Install with: pip install PyQt5")
            return False
        
        # Import diagnostics components
        from src.utilities.system.diagnostics_monitoring import (
            create_system_diagnostics_gui,
            MAIN_GUI_AVAILABLE
        )
        
        if not MAIN_GUI_AVAILABLE:
            print("Error: System Diagnostics GUI is not available.")
            print("Please check dependencies and try again.")
            return False
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create GUI
        if hub_integration:
            # Mock hub for standalone mode
            class MockHub:
                def update_tool_progress(self, tool_name, percentage, message):
                    print(f"Progress: {tool_name} - {percentage}% - {message}")
                
                def update_tool_status(self, tool_name, status):
                    print(f"Status: {tool_name} - {status}")
                
                def register_tool(self, tool_name, tool_instance):
                    print(f"Registered: {tool_name}")
                    return True
            
            hub = MockHub()
            gui = create_system_diagnostics_gui(hub_instance=hub)
        else:
            gui = create_system_diagnostics_gui()
        
        if gui:
            gui.show()
            print("System Diagnostics GUI launched successfully!")
            print("Close the window to exit.")
            return app.exec_() == 0
        else:
            print("Error: Failed to create System Diagnostics GUI.")
            return False
            
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return False

def launch_cli_mode():
    """Launch command-line mode."""
    print("System Diagnostics - Command Line Mode")
    print("=" * 50)
    
    try:
        # Import core components
        from src.utilities.system.diagnostics_monitoring import (
            PlatformDetector,
            CORE_AVAILABLE
        )
        
        if not CORE_AVAILABLE:
            print("Warning: Core components not fully available.")
            print("Some features may be limited.")
        
        # Platform information
        if PlatformDetector:
            print("\n1. Platform Information:")
            print("-" * 30)
            detector = PlatformDetector()
            platform_info = detector.get_platform_info()
            
            for key, value in platform_info.items():
                print(f"  {key.title()}: {value}")
        
        # System monitoring
        print("\n2. System Monitoring:")
        print("-" * 30)
        
        try:
            import psutil
            
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            print(f"  CPU Usage: {cpu_percent}%")
            print(f"  CPU Cores: {cpu_count}")
            
            # Memory information
            memory = psutil.virtual_memory()
            print(f"  Memory Usage: {memory.percent}%")
            print(f"  Memory Total: {memory.total / (1024**3):.1f} GB")
            print(f"  Memory Available: {memory.available / (1024**3):.1f} GB")
            
            # Disk information
            disk = psutil.disk_usage('/')
            print(f"  Disk Usage: {(disk.used / disk.total) * 100:.1f}%")
            print(f"  Disk Total: {disk.total / (1024**3):.1f} GB")
            print(f"  Disk Free: {disk.free / (1024**3):.1f} GB")
            
        except ImportError:
            print("  psutil not available - install with: pip install psutil")
        except Exception as e:
            print(f"  Error getting system info: {e}")
        
        # Battery information (if available)
        print("\n3. Battery Information:")
        print("-" * 30)
        
        try:
            import psutil
            battery = psutil.sensors_battery()
            
            if battery:
                print(f"  Battery Level: {battery.percent}%")
                print(f"  Power Plugged: {'Yes' if battery.power_plugged else 'No'}")
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    hours = battery.secsleft // 3600
                    minutes = (battery.secsleft % 3600) // 60
                    print(f"  Time Remaining: {hours}h {minutes}m")
            else:
                print("  No battery detected")
                
        except (ImportError, AttributeError):
            print("  Battery monitoring not available")
        except Exception as e:
            print(f"  Error getting battery info: {e}")
        
        print("\nCommand-line diagnostics completed.")
        return True
        
    except Exception as e:
        print(f"Error in CLI mode: {e}")
        return False

def run_tests():
    """Run diagnostic tests."""
    print("Running System Diagnostics Tests...")
    
    try:
        # Import and run the test script
        import subprocess
        result = subprocess.run([
            sys.executable, 'test_system_diagnostics.py'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="System Diagnostics Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch_system_diagnostics.py              # Launch GUI
  python launch_system_diagnostics.py --cli        # Command-line mode
  python launch_system_diagnostics.py --test       # Run tests
  python launch_system_diagnostics.py --check      # Check dependencies
        """
    )
    
    parser.add_argument('--gui', action='store_true', default=True,
                       help='Launch GUI mode (default)')
    parser.add_argument('--cli', action='store_true',
                       help='Launch command-line mode')
    parser.add_argument('--test', action='store_true',
                       help='Run diagnostic tests')
    parser.add_argument('--check', action='store_true',
                       help='Check system dependencies')
    parser.add_argument('--hub', action='store_true',
                       help='Enable hub integration (GUI mode only)')
    
    args = parser.parse_args()
    
    # If no specific mode is chosen, default to GUI
    if not any([args.cli, args.test, args.check]):
        args.gui = True
    
    success = True
    
    try:
        if args.check:
            success = check_dependencies()
        
        if args.test:
            success = run_tests() and success
        
        if args.cli:
            success = launch_cli_mode() and success
        
        if args.gui and not args.cli:
            success = launch_gui_mode(hub_integration=args.hub) and success
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        success = False
    except Exception as e:
        print(f"Unexpected error: {e}")
        success = False
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())