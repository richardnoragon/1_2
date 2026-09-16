#!/usr/bin/env python3
"""
Enhanced PDF Tools Widget for Richard's File Utilities Hub

This module provides a comprehensive PDF tools interface that dynamically
discovers and displays tools based on the folder structure, integrating
seamlessly into the main RFU hub.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.gui.themes import ThemeManager, token

# ---------------------------------------------------------------------------
# GRD-1a: Guardian registration (graceful no-op when guardian absent)
# ---------------------------------------------------------------------------
try:
    from src.core.guardian import register_gui_component
except ImportError:

    def register_gui_component(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# TEL: Telemetry helpers (graceful no-op when telemetry absent)
# ---------------------------------------------------------------------------
try:
    from src.gui.telemetry import emit_telemetry

    def _emit_telemetry(event_type, **kw):
        emit_telemetry(event_type, **kw)  # noqa: E731

except ImportError:

    def _emit_telemetry(*a, **kw):
        pass  # noqa: E731


# ---------------------------------------------------------------------------
# STR: Centralised string constants with fallback (P1-C15 / STR-1)
# ---------------------------------------------------------------------------
try:
    from src.rfu.ui_strings import PDFTools as _PDFStrings
except ImportError:

    class _PDFStrings:  # type: ignore[no-redef]
        TITLE = "PDF Tools"
        WINDOW_TITLE = "PDF Tools — RFU"
        LOADING = "Loading PDF Tools…"
        ERR_INIT_FAILED = (
            "Could not start PDF Tools. " "Please try again or restart the application."
        )
        ERR_NO_FILE = "No PDF file selected."
        ERR_LOAD_FAILED = "Failed to load the selected PDF file."


# ---------------------------------------------------------------------------
# CP: Shared UI components (graceful fallback when unavailable)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.modal import Modal
    from src.gui.components.toast import ToastNotification

    _CP_AVAILABLE = True
except ImportError:
    PrimaryButton = SecondaryButton = None  # type: ignore[assignment,misc]
    Modal = None  # type: ignore[assignment,misc]
    ToastNotification = None
    _CP_AVAILABLE = False


class PDFToolsStateManager:
    """Manages state and data sharing between PDF tool components."""

    def __init__(self):
        self.current_file = None
        self.recent_files = []
        self.tool_preferences = {}
        self.operation_history = []
        self.shared_data = {}
        self.active_operations = {}

    def set_current_file(self, file_path: str):
        """Set the current working PDF file."""
        if file_path:
            self.current_file = file_path
            if file_path not in self.recent_files:
                self.recent_files.insert(0, file_path)
                self.recent_files = self.recent_files[:10]
            return True
        return False

    def get_current_file(self) -> Optional[str]:
        """Get the current working PDF file."""
        return self.current_file

    def save_operation_state(self, tool_name: str, operation: str, parameters: Dict):
        """Save operation state for history tracking."""
        operation_record = {
            "tool": tool_name,
            "operation": operation,
            "parameters": parameters,
            "timestamp": datetime.now(),
            "file": self.current_file,
        }
        self.operation_history.append(operation_record)
        self.operation_history = self.operation_history[-50:]

    def share_data_between_tools(self, source_tool: str, target_tool: str, data: Dict):
        """Share data between PDF tool components."""
        key = (source_tool, target_tool)
        self.shared_data[key] = dict(data)
        return self.shared_data[key]

    def get_shared_data(self, source_tool: str, target_tool: str):
        """Return shared data for a tool pair."""
        return self.shared_data.get((source_tool, target_tool), {})

    def get_operation_history(self, tool_name: Optional[str] = None):
        """Return recent operations, optionally filtered by tool."""
        if tool_name is None:
            return list(self.operation_history)
        return [entry for entry in self.operation_history if entry.get("tool") == tool_name]


class EnhancedPDFToolsWidget(QWidget):
    """
    Enhanced PDF Tools widget with folder-based tool discovery
    """

    # Signals for communication with parent
    tool_operation_started = pyqtSignal(str, str)  # tool_name, operation
    tool_operation_completed = pyqtSignal(
        str, str, bool
    )  # tool_name, operation, success
    file_selected = pyqtSignal(str)  # file_path

    def __init__(self, parent=None, hub_instance=None):
        super().__init__(parent)
        self._hub = hub_instance
        self.parent_window = parent

        # Initialize managers
        self.state_manager = PDFToolsStateManager()
        self.logger = logging.getLogger("PDFTools")
        self._logger = self.logger  # HUB-1: canonical alias

        # UI components
        self.main_layout = None
        self.status_label = None
        self.progress_bar = None
        self.current_file_label = None
        self.categories_layout = None
        self.programs_container = None
        self.programs_layout = None
        self.category_title_label = None
        self.back_button = None

        self.init_ui()
        self.setup_connections()
        register_gui_component(
            self, tool_id="pdf_tools", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="pdf_tools")
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return self.main_layout is not None
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("EnhancedPDFToolsWidget entering degraded mode")
        except Exception:
            pass
        _emit_telemetry("ui_error_event", tool_id="pdf_tools", error_type="degraded")

    def init_ui(self):
        """Initialize the PDF tools interface"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Create header section
        self.create_header_section()

        # Create main interface
        self.create_main_interface()

        # Create status section
        self.create_status_section()

        # Apply styling
        self.apply_enhanced_styling()

    def create_header_section(self):
        """Create the header section with file selection and controls"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {token('dialog_background')};
                border: 1px solid {token('border_light')};
                border-radius: 8px;
                padding: 10px;
            }}
        """
        )

        header_layout = QHBoxLayout(header_frame)

        # Current file display
        file_group = _ui_widget(QGroupBox, 'Legacy.sa945443e70bd24a1', 'setTitle')
        file_layout = QHBoxLayout(file_group)

        self.current_file_label = _ui_widget(QLabel, 'Legacy.s26bfbd5c83f90db3', 'setText')
        self.current_file_label.setStyleSheet(
            f"font-weight: bold; color: {token('text_secondary')};"
        )
        file_layout.addWidget(self.current_file_label)

        # File selection button
        _PB = PrimaryButton if PrimaryButton else QPushButton
        select_file_btn = _PB("Select PDF File")
        select_file_btn.clicked.connect(self.select_pdf_file)
        file_layout.addWidget(select_file_btn)

        header_layout.addWidget(file_group)

        # Quick actions
        actions_group = _ui_widget(QGroupBox, 'Legacy.s2cc2b6f7f200e65c', 'setTitle')
        actions_layout = QHBoxLayout(actions_group)

        # Recent files button
        _SB = SecondaryButton if SecondaryButton else QPushButton
        recent_btn = _SB("Recent Files")
        recent_btn.clicked.connect(self.show_recent_files)
        actions_layout.addWidget(recent_btn)

        clear_cache_btn = _SB("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        actions_layout.addWidget(clear_cache_btn)

        header_layout.addWidget(actions_group)

        self.main_layout.addWidget(header_frame)

    def create_main_interface(self):
        """Create the main interface with PDF tools based on folder structure"""
        # Create main container widget
        main_container = QWidget()
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(15)

        # Create title
        title_label = _ui_widget(QLabel, 'Legacy.sbac111366bbf94a7', 'setText')
        title_label.setStyleSheet(
            f"""
            font: bold 16pt "Segoe UI";
            color: {token('text_primary')};
            margin: 10px 0;
        """
        )
        container_layout.addWidget(title_label)

        # Create scroll area for categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_widget = QWidget()
        self.categories_layout = QGridLayout(scroll_widget)
        self.categories_layout.setSpacing(15)

        # Discover and create category buttons from folder structure
        self.discover_and_create_categories()

        scroll_area.setWidget(scroll_widget)
        container_layout.addWidget(scroll_area)

        # Create programs display area (initially hidden)
        self.programs_container = QWidget()
        self.programs_container.setVisible(False)
        programs_layout = QVBoxLayout(self.programs_container)

        # Back button
        back_layout = QHBoxLayout()
        _SB2 = SecondaryButton if SecondaryButton else QPushButton
        self.back_button = _SB2("← Back to Categories")
        self.back_button.clicked.connect(self.show_categories)
        back_layout.addWidget(self.back_button)
        back_layout.addStretch()
        programs_layout.addLayout(back_layout)

        # Category title label
        self.category_title_label = QLabel()
        self.category_title_label.setStyleSheet(
            f"""
            font: bold 14pt "Segoe UI";
            color: {token('text_primary')};
            margin: 10px 0;
        """
        )
        programs_layout.addWidget(self.category_title_label)

        # Programs scroll area
        self.programs_scroll = QScrollArea()
        self.programs_scroll.setWidgetResizable(True)
        self.programs_scroll.setFrameStyle(QFrame.NoFrame)
        self.programs_widget = QWidget()
        self.programs_layout = QGridLayout(self.programs_widget)
        self.programs_layout.setSpacing(15)
        self.programs_scroll.setWidget(self.programs_widget)
        programs_layout.addWidget(self.programs_scroll)

        container_layout.addWidget(self.programs_container)

        self.main_layout.addWidget(main_container)

    def discover_and_create_categories(self):
        """Discover PDF tool categories from folder structure and create buttons"""
        # Define the PDF tools base path - fix path calculation
        # Current file is in: src/tools/pdf_tools/widgets/enhanced_pdf_tools_widget.py
        # We want to get to: src/tools/pdf_tools/
        base_path = Path(__file__).parent.parent

        # Category mapping with colors and descriptions
        category_config = {
            "pdf_basic_operations": {
                "display_name": "Basic Operations",
                "description": "Merge, split, and sign PDFs",
                "color": token("semantic_success"),
            },
            "pdf_content_extraction": {
                "display_name": "Content Extraction",
                "description": "Extract text, images, tables, and metadata",
                "color": token("button_primary"),
            },
            "pdf_security": {
                "display_name": "Security",
                "description": "Encrypt, decrypt, and manage security",
                "color": token("semantic_error"),
            },
            "pdf_enhancements": {
                "display_name": "Enhancements",
                "description": "Watermarks, OCR, and highlighting",
                "color": token("semantic_warning"),
            },
            "pdf_conversion": {
                "display_name": "Conversion",
                "description": "Convert PDFs to/from other formats",
                "color": token("color_purple"),
            },
            "pdf_view_analysis": {
                "display_name": "View & Analysis",
                "description": "View and analyze PDF contents",
                "color": token("color_blue_grey"),
            },
        }

        # Create category buttons
        row, col = 0, 0
        for folder_name, config in category_config.items():
            folder_path = base_path / folder_name

            if folder_path.exists() and folder_path.is_dir():
                # Create category button
                category_button = self.create_category_button(
                    config["display_name"],
                    config["description"],
                    config["color"],
                    folder_name,
                    folder_path,
                )

                self.categories_layout.addWidget(category_button, row, col)

                # Move to next position
                col += 1
                if col >= 2:  # 2 columns
                    col = 0
                    row += 1

        # Add stretch to push buttons to top
        self.categories_layout.setRowStretch(row + 1, 1)

    def create_category_button(
        self,
        name: str,
        description: str,
        color: str,
        folder_name: str,
        folder_path: Path,
    ):
        """Create a category button that shows programs when clicked"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {token('window_background')};
                border: 2px solid {token('border_light')};
                border-radius: 12px;
                margin: 5px;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: {token('dialog_background')};
            }}
        """
        )
        frame.setMinimumHeight(140)
        frame.setMaximumHeight(160)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Category button
        button = QPushButton(name)
        button.setAccessibleName(name)
        button.setMinimumHeight(44)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font: bold 14pt "Segoe UI";
                border: none;
                padding: 12px;
                border-radius: 8px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.2)};
            }}
        """
        )
        button.clicked.connect(
            lambda: self.show_category_programs(name, folder_name, folder_path)
        )
        layout.addWidget(button)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet(
            f"""

            color: {token('text_muted')};
            font-weight: normal;
        """
        )
        font_tokens.bind(desc_label, "font.body")
        layout.addWidget(desc_label)

        return frame

    def show_category_programs(
        self, category_name: str, folder_name: str, folder_path: Path
    ):
        """Show programs available in the selected category"""
        # Clear existing programs
        self.clear_programs_layout()

        # Set category title
        self.category_title_label.setText(f"{category_name} - Available Programs")

        # Discover programs in the folder
        programs = self.discover_programs_in_folder(folder_path)

        if not programs:
            # Show message if no programs found
            no_programs_label = _ui_widget(QLabel, 'Legacy.s0df49f6b2ebc9d69', 'setText')
            no_programs_label.setAlignment(Qt.AlignCenter)
            no_programs_label.setStyleSheet(
                f"""

                color: {token('text_muted')};
                margin: 50px;
            """
            )
            font_tokens.bind(no_programs_label, "font.body")
            self.programs_layout.addWidget(no_programs_label, 0, 0, 1, 2)
        else:
            # Create program buttons
            row, col = 0, 0
            for program_info in programs:
                program_button = self.create_program_button(
                    program_info["name"],
                    program_info["description"],
                    program_info["file_path"],
                    category_name,
                )

                self.programs_layout.addWidget(program_button, row, col)

                # Move to next position
                col += 1
                if col >= 2:  # 2 columns
                    col = 0
                    row += 1

        # Show programs container and hide categories
        self.programs_container.setVisible(True)
        # Hide categories (find the parent of categories_layout)
        categories_widget = self.categories_layout.parent()
        while categories_widget and not hasattr(categories_widget, "setVisible"):
            categories_widget = categories_widget.parent()
        if categories_widget and hasattr(categories_widget, "setVisible"):
            categories_widget.parent().setVisible(False)

    def discover_programs_in_folder(self, folder_path: Path) -> List[Dict[str, str]]:
        """Discover Python programs in a folder and extract information"""
        programs = []

        # Look for .py files (excluding __init__.py and backup files)
        for py_file in folder_path.glob("*.py"):
            if py_file.name not in ["__init__.py"]:
                # Skip error files and backup files
                if (
                    "error" in py_file.name.lower()
                    or "backup" in py_file.name.lower()
                    or py_file.name.endswith("_error.txt")
                ):
                    continue

                program_name = py_file.stem
                # Clean up program name for display
                display_name = program_name.replace("_", " ").title()

                # Try to extract description from file
                description = self.extract_program_description(py_file)

                programs.append(
                    {
                        "name": display_name,
                        "description": description,
                        "file_path": str(py_file),
                        "module_name": program_name,
                    }
                )

        return sorted(programs, key=lambda x: x["name"])

    def extract_program_description(self, file_path: Path) -> str:
        """Extract description from a Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for module docstring
            import ast

            try:
                tree = ast.parse(content)
                if (
                    tree.body
                    and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant)
                    and isinstance(tree.body[0].value.value, str)
                ):
                    docstring = tree.body[0].value.value.strip()
                    # Return first line of docstring
                    return docstring.split("\n")[0][:100]
            except:
                pass

            # Fallback: look for comments at the top
            lines = content.split("\n")
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if line.startswith("#") and len(line) > 5:
                    return line[1:].strip()[:100]

        except (
            Exception
        ):  # ERR: non-fatal — description fallback returns default; non-critical
            pass

    def create_program_button(
        self, name: str, description: str, file_path: str, category: str
    ):
        """Create a button for an individual program"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {token('window_background')};
                border: 2px solid {token('border_light')};
                border-radius: 12px;
                margin: 5px;
            }}
            QFrame:hover {{
                border-color: {token('button_primary')};
                background-color: {token('dialog_background')};
            }}
        """
        )
        frame.setMinimumHeight(120)
        frame.setMaximumHeight(140)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Program button
        button = QPushButton(name)
        button.setAccessibleName(name)
        button.setMinimumHeight(44)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {token('button_primary')};
                color: white;
                font: bold 12pt "Segoe UI";
                border: none;
                padding: 10px;
                border-radius: 6px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {token('button_primary')};
            }}
            QPushButton:pressed {{
                background-color: {token('color_navy_dark')};
            }}
        """
        )
        button.clicked.connect(lambda: self.launch_program(name, file_path, category))
        layout.addWidget(button)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet(
            f"""

            color: {token('text_muted')};
            font-weight: normal;
        """
        )
        font_tokens.bind(desc_label, "font.body")
        layout.addWidget(desc_label)

        return frame

    def clear_programs_layout(self):
        """Clear all widgets from the programs layout"""
        while self.programs_layout.count():
            child = self.programs_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_categories(self):
        """Show the categories view and hide programs view"""
        self.programs_container.setVisible(False)
        # Show categories container
        categories_widget = self.categories_layout.parent()
        while categories_widget and not hasattr(categories_widget, "setVisible"):
            categories_widget = categories_widget.parent()
        if categories_widget and hasattr(categories_widget, "setVisible"):
            categories_widget.parent().setVisible(True)

    def launch_program(self, name: str, file_path: str, category: str):
        """Launch the selected PDF program"""
        if (
            not self.state_manager.current_file
        ):  # ERR: non-fatal — surfaced via status_label; no PDF loaded
            self.status_label.setText(_PDFStrings.ERR_NO_FILE)
            return

        try:
            # Update status
            self.status_label.setText(f"Launching {name}...")

            # Try to execute the program
            import subprocess
            import sys

            # Run the program with the current PDF file as argument
            cmd = [sys.executable, file_path, self.state_manager.current_file]

            # For GUI programs, don't wait for completion
            subprocess.Popen(cmd, cwd=os.path.dirname(file_path))

            self.status_label.setText(f"Launched {name}")

            # Log the operation
            self.state_manager.save_operation_state(
                category,
                f"launch_{name}",
                {
                    "program_path": file_path,
                    "pdf_file": self.state_manager.current_file,
                },
            )

        except Exception as e:  # ERR: non-fatal — surfaced via status_label
            self._logger.error(f"Error launching program '{name}': {e}", exc_info=True)
            self.status_label.setText(
                f"Could not launch {name}. See Help > Logs for details."
            )

    def _darken_color(self, hex_color: str, factor: float = 0.1) -> str:
        """Darken a hex color by a given factor"""
        # Remove # if present
        hex_color = hex_color.lstrip("#")

        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Darken
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def create_status_section(self):
        """Create the status section with progress and information"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_frame.setStyleSheet(
            """
            QFrame {
                background-color: {token('dialog_background')};
                border: 1px solid {token('border_light')};
                border-radius: 8px;
                padding: 10px;
            }
        """
        )

        status_layout = QHBoxLayout(status_frame)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid {token('border_light')};
                border-radius: 4px;
                text-align: center;
                background-color: {token('dialog_background')};
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: {token('button_primary')};
                border-radius: 3px;
            }
        """
        )
        status_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = _ui_widget(QLabel, 'Legacy.s5fa7aac5375c5815', 'setText')
        self.status_label.setStyleSheet(
            f"font-weight: bold; color: {token('text_secondary')};"
        )
        status_layout.addWidget(self.status_label)

        self.main_layout.addWidget(status_frame)

    def apply_enhanced_styling(self):
        """Apply enhanced styling consistent with RFU hub"""
        self.setStyleSheet(
            """
            QWidget {
                background-color: {token('window_background')};

            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid {token('border_light')};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )
        font_tokens.bind(self, "font.body")

    def setup_connections(self):
        """Setup signal connections and event handlers"""
        # Setup performance monitoring timer (if needed)
        pass

    def select_pdf_file(self):
        """Open file dialog to select a PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)"
        )

        if file_path:
            if self.state_manager.set_current_file(file_path):
                self.current_file_label.setText(os.path.basename(file_path))
                self.current_file_label.setToolTip(file_path)
                self.file_selected.emit(file_path)
                self.status_label.setText(
                    f"File selected: {os.path.basename(file_path)}"
                )
            else:
                if Modal:
                    Modal(
                        "Invalid File", "Please select a valid PDF file.", ["OK"], self
                    ).exec_()
                else:
                    QMessageBox.warning(
                        self, "Invalid File", "Please select a valid PDF file."
                    )

    def show_recent_files(self):
        """Show recent files menu"""
        if not self.state_manager.recent_files:
            if Modal:
                Modal(
                    "Recent Files", "No recent files available.", ["OK"], self
                ).exec_()
            else:
                QMessageBox.information(
                    self, "Recent Files", "No recent files available."
                )
            return

        # Create a simple dialog with recent files
        from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QListWidget

        dialog = QDialog(self)
        _ui_bind(dialog, 'setWindowTitle', 'Legacy.s46a0a51c6c005e8a')
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        file_list = QListWidget()
        _ui_bind(file_list, 'setAccessibleName', 'Legacy.sb29724f35ef1bc57')
        for file_path in self.state_manager.recent_files:
            if os.path.exists(file_path):
                file_list.addItem(f"{os.path.basename(file_path)} - {file_path}")

        layout.addWidget(file_list)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted and file_list.currentItem():
            selected_text = file_list.currentItem().text()
            file_path = selected_text.split(" - ", 1)[1]
            if self.state_manager.set_current_file(file_path):
                self.current_file_label.setText(os.path.basename(file_path))
                self.current_file_label.setToolTip(file_path)
                self.file_selected.emit(file_path)

    def clear_cache(self):
        """Clear operation cache and temporary data"""
        self.state_manager.shared_data.clear()
        self.status_label.setText("Cache cleared")
        if ToastNotification:
            ToastNotification(self).show_message(
                "Operation cache and temporary data have been cleared.", "success"
            )
        else:
            QMessageBox.information(
                self,
                "Cache Cleared",
                "Operation cache and temporary data have been cleared.",
            )


if __name__ == "__main__":
    """Test the enhanced PDF tools widget"""
    import sys

    from PyQt5.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    # Create test window
    window = QMainWindow()
    _ui_bind(window, 'setWindowTitle', 'Legacy.s4aef30658a21c96e')
    window.setGeometry(200, 200, 1000, 800)

    # Create and set the PDF tools widget
    pdf_widget = EnhancedPDFToolsWidget()
    window.setCentralWidget(pdf_widget)

    window.show()
    sys.exit(app.exec_())
