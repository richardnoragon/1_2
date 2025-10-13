"""
Migration script to standardize all GUI windows to use the new StandardWindow class.

This script will update existing utilities to use consistent styling and layout.
"""

import os
import re
import sys
from pathlib import Path

from core.error_handler import error_handler


class WindowStandardizer:
    """Class to handle standardizing GUI windows."""

    def __init__(self, workspace_path):
        """Initialize the standardizer.

        Args:
            workspace_path (Path): Path to the workspace directory
        """
        self.workspace_path = Path(workspace_path)
        self.files_updated = []
        self.files_skipped = []

    def find_gui_files(self):
        """Find all Python files that contain GUI classes."""
        gui_files = []

        # Patterns to identify GUI files
        gui_patterns = [
            r"class\s+\w+GUI\s*\(",
            r"class\s+\w+Window\s*\(",
            r"class\s+MyGUI\s*\(",
            r"QMainWindow",
            r"QDialog",
            r"QWidget",
        ]

        # Files to process
        target_files = [
            "check_sum.py",
            "compress_decompress.py",
            "edit_image_metadata.py",
            "empty_folders.py",
            "en_and_decrypt.py",
            "file_finder.py",
            "file_splitter_joiner.py",
            "file_touch.py",
            "find_duplicate_files.py",
            "src/tools/metadata/office_metadata/office_meta_data_editor.py",
            "permissions_editor.py",
            "file_utilities_2/gui/rename_gui.py",
            "secure_delete.py",
            "size_analyzer.py",
            "synchronization_backup/sync.py",
            "tag_viewer_editor.py",
            "tree_map.py",
        ]

        for file_name in target_files:
            file_path = self.workspace_path / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")

                    # Check if it's a GUI file
                    for pattern in gui_patterns:
                        if re.search(pattern, content):
                            gui_files.append(file_path)
                            break

                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        return gui_files

    def standardize_file(self, file_path):
        """Standardize a single GUI file.

        Args:
            file_path (Path): Path to the file to standardize
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Skip if already using StandardWindow
            if "StandardWindow" in content or "standard_window" in content:
                self.files_skipped.append(str(file_path))
                return

            # Determine the class name
            class_match = re.search(r"class\s+(\w+(?:GUI|Window|App))\s*\(", content)
            if not class_match:
                self.files_skipped.append(str(file_path))
                return

            class_name = class_match.group(1)

            # Update imports
            new_imports = [
                "from gui.common.standard_window import StandardWindow, StandardDialog",
                "from gui.themes import ThemeManager",
            ]

            # Add imports after existing PyQt5 imports
            qt_import_pattern = r"(from\s+PyQt5\..*?\n)+"
            qt_import_match = re.search(qt_import_pattern, content)

            if qt_import_match:
                import_section = qt_import_match.group(0)
                new_import_section = import_section
                for new_import in new_imports:
                    if new_import not in content:
                        new_import_section += f"{new_import}\n"
                content = content.replace(import_section, new_import_section)
            else:
                # Add imports at the top
                import_section = "\n".join(new_imports) + "\n\n"
                content = import_section + content

            # Update class inheritance
            old_inheritance_pattern = rf"class\s+{class_name}\s*\(\s*QMainWindow\s*\)"
            new_inheritance = f"class {class_name}(StandardWindow)"
            content = re.sub(old_inheritance_pattern, new_inheritance, content)

            # Update class inheritance for QDialog
            old_dialog_pattern = rf"class\s+{class_name}\s*\(\s*QDialog\s*\)"
            new_dialog_inheritance = f"class {class_name}(StandardDialog)"
            content = re.sub(old_dialog_pattern, new_dialog_inheritance, content)

            # Update __init__ method
            init_pattern = rf"def\s+__init__\s*\(\s*self\s*(?:,\s*[^)]*)?\):"
            init_match = re.search(init_pattern, content)

            if init_match:
                # Find the __init__ method and update it
                lines = content.split("\n")
                new_lines = []
                in_init = False
                init_updated = False

                for line in lines:
                    if re.match(rf"\s*def\s+__init__\s*\(", line):
                        in_init = True
                        # Update super().__init__ call
                        if (
                            "super()" in line
                            or "QMainWindow" in line
                            or "QDialog" in line
                        ):
                            continue

                    if in_init and not init_updated:
                        # Look for super().__init__ call
                        if (
                            "super()" in line
                            or "QMainWindow" in line
                            or "QDialog" in line
                        ):
                            # Replace with StandardWindow initialization
                            indent = len(line) - len(line.lstrip())
                            new_lines.append(
                                " " * indent
                                + 'super().__init__("'
                                + class_name.replace("GUI", "")
                                .replace("Window", "")
                                .replace("App", "")
                                + '")'
                            )
                            init_updated = True
                            continue

                    new_lines.append(line)

                content = "\n".join(new_lines)

            # Write updated content
            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                self.files_updated.append(str(file_path))
                print(f"Updated: {file_path}")
            else:
                self.files_skipped.append(str(file_path))

        except Exception as e:
            print(f"Error standardizing {file_path}: {e}")
            self.files_skipped.append(str(file_path))

    def standardize_all(self):
        """Standardize all GUI files."""
        print("Starting GUI standardization...")

        gui_files = self.find_gui_files()
        print(f"Found {len(gui_files)} GUI files to process")

        for file_path in gui_files:
            self.standardize_file(file_path)

        print(f"\nStandardization complete:")
        print(f"Files updated: {len(self.files_updated)}")
        print(f"Files skipped: {len(self.files_skipped)}")

        if self.files_updated:
            print("\nUpdated files:")
            for file_path in self.files_updated:
                print(f"  - {file_path}")

        if self.files_skipped:
            print("\nSkipped files:")
            for file_path in self.files_skipped:
                print(f"  - {file_path}")

    def create_example_usage(self):
        """Create an example of how to use the StandardWindow."""
        example_content = '''"""
Example of using StandardWindow for a new utility.

This demonstrates how to create a new utility with consistent styling.
"""

from gui.common.standard_window import StandardWindow
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton


class MyNewUtility(StandardWindow):
    """A new utility using the standard window."""
    
    def __init__(self):
        """Initialize the utility."""
        super().__init__("My New Utility")
        
        # Add custom content
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Get content layout
        layout = self.get_content_layout()
        
        # Add custom widgets
        label = QLabel("Welcome to My New Utility")
        layout.addWidget(label)
        
        # Add custom buttons
        self.add_primary_button("Process", self.process_data)
        self.add_secondary_button("Settings", self.show_settings)
    
    def process_data(self):
        """Process data with standard progress indication."""
        self.show_progress("Processing data...")
        
        # Do processing here
        # ...
        
        self.hide_progress("Processing complete")
        self.show_success_message("Data processed successfully")
    
    def show_settings(self):
        """Show settings dialog."""
        self.show_info_message("Settings dialog would open here")


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MyNewUtility()
    window.show()
    sys.exit(app.exec_())
'''

        example_path = self.workspace_path / "examples" / "standard_window_example.py"
        example_path.parent.mkdir(exist_ok=True)
        example_path.write_text(example_content, encoding="utf-8")
        print(f"Created example: {example_path}")


def main():
    """Main function to run the standardizer."""
    workspace_path = Path.cwd()
    standardizer = WindowStandardizer(workspace_path)
    standardizer.standardize_all()
    standardizer.create_example_usage()


if __name__ == "__main__":
    main()
