"""
Script to add error handling to all Python files in the workspace.
"""
import os
from pathlib import Path
import re

from src.core.error_handler import error_handler


def add_error_imports(content: str) -> str:
    """Add error handler import if not present."""
    if "from src.core.error_handler import error_handler" not in content:
        import_line = "from src.core.error_handler import error_handler\n"
        # Add after other imports or at start of file
        if "import " in content:
            content = re.sub(r'((?:^|\n)import [^\n]+\n(?:from [^\n]+\n)*)',
                           r'\1\n' + import_line, content)
        else:
            content = import_line + "\n" + content
    return content

def wrap_functions_with_error_handling(content: str) -> str:
    """Wrap function bodies with try-except blocks."""
    lines = content.split('\n')
    new_lines = []
    in_function = False
    indent = ""
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Detect function definitions
        func_match = re.match(r'^(\s*)def\s+(\w+)\s*\([^)]*\)\s*:', line)
        if func_match:
            in_function = True
            indent = re.match(r'^(\s*)', line).group(1)
            new_lines.append(line)
            
            # Add try block
            i += 1
            if i < len(lines):
                func_body_indent = re.match(r'^(\s*)', lines[i]).group(1)
                new_lines.append(f"{func_body_indent}try:")
                
                # Continue until next def or end of indented block
                while i < len(lines):
                    line = lines[i]
                    if not line.strip() or line.startswith(func_body_indent):
                        new_lines.append("    " + line)
                        i += 1
                    else:
                        break
                
                # Add except block
                new_lines.append(f"{func_body_indent}except Exception as e:")
                new_lines.append(f"{func_body_indent}    return error_handler.handle_error(")
                new_lines.append(f"{func_body_indent}        error=e,")
                new_lines.append(f"{func_body_indent}        operation=f\"executing {func_name}\",")
                new_lines.append(f"{func_body_indent}    )")
                in_function = False
        else:
            new_lines.append(line)
            i += 1
    
    return '\n'.join(new_lines)

def process_file(file_path: Path) -> None:
    """Process a single Python file to add error handling."""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add imports
        content = add_error_imports(content)
        
        # Wrap functions
        content = wrap_functions_with_error_handling(content)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Processed: {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    """Main function to process all Python files."""
    workspace_root = Path(__file__).parent
    
    # Process all Python files
    for root, _, files in os.walk(workspace_root):
        for file in files:
            if file.endswith('.py') and not file == __file__:
                file_path = Path(root) / file
                process_file(file_path)

if __name__ == "__main__":
    main()
    print("Error handling integration complete.")
