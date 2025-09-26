#!/usr/bin/env python3
"""
Rollback script for compress_decompress migration
Created: 2025-01-27T15:04:00
"""

import os
import shutil
from pathlib import Path

def rollback():
    """Restore files from backup."""
    backup_dir = Path('backup/compress_decompress_migration/2025-01-27_15-04-00')
    source_files = ['compress_decompress.py', 'compress_decompress.ui']
    
    print('🔄 ROLLING BACK COMPRESS_DECOMPRESS MIGRATION')
    print('=' * 50)
    
    for file_path in source_files:
        backup_file = backup_dir / file_path
        if backup_file.exists():
            shutil.copy2(backup_file, file_path)
            print(f'✅ Restored: {file_path}')
        else:
            print(f'❌ Backup not found: {file_path}')
    
    print('🎯 Rollback completed!')

if __name__ == '__main__':
    rollback()