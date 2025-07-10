"""
Script to add error handling to all Python files in the workspace.
Handles errors gracefully and adds consistent error handling across modules.
"""
import os
from pathlib import Path
import re


def create_error_handler():
    """Create the error handler module if it doesn't exist."""
    error_handler_content = '''"""
Centralized error handling for the application.
Provides consistent error handling and logging across all modules.
"""
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Dict
from PyQt5.QtWidgets import QMessageBox

from core.error_handler import error_handler



class ErrorHandler:
    """Singleton class for handling errors across the application."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ErrorHandler, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize logging and other error handling components."""
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "rfu.log"
        
        logging.basicConfig(
            filename=str(self.log_file),
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)
    
    def handle_error(
        self,
        error: Exception,
        operation: str,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        show_dialog: bool = True
    ) -> bool:
        """
        Handle an error gracefully with logging and user notification.
        
        Args:
            error: The caught exception
            operation: Description of the operation that failed
            user_message: Optional custom message for the user
            context: Optional additional context for logging
            show_dialog: Whether to show error dialog to user
            
        Returns:
            bool: False to indicate error occurred
        """
        # Build error message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = [
            f"Time: {timestamp}",
            f"Operation: {operation}",
            f"Error: {str(error)}",
        ]
        
        if context:
            error_msg.append(f"Context: {context}")
            
        error_msg.append(f"Traceback:\\n{traceback.format_exc()}")
        
        # Log the error
        self.logger.error("\\n".join(error_msg))
        
        # Show user dialog if requested
        if show_dialog:
            msg = user_message or f"An error occurred while {operation}."
            msg += "\\nThe error has been logged."
            self._show_error_dialog(msg)
            
        return False
    
    def _show_error_dialog(self, message: str):
        """Display error message to user."""
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Warning)
        dialog.setText(message)
        dialog.setWindowTitle("Error")
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()


# Global instance
error_handler = ErrorHandler()
'''
    
    core_dir = Path("core")
    core_dir.mkdir(exist_ok=True)
    
    handler_path = core_dir / "error_handler.py"
    if not handler_path.exists():
        with open(handler_path, "w", encoding="utf-8") as f:
            f.write(error_handler_content)


def add_error_handling(file_path: Path) -> None:
    """Add error handling to a Python file."""
    try:
        # Skip __init__.py files
        if file_path.name == "__init__.py":
            return
            
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.readlines()
            
        new_content = []
        imports_end = 0
        
        # Find end of imports
        for i, line in enumerate(content):
            if line.startswith(("import ", "from ")):
                imports_end = i + 1
                
        # Add error handler import after other imports
        error_import = "from core.error_handler import error_handler\n"
        if error_import not in content:
            new_content = (
                content[:imports_end] +
                ["\n", error_import, "\n"] +
                content[imports_end:]
            )
        else:
            new_content = content
            
        # Write back changes
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_content)
            
        print(f"Added error handling to: {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def process_workspace():
    """Add error handling to all Python files in workspace."""
    # Create error handler module
    create_error_handler()
    
    # Process all Python files
    workspace = Path.cwd()
    for path in workspace.rglob("*.py"):
        if path.is_file():
            add_error_handling(path)


if __name__ == "__main__":
    process_workspace()
    print("\nError handling implementation complete.")
    print("Remember to wrap your function bodies in try-except blocks:")
    print("""
    def your_function():
        try:
            # Your code here
            pass
        except Exception as e:
            return error_handler.handle_error(
                error=e,
                operation="description of operation",
            )
    """)
