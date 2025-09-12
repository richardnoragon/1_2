#!/usr/bin/env python3
"""Fix linting issues in search_cache.py"""

import re
from pathlib import Path


def fix_search_cache_linting():
    """Fix all linting issues in search_cache.py"""
    file_path = Path("src/rfu/advanced_folders/core/search_cache.py")
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix trailing whitespace and add final newline
    lines = content.split('\n')
    fixed_lines = [line.rstrip() for line in lines]
    if fixed_lines and fixed_lines[-1]:
        fixed_lines.append('')
    
    content = '\n'.join(fixed_lines)
    
    # Apply specific fixes for long lines
    fixes = [
        # Memory usage bytes assignment
        (r'(\s+)self\.statistics\.memory_usage_bytes = memory_stats\[\'memory_usage_bytes\'\]',
         r'\1self.statistics.memory_usage_bytes = (\n\1    memory_stats[\'memory_usage_bytes\']\n\1)'),
        
        # Search type assignment
        (r'(\s+)\'search_type\': parameters\.search_type\.value if parameters\.search_type else None,',
         r'\1\'search_type\': (\n\1    parameters.search_type.value\n\1    if parameters.search_type else None\n\1),'),
        
        # Root paths assignment
        (r'(\s+)\'root_paths\': sorted\(parameters\.root_paths\) if parameters\.root_paths else \[\],',
         r'\1\'root_paths\': (\n\1    sorted(parameters.root_paths)\n\1    if parameters.root_paths else []\n\1),'),
        
        # Include extensions
        (r'(\s+)\'include_extensions\': sorted\(parameters\.file_type_filter\.include_extensions\) if parameters\.file_type_filter\.include_extensions else \[\],',
         r'\1\'include_extensions\': (\n\1    sorted(parameters.file_type_filter.include_extensions)\n\1    if parameters.file_type_filter.include_extensions else []\n\1),'),
        
        # Exclude extensions
        (r'(\s+)\'exclude_extensions\': sorted\(parameters\.file_type_filter\.exclude_extensions\) if parameters\.file_type_filter\.exclude_extensions else \[\],',
         r'\1\'exclude_extensions\': (\n\1    sorted(parameters.file_type_filter.exclude_extensions)\n\1    if parameters.file_type_filter.exclude_extensions else []\n\1),'),
        
        # MIME types
        (r'(\s+)\'mime_types\': sorted\(parameters\.file_type_filter\.mime_types\) if parameters\.file_type_filter\.mime_types else \[\]',
         r'\1\'mime_types\': (\n\1    sorted(parameters.file_type_filter.mime_types)\n\1    if parameters.file_type_filter.mime_types else []\n\1)'),
        
        # Cleanup interval check
        (r'(\s+)if datetime\.now\(\) - self\._last_cleanup >= self\.cleanup_interval:',
         r'\1if (datetime.now() - self._last_cleanup >=\n\1        self.cleanup_interval):'),
        
        # Search type in cache key
        (r'(\s+)\'search_type\': search_parameters\.search_type\.value if search_parameters\.search_type else \'name\',',
         r'\1\'search_type\': (\n\1    search_parameters.search_type.value\n\1    if search_parameters.search_type else \'name\'\n\1),'),
        
        # Root paths in cache key
        (r'(\s+)\'root_paths\': sorted\(search_parameters\.root_paths\) if search_parameters\.root_paths else \[\],',
         r'\1\'root_paths\': (\n\1    sorted(search_parameters.root_paths)\n\1    if search_parameters.root_paths else []\n\1),'),
        
        # Include ext in cache key
        (r'(\s+)\'include_ext\': sorted\(search_parameters\.file_type_filter\.include_extensions or \[\]\),',
         r'\1\'include_ext\': sorted(\n\1    search_parameters.file_type_filter.include_extensions or []\n\1),'),
        
        # Exclude ext in cache key
        (r'(\s+)\'exclude_ext\': sorted\(search_parameters\.file_type_filter\.exclude_extensions or \[\]\),',
         r'\1\'exclude_ext\': sorted(\n\1    search_parameters.file_type_filter.exclude_extensions or []\n\1),'),
        
        # MIME types in cache key
        (r'(\s+)\'mime_types\': sorted\(search_parameters\.file_type_filter\.mime_types or \[\]\)',
         r'\1\'mime_types\': sorted(\n\1    search_parameters.file_type_filter.mime_types or []\n\1)'),
        
        # Start date assignment
        (r'(\s+)\'start_date\': search_parameters\.date_filter\.start_date\.isoformat\(\) if search_parameters\.date_filter\.start_date else None,',
         r'\1\'start_date\': (\n\1    search_parameters.date_filter.start_date.isoformat()\n\1    if search_parameters.date_filter.start_date else None\n\1),'),
        
        # End date assignment
        (r'(\s+)\'end_date\': search_parameters\.date_filter\.end_date\.isoformat\(\) if search_parameters\.date_filter\.end_date else None,',
         r'\1\'end_date\': (\n\1    search_parameters.date_filter.end_date.isoformat()\n\1    if search_parameters.date_filter.end_date else None\n\1),'),
        
        # Filter type assignment
        (r'(\s+)\'filter_type\': search_parameters\.date_filter\.filter_type\.value if search_parameters\.date_filter\.filter_type else None',
         r'\1\'filter_type\': (\n\1    search_parameters.date_filter.filter_type.value\n\1    if search_parameters.date_filter.filter_type else None\n\1)'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed linting issues in {file_path}")

if __name__ == "__main__":
    fix_search_cache_linting()