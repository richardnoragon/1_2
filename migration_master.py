#!/usr/bin/env python3
"""
Migration Master Controller
==========================

This script provides a unified interface for executing the complete migration
from src/utilities to src/tools directory structure.

Features:
- Interactive migration wizard
- Automated pre-checks and validation
- Step-by-step execution
- Real-time progress monitoring
- Automatic rollback on failure
- Comprehensive reporting

Usage:
    python migration_master.py [--interactive] [--auto] [--status]
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MigrationMaster:
    """Master controller for the complete migration process."""
    
    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        self.project_root = Path(__file__).parent
        self.setup_logging()
        
        # Migration state tracking
        self.migration_state = {
            "phase": "not_started",
            "current_step": None,
            "start_time": None,
            "backup_dir": None,
            "rollback_script": None,
            "success": False,
            "errors": []
        }
        
        # Load previous state if exists
        self.load_migration_state()
    
    def setup_logging(self):
        """Setup master controller logging."""
        log_dir = self.project_root / "migration_master_logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"migration_master_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Migration Master Controller started")
    
    def load_migration_state(self):
        """Load previous migration state if exists."""
        state_file = self.project_root / "migration_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    saved_state = json.load(f)
                    self.migration_state.update(saved_state)
                self.logger.info("Loaded previous migration state")
            except Exception as e:
                self.logger.warning(f"Could not load migration state: {e}")
    
    def save_migration_state(self):
        """Save current migration state."""
        state_file = self.project_root / "migration_state.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(self.migration_state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save migration state: {e}")
    
    def print_banner(self):
        """Print migration banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Migration Master Controller               ║
║                                                              ║
║    Automated Migration: src/utilities → src/tools           ║
║                                                              ║
║    This tool will safely migrate all contents from          ║
║    src/utilities to src/tools with full backup and          ║
║    rollback capabilities.                                    ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Check all prerequisites for migration."""
        self.logger.info("Checking migration prerequisites...")
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Disk Space", self.check_disk_space),
            ("Project Structure", self.check_project_structure),
            ("Dependencies", self.check_dependencies),
            ("File Permissions", self.check_permissions)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "[PASS]" if result else "[FAIL]"
                self.logger.info(f"{check_name}: {status}")
                if not result:
                    all_passed = False
            except Exception as e:
                self.logger.error(f"{check_name}: [ERROR] - {e}")
                all_passed = False
        
        return all_passed
    
    def check_python_version(self) -> bool:
        """Check Python version."""
        return sys.version_info >= (3, 7)
    
    def check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.project_root)
            # Need at least 2GB free space
            return free > 2 * 1024 * 1024 * 1024
        except Exception:
            return False
    
    def check_project_structure(self) -> bool:
        """Check project structure."""
        required_paths = [
            "src",
            "src/utilities",
            "src/rfu"
        ]
        
        for path in required_paths:
            if not (self.project_root / path).exists():
                return False
        
        return True
    
    def check_dependencies(self) -> bool:
        """Check required dependencies."""
        try:
            import PyQt5
            return True
        except ImportError:
            return False
    
    def check_permissions(self) -> bool:
        """Check file permissions."""
        try:
            # Test write permission
            test_file = self.project_root / "permission_test.tmp"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
    
    def get_user_confirmation(self, message: str) -> bool:
        """Get user confirmation for interactive mode."""
        if not self.interactive:
            return True
        
        while True:
            response = input(f"\n{message} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def run_script(self, script_name: str, args: List[str] = None) -> Tuple[bool, str]:
        """Run a migration script and return success status and output."""
        cmd = [sys.executable, script_name]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Script execution timed out"
        except Exception as e:
            return False, f"Script execution failed: {e}"
    
    def execute_migration_phase(self, phase_name: str, phase_func) -> bool:
        """Execute a migration phase with error handling."""
        self.migration_state["phase"] = phase_name
        self.migration_state["current_step"] = phase_name
        self.save_migration_state()
        
        self.logger.info(f"Starting phase: {phase_name}")
        
        try:
            success = phase_func()
            if success:
                self.logger.info(f"Phase completed successfully: {phase_name}")
            else:
                self.logger.error(f"Phase failed: {phase_name}")
                self.migration_state["errors"].append(f"Phase failed: {phase_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Phase crashed: {phase_name} - {e}")
            self.migration_state["errors"].append(f"Phase crashed: {phase_name} - {e}")
            return False
    
    def phase_pre_migration_tests(self) -> bool:
        """Phase 1: Run pre-migration tests."""
        success, output = self.run_script("migration_testing.py", ["--pre-migration"])
        
        if not success:
            self.logger.error("Pre-migration tests failed")
            self.logger.error(output)
        
        return success
    
    def phase_migration_execution(self) -> bool:
        """Phase 2: Execute migration."""
        # First run dry run
        self.logger.info("Running migration dry run...")
        success, output = self.run_script("migration_automation.py", ["--dry-run"])
        
        if not success:
            self.logger.error("Migration dry run failed")
            self.logger.error(output)
            return False
        
        # Get user confirmation for actual migration
        if not self.get_user_confirmation("Dry run successful. Proceed with actual migration?"):
            self.logger.info("Migration cancelled by user")
            return False
        
        # Execute actual migration
        self.logger.info("Executing actual migration...")
        success, output = self.run_script("migration_automation.py")
        
        if success:
            # Extract backup directory from output
            lines = output.split('\n')
            for line in lines:
                if "Backup available at:" in line:
                    self.migration_state["backup_dir"] = line.split(":")[-1].strip()
                elif "Rollback script:" in line:
                    self.migration_state["rollback_script"] = line.split(":")[-1].strip()
        
        return success
    
    def phase_post_migration_validation(self) -> bool:
        """Phase 3: Post-migration validation."""
        success, output = self.run_script("migration_validation.py", ["--all"])
        
        if not success:
            self.logger.error("Post-migration validation failed")
            self.logger.error(output)
        
        return success
    
    def phase_post_migration_tests(self) -> bool:
        """Phase 4: Post-migration tests."""
        success, output = self.run_script("migration_testing.py", ["--post-migration"])
        
        if not success:
            self.logger.error("Post-migration tests failed")
            self.logger.error(output)
        
        return success
    
    def execute_rollback(self) -> bool:
        """Execute rollback procedure."""
        self.logger.info("Initiating rollback procedure...")
        
        if self.migration_state.get("rollback_script"):
            rollback_script = self.migration_state["rollback_script"]
            success, output = self.run_script(rollback_script)
            
            if success:
                self.logger.info("Rollback completed successfully")
                # Reset migration state
                self.migration_state = {
                    "phase": "rolled_back",
                    "success": False,
                    "rollback_completed": True
                }
                self.save_migration_state()
                return True
            else:
                self.logger.error("Rollback failed")
                self.logger.error(output)
                return False
        else:
            self.logger.error("No rollback script available")
            return False
    
    def run_interactive_migration(self) -> bool:
        """Run interactive migration with user prompts."""
        self.print_banner()
        
        # Show current state
        if self.migration_state.get("phase") != "not_started":
            print(f"\nPrevious migration detected:")
            print(f"Phase: {self.migration_state.get('phase')}")
            print(f"Success: {self.migration_state.get('success')}")
            
            if not self.get_user_confirmation("Start new migration (this will reset state)?"):
                return False
        
        # Prerequisites check
        print("\n" + "="*60)
        print("STEP 1: Prerequisites Check")
        print("="*60)
        
        if not self.check_prerequisites():
            print("\n[FAIL] Prerequisites check failed!")
            print("Please fix the issues above before proceeding.")
            return False
        
        print("\n[PASS] All prerequisites passed!")
        
        if not self.get_user_confirmation("Proceed with migration?"):
            return False
        
        # Initialize migration state
        self.migration_state = {
            "phase": "started",
            "start_time": datetime.now().isoformat(),
            "success": False,
            "errors": []
        }
        
        # Execute migration phases
        phases = [
            ("Pre-Migration Tests", self.phase_pre_migration_tests),
            ("Migration Execution", self.phase_migration_execution),
            ("Post-Migration Validation", self.phase_post_migration_validation),
            ("Post-Migration Tests", self.phase_post_migration_tests)
        ]
        
        for phase_name, phase_func in phases:
            print(f"\n" + "="*60)
            print(f"STEP: {phase_name}")
            print("="*60)
            
            success = self.execute_migration_phase(phase_name, phase_func)
            
            if not success:
                print(f"\n[FAIL] {phase_name} failed!")
                
                if self.get_user_confirmation("Attempt rollback?"):
                    if self.execute_rollback():
                        print("\n[PASS] Rollback completed successfully")
                    else:
                        print("\n[FAIL] Rollback failed - manual intervention required")
                
                return False
            
            print(f"\n[PASS] {phase_name} completed successfully!")
        
        # Migration completed successfully
        self.migration_state["phase"] = "completed"
        self.migration_state["success"] = True
        self.save_migration_state()
        
        print("\n" + "="*60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY! 🎉")
        print("="*60)
        print(f"Backup available at: {self.migration_state.get('backup_dir', 'Unknown')}")
        print(f"Total time: {self.calculate_migration_time()}")
        
        return True
    
    def run_automated_migration(self) -> bool:
        """Run fully automated migration without user interaction."""
        self.logger.info("Starting automated migration...")
        
        # Prerequisites check
        if not self.check_prerequisites():
            self.logger.error("Prerequisites check failed")
            return False
        
        # Initialize migration state
        self.migration_state = {
            "phase": "started",
            "start_time": datetime.now().isoformat(),
            "success": False,
            "errors": []
        }
        
        # Execute all phases
        phases = [
            ("Pre-Migration Tests", self.phase_pre_migration_tests),
            ("Migration Execution", self.phase_migration_execution),
            ("Post-Migration Validation", self.phase_post_migration_validation),
            ("Post-Migration Tests", self.phase_post_migration_tests)
        ]
        
        for phase_name, phase_func in phases:
            success = self.execute_migration_phase(phase_name, phase_func)
            
            if not success:
                self.logger.error(f"Automated migration failed at: {phase_name}")
                # Automatic rollback in automated mode
                self.execute_rollback()
                return False
        
        # Migration completed successfully
        self.migration_state["phase"] = "completed"
        self.migration_state["success"] = True
        self.save_migration_state()
        
        self.logger.info("Automated migration completed successfully")
        return True
    
    def show_migration_status(self):
        """Show current migration status."""
        print("\n" + "="*60)
        print("MIGRATION STATUS")
        print("="*60)
        
        print(f"Phase: {self.migration_state.get('phase', 'Unknown')}")
        print(f"Success: {self.migration_state.get('success', False)}")
        
        if self.migration_state.get('start_time'):
            print(f"Start Time: {self.migration_state['start_time']}")
            print(f"Duration: {self.calculate_migration_time()}")
        
        if self.migration_state.get('backup_dir'):
            print(f"Backup Directory: {self.migration_state['backup_dir']}")
        
        if self.migration_state.get('rollback_script'):
            print(f"Rollback Script: {self.migration_state['rollback_script']}")
        
        if self.migration_state.get('errors'):
            print(f"\nErrors ({len(self.migration_state['errors'])}):")
            for error in self.migration_state['errors']:
                print(f"  - {error}")
        
        # Check current directory state
        utilities_exists = (self.project_root / "src" / "utilities").exists()
        tools_exists = (self.project_root / "src" / "tools").exists()
        
        print(f"\nDirectory Status:")
        print(f"  src/utilities exists: {utilities_exists}")
        print(f"  src/tools exists: {tools_exists}")
        
        if utilities_exists and tools_exists:
            utilities_files = len(list((self.project_root / "src" / "utilities").rglob("*.py")))
            tools_files = len(list((self.project_root / "src" / "tools").rglob("*.py")))
            print(f"  Python files in utilities: {utilities_files}")
            print(f"  Python files in tools: {tools_files}")
    
    def calculate_migration_time(self) -> str:
        """Calculate migration duration."""
        if not self.migration_state.get('start_time'):
            return "Unknown"
        
        start_time = datetime.fromisoformat(self.migration_state['start_time'])
        duration = datetime.now() - start_time
        
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Migration Master Controller")
    parser.add_argument("--interactive", action="store_true", default=True,
                       help="Run in interactive mode (default)")
    parser.add_argument("--auto", action="store_true",
                       help="Run in fully automated mode")
    parser.add_argument("--status", action="store_true",
                       help="Show migration status")
    parser.add_argument("--rollback", action="store_true",
                       help="Execute rollback procedure")
    
    args = parser.parse_args()
    
    # Create master controller
    interactive_mode = not args.auto
    master = MigrationMaster(interactive=interactive_mode)
    
    # Handle different modes
    if args.status:
        master.show_migration_status()
        return 0
    
    if args.rollback:
        success = master.execute_rollback()
        return 0 if success else 1
    
    # Run migration
    if args.auto:
        success = master.run_automated_migration()
    else:
        success = master.run_interactive_migration()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())