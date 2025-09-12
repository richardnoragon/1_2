#!/usr/bin/env python3
"""
Script to fix systematic issues in main.py while maintaining functionality
"""
import re

def fix_lazy_logging(content):
    """Fix f-string logging to use lazy % formatting"""
    patterns = [
        (r'self\.logger\.error\(f"([^"]*): \{([^}]+)\}"\)', r'self.logger.error("\1: %s", \2)'),
        (r'self\.logger\.warning\(f"([^"]*): \{([^}]+)\}"\)', r'self.logger.warning("\1: %s", \2)'),
        (r'self\.logger\.info\(f"([^"]*): \{([^}]+)\}"\)', r'self.logger.info("\1: %s", \2)'),
        (r'self\.logger\.debug\(f"([^"]*): \{([^}]+)\}"\)', r'self.logger.debug("\1: %s", \2)'),
        (r'self\.logger\.error\(f"([^"]*)"\)', r'self.logger.error("\1")'),
        (r'self\.logger\.warning\(f"([^"]*)"\)', r'self.logger.warning("\1")'),
        (r'self\.logger\.info\(f"([^"]*)"\)', r'self.logger.info("\1")'),
        (r'self\.logger\.debug\(f"([^"]*)"\)', r'self.logger.debug("\1")'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_exception_handling(content):
    """Fix overly broad exception handling"""
    # Map of common exception replacements
    replacements = [
        ('except Exception as e:', 'except (ImportError, AttributeError, OSError) as e:'),
    ]
    
    for old, new in replacements:
        # Be careful not to replace exceptions that are already specific
        if 'except (ImportError' not in content or 'except (OSError' not in content:
            content = content.replace(old, new)
    
    return content

def main():
    """Main fixing function"""
    # Read the file
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Original content length:", len(content))
    
    # Apply fixes
    content = fix_lazy_logging(content)
    print("After lazy logging fix")
    
    # Write back
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixes applied successfully!")

if __name__ == "__main__":
    main()