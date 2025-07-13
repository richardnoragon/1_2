"""Script to apply GUI migrations with proper path handling."""
import os
import sys
from pathlib import Path
import argparse
import logging
import importlib.util
from typing import List, Optional

from core.error_handler import error_handler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_migration_module(script_path: Path) -> Optional[object]:
    """Load a Python module from file path."""
    try:
        spec = importlib.util.spec_from_file_location(
            script_path.stem,
            script_path
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except Exception as e:
        logger.error(f"Error loading module {script_path}: {e}")
    return None

def get_migration_scripts(migration_dir: Path) -> List[Path]:
    """Get all migration scripts in the directory."""
    return list(migration_dir.glob('migrate_*.py'))

def backup_file(file_path: Path) -> Optional[Path]:
    """Create a backup of a file before migration."""
    try:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        if file_path.exists():
            file_path.rename(backup_path)
            return backup_path
        return None
    except Exception as e:
        logger.error(f"Error creating backup of {file_path}: {e}")
        return None

def restore_backup(backup_path: Path, original_path: Path) -> bool:
    """Restore file from backup if migration fails."""
    try:
        if backup_path.exists():
            backup_path.rename(original_path)
            return True
        return False
    except Exception as e:
        logger.error(
            f"Error restoring backup {backup_path} to {original_path}: {e}"
        )
        return False

def get_target_file_path(script_name: str, workspace_path: Path) -> Optional[Path]:
    """Get the target file path from the migration script name."""
    # Remove 'migrate_' prefix and get the original filename
    original_name = script_name.replace('migrate_', '', 1)
    
    # Search for the file in the workspace
    possible_paths = list(workspace_path.rglob(f"{original_name}.py"))
    
    if not possible_paths:
        logger.warning(f"Could not find target file for {original_name}")
        return None
        
    # If multiple matches found, try to find the most likely one
    if len(possible_paths) > 1:
        # Prefer files in the root directory or main source directory
        root_matches = [p for p in possible_paths if len(p.parts) <= 3]
        if root_matches:
            return root_matches[0]
    
    return possible_paths[0]

def apply_migration(
    script_path: Path,
    target_file: Path,
    create_backup: bool
) -> bool:
    """Apply a single migration script."""
    try:
        logger.info(f"Applying migration to {target_file}")
        
        # Create backup if requested
        backup_path = None
        if create_backup:
            backup_path = backup_file(target_file)
            if not backup_path and target_file.exists():
                logger.error(f"Failed to create backup for {target_file}")
                return False
        
        # Load and run the migration
        module = load_migration_module(script_path)
        if module and hasattr(module, 'migrate'):
            try:
                module.migrate()
                logger.info(f"Successfully migrated {target_file}")
                return True
            except Exception as e:
                logger.error(f"Error during migration: {e}")
                if backup_path:
                    restore_backup(backup_path, target_file)
                return False
        else:
            logger.error(f"Invalid migration script: {script_path}")
            if backup_path:
                restore_backup(backup_path, target_file)
            return False
            
    except Exception as e:
        logger.error(f"Error applying migration {script_path}: {e}")
        return False

def main():
    """main."""
    parser = argparse.ArgumentParser(
        description="Apply GUI migrations to files"
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Directory containing migration scripts"
    )
    parser.add_argument(
        "--workspace",
        required=True,
        help="Workspace root directory"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backups before migration"
    )
    
    args = parser.parse_args()
    migration_dir = Path(args.dir)
    workspace_path = Path(args.workspace)
    
    if not migration_dir.is_dir():
        logger.error(f"Migration directory {migration_dir} does not exist")
        sys.exit(1)
        
    if not workspace_path.is_dir():
        logger.error(f"Workspace directory {workspace_path} does not exist")
        sys.exit(1)
    
    scripts = get_migration_scripts(migration_dir)
    if not scripts:
        logger.error(f"No migration scripts found in {migration_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(scripts)} migration scripts")
    
    success_count = 0
    for script in scripts:
        try:
            target_file = get_target_file_path(script.stem, workspace_path)
            if not target_file:
                continue
                
            if apply_migration(script, target_file, args.backup):
                success_count += 1
                
        except Exception as e:
            logger.error(f"Error processing {script}: {e}")
    
    logger.info(
        f"Migration complete: {success_count} of {len(scripts)} files migrated"
    )

if __name__ == '__main__':
    main()
