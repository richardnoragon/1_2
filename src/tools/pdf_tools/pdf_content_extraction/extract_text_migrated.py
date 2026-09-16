"""
PDF Text Extraction Module - Migrated Version
Integrated with main project architecture using BaseWindow.
Phase 3.1 of PDF utilities integration.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

import sys
import os
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QApplication,
)
import pdfplumber

from src.gui.components.loading_indicator import LoadingIndicator

# Add parent directory to path for main project imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.common.base_window import BaseWindow
from core.logging_manager import LogManager
from config_manager import ConfigManager


class ExtractTextWindow(BaseWindow):
    """
    PDF Text Extraction Window using BaseWindow architecture.

    Provides functionality to extract text from PDF files with options for
    page selection, format selection, and text processing.
    """

    def __init__(self):
        """Initialize the Extract Text window."""
        # Initialize with UI file
        ui_file = Path(__file__).parent / "extract_text.ui"
        super().__init__(ui_file)

        # Set window title
        _ui_bind(self, 'setWindowTitle', 'Legacy.sfe3f6409ec6b4870')

        # Initialize logging
        self.logger = LogManager().get_logger("PDF.ExtractText")
        self.logger.info("Initializing PDF Text Extraction window")

        # Initialize configuration
        self.config = ConfigManager()

        # Initialize state
        self.current_file: Optional[str] = None
        self.extracted_text: str = ""

        # Setup UI components
        self._setup_ui_components()
        self._load_settings()

        self.logger.debug("Extract Text window initialized successfully")

    def _setup_ui_components(self):
        """Setup additional UI components and connections."""
        try:
            # Add progress bar to status bar (BaseWindow provides statusBar)
            self.progress_bar = LoadingIndicator(parent=self, message="Working...")
            self.statusBar().addPermanentWidget(self.progress_bar)
            self.progress_bar.hide()

            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.extractButton.clicked.connect(self.extract_text)
            self.saveButton.clicked.connect(self.save_text)

            # Initialize button states
            self.extractButton.setEnabled(False)
            self.saveButton.setEnabled(False)

            # Set initial status
            self.set_status_message("Ready - Select a PDF file to begin")

            self.logger.debug("UI components setup completed")

        except Exception as e:
            self.logger.error(
                f"Error setting up UI components: {e}", exc_info=True
            )
            QMessageBox.critical(
                self, "Setup Error", f"Failed to setup UI components: {e}"
            )

    def _load_settings(self):
        """Load saved settings from configuration."""
        try:
            # Load extract_text specific settings
            extract_config = self.config.get_module_config("extract_text")

            # Set default format if available
            default_format = extract_config.get("default_format", "txt")
            if hasattr(self, "formatComboBox"):
                index = self.formatComboBox.findText(default_format.upper())
                if index >= 0:
                    self.formatComboBox.setCurrentIndex(index)

            # Load include page numbers setting
            include_pages = extract_config.get("include_page_numbers", True)
            if hasattr(self, "includePageNumbersCheckBox"):
                self.includePageNumbersCheckBox.setChecked(include_pages)

            # Load preserve layout setting
            preserve_layout = extract_config.get("preserve_layout", False)
            if hasattr(self, "preserveLayoutCheckBox"):
                self.preserveLayoutCheckBox.setChecked(preserve_layout)

            # Load last directory
            self.last_directory = self.config.get_setting(
                "general", "last_opened_directory", str(Path.home())
            )

            self.logger.debug("Settings loaded successfully")

        except Exception as e:
            self.logger.warning(f"Error loading settings: {e}")
            # Use defaults
            self.last_directory = str(Path.home())

    def _save_settings(self):
        """Save current settings to configuration."""
        try:
            settings = {}

            # Save format preference
            if hasattr(self, "formatComboBox"):
                settings["default_format"] = (
                    self.formatComboBox.currentText().lower()
                )

            # Save page numbers preference
            if hasattr(self, "includePageNumbersCheckBox"):
                settings["include_page_numbers"] = (
                    self.includePageNumbersCheckBox.isChecked()
                )

            # Save layout preference
            if hasattr(self, "preserveLayoutCheckBox"):
                settings["preserve_layout"] = (
                    self.preserveLayoutCheckBox.isChecked()
                )

            # Save settings
            self.config.set_module_config("extract_text", settings)

            # Save last directory
            if hasattr(self, "last_directory"):
                self.config.set_setting(
                    "general", "last_opened_directory", self.last_directory
                )

            self.logger.debug("Settings saved successfully")

        except Exception as e:
            self.logger.warning(f"Error saving settings: {e}")

    def browse_file(self):
        """Browse for PDF file to extract text from."""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select PDF File",
                self.last_directory,
                "PDF Files (*.pdf);;All Files (*)",
            )

            if filename:
                self.logger.info(f"Selected input file: {filename}")
                self.current_file = filename
                self.last_directory = str(Path(filename).parent)

                # Update UI
                self.inputFileEdit.setText(filename)
                self.extractButton.setEnabled(True)
                self.outputText.clear()
                self.saveButton.setEnabled(False)
                self.extracted_text = ""

                # Update status
                self.set_status_message(
                    f"File selected: {Path(filename).name}"
                )

                # Save last directory
                self._save_settings()

        except Exception as e:
            self.logger.error(f"Error browsing file: {e}", exc_info=True)
            QMessageBox.critical(
                self, "File Selection Error", f"Error selecting file: {e}"
            )

    def extract_text(self):
        """Extract text from the selected PDF file."""
        try:
            if not self.current_file:
                self.logger.warning("No input file selected")
                QMessageBox.warning(
                    self, "No File Selected", "Please select a PDF file first!"
                )
                return

            # Get extraction parameters
            pages_text = (
                self.pagesEdit.text().strip()
                if hasattr(self, "pagesEdit")
                else ""
            )
            include_page_numbers = (
                self.includePageNumbersCheckBox.isChecked()
                if hasattr(self, "includePageNumbersCheckBox")
                else True
            )
            preserve_layout = (
                self.preserveLayoutCheckBox.isChecked()
                if hasattr(self, "preserveLayoutCheckBox")
                else False
            )

            # Show progress
            self.progress_bar.start()
            self.progress_bar.set_progress(0)
            self.set_status_message("Loading document...")
            QApplication.processEvents()

            # Extract text
            result = self._extract_text_from_pdf(
                self.current_file,
                pages_text,
                include_page_numbers,
                preserve_layout,
            )

            if result:
                self.extracted_text = result
                self.outputText.setPlainText(result)
                self.saveButton.setEnabled(True)
                self.set_status_message(
                    "Text extraction completed successfully"
                )
                self.logger.info("Text extraction completed successfully")
            else:
                self.set_status_message("Text extraction failed")
                self.logger.warning("Text extraction failed")

        except Exception as e:
            self.logger.error(
                f"Error in extract operation: {e}", exc_info=True
            )
            QMessageBox.critical(
                self, "Extraction Error", f"Error during text extraction: {e}"
            )
            self.set_status_message("Error during extraction")
        finally:
            self.progress_bar.hide()

    def _extract_text_from_pdf(
        self,
        input_file: str,
        pages_text: str = "",
        include_page_numbers: bool = True,
        preserve_layout: bool = False,
    ) -> Optional[str]:
        """
        Extract text from PDF file.

        Args:
            input_file: Path to PDF file
            pages_text: Page range specification (e.g., "1-3,5,7-9")
            include_page_numbers: Whether to include page numbers in output
            preserve_layout: Whether to preserve text layout

        Returns:
            Extracted text or None if failed
        """
        try:
            self.logger.info(f"Starting text extraction from: {input_file}")

            # Validate input file
            if not os.path.exists(input_file):
                self.logger.error(f"Input file not found: {input_file}")
                QMessageBox.critical(
                    self,
                    "File Not Found",
                    f"Input file not found: {input_file}",
                )
                return None

            # Update progress
            self.progress_bar.set_progress(20)
            self.set_status_message("Opening PDF...")
            QApplication.processEvents()

            # Open PDF file
            with pdfplumber.open(input_file) as pdf:
                self.logger.debug(
                    f"PDF opened successfully, pages: {len(pdf.pages)}"
                )

                # Parse page range
                page_list = self._parse_page_range(pages_text, len(pdf.pages))
                if page_list is None:
                    return None

                # Update progress
                self.progress_bar.set_progress(40)
                self.set_status_message("Extracting text...")
                QApplication.processEvents()

                # Extract text from pages
                text_parts = []
                total_pages = len(page_list)

                for idx, page_num in enumerate(page_list):
                    try:
                        if 0 <= page_num < len(pdf.pages):
                            page = pdf.pages[page_num]

                            # Extract text with layout preservation option
                            if preserve_layout:
                                page_text = page.extract_text(layout=True)
                            else:
                                page_text = page.extract_text()

                            if page_text:
                                if include_page_numbers:
                                    text_parts.append(
                                        f"\n=== Page {page_num + 1} ===\n{page_text}\n"
                                    )
                                else:
                                    text_parts.append(page_text + "\n")

                            self.logger.debug(
                                f"Extracted text from page {page_num + 1}"
                            )
                        else:
                            self.logger.warning(
                                f"Page {page_num + 1} out of range"
                            )

                        # Update progress
                        progress = 40 + int((idx + 1) / total_pages * 50)
                        self.progress_bar.set_progress(progress)
                        QApplication.processEvents()

                    except Exception as e:
                        self.logger.error(
                            f"Error extracting text from page {page_num + 1}: {e}"
                        )
                        QMessageBox.warning(
                            self,
                            "Page Extraction Warning",
                            f"Error extracting text from page {page_num + 1}: {e}",
                        )

                # Finalize
                self.progress_bar.set_progress(100)
                extracted_text = "".join(text_parts)

                if not extracted_text.strip():
                    QMessageBox.warning(
                        self,
                        "No Text Found",
                        "No text could be extracted from the selected pages.",
                    )
                    return None

                self.logger.info("Text extraction completed successfully")
                return extracted_text

        except Exception as e:
            self.logger.error(f"Error opening PDF: {e}", exc_info=True)
            QMessageBox.critical(self, "PDF Error", f"Error opening PDF: {e}")
            return None

    def _parse_page_range(
        self, pages_text: str, total_pages: int
    ) -> Optional[list]:
        """
        Parse page range specification.

        Args:
            pages_text: Page range text (e.g., "1-3,5,7-9")
            total_pages: Total number of pages in document

        Returns:
            List of page indices (0-based) or None if invalid
        """
        if not pages_text:
            return list(range(total_pages))

        try:
            page_list = []
            for part in pages_text.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    page_list.extend(
                        range(start - 1, end)
                    )  # Convert to 0-based
                else:
                    page_list.append(int(part) - 1)  # Convert to 0-based

            # Validate page numbers
            invalid_pages = [
                p + 1 for p in page_list if p < 0 or p >= total_pages
            ]
            if invalid_pages:
                QMessageBox.critical(
                    self,
                    "Invalid Page Range",
                    f"Invalid page numbers: {invalid_pages}\n"
                    f"Document has {total_pages} pages.",
                )
                return None

            self.logger.debug(
                f"Processing pages: {[p + 1 for p in page_list]}"
            )
            return page_list

        except ValueError as e:
            self.logger.error(f"Invalid page range format: {pages_text}")
            QMessageBox.critical(
                self,
                "Invalid Format",
                "Invalid page range format!\n" "Use format like: 1-3,5,7-9",
            )
            return None

    def save_text(self):
        """Save extracted text to file."""
        try:
            if not self.extracted_text:
                self.logger.warning("No text to save")
                QMessageBox.warning(self, "No Text", "No text to save!")
                return

            # Get format preference
            file_format = "txt"
            if hasattr(self, "formatComboBox"):
                file_format = self.formatComboBox.currentText().lower()

            # Set up file dialog
            if file_format == "txt":
                filter_text = "Text Files (*.txt);;All Files (*)"
                default_ext = ".txt"
            else:
                filter_text = "Text Files (*.txt);;All Files (*)"
                default_ext = ".txt"

            # Get save filename
            default_name = ""
            if self.current_file:
                base_name = Path(self.current_file).stem
                default_name = f"{base_name}_extracted{default_ext}"

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Extracted Text",
                str(Path(self.last_directory) / default_name),
                filter_text,
            )

            if filename:
                self.progress_bar.start()
                self.progress_bar.set_progress(0)
                self.set_status_message("Saving text...")
                QApplication.processEvents()

                try:
                    self.logger.info(f"Saving text to: {filename}")

                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(self.extracted_text)

                    self.progress_bar.set_progress(100)
                    self.set_status_message("Save completed successfully")

                    QMessageBox.information(
                        self,
                        "Save Successful",
                        f"Text saved successfully!\nSaved to: {filename}",
                    )

                    # Add to recent files
                    self.config.add_recent_file(filename)

                except Exception as e:
                    self.logger.error(f"Error saving text: {e}", exc_info=True)
                    QMessageBox.critical(
                        self, "Save Error", f"Error saving text: {e}"
                    )
                    self.set_status_message("Error saving text")
                finally:
                    self.progress_bar.stop()

        except Exception as e:
            self.logger.error(f"Error in save operation: {e}", exc_info=True)
            QMessageBox.critical(
                self, "Save Operation Error", f"Error in save operation: {e}"
            )

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Save settings before closing
            self._save_settings()
            self.logger.info("Extract Text window closing")
            event.accept()
        except Exception as e:
            self.logger.error(f"Error during window close: {e}")
            event.accept()


def main():
    """Main function for standalone execution."""
    try:
        app = QApplication(sys.argv)
        window = ExtractTextWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
