"""
Script to add detailed docstrings to all Python files in the workspace.
"""
import ast
import re
from pathlib import Path


class DocstringUpdater:
    """Class to handle adding and updating docstrings in Python files."""

    def __init__(self, workspace_path: str):
        """Initialize the DocstringUpdater.

        Args:
            workspace_path (str): Path to the workspace root directory.
        """
        self.workspace_path = Path(workspace_path)

    def process_workspace(self) -> None:
        """Process all Python files in the workspace to add/update docstrings."""
        for py_file in self.workspace_path.rglob("*.py"):
            if py_file.is_file() and not py_file.name.startswith("__"):
                self.process_file(py_file)

    def process_file(self, file_path: Path) -> None:
        """Process a single Python file to add/update docstrings.

        Args:
            file_path (Path): Path to the Python file to process.
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the file
            tree = ast.parse(content)
            
            # Process classes and functions
            updated_content = self._add_docstrings(content, tree)

            # Write back if changes were made
            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"Updated docstrings in: {file_path}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _add_docstrings(self, content: str, tree: ast.AST) -> str:
        """Add docstrings to classes and functions in the AST.

        Args:
            content (str): Original file content.
            tree (ast.AST): AST of the Python file.

        Returns:
            str: Updated file content with added docstrings.
        """
        # Get all classes and functions
        updates = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                # Check if node needs a docstring
                if not ast.get_docstring(node):
                    docstring = self._generate_docstring(node)
                    updates.append((node, docstring))

        # Apply updates from last to first to maintain correct line numbers
        updates.sort(key=lambda x: x[0].lineno, reverse=True)
        lines = content.split('\n')

        for node, docstring in updates:
            indent = ' ' * node.col_offset
            docstring_lines = [f'{indent}    """{docstring}"""']
            
            # Find the line after the definition
            def_line = node.lineno
            _ = node.body[0].lineno if node.body else def_line + 1
            
            # Insert docstring
            lines[def_line:def_line] = docstring_lines

        return '\n'.join(lines)

    def _generate_docstring(self, node: ast.AST) -> str:
        """Generate an appropriate docstring for a class or function.

        Args:
            node (ast.AST): The AST node representing a class or function.

        Returns:
            str: Generated docstring for the node.
        """
        if isinstance(node, ast.ClassDef):
            return self._generate_class_docstring(node)
        elif isinstance(node, ast.FunctionDef):
            return self._generate_function_docstring(node)
        return ""

    def _generate_class_docstring(self, node: ast.ClassDef) -> str:
        """Generate a docstring for a class definition.

        Args:
            node (ast.ClassDef): The AST node representing a class.

        Returns:
            str: Generated docstring for the class.
        """
        bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
        class_desc = "A class that "
        
        # Infer purpose from class name
        words = re.findall('[A-Z][a-z]*', node.name)
        if words:
            class_desc += f"handles {' '.join(words).lower()}"
            if bases:
                class_desc += f" and inherits from {', '.join(bases)}"
        else:
            class_desc += f"provides {node.name} functionality"
            if bases:
                class_desc += f" (inherits from {', '.join(bases)})"
        
        return class_desc + "."

    def _generate_function_docstring(self, node: ast.FunctionDef) -> str:
        """Generate a docstring for a function definition.

        Args:
            node (ast.FunctionDef): The AST node representing a function.

        Returns:
            str: Generated docstring for the function.
        """
        # Start with function description
        func_name_parts = re.findall('[a-z]+|[A-Z][a-z]*', node.name)
        func_desc = f"{''.join(func_name_parts).replace('_', ' ').lower()}."
        
        # Add Args section if there are arguments
        args_list = []
        for arg in node.args.args:
            if arg.arg != 'self':
                arg_type = self._get_arg_type(arg)
                args_list.append(
                    f"\n        Args:\n            {arg.arg} ({arg_type}): "
                    f"Description of {arg.arg}"
                )
        
        # Add Returns section if function has return annotation
        returns = ""
        if node.returns:
            return_type = self._get_return_type(node.returns)
            returns = (
                f"\n        Returns:\n            {return_type}: Description of value"
            )
        
        # Combine all sections
        docstring = func_desc
        if args_list:
            docstring += ''.join(args_list)
        if returns:
            docstring += returns
            
        return docstring

    def _get_arg_type(self, arg: ast.arg) -> str:
        """Get the type annotation of an argument.

        Args:
            arg (ast.arg): The AST node representing a function argument.

        Returns:
            str: The type annotation as a string.
        """
        if arg.annotation:
            if isinstance(arg.annotation, ast.Name):
                return arg.annotation.id
            elif isinstance(arg.annotation, ast.Subscript):
                # For complex types like List[str], Union[str, int], etc.
                return 'Any'
        return 'Any'

    def _get_return_type(self, returns: ast.AST) -> str:
        """Get the return type annotation of a function.

        Args:
            returns (ast.AST): The AST node representing the return annotation.

        Returns:
            str: The return type as a string.
        """
        if isinstance(returns, ast.Name):
            return returns.id
        elif isinstance(returns, ast.Subscript):
            # For complex types like List[str], Union[str, int], etc.
            return 'Any'
        return 'Any'


def main():
    """Main entry point of the script."""
    workspace_path = str(Path(__file__).parent.parent)
    updater = DocstringUpdater(workspace_path)
    print("Starting docstring updates...")
    updater.process_workspace()
    print("Docstring updates complete!")


if __name__ == "__main__":
    main()
