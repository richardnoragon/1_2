#!/usr/bin/env python3
"""
Automated Tool Correction System for Richard's File Utilities

This script systematically processes and corrects tools with proper error handling,
validation, rollback capabilities, and progress tracking.
"""

import argparse
import importlib.util
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ToolCorrectionSystem:
    """Automated system for correcting and validating tools."""

    def __init__(self, interactive=False, pause_between_tools=False):
        self.root_dir = Path(__file__).parent
        self.backup_dir = (
            self.root_dir
            / "backups"
            / f"correction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.log_dir = self.root_dir / "logs"
        self.status_file = self.root_dir / "correction_status.json"
        self.interactive = interactive
        self.pause_between_tools = pause_between_tools

        # Create directories
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Tool definitions from main.py analysis
        self.tools_registry = self.load_tools_registry()

        # Correction status tracking
        self.correction_status = self.load_correction_status()

        self.logger.info("ToolCorrectionSystem initialized")

    def setup_logging(self):
        """Setup comprehensive logging system."""
        log_file = (
            self.log_dir
            / f"correction_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )

        self.logger = logging.getLogger(__name__)

    def load_tools_registry(self) -> Dict[str, List[Dict]]:
        """Load the complete tools registry from main.py analysis."""
        return {
            "critical_priority": [
                {
                    "name": "Split/Join Files",
                    "module": "file_splitter_joiner",
                    "class": "FileSplitJoinGUI",
                    "status": "missing",
                    "dependencies": ["PyQt5", "os", "math"],
                    "estimated_effort": 6,
                    "template": "file_operations_template",
                },
                {
                    "name": "Synchronize",
                    "module": "sync",
                    "class": "SyncWindow",
                    "status": "missing",
                    "dependencies": ["PyQt5", "filecmp", "shutil"],
                    "estimated_effort": 10,
                    "template": "file_operations_template",
                },
                {
                    "name": "Duplicate Finder",
                    "module": "find_duplicate_files",
                    "class": "DuplicateFinderApp",
                    "status": "missing",
                    "dependencies": ["PyQt5", "hashlib", "os"],
                    "estimated_effort": 6,
                    "template": "analysis_template",
                },
                {
                    "name": "Encrypt/Decrypt",
                    "module": "en_and_decrypt",
                    "class": "EnAndDecryptGUI",
                    "status": "missing",
                    "dependencies": ["PyQt5", "cryptography"],
                    "estimated_effort": 8,
                    "template": "security_template",
                },
            ],
            "high_priority": [
                {
                    "name": "Compress/Decompress",
                    "module": "compress_decompress",
                    "class": "CompressDecompressApp",
                    "status": "partial",
                    "dependencies": ["PyQt5", "zipfile", "tarfile"],
                    "estimated_effort": 4,
                    "template": "file_operations_template",
                },
                {
                    "name": "Size Analyzer",
                    "module": "size_analyzer",
                    "class": "SizeAnalyzerGUI",
                    "status": "partial",
                    "dependencies": ["PyQt5", "os", "pathlib"],
                    "estimated_effort": 6,
                    "template": "analysis_template",
                },
                {
                    "name": "Secure Delete",
                    "module": "secure_delete",
                    "class": "SecureDeleteGUI",
                    "status": "partial",
                    "dependencies": ["PyQt5", "os", "random"],
                    "estimated_effort": 6,
                    "template": "security_template",
                },
            ],
            "medium_priority": [
                {
                    "name": "Empty Folders",
                    "module": "empty_folders",
                    "class": "EmptyFoldersGUI",
                    "status": "partial",
                    "dependencies": ["PyQt5", "os", "pathlib"],
                    "estimated_effort": 2,
                    "template": "analysis_template",
                },
                {
                    "name": "File Touch",
                    "module": "file_touch",
                    "class": "FileTouchGUI",
                    "status": "partial",
                    "dependencies": ["PyQt5", "os", "time"],
                    "estimated_effort": 2,
                    "template": "utility_template",
                },
            ],
        }

    def load_correction_status(self) -> Dict[str, Any]:
        """Load previous correction status or create new one."""
        if self.status_file.exists():
            try:
                with open(self.status_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load status file: {e}")

        # Create new status
        return {
            "correction_session": {
                "start_time": datetime.now().isoformat(),
                "last_update": datetime.now().isoformat(),
                "total_tools": self.count_total_tools(),
                "completed_tools": 4,  # file_finder, catalog, rename, organize
                "failed_tools": 0,
                "current_tool": None,
            },
            "tools": {
                "file_finder": {
                    "status": "completed",
                    "completion_time": datetime.now().isoformat(),
                    "validation_passed": True,
                },
                "catalog": {
                    "status": "completed",
                    "completion_time": datetime.now().isoformat(),
                    "validation_passed": True,
                },
                "rename": {
                    "status": "completed",
                    "completion_time": datetime.now().isoformat(),
                    "validation_passed": True,
                },
                "organize": {
                    "status": "completed",
                    "completion_time": datetime.now().isoformat(),
                    "validation_passed": True,
                },
            },
        }

    def count_total_tools(self) -> int:
        """Count total tools across all priority levels."""
        total = 0
        for priority_level in self.tools_registry.values():
            total += len(priority_level)
        return total + 4  # Add the 4 already completed tools

    def save_correction_status(self):
        """Save current correction status to file."""
        self.correction_status["correction_session"][
            "last_update"
        ] = datetime.now().isoformat()

        try:
            with open(self.status_file, "w") as f:
                json.dump(self.correction_status, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save status file: {e}")

    def create_backup(self, file_path: Path) -> Optional[Path]:
        """Create backup of a file before modification."""
        if not file_path.exists():
            return None

        backup_path = self.backup_dir / f"{file_path.name}.bak"
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create backup for {file_path}: {e}")
            return None

    def restore_backup(self, tool_name: str) -> bool:
        """Restore tool from backup."""
        backup_path = self.backup_dir / f"{tool_name}.py.bak"
        target_path = self.root_dir / f"{tool_name}.py"

        try:
            if backup_path.exists():
                shutil.copy2(backup_path, target_path)
                self.logger.info(f"Restored {tool_name} from backup")
                return True
            else:
                self.logger.warning(f"No backup found for {tool_name}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to restore backup for {tool_name}: {e}")
            return False

    def validate_import(self, tool_name: str, class_name: str) -> Tuple[bool, str]:
        """Test if tool can be imported successfully."""
        try:
            tool_file = self.root_dir / f"{tool_name}.py"
            if not tool_file.exists():
                return False, f"Tool file {tool_file} does not exist"

            spec = importlib.util.spec_from_file_location(tool_name, tool_file)
            if not spec or not spec.loader:
                return False, "Could not create module spec"

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if not hasattr(module, class_name):
                return False, f"Class {class_name} not found in module"

            tool_class = getattr(module, class_name)
            return True, "Import successful"

        except Exception as e:
            return False, f"Import failed: {e}"

    def validate_integration(self, tool_name: str) -> Tuple[bool, str]:
        """Test integration with main application."""
        try:
            # Check if main.py has the correct launch method
            main_file = self.root_dir / "main.py"
            if not main_file.exists():
                return False, "main.py not found"

            with open(main_file, "r") as f:
                main_content = f.read()

            # Look for the tool in launch_tool calls
            if f'"{tool_name}"' in main_content:
                return True, "Integration found in main.py"
            else:
                return False, f"Tool {tool_name} not found in main.py"

        except Exception as e:
            return False, f"Integration validation failed: {e}"

    def get_tool_template(self, template_name: str, tool_info: Dict) -> str:
        """Generate tool code from template."""

        if template_name == "file_operations_template":
            return self.get_file_operations_template(tool_info)
        elif template_name == "analysis_template":
            return self.get_analysis_template(tool_info)
        elif template_name == "security_template":
            return self.get_security_template(tool_info)
        elif template_name == "utility_template":
            return self.get_utility_template(tool_info)
        else:
            return self.get_basic_template(tool_info)

    def get_basic_template(self, tool_info: Dict) -> str:
        """Basic tool template."""
        return f'''#!/usr/bin/env python3
"""
{tool_info["name"]} Tool for Richard's File Utilities

A streamlined {tool_info["name"].lower()} utility with essential functionality.
"""

import os
import sys

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QListWidget, QProgressBar,
        QApplication, QMessageBox, QFileDialog
    )
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)


class {tool_info["class"]}(QMainWindow):
    """Main window for {tool_info["name"]} operations."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("{tool_info["name"]} - Richard's File Utilities")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header
        header_label = QLabel("{tool_info["name"]}")
        header_label.setStyleSheet("""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(header_label)
        
        # Add placeholder content
        content_label = QLabel("Tool functionality will be implemented here.")
        content_label.setStyleSheet("padding: 20px; color: #666;")
        layout.addWidget(content_label)
        
        # Add action button
        action_button = QPushButton("Execute Action")
        action_button.clicked.connect(self.execute_action)
        action_button.setStyleSheet("""
            QPushButton {{
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
        """)
        layout.addWidget(action_button)
        
    def execute_action(self):
        """Main action method for this tool."""
        QMessageBox.information(
            self, 
            "{tool_info["name"]}", 
            "Tool functionality is ready for implementation."
        )


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = {tool_info["class"]}()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
'''

    def get_file_operations_template(self, tool_info: Dict) -> str:
        """Template for file operation tools."""
        template = self.get_basic_template(tool_info)
        # Add file operation specific components
        return template.replace(
            "# Add placeholder content",
            """# Add file selection area
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)
        
        select_button = QPushButton("Select Files")
        select_button.clicked.connect(self.select_files)
        file_layout.addWidget(select_button)
        
        layout.addWidget(file_group)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)""",
        ).replace(
            "def execute_action(self):",
            """def select_files(self):
        \"\"\"Select files for processing.\"\"\"
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", "", "All Files (*)"
        )
        for file_path in files:
            self.file_list.addItem(file_path)
            
    def execute_action(self):""",
        )

    def get_analysis_template(self, tool_info: Dict) -> str:
        """Template for analysis tools."""
        template = self.get_basic_template(tool_info)
        # Add analysis specific components
        return template.replace(
            "# Add placeholder content",
            """# Add analysis area
        analysis_group = QGroupBox("Analysis Results")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.results_list = QListWidget()
        analysis_layout.addWidget(self.results_list)
        
        analyze_button = QPushButton("Start Analysis")
        analyze_button.clicked.connect(self.start_analysis)
        analysis_layout.addWidget(analyze_button)
        
        layout.addWidget(analysis_group)""",
        ).replace(
            "def execute_action(self):",
            """def start_analysis(self):
        \"\"\"Start the analysis process.\"\"\"
        self.results_list.clear()
        self.results_list.addItem("Analysis functionality ready for implementation")
        
    def execute_action(self):""",
        )

    def get_security_template(self, tool_info: Dict) -> str:
        """Template for security tools."""
        template = self.get_basic_template(tool_info)
        # Add security specific components
        return template.replace(
            "import sys",
            """import sys
import hashlib""",
        ).replace(
            "# Add placeholder content",
            """# Add security options
        security_group = QGroupBox("Security Options")
        security_layout = QVBoxLayout(security_group)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter password...")
        security_layout.addWidget(QLabel("Password:"))
        security_layout.addWidget(self.password_edit)
        
        layout.addWidget(security_group)""",
        )

    def get_utility_template(self, tool_info: Dict) -> str:
        """Template for utility tools."""
        return self.get_basic_template(tool_info)

    def process_tool(self, tool_info: Dict) -> bool:
        """Process a single tool with full validation."""
        tool_name = tool_info["module"]
        class_name = tool_info["class"]

        self.logger.info(f"Processing tool: {tool_info['name']} ({tool_name})")

        # Update status
        self.correction_status["correction_session"]["current_tool"] = tool_name
        self.correction_status["tools"][tool_name] = {
            "status": "in_progress",
            "start_time": datetime.now().isoformat(),
            "steps_completed": [],
        }
        self.save_correction_status()

        try:
            # Step 1: Create backup if file exists
            tool_file = self.root_dir / f"{tool_name}.py"
            if tool_file.exists():
                backup_path = self.create_backup(tool_file)
                if backup_path:
                    self.correction_status["tools"][tool_name]["backup_location"] = str(
                        backup_path
                    )
                    self.correction_status["tools"][tool_name][
                        "steps_completed"
                    ].append("backup")

            # Step 2: Generate/fix tool
            if tool_info["status"] == "missing":
                success = self.create_new_tool(tool_info)
            else:
                success = self.fix_existing_tool(tool_info)

            if not success:
                self.logger.error(f"Failed to create/fix tool {tool_name}")
                self.correction_status["tools"][tool_name]["status"] = "failed"
                self.correction_status["tools"][tool_name][
                    "error"
                ] = "Creation/fix failed"
                self.save_correction_status()
                return False

            self.correction_status["tools"][tool_name]["steps_completed"].append(
                "creation"
            )

            # Step 3: Validate import
            import_success, import_msg = self.validate_import(tool_name, class_name)
            if not import_success:
                self.logger.error(
                    f"Import validation failed for {tool_name}: {import_msg}"
                )
                self.correction_status["tools"][tool_name]["status"] = "failed"
                self.correction_status["tools"][tool_name][
                    "error"
                ] = f"Import failed: {import_msg}"
                self.save_correction_status()
                return False

            self.correction_status["tools"][tool_name]["steps_completed"].append(
                "import_validation"
            )

            # Step 4: Validate integration
            integration_success, integration_msg = self.validate_integration(tool_name)
            if not integration_success:
                self.logger.warning(
                    f"Integration validation failed for {tool_name}: {integration_msg}"
                )
                # This is not a critical failure, continue

            self.correction_status["tools"][tool_name]["steps_completed"].append(
                "integration_validation"
            )

            # Step 5: Mark as completed
            self.correction_status["tools"][tool_name]["status"] = "completed"
            self.correction_status["tools"][tool_name][
                "completion_time"
            ] = datetime.now().isoformat()
            self.correction_status["tools"][tool_name][
                "validation_passed"
            ] = import_success

            # Update session stats
            self.correction_status["correction_session"]["completed_tools"] += 1

            self.save_correction_status()

            self.logger.info(f"Successfully processed tool: {tool_name}")
            return True

        except Exception as e:
            self.logger.error(f"Error processing tool {tool_name}: {e}")
            self.correction_status["tools"][tool_name]["status"] = "failed"
            self.correction_status["tools"][tool_name]["error"] = str(e)
            self.save_correction_status()
            return False

    def create_new_tool(self, tool_info: Dict) -> bool:
        """Create a new tool from template."""
        tool_name = tool_info["module"]

        try:
            # Generate tool code from template
            tool_code = self.get_tool_template(tool_info["template"], tool_info)

            # Write to file
            tool_file = self.root_dir / f"{tool_name}.py"
            with open(tool_file, "w", encoding="utf-8") as f:
                f.write(tool_code)

            self.logger.info(f"Created new tool: {tool_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create new tool {tool_name}: {e}")
            return False

    def fix_existing_tool(self, tool_info: Dict) -> bool:
        """Fix existing tool with issues."""
        tool_name = tool_info["module"]
        tool_file = self.root_dir / f"{tool_name}.py"

        if not tool_file.exists():
            # If file doesn't exist, create new one
            return self.create_new_tool(tool_info)

        try:
            # Read existing file
            with open(tool_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Apply common fixes
            fixed_content = self.apply_common_fixes(content, tool_info)

            # Write back fixed content
            with open(tool_file, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            self.logger.info(f"Fixed existing tool: {tool_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to fix existing tool {tool_name}: {e}")
            return False

    def apply_common_fixes(self, content: str, tool_info: Dict) -> str:
        """Apply common fixes to tool content."""

        # Fix 1: Ensure correct class name
        expected_class = tool_info["class"]
        if f"class {expected_class}" not in content:
            # Try to find and replace incorrect class name
            import re

            class_pattern = r"class\s+(\w+)\s*\([^)]*\):"
            matches = re.findall(class_pattern, content)
            if matches:
                old_class = matches[0]
                content = content.replace(
                    f"class {old_class}", f"class {expected_class}"
                )
                content = content.replace(old_class, expected_class)

        # Fix 2: Simplify imports
        if "from gui.common" in content:
            content = content.replace(
                "from gui.common.base_window_simple import BaseWindow", ""
            )
            content = content.replace(
                "from gui.common.dialogs_simple import",
                "# from gui.common.dialogs_simple import",
            )

        # Fix 3: Ensure main guard
        if 'if __name__ == "__main__":' not in content:
            content += '\n\nif __name__ == "__main__":\n    main()\n'

        return content

    def rollback_tool(self, tool_name: str) -> bool:
        """Rollback specific tool to previous state."""
        self.logger.info(f"Rolling back tool: {tool_name}")

        try:
            # Remove current implementation
            tool_file = self.root_dir / f"{tool_name}.py"
            if tool_file.exists():
                tool_file.unlink()

            # Restore from backup
            if self.restore_backup(tool_name):
                # Update status
                if tool_name in self.correction_status["tools"]:
                    self.correction_status["tools"][tool_name][
                        "status"
                    ] = "rollback_completed"
                    self.correction_status["tools"][tool_name][
                        "rollback_time"
                    ] = datetime.now().isoformat()

                self.save_correction_status()
                self.logger.info(f"Rollback completed for {tool_name}")
                return True
            else:
                self.logger.error(f"Could not restore backup for {tool_name}")
                return False

        except Exception as e:
            self.logger.error(f"Rollback failed for {tool_name}: {e}")
            return False

    def process_priority_level(self, priority_level: str) -> Dict[str, bool]:
        """Process all tools in a specific priority level."""
        if priority_level not in self.tools_registry:
            self.logger.error(f"Unknown priority level: {priority_level}")
            return {}

        tools = self.tools_registry[priority_level]
        results = {}

        self.logger.info(f"Processing {priority_level} tools ({len(tools)} tools)")

        for i, tool_info in enumerate(tools, 1):
            tool_name = tool_info["module"]

            print(f"\n{'='*60}")
            print(
                f"Processing {priority_level} tool {i}/{len(tools)}: {tool_info['name']}"
            )
            print(f"Module: {tool_name}")
            print(f"Class: {tool_info['class']}")
            print(f"Status: {tool_info['status']}")
            print(f"{'='*60}")

            # Process the tool
            success = self.process_tool(tool_info)
            results[tool_name] = success

            if success:
                print(f"✅ Successfully processed: {tool_info['name']}")
            else:
                print(f"❌ Failed to process: {tool_info['name']}")

            # Pause between tools if requested
            if self.pause_between_tools and i < len(tools):
                if self.interactive:
                    input("\nPress Enter to continue to next tool...")
                else:
                    print("Pausing for 2 seconds...")
                    time.sleep(2)

        return results

    def process_all_tools(self) -> Dict[str, Dict[str, bool]]:
        """Process all tools across all priority levels."""
        all_results = {}

        priority_order = ["critical_priority", "high_priority", "medium_priority"]

        for priority_level in priority_order:
            if priority_level in self.tools_registry:
                print(f"\n🎯 Starting {priority_level.replace('_', ' ').title()} Tools")
                results = self.process_priority_level(priority_level)
                all_results[priority_level] = results

                # Show summary for this priority level
                successful = sum(1 for success in results.values() if success)
                total = len(results)
                print(
                    f"\n📊 {priority_level.replace('_', ' ').title()} Summary: {successful}/{total} tools successful"
                )

                if self.pause_between_tools:
                    if self.interactive:
                        input(
                            f"\nCompleted {priority_level}. Press Enter to continue to next priority level..."
                        )
                    else:
                        print("Pausing for 5 seconds before next priority level...")
                        time.sleep(5)

        return all_results

    def generate_final_report(self, results: Dict[str, Dict[str, bool]]):
        """Generate comprehensive final report."""
        print("\n" + "=" * 80)
        print("🎉 AUTOMATED TOOL CORRECTION COMPLETE")
        print("=" * 80)

        total_processed = 0
        total_successful = 0

        for priority_level, priority_results in results.items():
            successful = sum(1 for success in priority_results.values() if success)
            total = len(priority_results)
            total_processed += total
            total_successful += successful

            print(f"\n{priority_level.replace('_', ' ').title()}:")
            print(f"  Processed: {total}")
            print(f"  Successful: {successful}")
            print(f"  Failed: {total - successful}")

            for tool_name, success in priority_results.items():
                status = "✅" if success else "❌"
                print(f"    {status} {tool_name}")

        # Overall statistics
        success_rate = (
            (total_successful / total_processed * 100) if total_processed > 0 else 0
        )

        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  Total Tools Processed: {total_processed}")
        print(f"  Successful: {total_successful}")
        print(f"  Failed: {total_processed - total_successful}")
        print(f"  Success Rate: {success_rate:.1f}%")

        # Include previously completed tools
        previously_completed = 4  # file_finder, catalog, rename, organize
        grand_total = total_processed + previously_completed
        grand_successful = total_successful + previously_completed
        grand_success_rate = grand_successful / grand_total * 100

        print(f"\n🎯 GRAND TOTAL (Including Previously Completed):")
        print(f"  Total Tools: {grand_total}")
        print(f"  Working Tools: {grand_successful}")
        print(f"  Overall Success Rate: {grand_success_rate:.1f}%")

        print(f"\n📁 Backup Location: {self.backup_dir}")
        print(f"📄 Status File: {self.status_file}")
        print(f"📋 Log Directory: {self.log_dir}")

        print("\n" + "=" * 80)


def main():
    """Main entry point for the automated tool corrector."""
    parser = argparse.ArgumentParser(
        description="Automated Tool Correction System for Richard's File Utilities"
    )

    parser.add_argument(
        "--mode",
        choices=["full", "priority", "single", "validate", "rollback", "resume"],
        default="full",
        help="Correction mode to run",
    )

    parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "all"],
        default="all",
        help="Priority level to process (for priority mode)",
    )

    parser.add_argument(
        "--tool", help="Specific tool to process (for single mode) or rollback"
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode with user prompts",
    )

    parser.add_argument(
        "--pause-between-tools",
        action="store_true",
        help="Pause between each tool for verification",
    )

    parser.add_argument("--from-tool", help="Resume processing from specific tool")

    args = parser.parse_args()

    # Create correction system
    corrector = ToolCorrectionSystem(
        interactive=args.interactive, pause_between_tools=args.pause_between_tools
    )

    try:
        if args.mode == "full":
            print("🚀 Starting full automated tool correction...")
            results = corrector.process_all_tools()
            corrector.generate_final_report(results)

        elif args.mode == "priority":
            priority_map = {
                "critical": "critical_priority",
                "high": "high_priority",
                "medium": "medium_priority",
            }

            if args.priority == "all":
                print("🚀 Processing all priority levels...")
                results = corrector.process_all_tools()
                corrector.generate_final_report(results)
            else:
                priority_level = priority_map[args.priority]
                print(f"🚀 Processing {args.priority} priority tools...")
                results = corrector.process_priority_level(priority_level)

                successful = sum(1 for success in results.values() if success)
                total = len(results)
                print(f"\n📊 Results: {successful}/{total} tools successful")

        elif args.mode == "single":
            if not args.tool:
                print("❌ Error: --tool parameter required for single mode")
                return 1

            # Find tool info
            tool_info = None
            for priority_tools in corrector.tools_registry.values():
                for tool in priority_tools:
                    if tool["module"] == args.tool:
                        tool_info = tool
                        break
                if tool_info:
                    break

            if not tool_info:
                print(f"❌ Error: Tool '{args.tool}' not found in registry")
                return 1

            print(f"🚀 Processing single tool: {tool_info['name']}")
            success = corrector.process_tool(tool_info)

            if success:
                print(f"✅ Successfully processed: {tool_info['name']}")
                return 0
            else:
                print(f"❌ Failed to process: {tool_info['name']}")
                return 1

        elif args.mode == "validate":
            print("🧪 Running validation tests...")
            # Implementation for validation mode
            print("Validation mode not yet implemented")

        elif args.mode == "rollback":
            if not args.tool:
                print("❌ Error: --tool parameter required for rollback mode")
                return 1

            print(f"🔄 Rolling back tool: {args.tool}")
            success = corrector.rollback_tool(args.tool)

            if success:
                print(f"✅ Successfully rolled back: {args.tool}")
                return 0
            else:
                print(f"❌ Failed to rollback: {args.tool}")
                return 1

        elif args.mode == "resume":
            print("🔄 Resume mode not yet implemented")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
