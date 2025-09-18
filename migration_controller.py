#!/usr/bin/env python3
"""
Advanced Folders Migration Executive Controller
==============================================

This script orchestrates the complete migration process for moving
src/advanced_folders to src/tools/file_management/advanced_folders_legacy.

It provides a unified interface for:
- Pre-migration validation
- Migration execution  
- Post-migration validation
- Rollback if needed

Author: GitHub Copilot
Date: September 17, 2025
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class MigrationController:
    """Controls the entire migration process"""
    
    def __init__(self):
        self.root_path = Path(".").resolve()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Script paths
        self.migration_script = self.root_path / "comprehensive_advanced_folders_migration_plan.py"
        self.validation_script = self.root_path / "migration_validation_tools.py"
        
        # Documentation paths
        self.migration_plan = self.root_path / "COMPREHENSIVE_ADVANCED_FOLDERS_MIGRATION_PLAN.md"
        self.rollback_guide = self.root_path / "ADVANCED_FOLDERS_MIGRATION_ROLLBACK_STRATEGY.md"

    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'=' * 60}")
        print(f"{title:^60}")
        print(f"{'=' * 60}")

    def print_status(self, message: str, status: str = "INFO"):
        """Print formatted status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")

    def run_command(self, command: list, description: str) -> bool:
        """Run a command and return success status"""
        self.print_status(f"Running: {description}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, cwd=self.root_path)
            if result.returncode == 0:
                self.print_status(f"[SUCCESS] {description} completed successfully", "SUCCESS")
                if result.stdout.strip():
                    print(result.stdout)
                return True
            else:
                self.print_status(f"[FAILED] {description} failed", "ERROR")
                if result.stderr.strip():
                    print(f"Error: {result.stderr}")
                return False
        except Exception as e:
            self.print_status(f"[FAILED] {description} failed with exception: {e}", "ERROR")
            return False

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.print_header("PREREQUISITES CHECK")
        
        # Check Python version
        if sys.version_info < (3, 7):
            self.print_status("Python 3.7+ required", "ERROR")
            return False
        self.print_status(f"Python version: {sys.version}", "SUCCESS")
        
        # Check if migration script exists
        if not self.migration_script.exists():
            self.print_status(f"Migration script not found: {self.migration_script}", "ERROR")
            return False
        self.print_status("Migration script found", "SUCCESS")
        
        # Check if validation script exists
        if not self.validation_script.exists():
            self.print_status(f"Validation script not found: {self.validation_script}", "ERROR")
            return False
        self.print_status("Validation script found", "SUCCESS")
        
        # Check source directory
        source_path = self.root_path / "src" / "advanced_folders"
        if not source_path.exists():
            self.print_status(f"Source directory not found: {source_path}", "ERROR")
            return False
        self.print_status("Source directory found", "SUCCESS")
        
        # Check write permissions
        try:
            test_file = self.root_path / "migration_test.tmp"
            test_file.touch()
            test_file.unlink()
            self.print_status("Write permissions verified", "SUCCESS")
        except Exception as e:
            self.print_status(f"No write permissions: {e}", "ERROR")
            return False
        
        return True

    def run_pre_migration_validation(self) -> bool:
        """Run pre-migration validation"""
        self.print_header("PRE-MIGRATION VALIDATION")
        
        return self.run_command(
            [sys.executable, str(self.validation_script), "pre"],
            "Pre-migration validation"
        )

    def execute_migration(self) -> bool:
        """Execute the migration"""
        self.print_header("MIGRATION EXECUTION")
        
        return self.run_command(
            [sys.executable, str(self.migration_script), "automated"],
            "Migration execution"
        )

    def run_post_migration_validation(self) -> bool:
        """Run post-migration validation"""
        self.print_header("POST-MIGRATION VALIDATION")
        
        return self.run_command(
            [sys.executable, str(self.validation_script), "post"],
            "Post-migration validation"
        )

    def display_summary(self, success: bool):
        """Display migration summary"""
        self.print_header("MIGRATION SUMMARY")
        
        if success:
            print("[SUCCESS] MIGRATION COMPLETED SUCCESSFULLY!")
            print("\n[+] What was accomplished:")
            print("   - Source directory migrated to legacy location")
            print("   - All import statements updated")
            print("   - Test files migrated and updated")
            print("   - Documentation updated")
            print("   - Backup created for rollback")
            print("   - Validation tests passed")
            
            print("\n[NEXT] Next Steps:")
            print("   1. Run your application tests")
            print("   2. Verify functionality in development environment")
            print("   3. Test integration with existing advanced_folders")
            print("   4. Deploy to staging environment for testing")
            print("   5. If satisfied, remove original source (optional)")
            
            print("\n[FILES] Important Files:")
            print(f"   - Migration Plan: {self.migration_plan}")
            print(f"   - Rollback Guide: {self.rollback_guide}")
            print("   - Migration Report: migration_report_*.json")
            print("   - Validation Report: migration_validation_report_*.json")
            print("   - Backup Location: migration_backup_*")
            
        else:
            print("[FAILED] MIGRATION FAILED!")
            print("\n[TROUBLESHOOTING] Steps:")
            print("   1. Check the migration logs for detailed error information")
            print("   2. Review the validation report")
            print("   3. If needed, use the rollback strategy")
            print("   4. Contact technical support if issues persist")
            
            print("\n[FILES] Check These Files:")
            print("   • Migration logs in console output")
            print("   • Error details in generated reports")
            print(f"   • Rollback guide: {self.rollback_guide}")

    def interactive_migration(self) -> bool:
        """Run interactive migration with user prompts"""
        self.print_header("ADVANCED FOLDERS MIGRATION")
        
        print("This tool will migrate src/advanced_folders to src/tools/file_management/advanced_folders_legacy")
        print("while preserving the existing advanced_folders implementation.")
        print("\nThe migration includes:")
        print("- File structure migration")
        print("- Import statement updates")
        print("- Test file migration")
        print("- Documentation updates")
        print("• Comprehensive backup and rollback capability")
        
        # Get user confirmation
        response = input("\nDo you want to proceed with the migration? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled by user.")
            return False
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\nPrerequisites check failed. Please resolve issues before proceeding.")
            return False
        
        # Pre-migration validation
        if not self.run_pre_migration_validation():
            print("\nPre-migration validation failed.")
            response = input("Do you want to continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled due to validation failures.")
                return False
        
        # Execute migration
        if not self.execute_migration():
            print("\nMigration execution failed.")
            self.print_status("Check migration logs for details", "ERROR")
            return False
        
        # Post-migration validation
        if not self.run_post_migration_validation():
            print("\nPost-migration validation failed.")
            self.print_status("Migration completed but validation failed", "WARNING")
            response = input("Do you want to proceed with rollback? (y/N): ")
            if response.lower() == 'y':
                self.print_status("Please run the rollback script manually", "INFO")
                return False
        
        return True

    def automated_migration(self) -> bool:
        """Run fully automated migration (no user interaction)"""
        success = True
        success &= self.check_prerequisites()
        success &= self.run_pre_migration_validation()
        
        if success:
            success &= self.execute_migration()
            success &= self.run_post_migration_validation()
        
        return success

    def validation_only(self, mode: str = "complete") -> bool:
        """Run validation only (no migration)"""
        self.print_header(f"VALIDATION ONLY - {mode.upper()}")
        
        return self.run_command(
            [sys.executable, str(self.validation_script), mode],
            f"Validation ({mode})"
        )

    def show_help(self):
        """Show help information"""
        help_text = """
Advanced Folders Migration Controller

Usage:
    python migration_controller.py [command]

Commands:
    interactive     Run interactive migration with user prompts (default)
    automated       Run fully automated migration
    validate        Run validation only (post-migration)
    validate-pre    Run pre-migration validation only  
    validate-complete  Run complete validation
    help            Show this help message

Examples:
    python migration_controller.py                    # Interactive migration
    python migration_controller.py automated          # Automated migration
    python migration_controller.py validate           # Post-migration validation
    python migration_controller.py validate-pre       # Pre-migration validation

Files created:
    • migration_report_*.json              Migration execution report
    • migration_validation_report_*.json   Validation results
    • migration_backup_*                   Backup directory
    • rollback_migration_*.py              Rollback script

For detailed information, see:
    • COMPREHENSIVE_ADVANCED_FOLDERS_MIGRATION_PLAN.md
    • ADVANCED_FOLDERS_MIGRATION_ROLLBACK_STRATEGY.md
"""
        print(help_text)


def main():
    """Main execution function"""
    controller = MigrationController()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help":
            controller.show_help()
            return True
        elif command == "automated":
            success = controller.automated_migration()
        elif command == "validate":
            success = controller.validation_only("post")
        elif command == "validate-pre":
            success = controller.validation_only("pre")
        elif command == "validate-complete":
            success = controller.validation_only("complete")
        elif command == "interactive":
            success = controller.interactive_migration()
        else:
            print(f"Unknown command: {command}")
            controller.show_help()
            return False
    else:
        # Default to interactive mode
        success = controller.interactive_migration()
    
    # Display summary
    controller.display_summary(success)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)