"""Runner script for the GUI migrator."""
import sys
from pathlib import Path

from gui_migrator_v2 import GUIMigrationAutomator

from core.error_handler import error_handler


def main():
    """main."""
    # Get workspace path from environment or use current directory
    workspace_path = Path.cwd()
    
    print(f"Starting GUI migration in workspace: {workspace_path}")
    
    # Create and run automator
    automator = GUIMigrationAutomator(workspace_path)
    
    # Find GUI files
    gui_files = automator.find_gui_files()
    print(f"\nFound {len(gui_files)} GUI files:")
    for file in gui_files:
        print(f"  - {file.relative_to(workspace_path)}")
    
    # Create migration scripts
    print("\nCreating migration scripts...")
    automator.create_migration_scripts()
    
    # Confirm before applying migrations
    response = input(
        "\nReady to apply migrations. Files will be backed up first. "
        "Continue? [y/N] "
    )
    
    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Apply migrations
    print("\nApplying migrations...")
    automator.apply_migrations(create_backups=True)
    
    print("\nMigration complete!")


if __name__ == '__main__':
    main()
