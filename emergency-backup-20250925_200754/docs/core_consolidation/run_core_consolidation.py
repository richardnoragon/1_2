#!/usr/bin/env python3
"""
Core Consolidation Migration Master Script
Orchestrates the complete migration process with user interaction

Date: September 17, 2025
Project: Richard's File Utilities (RFU)
Purpose: Master script to run the complete core consolidation migration
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


class CoreConsolidationMaster:
    """Master controller for the core consolidation migration."""
    
    def __init__(self, workspace_root: Path):
        """Initialize the master controller.
        
        Args:
            workspace_root: Path to the workspace root directory
        """
        self.workspace_root = Path(workspace_root)
        self.docs_path = self.workspace_root / "docs" / "core_consolidation"
        
        # Script paths
        self.migrator_script = self.docs_path / "core_consolidation_migrator.py"
        self.validator_script = self.docs_path / "core_consolidation_validator.py"
        self.rollback_script = self.docs_path / "core_consolidation_rollback.py"
    
    def display_banner(self):
        """Display the welcome banner."""
        print("=" * 70)
        print("🚀 CORE CONSOLIDATION MIGRATION MASTER")
        print("   Richard's File Utilities (RFU)")
        print(f"   Workspace: {self.workspace_root}")
        print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()
    
    def display_menu(self) -> str:
        """Display the main menu and get user choice.
        
        Returns:
            User's menu choice
        """
        print("📋 MIGRATION OPTIONS:")
        print("1. 🏃 Run Complete Migration (Recommended)")
        print("2. 🧪 Validate Current State Only")
        print("3. 🔄 Rollback Previous Migration")
        print("4. 📊 Show Migration Status")
        print("5. 📖 View Migration Plan")
        print("6. ❌ Exit")
        print()
        
        while True:
            choice = input("🤔 Select an option (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            print("❌ Invalid choice. Please select 1-6.")
    
    def run_script(self, script_path: Path, description: str) -> bool:
        """Run a Python script and return success status.
        
        Args:
            script_path: Path to the script to run
            description: Description of the script
            
        Returns:
            True if script executed successfully
        """
        print(f"\n🚀 {description}")
        print(f"📜 Executing: {script_path.name}")
        print("-" * 50)
        
        try:
            # Run the script
            result = subprocess.run([
                sys.executable, str(script_path)
            ], cwd=str(self.workspace_root), capture_output=False)
            
            if result.returncode == 0:
                print(f"\n✅ {description} completed successfully!")
                return True
            else:
                print(f"\n❌ {description} failed with exit code {result.returncode}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error running {description}: {e}")
            return False
    
    def show_migration_status(self):
        """Display current migration status."""
        print("\n📊 MIGRATION STATUS")
        print("-" * 30)
        
        # Check for migration state file
        state_file = self.docs_path / "migration_state.json"
        if state_file.exists():
            try:
                import json
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                print(f"📅 Last Update: {state.get('last_updated', 'Unknown')}")
                print(f"🔄 Phase: {state.get('phase', 'Unknown')}")
                print(f"📁 Backup: {state.get('backup_location', 'None')}")
                print(f"📝 Files Migrated: {len(state.get('files_migrated', []))}")
                print(f"⚠️ Conflicts Resolved: {len(state.get('conflicts_resolved', []))}")
                print(f"❌ Errors: {len(state.get('errors', []))}")
                
                if state.get('errors'):
                    print("\\n🚨 Recent Errors:")
                    for error in state['errors'][-3:]:  # Show last 3 errors
                        print(f"   • {error}")
                
            except Exception as e:
                print(f"❌ Error reading migration state: {e}")
        else:
            print("📄 No migration state file found")
        
        # Check directory status
        src_path = self.workspace_root / "src"
        core_path = src_path / "core"
        core_rfu_path = src_path / "core_rfu"
        
        print("\\n📁 Directory Status:")
        print(f"   src/core: {'✅ Exists' if core_path.exists() else '❌ Missing'}")
        print(f"   src/core_rfu: {'✅ Exists' if core_rfu_path.exists() else '❌ Missing'}")
        
        if core_path.exists():
            py_files = list(core_path.rglob("*.py"))
            print(f"   src/core Python files: {len(py_files)}")
        
        if core_rfu_path.exists():
            py_files = list(core_rfu_path.rglob("*.py"))
            print(f"   src/core_rfu Python files: {len(py_files)}")
    
    def show_migration_plan(self):
        """Display the migration plan."""
        plan_file = self.docs_path / "consolidation_core_core_rfu_migration_plan.md"
        
        if plan_file.exists():
            print("\\n📖 MIGRATION PLAN SUMMARY")
            print("-" * 40)
            
            try:
                with open(plan_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract and show key sections
                lines = content.split('\\n')
                in_summary = False
                in_strategy = False
                
                for line in lines:
                    if line.startswith("## Executive Summary"):
                        in_summary = True
                        print("📋 EXECUTIVE SUMMARY:")
                        continue
                    elif line.startswith("## 2. Migration Strategy"):
                        in_summary = False
                        in_strategy = True
                        print("\\n🎯 MIGRATION STRATEGY:")
                        continue
                    elif line.startswith("## 3.") or line.startswith("---"):
                        in_summary = False
                        in_strategy = False
                    
                    if in_summary or in_strategy:
                        if line.strip() and not line.startswith('#'):
                            print(f"   {line}")
                
                print(f"\\n📄 Full plan available at: {plan_file}")
                
            except Exception as e:
                print(f"❌ Error reading migration plan: {e}")
        else:
            print("❌ Migration plan not found")
    
    def run_complete_migration(self) -> bool:
        """Run the complete migration process.
        
        Returns:
            True if migration was successful
        """
        print("\\n🚀 STARTING COMPLETE MIGRATION PROCESS")
        print("=" * 50)
        
        # Step 1: Pre-migration validation
        print("\\n📋 Step 1: Pre-Migration Validation")
        if not self.run_script(self.validator_script, "Pre-Migration Validation"):
            print("⚠️ Pre-migration validation had issues. Continue anyway?")
            response = input("Continue with migration? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("❌ Migration cancelled by user")
                return False
        
        # Step 2: Execute migration
        print("\\n🔄 Step 2: Migration Execution")
        if not self.run_script(self.migrator_script, "Core Consolidation Migration"):
            print("❌ Migration failed! Check logs for details.")
            print("🔄 You can try to rollback using option 3 from the main menu.")
            return False
        
        # Step 3: Post-migration validation
        print("\\n✅ Step 3: Post-Migration Validation")
        if not self.run_script(self.validator_script, "Post-Migration Validation"):
            print("⚠️ Post-migration validation detected issues!")
            print("🔍 Check the validation report for details.")
            print("🔄 Consider running rollback if issues are critical.")
            return False
        
        print("\\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ All phases completed without critical errors")
        print("📊 Check validation reports for detailed results")
        print("💾 Backup is available for rollback if needed")
        
        return True
    
    def run_validation_only(self) -> bool:
        """Run validation only.
        
        Returns:
            True if validation passed
        """
        print("\\n🧪 RUNNING VALIDATION ONLY")
        print("=" * 40)
        
        return self.run_script(self.validator_script, "Core Migration Validation")
    
    def run_rollback(self) -> bool:
        """Run the rollback process.
        
        Returns:
            True if rollback was successful
        """
        print("\\n🔄 STARTING MIGRATION ROLLBACK")
        print("=" * 40)
        
        print("⚠️  WARNING: This will restore the original directory structure")
        print("   Any changes made after migration will be lost!")
        
        response = input("\\nAre you sure you want to proceed? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Rollback cancelled by user")
            return False
        
        return self.run_script(self.rollback_script, "Migration Rollback")
    
    def run(self):
        """Run the master migration controller."""
        self.display_banner()
        
        while True:
            choice = self.display_menu()
            
            if choice == '1':
                # Run complete migration
                success = self.run_complete_migration()
                if success:
                    print("\\n🎯 Migration completed! You may now exit or run validation again.")
                else:
                    print("\\n⚠️ Migration had issues. Check logs and consider rollback.")
            
            elif choice == '2':
                # Validate current state only
                self.run_validation_only()
            
            elif choice == '3':
                # Rollback previous migration
                success = self.run_rollback()
                if success:
                    print("\\n🔄 Rollback completed successfully!")
                else:
                    print("\\n❌ Rollback failed. Check logs for details.")
            
            elif choice == '4':
                # Show migration status
                self.show_migration_status()
            
            elif choice == '5':
                # View migration plan
                self.show_migration_plan()
            
            elif choice == '6':
                # Exit
                print("\\n👋 Goodbye!")
                break
            
            # Wait for user input before showing menu again
            input("\\n⏎ Press Enter to continue...")
            print("\\n")


def main():
    """Main execution function."""
    # Get workspace root
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent.parent
    
    # Initialize and run master controller
    master = CoreConsolidationMaster(workspace_root)
    master.run()


if __name__ == "__main__":
    main()