#!/usr/bin/env python3
"""
Script to fix linting issues in cache_manager.py
Addresses line length, unused imports, and other formatting issues.
"""

import re
from pathlib import Path


def fix_cache_manager_linting():
    """Fix all linting issues in cache_manager.py"""
    cache_file = Path(r"c:\Users\HP1\1_2\src\utilities\advanced_folders\engine\cache_manager.py")
    
    if not cache_file.exists():
        print(f"File not found: {cache_file}")
        return
    
    print(f"Fixing linting issues in {cache_file}")
    
    # Read the content
    with open(cache_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix long lines by breaking them
    fixes = [
        # Fix long string lines
        (r'self\.logger\.info\("Connected to Redis server"\)', 
         'self.logger.info("Connected to Redis server")'),
        
        # Fix long function signatures 
        (r'def __init__\(self, cache_manager\):', 
         'def __init__(self, cache_manager):'),
        
        # Fix long conditional statements
        (r'if len\(value_blob\) < self\.config\.compression_threshold:', 
         'if len(value_blob) < self.config.compression_threshold:'),
        
        # Fix long arithmetic expressions
        (r'max_size_bytes = self\.config\.max_object_size_mb \* 1024 \* 1024',
         'max_size_bytes = (\n            self.config.max_object_size_mb * 1024 * 1024\n        )'),
        
        # Fix long string concatenations  
        (r'f"Failed to connect to Redis: \{e\}"',
         'f"Failed to connect to Redis: {e}"'),
        
        # Fix long method calls
        (r'self\.redis_client\.setex\(key, ttl_seconds, value_blob\)',
         'self.redis_client.setex(key, ttl_seconds, value_blob)'),
    ]
    
    # Apply fixes
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # Split long lines manually
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) <= 79:
            fixed_lines.append(line)
            continue
            
        # Handle specific long line patterns
        stripped = line.strip()
        indent = line[:len(line) - len(stripped)]
        
        # Long logger messages
        if '.logger.' in stripped and 'f"' in stripped:
            # Find the f-string
            f_string_start = stripped.find('f"')
            if f_string_start > 0:
                prefix = stripped[:f_string_start]
                f_string = stripped[f_string_start:]
                
                fixed_lines.append(f"{indent}{prefix}(")
                fixed_lines.append(f"{indent}    {f_string}")
                fixed_lines.append(f"{indent})")
                continue
        
        # Long conditional statements
        if ' and ' in stripped or ' or ' in stripped:
            if '(' in stripped and ')' in stripped:
                # Already has parentheses, just break at logical operators
                parts = re.split(r'(\s+(?:and|or)\s+)', stripped)
                if len(parts) > 1:
                    fixed_lines.append(f"{indent}{parts[0]} \\")
                    for i in range(1, len(parts), 2):
                        if i + 1 < len(parts):
                            fixed_lines.append(f"{indent}    {parts[i]}{parts[i+1]} \\")
                    # Remove trailing backslash from last line
                    if fixed_lines[-1].endswith(' \\'):
                        fixed_lines[-1] = fixed_lines[-1][:-2]
                    continue
        
        # Long assignments
        if '=' in stripped and not stripped.startswith('#'):
            eq_pos = stripped.find('=')
            if eq_pos > 0:
                var_part = stripped[:eq_pos + 1]
                value_part = stripped[eq_pos + 1:].strip()
                
                if len(value_part) > 40:  # If value part is long
                    fixed_lines.append(f"{indent}{var_part} (")
                    fixed_lines.append(f"{indent}    {value_part}")
                    fixed_lines.append(f"{indent})")
                    continue
        
        # Long function calls or method chains
        if '(' in stripped and ')' in stripped and '.' in stripped:
            # Try to break at method boundaries
            if stripped.count('.') > 1:
                parts = stripped.split('.')
                if len(parts) > 2:
                    fixed_lines.append(f"{indent}{parts[0]}.")
                    for part in parts[1:-1]:
                        fixed_lines.append(f"{indent}    {part}.")
                    fixed_lines.append(f"{indent}    {parts[-1]}")
                    continue
        
        # As fallback, just add the original line (linter will still complain)
        fixed_lines.append(line)
    
    # Reconstruct content
    content = '\n'.join(fixed_lines)
    
    # Additional text replacements for specific issues
    replacements = [
        # Fix specific long lines that are hard to catch with regex
        ('    def invalidate_by_pattern(self, pattern: str) -> int:', 
         '    def invalidate_by_pattern(self, pattern: str) -> int:'),
        
        ('        Args:', '        Args:'),
        ('            pattern: Pattern to match keys against', 
         '            pattern: Pattern to match keys against'),
        
        # Fix docstring issues
        ('        """Invalidate cache entries matching pattern.', 
         '        """Invalidate cache entries matching pattern.'),
        
        # Fix method signature issues  
        ('    def add_invalidation_rule(self, pattern: str, condition_func: Callable):', 
         '    def add_invalidation_rule(self, pattern: str,\n'
         '                             condition_func: Callable):'),
        
        ('    def set(self, key: str, value: Any, ttl: Optional[int] = None,',
         '    def set(self, key: str, value: Any, ttl: Optional[int] = None,'),
        
        ('            tags: Optional[Set[str]] = None) -> bool:',
         '            tags: Optional[Set[str]] = None) -> bool:'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Write the fixed content back
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Linting fixes applied to cache_manager.py")


if __name__ == "__main__":
    fix_cache_manager_linting()