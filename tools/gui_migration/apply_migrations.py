"""Script to apply GUI migrations to multiple files."""
import os
import sys
from pathlib import Path
import argparse
import logging
from typing import List, Optional

from core.error_handler import error_handler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_migration_scripts(migration_dir: Path) -> List[Path]:
    """Get all migration scripts in the directory."""
    return list(migration_dir.glob('migrate_*.py'))

def apply_migration(script_path: Path) -> bool:
    """Apply a single migration script."""
    try:
        logger.info(f"Applying migration from {script_path}")
        
        # Import and run the migration script
        sys.path.insert(0, str(script_path.parent))
        migration_module = __import__(script_path.stem)
        migration_module.migrate()
        sys.path.pop(0)
        
        return True
    except Exception as e:
        logger.error(f"Error applying migration {script_path}: {e}")
        return False

def backup_file(file_path: Path) -> Optional[Path]:
    """Create a backup of a file before migration."""
    try:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        file_path.rename(backup_path)
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup of {file_path}: {e}")
        return None

def restore_backup(backup_path: Path, original_path: Path) -> bool:
    """Restore file from backup if migration fails."""
    try:
        backup_path.rename(original_path)
        return True
    except Exception as e:
        logger.error(
            f"Error restoring backup {backup_path} to {original_path}: {e}"
        )
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Apply GUI migrations to multiple files"
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Directory containing migration scripts"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backups before migration"
    )
    
    args = parser.parse_args()
    migration_dir = Path(args.dir)
    
    if not migration_dir.is_dir():
        logger.error(f"Migration directory {migration_dir} does not exist")
        sys.exit(1)
    
    scripts = get_migration_scripts(migration_dir)
    if not scripts:
        logger.error(f"No migration scripts found in {migration_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(scripts)} migration scripts")
    
    success_count = 0
    for script in scripts:
        try:
            # Get the target file path from the script name
            target_file = Path(script.stem.replace('migrate_', ''))
            if not target_file.exists():
                logger.warning(f"Target file {target_file} not found, skipping")
                continue
            
            # Create backup if requested
            backup_path = None
            if args.backup:
                backup_path = backup_file(target_file)
                if not backup_path:
                    logger.error(f"Failed to create backup for {target_file}")
                    continue
            
            # Apply migration
            if apply_migration(script):
                success_count += 1
                logger.info(f"Successfully migrated {target_file}")
            elif backup_path:
                logger.info(f"Migration failed, restoring backup for {target_file}")
                restore_backup(backup_path, target_file)
                
        except Exception as e:
            logger.error(f"Error processing {script}: {e}")
    
    logger.info(
        f"Migration complete: {success_count} of {len(scripts)} files migrated"
    )

if __name__ == '__main__':
    main()
