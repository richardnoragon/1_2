from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.gui import menu_surfaces
import datetime
import logging
import os
import pathlib
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, List, Optional

try:
    import chardet
except ImportError:  # pragma: no cover - graceful runtime fallback
    chardet = None

try:
    import docx
except ImportError:  # pragma: no cover - graceful runtime fallback
    docx = None

try:
    import PyPDF2
except ImportError:  # pragma: no cover - graceful runtime fallback
    PyPDF2 = None
from PyQt5 import uic
from PyQt5.QtCore import QDate, QModelIndex, QObject, QThread, pyqtSignal
from PyQt5.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QStandardItem,
    QStandardItemModel,
)
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QHeaderView,
    QLineEdit,
    QMenu,
)

from src.gui.themes import ThemeManager, token

from ....gui.common.base_window import BaseWindow
from ....gui.common.dialogs import get_existing_directory, show_error_dialog
from ....gui.common.widgets import ProgressWidget
from ....log_manager import get_log_manager

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
    from src.rfu.ui_strings import FileFinder as _FileFinderStrings
except ImportError:

    class _FileFinderStrings:  # type: ignore[no-redef]
        TITLE = "File Finder"
        WINDOW_TITLE = "File Finder — RFU"
        LOADING = "Loading File Finder…"
        ERR_INIT_FAILED = (
            "Could not start File Finder. "
            "Please try again or restart the application."
        )
        ERR_SEARCH_FAILED = "Could not complete the file search. Please try again."


# ---------------------------------------------------------------------------
# CP: Component replacement imports (CP-1 through CP-2)
# ---------------------------------------------------------------------------
try:
    from src.gui.components.buttons import PrimaryButton, SecondaryButton

    _CP_AVAILABLE = True
except ImportError:
    from PyQt5.QtWidgets import QPushButton as PrimaryButton
    from PyQt5.QtWidgets import QPushButton as SecondaryButton

    _CP_AVAILABLE = False


# ---------------------------------------------------------------------------
# PERF-1d: Background worker for file search (QThread pattern)
# ---------------------------------------------------------------------------
class FileSearchWorker(QObject):
    """Runs os.walk-based file search off the UI thread."""

    finished = pyqtSignal(list)  # list of relative file paths
    error = pyqtSignal(str)

    def __init__(
        self,
        directory,
        filetype,
        from_date,
        till_date,
        created,
        modified,
        created_modified,
        office,
        media,
        all_files,
        in_date_range_fn,
    ):
        super().__init__()
        self._directory = directory
        self._filetype = filetype
        self._from_date = from_date
        self._till_date = till_date
        self._created = created
        self._modified = modified
        self._created_modified = created_modified
        self._office = office
        self._media = media
        self._all_files = all_files
        self._in_date_range_fn = in_date_range_fn

    def run(self):
        import os

        try:
            extensions = []
            if self._office:
                extensions.extend(["docx", "doc", "xlsx", "xls", "pptx", "ppt"])
            if self._media:
                extensions.extend(["mp3", "mp4", "avi", "mkv", "jpg", "png", "gif"])
            if self._all_files:
                extensions = ["*"]
            files = []
            for root, dirs, filenames in os.walk(self._directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, self._directory)
                    if extensions != ["*"]:
                        file_ext = (
                            filename.split(".")[-1].lower() if "." in filename else ""
                        )
                        if (
                            file_ext not in extensions
                            and self._filetype not in filename.lower()
                        ):
                            continue
                    if not self._in_date_range_fn(
                        file_path,
                        self._from_date,
                        self._till_date,
                        self._created,
                        self._modified,
                        self._created_modified,
                    ):
                        continue
                    files.append(relative_path)
            self.finished.emit(sorted(files))
        except Exception as exc:  # ERR: non-fatal — surfaced via error signal
            self.error.emit(str(exc))


class FileFinderWindow(BaseWindow):
    """A GUI application for finding and viewing files based on various criteria.

    This class provides a graphical interface for:
    - Searching files by type (office documents, media files, or all)
    - Filtering files by creation/modification dates
    - Displaying file metadata
    - Content searching within supported file types
    - Viewing and managing search results
    - Opening files with their default applications

    Inherits from BaseWindow to maintain consistent GUI behavior.
    """

    def __init__(self, hub_instance=None, config_manager=None) -> None:
        """Initialize the file finder GUI."""
        self._hub = hub_instance
        self.config_manager = config_manager
        self.logger = get_log_manager().get_logger("FileFinderWindow")
        self._logger = self.logger  # harmonization alias
        self._signals_ready = False
        self._signals_connected = False
        super().__init__()
        self.logger.info("Initializing File Finder")

        self._init_models()
        self._setup_ui()
        self._validate_ui_components()
        self._setup_icons()
        self._signals_ready = True
        self._connect_signals()
        self._set_initial_state()
        self._notify_missing_optional_dependencies()
        register_gui_component(
            self, tool_id="file_finder", recovery_callback=self.degraded_fallback
        )
        _emit_telemetry("ui_view_load", tool_id="file_finder")

    def health_check(self) -> bool:
        """Return True if core UI is functional (GRD-3a)."""
        try:
            return (
                hasattr(self, "search_pushButton")
                and self.search_pushButton is not None
            )
        except Exception:
            return False

    def degraded_fallback(self) -> None:
        """Enter degraded / read-only state (GRD-3b)."""
        try:
            self._logger.warning("FileFinderWindow entering degraded mode")
        except Exception:
            pass
        _emit_telemetry("ui_error_event", tool_id="file_finder", error_type="degraded")

    def _init_models(self) -> None:
        """Initialize data models and internal state."""
        # Add directory and filetype attributes
        self.directory = ""
        self.filetype = ""

    def _setup_ui(self) -> None:
        """Initialize and load the UI file."""
        try:
            ui_file = Path(__file__).parent / "file_finder.ui"
            if not ui_file.exists():
                raise FileNotFoundError(f"UI file not found: {ui_file}")
            uic.loadUi(str(ui_file), self)
        except Exception as e:  # ERR: fatal — UI setup failed; tool cannot render
            self.logger.error(
                f"Failed to initialize UI for FileFinderWindow: {e}", exc_info=True
            )
            raise

    def _validate_ui_components(self) -> None:
        """Ensure required widgets exist and provide minimal fallbacks."""
        required_names = [
            "select_pushButton",
            "search_pushButton",
            "listView",
            "meta_info_tableView",
            "directory_lineEdit",
        ]
        missing: List[str] = []
        for name in required_names:
            if getattr(self, name, None) is None:
                widget = self.findChild(QObject, name)
                if widget is None:
                    missing.append(name)
                else:
                    setattr(self, name, widget)

        if missing:
            message = "File Finder UI is missing required widgets: " + ", ".join(
                missing
            )
            self.logger.error(message)
            show_error_dialog(message, "Initialization Error", self)
            raise AttributeError(message)

        if getattr(self, "statusbar", None) is None:
            # Ensure status bar exists when designer bindings fail.
            status_bar = self.statusBar()
            status_bar.setObjectName("statusbar")
            self.statusbar = status_bar

        # Ensure hub integrations can always locate the exit action.
        try:
            self._ensure_exit_action()
        except (
            Exception
        ) as exc:  # ERR: fatal — menu action setup failed; tool cannot render
            self.logger.error(f"Failed to prepare menu actions: {exc}", exc_info=True)
            raise

    def _setup_icons(self) -> None:
        """Setup icons and UI styling."""
        # Icons are handled by the UI file
        pass

    def _connect_signals(self) -> None:
        """Connect UI signals to their respective slots."""
        if not getattr(self, "_signals_ready", False):
            return

        if getattr(self, "_signals_connected", False):
            return

        exit_action = self._ensure_exit_action()
        exit_action.triggered.connect(self._on_exit_triggered)

        select_button = getattr(self, "select_pushButton", None)
        if select_button is not None:
            select_button.clicked.connect(self.select_directory)
        else:
            self.logger.warning(
                "Missing 'select_pushButton'; directory selection disabled"
            )

        search_button = getattr(self, "search_pushButton", None)
        if search_button is not None:
            search_button.clicked.connect(self.search)
        else:
            self.logger.warning("Missing 'search_pushButton'; search action disabled")

        list_view = getattr(self, "listView", None)
        if list_view is not None:
            list_view.doubleClicked.connect(self.open_file)
            list_view.clicked.connect(self.show_metadata)
        else:
            self.logger.warning("Missing 'listView'; result interactions disabled")

        self._signals_connected = True

    def _on_exit_triggered(self) -> None:
        """Handle exit action activation."""
        self.logger.info("File Finder exit action invoked")
        self.close()

    def _ensure_exit_action(self) -> QAction:
        """Return a valid exit action, creating a fallback if necessary."""
        exit_action: Optional[QAction] = getattr(self, "actionexit", None)
        if exit_action is None:
            exit_action = self.findChild(QAction, "actionexit")
            if exit_action is not None:
                setattr(self, "actionexit", exit_action)

        if exit_action is None:
            file_menu = self._resolve_file_menu()
            exit_action = _ui_widget(QAction, 'Legacy.sd17d84a604994b72', 'setText', self)
            exit_action.setObjectName("actionexit")
            exit_action.setShortcut("Ctrl+Q")
            _ui_bind(exit_action, 'setStatusTip', 'Legacy.sce59c0e9d6ab93b5')
            file_menu.addAction(exit_action)
            setattr(self, "actionexit", exit_action)
            self.logger.warning(
                "Missing 'actionexit' action in UI; created fallback action"
            )

        # Provide common attribute aliases for integration checks.
        if not hasattr(self, "actionExit"):
            setattr(self, "actionExit", exit_action)
        if not hasattr(self, "action_exit"):
            setattr(self, "action_exit", exit_action)

        return exit_action

    def _resolve_file_menu(self) -> QMenu:
        """Locate or create the File menu to host the exit action."""
        menu = getattr(self, "menuFile", None)
        if menu is None:
            for action in self.menuBar().actions():
                if action.text().replace("&", "").strip().lower() == "file":
                    menu = action.menu()
                    break

        if menu is None:
            menu = menu_surfaces.add_menu(self.menuBar(), 'File')
            menu.setObjectName("menuFile")
            self.logger.info("Created fallback File menu for File Finder")

        setattr(self, "menuFile", menu)
        return menu

    def _set_initial_state(self) -> None:
        """Set the initial state of UI elements."""
        # create a model for the listview
        self.model = QStandardItemModel()
        # set the model for the listview
        self.listView.setModel(self.model)

        # create a model for the metadata table
        self.meta_model = QStandardItemModel()
        self.meta_model.setHorizontalHeaderLabels(["Property", "Value"])
        self.meta_info_tableView.setModel(self.meta_model)
        self.meta_info_tableView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # Set today as default for till_dateEdit
        today = QDate.currentDate()
        self.till_dateEdit.setDate(today)

        # Set 30 days ago as default for from_dateEdit
        thirty_days_ago = today.addDays(-30)
        self.from_dateEdit.setDate(thirty_days_ago)

        # Enable drag and drop
        self.setAcceptDrops(True)
        self.directory_lineEdit.setAcceptDrops(True)

        # Add progress widget
        self.progress_widget = ProgressWidget(self)
        self.statusbar.addPermanentWidget(self.progress_widget)
        self.progress_widget.hide()

        # show the GUI
        self.show()

    def _notify_missing_optional_dependencies(self) -> None:
        """Warn users when optional packages are unavailable."""
        missing: List[str] = []
        if chardet is None:
            missing.append("chardet")
        if docx is None:
            missing.append("python-docx")
        if PyPDF2 is None:
            missing.append("PyPDF2")

        if missing:
            message = (
                "Limited search features: missing optional packages "
                f"{', '.join(missing)}"
            )
            self.logger.warning(message)
            try:
                self.statusbar.showMessage(message, 8000)
            except (
                Exception
            ):  # ERR: non-fatal — statusbar not available; message skipped
                # Status bar may not exist in some tests
                pass

    def select_directory(self) -> None:
        """Open directory selection dialog and update window state.

        Opens a dialog for directory selection and if a directory is chosen:
        - Sets the current working directory
        - Updates the window title to show selected directory
        - Sets the directory path in the line edit field
        """
        # Open a dialog to select a directory
        dir_path = get_existing_directory(
            self, "Select Directory", directory=self.directory
        )
        # Display the selected directory in window title and line edit
        if dir_path:
            self.directory = str(dir_path)
            self.setWindowTitle(f"File Finder - {self.directory}")
            self.directory_lineEdit.setText(self.directory)

    # Method to open a file when double-clicked in the listview
    def open_file(self, index: QModelIndex) -> None:
        """Open a file when double-clicked in the listview.

        Args:
            index: The index of the selected file in the list view
        """
        file_path = self.model.data(index)
        if file_path:
            full_path = os.path.join(self.directory, file_path)
            try:
                if os.name == "nt":  # Windows
                    os.startfile(full_path)
                else:  # macOS and Linux
                    subprocess.run(["open", full_path])
            except Exception as e:  # ERR: non-fatal — surfaced via statusbar
                self.logger.error(
                    f"Error opening file '{full_path}': {e}", exc_info=True
                )
                self.statusbar.showMessage(_FileFinderStrings.ERR_OPEN_FAILED, 5000)

    # Method to show metadata when a file is selected
    def show_metadata(self, index: QModelIndex) -> None:
        """Display metadata for the selected file.

        Args:
            index: The index of the selected file in the list view
        """
        file_path = self.model.data(index)
        if not file_path:
            return

        full_path = os.path.join(self.directory, file_path)
        file_name = os.path.basename(full_path)

        try:
            # Clear existing metadata
            self.meta_model.removeRows(0, self.meta_model.rowCount())

            # Get file info
            file_info = pathlib.Path(full_path)

            # Add basic file properties
            self.add_meta_row("Name", file_name)
            self.add_meta_row("Path", full_path)
            self.add_meta_row("Size", f"{file_info.stat().st_size:,} bytes")

            # Format dates
            created_time = datetime.datetime.fromtimestamp(
                file_info.stat().st_ctime
            ).strftime("%Y-%m-%d %H:%M:%S")
            modified_time = datetime.datetime.fromtimestamp(
                file_info.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M:%S")

            self.add_meta_row("Created", created_time)
            self.add_meta_row("Modified", modified_time)

            self.statusbar.showMessage(f"Metadata loaded for {file_name}", 3000)
        except Exception as e:
            self.statusbar.showMessage(f"Error loading metadata: {str(e)}", 5000)
            self.logger.error(f"Error loading metadata: {str(e)}", exc_info=True)

    def add_meta_row(self, property_name: str, value: Any) -> None:
        """Helper method to add a row to the metadata table.

        Args:
            property_name: The name of the property to display
            value: The value of the property
        """
        row = self.meta_model.rowCount()
        self.meta_model.setItem(row, 0, QStandardItem(property_name))
        self.meta_model.setItem(row, 1, QStandardItem(str(value)))

    def search(self) -> None:
        """Perform file search based on current criteria (off UI thread, PERF-1d)."""
        if (
            hasattr(self, "_search_thread")
            and self._search_thread
            and self._search_thread.isRunning()
        ):
            return  # already searching

        # clear the model
        self.model.clear()
        self.meta_model.removeRows(0, self.meta_model.rowCount())

        directory = self.directory
        filetype = self.filetype_lineEdit.text().strip()
        from_date = self.from_dateEdit.date().toPyDate()
        till_date = self.till_dateEdit.date().toPyDate()
        office = self.office_checkBox.isChecked()
        media = self.media_checkBox.isChecked()
        all_files = self.all_checkBox.isChecked()
        created = self.created_radioButton.isChecked()
        modified = self.modified_radioButton.isChecked()
        created_modified = self.created_modified_radioButton.isChecked()

        if not directory or not os.path.exists(directory):
            show_error_dialog(self, "Error", "Please select a valid directory")
            return

        # PERF-3a: show progress before starting worker
        self.progress_widget.show()

        self._search_worker = FileSearchWorker(
            directory,
            filetype,
            from_date,
            till_date,
            created,
            modified,
            created_modified,
            office,
            media,
            all_files,
            self.in_date_range,
        )
        self._search_thread = QThread()
        self._search_worker.moveToThread(self._search_thread)
        self._search_thread.started.connect(self._search_worker.run)
        self._search_worker.finished.connect(self._on_search_done)
        self._search_worker.error.connect(self._on_search_error)
        # PERF-4a/4b: hide progress on both completion and error
        self._search_worker.finished.connect(self._stop_search_progress)
        self._search_worker.error.connect(self._stop_search_progress)
        self._search_thread.start()

    def _stop_search_progress(self):
        """Stop progress indicator and clean up search thread."""
        self.progress_widget.hide()
        if self._search_thread:
            self._search_thread.quit()
            self._search_thread = None
        self._search_worker = None

    def _on_search_done(self, files: list) -> None:
        """Display search results after background scan completes."""
        for file_path in files:
            self.model.appendRow(QStandardItem(file_path))
        self.statusbar.showMessage(f"Found {len(files)} files", 3000)
        self.logger.info(f"Found {len(files)} files")

    def _on_search_error(self, message: str) -> None:  # ERR: non-fatal
        self.logger.error(f"File search error: {message}")
        show_error_dialog(self, "Search Error", _FileFinderStrings.ERR_SEARCH_FAILED)

    def search_file_content(self, file_path: str, search_text: str) -> bool:
        """Search for text within file content.

        Args:
            file_path: Path to the file to search
            search_text: Text to search for

        Returns:
            True if text is found, False otherwise
        """
        try:
            file_path_obj = pathlib.Path(file_path)

            if file_path_obj.suffix.lower() == ".txt":
                return self.search_text_file(str(file_path_obj), search_text)
            elif file_path_obj.suffix.lower() == ".docx":
                return self.search_word_document(str(file_path_obj), search_text)
            elif file_path_obj.suffix.lower() == ".pdf":
                return self.search_pdf_document(str(file_path_obj), search_text)
            else:
                return False
        except (
            Exception
        ):  # ERR: non-fatal — returns False; individual file skipped during content search
            return False

    def search_text_file(self, file_path: str, search_text: str) -> bool:
        """Search for text in a text file.

        Args:
            file_path: Path to the text file
            search_text: Text to search for

        Returns:
            True if text is found, False otherwise
        """
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read()

            encoding = "utf-8"
            if chardet is not None:
                result = chardet.detect(raw_data)
                if result.get("encoding"):
                    encoding = result["encoding"]
            else:
                self.logger.debug(
                    "chardet not available; defaulting to utf-8 for %s",
                    file_path,
                )

            text = raw_data.decode(encoding, errors="ignore")
            return search_text.lower() in text.lower()
        except (
            Exception
        ):  # ERR: non-fatal — returns False; text file content unreadable
            return False

    def search_word_document(self, file_path: str, search_text: str) -> bool:
        """Search for text in a Word document.

        Args:
            file_path: Path to the Word document
            search_text: Text to search for

        Returns:
            True if text is found, False otherwise
        """
        if docx is None:
            self.logger.warning(
                "python-docx not installed; skipping DOCX content search"
            )
            return False

        try:
            document = docx.Document(file_path)
            text_content = " ".join([p.text for p in document.paragraphs])
            return search_text.lower() in text_content.lower()
        except Exception:  # ERR: non-fatal — returns False; Word document unreadable
            return False

    def search_pdf_document(self, file_path: str, search_text: str) -> bool:
        """Search for text in a PDF document.

        Args:
            file_path: Path to the PDF document
            search_text: Text to search for

        Returns:
            True if text is found, False otherwise
        """
        if PyPDF2 is None:
            self.logger.warning("PyPDF2 not installed; skipping PDF content search")
            return False

        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text()
                return search_text.lower() in text_content.lower()
        except Exception:  # ERR: non-fatal — returns False; PDF content unreadable
            return False

    def get_files(
        self,
        directory: str,
        filetype: str,
        from_date: datetime.date,
        till_date: datetime.date,
        created: bool,
        modified: bool,
        created_modified: bool,
        office: bool,
        media: bool,
        all_files: bool,
    ) -> List[str]:
        """Find files matching the specified criteria.

        Args:
            directory: Base directory to search
            filetype: File extension or name pattern to match
            from_date: Start date for file filtering
            till_date: End date for file filtering
            created: Consider file creation date
            modified: Consider file modification date
            created_modified: Consider both creation and modification dates
            office: Include office document types
            media: Include media file types
            all_files: Include all file types

        Returns:
            List of file paths relative to the base directory
        """
        files = []

        # Determine file extensions to include
        extensions = []
        if office:
            extensions.extend(["docx", "doc", "xlsx", "xls", "pptx", "ppt"])
        if media:
            extensions.extend(["mp3", "mp4", "avi", "mkv", "jpg", "png", "gif"])
        if all_files:
            extensions = ["*"]

        # Walk through directory
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, directory)

                # Check file type
                if extensions != ["*"]:
                    file_ext = (
                        filename.split(".")[-1].lower() if "." in filename else ""
                    )
                    if file_ext not in extensions and filetype not in filename.lower():
                        continue

                # Check date range
                if not self.in_date_range(
                    file_path,
                    from_date,
                    till_date,
                    created,
                    modified,
                    created_modified,
                ):
                    continue

                files.append(relative_path)

        return sorted(files)

    def in_date_range(
        self,
        file_path: str,
        from_date: datetime.date,
        till_date: datetime.date,
        created: bool,
        modified: bool,
        created_modified: bool,
    ) -> bool:
        """Check if file falls within specified date range.

        Args:
            file_path: Path to the file
            from_date: Start date for filtering
            till_date: End date for filtering
            created: Check creation date
            modified: Check modification date
            created_modified: Check both dates

        Returns:
            True if file is within date range, False otherwise
        """
        try:
            file_stat = os.stat(file_path)

            if created:
                file_date = datetime.date.fromtimestamp(file_stat.st_ctime)
            elif modified:
                file_date = datetime.date.fromtimestamp(file_stat.st_mtime)
            elif created_modified:
                create_date = datetime.date.fromtimestamp(file_stat.st_ctime)
                modify_date = datetime.date.fromtimestamp(file_stat.st_mtime)
                return (
                    from_date <= create_date <= till_date
                    or from_date <= modify_date <= till_date
                )
            else:
                return True

            return from_date <= file_date <= till_date
        except (
            Exception
        ):  # ERR: non-fatal — returns False; file stat unavailable; file excluded from results
            return False

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events for directory dropping.

        Args:
            event: The drag enter event to handle
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle directory drop events.

        Args:
            event: The drop event to handle
        """
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.directory = path
                self.directory_lineEdit.setText(path)
                self.setWindowTitle(f"File Finder - {path}")

    def save_settings(self) -> None:
        """Save current settings for future sessions."""
        pass

    def show(self) -> None:
        """Show the file finder window."""
        super().show()

    def close(self) -> None:
        """Close the file finder window."""
        super().close()


class FileFinderLogic:
    """Core logic class for file finding operations."""

    def __init__(self, config_manager=None):
        """Initialize the file finder logic."""
        self.config_manager = config_manager
        self.logger = get_log_manager().get_logger("FileFinderLogic")
        self.logger.info("Initializing File Finder Logic")

        # Add placeholder attributes that tests expect
        self.search_dir = None
        self.pattern_edit = None
        self.search_button = None
        self.results_list = None
        self.recursive_check = None
        self.show_hidden_check = None


class FileFinder(QDialog):
    """Dialog wrapper for FileFinderWindow to provide test compatibility.

    This class inherits from QDialog and delegates functionality to
    FileFinderWindow, providing the interface expected by tests while
    maintaining the full GUI functionality.
    """

    def __init__(self, config_manager=None):
        """Initialize the FileFinder dialog."""
        super().__init__()
        self.config_manager = config_manager
        self.gui = FileFinderWindow(config_manager)

        from PyQt5.QtCore import QDate
        from PyQt5.QtWidgets import (
            QCheckBox,
            QComboBox,
            QDateEdit,
            QListWidget,
            QPushButton,
            QSpinBox,
            QStatusBar,
        )

        self.pattern_edit = QLineEdit()
        _ui_bind(self.pattern_edit, 'setAccessibleName', 'Legacy.s82c1d898eb446115')
        _ui_bind(self.pattern_edit, 'setAccessibleDescription', 'Legacy.s048ea900e2348923')
        _ui_bind(self.pattern_edit, 'setPlaceholderText', 'Legacy.s79e81fa3bb645261')

        self.recursive_check = _ui_widget(QCheckBox, 'Legacy.s6e7bc12c5b82601b', 'setText')
        _ui_bind(self.recursive_check, 'setAccessibleName', 'Legacy.s013002ff21455712')
        self.recursive_check.setMinimumHeight(44)
        self.show_hidden_check = _ui_widget(QCheckBox, 'Legacy.se20432c9b6cde04b', 'setText')
        _ui_bind(self.show_hidden_check, 'setAccessibleName', 'Legacy.sb5ede7fb45df0951')
        self.show_hidden_check.setMinimumHeight(44)

        self.type_combo = QComboBox()
        _ui_bind(self.type_combo, 'setAccessibleName', 'Legacy.s1f8e0eb460004235')
        self.type_combo.addItems(["All Files", "Text Files", "Images", "Documents"])

        self.min_size_spin = QSpinBox()
        _ui_bind(self.min_size_spin, 'setAccessibleName', 'Legacy.s91a5e537e1bf2422')
        _ui_bind(self.min_size_spin, 'setAccessibleDescription', 'Legacy.sf46694ae5b264464')
        self.min_size_spin.setMinimumHeight(44)
        self.min_size_spin.setMaximum(999999)
        self.max_size_spin = QSpinBox()
        _ui_bind(self.max_size_spin, 'setAccessibleName', 'Legacy.s0024b1d5348849ce')
        _ui_bind(self.max_size_spin, 'setAccessibleDescription', 'Legacy.s5c07dc51f6336c9c')
        self.max_size_spin.setMinimumHeight(44)
        self.max_size_spin.setMaximum(999999)
        self.max_size_spin.setValue(100)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.use_date_check = _ui_widget(QCheckBox, 'Legacy.sde9b387c3950c763', 'setText')
        _ui_bind(self.use_date_check, 'setAccessibleName', 'Legacy.secfff0cbbe031759')
        _ui_bind(self.use_date_check, 'setAccessibleDescription', 'Legacy.sd1fd1c42b7e0ced6')
        self.use_date_check.setMinimumHeight(44)

        self.open_button = _ui_widget(PrimaryButton, 'Legacy.sed077f3d8125d60d', 'setText')
        self.copy_path_button = _ui_widget(SecondaryButton, 'Legacy.s0e0269180969ded3', 'setText')
        self.cancel_button = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')

        self.status_bar = QStatusBar()

        self.search_dir = QLineEdit()
        _ui_bind(self.search_dir, 'setAccessibleName', 'Legacy.s38c67f1341ef12a9')
        _ui_bind(self.search_dir, 'setPlaceholderText', 'Legacy.s38c67f1341ef12a9')

        self.search_button = self.gui.search_pushButton

        self.results_list = QListWidget()
        _ui_bind(self.results_list, 'setAccessibleName', 'Legacy.se978b00de465a271')

        self.gui.model.rowsInserted.connect(self._sync_results_to_wrapper)
        self.gui.model.modelReset.connect(self._sync_results_to_wrapper)

        self.search_button.clicked.disconnect()
        self.search_button.clicked.connect(self._handle_pattern_search)

        _ui_bind(self, 'setWindowTitle', 'Legacy.s6f6e552fa045bf84')
        self.setModal(True)
        ThemeManager.add_theme_changed_callback(self._on_theme_changed)

    def _on_theme_changed(self, variant: str) -> None:
        """Re-apply token-based stylesheets when the active theme variant changes."""
        pass  # stylesheets applied at init; live re-apply pending TH-4c/4d

    def _sync_results_to_wrapper(self):
        """Sync data from GUI QListView to wrapper QListWidget"""
        self.results_list.clear()
        for row in range(self.gui.model.rowCount()):
            item = self.gui.model.item(row)
            if item:
                self.results_list.addItem(item.text())

    def _handle_pattern_search(self):
        """Handle search based on pattern_edit field"""
        search_dir_text = self.search_dir.text()

        if search_dir_text:
            self.gui.directory = search_dir_text

        pattern = self.pattern_edit.text()

        if pattern:
            if pattern.startswith("*."):
                ext = pattern[2:]
                if ext in ["txt", "log", "md", "py", "json", "xml", "csv"]:
                    self.gui.all_checkBox.setChecked(True)
                    self.gui.office_checkBox.setChecked(False)
                    self.gui.media_checkBox.setChecked(False)
                    self.gui.filetype = "." + ext
                elif ext in ["jpg", "png", "gif", "bmp", "jpeg"]:
                    self.gui.all_checkBox.setChecked(True)
                    self.gui.office_checkBox.setChecked(False)
                    self.gui.media_checkBox.setChecked(False)
                    self.gui.filetype = "." + ext
                elif ext in ["pptx", "docx", "xlsx"]:
                    self.gui.office_checkBox.setChecked(True)
                    self.gui.all_checkBox.setChecked(False)
                    self.gui.media_checkBox.setChecked(False)
                    self.gui.filetype = "." + ext
                elif ext in ["avi", "mp3", "mkv", "mp4", "wav", "mov"]:
                    self.gui.media_checkBox.setChecked(True)
                    self.gui.all_checkBox.setChecked(False)
                    self.gui.office_checkBox.setChecked(False)
                    self.gui.filetype = "." + ext
                else:
                    self.gui.all_checkBox.setChecked(True)
                    self.gui.office_checkBox.setChecked(False)
                    self.gui.media_checkBox.setChecked(False)
                    self.gui.filetype = "." + ext
            else:
                self.gui.all_checkBox.setChecked(True)
                self.gui.filetype = pattern
        else:
            self.gui.all_checkBox.setChecked(True)
            self.gui.filetype = ""

        self.gui.search()

    def save_settings(self):
        """Save current search settings to config"""
        if self.config_manager:
            settings = {
                "search_dir": self.search_dir.text(),
                "pattern": self.pattern_edit.text(),
                "recursive": self.recursive_check.isChecked(),
                "show_hidden": self.show_hidden_check.isChecked(),
                "type_filter": self.type_combo.currentText(),
                "min_size": self.min_size_spin.value(),
                "max_size": self.max_size_spin.value(),
                "use_date": self.use_date_check.isChecked(),
                "date": self.date_edit.date().toString(),
            }
            self.config_manager.update_config("file_finder", settings)

    def show(self):
        """Show the GUI window."""
        self.gui.show()
        return super().show()

    def close(self):
        """Close the GUI window."""
        self.gui.close()
        return super().close()


def main() -> int:
    """Application entry point for launching the File Finder GUI."""
    app = QApplication(sys.argv)
    window = FileFinderWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    try:
        print("Starting File Finder...")
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
