#!/usr/bin/env python3
"""
Execute the Advanced Folders live migration.
"""

from advanced_folders_migration_script import AdvancedFoldersMigration

if __name__ == "__main__":
    print("[MIGRATION] Starting live migration execution...")
    
    migration = AdvancedFoldersMigration()
    
    try:
        # Execute live migration
        plan = migration.execute_migration(dry_run=False)
        
        # Validate results
        validation = migration.validate_migration()
        
        print(f"\n[RESULTS] Migration completed successfully!")
        print(f"[STATS] Plan timestamp: {plan['timestamp']}")
        print(f"[VALIDATION] Target exists: {validation['target_exists']}")
        
        # Count successful components
        core_success = sum(1 for c in validation['core_components_present'] if c['exists'])
        gui_success = sum(1 for c in validation['gui_components_present'] if c['exists'])
        
        print(f"[COMPONENTS] Core components: {core_success}/{len(validation['core_components_present'])}")
        print(f"[COMPONENTS] GUI components: {gui_success}/{len(validation['gui_components_present'])}")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {str(e)}")
        raise