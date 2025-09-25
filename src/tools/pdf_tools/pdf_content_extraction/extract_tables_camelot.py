import sys
import os
import json
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
import camelot
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)


def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Error loading config: %s", str(e))
        return None


def save_config(config):
    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        logger.error("Error saving config: %s", str(e))
        return False


def extract_tables(
    input_file: str, output_folder: str = None, **kwargs
) -> bool:
    """Extract tables from PDF file using Camelot with configurable parameters"""
    try:
        logger.info("Starting table extraction from: %s", input_file)
        logger.debug(
            "Parameters - Output folder: %s, Settings: %s",
            output_folder,
            kwargs,
        )

        if not output_folder:
            output_folder = os.path.join(
                os.path.dirname(input_file), "extracted_tables"
            )
        if not os.path.exists(output_folder):
            logger.info("Creating output folder: %s", output_folder)
            os.makedirs(output_folder)

        # Extract tables using Camelot with provided parameters
        logger.info("Reading tables from PDF with parameters: %s", kwargs)
        tables = camelot.read_pdf(input_file, **kwargs)
        logger.info("Found %d tables", len(tables))

        if not tables:
            logger.warning("No tables found in the document")
            return False

        # Save each table
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        for i, table in enumerate(tables, 1):
            try:
                output_file = os.path.join(
                    output_folder, f"{base_name}_table_{i}.csv"
                )
                logger.debug("Saving table %d to: %s", i, output_file)
                table.to_csv(output_file)
            except Exception as e:
                logger.error("Failed to save table %d: %s", i, str(e))
                QMessageBox.warning(
                    None, "Warning", f"Failed to save table {i}: {str(e)}"
                )
                continue

        logger.info("Table extraction completed successfully")
        return True

    except Exception as e:
        logger.error("Error in table extraction: %s", str(e))
        QMessageBox.critical(None, "Error", str(e))
        return False


class TableExtractorWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            uic.loadUi("extract_tables_camelot.ui", self)
            self.config = load_config()
            self.initUI()

            logger.info("Table extractor initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize table extractor: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Failed to initialize UI: {str(e)}"
            )
            self.close()

    def initUI(self):
        try:
            # Connect buttons to functions
            self.browseButton.clicked.connect(self.browse_file)
            self.extractButton.clicked.connect(self.extract_tables)
            self.saveSettingsButton.clicked.connect(self.save_settings)
            self.actionExit.triggered.connect(self.close)

            # Load settings from config
            if self.config:
                settings = self.config.get("extract_tables", {})
                self.flavorCombo.setCurrentText(
                    settings.get("flavor", "lattice")
                )
                self.lineScaleSpinBox.setValue(settings.get("line_scale", 15))
                self.backgroundCheckBox.setChecked(
                    settings.get("process_background", False)
                )
                self.tableBordersCombo.setCurrentText(
                    settings.get("table_borders", "normal")
                )
                self.edgeToleranceSpinBox.setValue(
                    settings.get("edge_tol", 50)
                )
                self.rowToleranceSpinBox.setValue(settings.get("row_tol", 2))
                self.columnToleranceSpinBox.setValue(
                    settings.get("column_tol", 2)
                )
                self.pagesEdit.setText(settings.get("pages", ""))

            # Initially disable extract button
            self.extractButton.setEnabled(False)

            # Initialize progress bar
            self.progressBar.setValue(0)

            logger.debug("UI initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize UI components: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to initialize UI components: %s",
                str(e),
            )
            self.close()

    def save_settings(self):
        try:
            if not self.config:
                self.config = {}

            self.config["extract_tables"] = {
                "flavor": self.flavorCombo.currentText(),
                "line_scale": self.lineScaleSpinBox.value(),
                "process_background": self.backgroundCheckBox.isChecked(),
                "table_borders": self.tableBordersCombo.currentText(),
                "edge_tol": self.edgeToleranceSpinBox.value(),
                "row_tol": self.rowToleranceSpinBox.value(),
                "column_tol": self.columnToleranceSpinBox.value(),
                "pages": self.pagesEdit.text(),
            }

            if save_config(self.config):
                logger.info("Settings saved successfully")
                QMessageBox.information(
                    self, "Success", "Settings saved successfully!"
                )
            else:
                logger.error("Failed to save settings")
                QMessageBox.warning(self, "Warning", "Failed to save settings")

        except Exception as e:
            logger.error("Error saving settings: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error saving settings: %s", str(e)
            )

    def browse_file(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Select PDF File", "", "PDF Files (*.pdf)"
            )
            if file_name:
                logger.info("Selected input file: %s", file_name)
                self.inputFileEdit.setText(file_name)
                self.extractButton.setEnabled(True)
                self.outputText.clear()
                self.progressBar.setValue(0)

        except Exception as e:
            logger.error("Error browsing for file: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error browsing file: %str(e)"
            )

    def extract_tables(self):
        try:
            if not self.input_file:
                logger.warning("No input file selected")
                QMessageBox.warning(
                    self, "Warning", "Please select a PDF file first!"
                )
                return

            output_folder = self.outputFolderEdit.text()
            if not output_folder or not os.path.isdir(output_folder):
                logger.warning("Invalid output folder")
                QMessageBox.warning(
                    self, "Warning", "Please select a valid output folder!"
                )
                return

            # Get extraction parameters
            params = {
                "flavor": self.flavorCombo.currentText(),
                "line_scale": self.lineScaleSpinBox.value(),
                "process_background": self.backgroundCheckBox.isChecked(),
                "table_borders": self.tableBordersCombo.currentText(),
                "edge_tol": self.edgeToleranceSpinBox.value(),
                "row_tol": self.rowToleranceSpinBox.value(),
                "column_tol": self.columnToleranceSpinBox.value(),
                "pages": (
                    self.pagesEdit.text() if self.pagesEdit.text() else None
                ),
            }

            self.progressBar.show()
            self.progressBar.setValue(0)
            self.statusBar().showMessage("Loading document...")
            QtWidgets.QApplication.processEvents()

            # Initialize document
            self.progressBar.setValue(10)
            QtWidgets.QApplication.processEvents()

            try:
                # Start table extraction
                self.statusBar().showMessage("Extracting tables...")
                self.progressBar.setValue(25)
                QtWidgets.QApplication.processEvents()

                # Progress updates at key points
                def progress_callback(current_page, total_pages):
                    progress = 25 + int((current_page / total_pages) * 50)
                    self.progressBar.setValue(progress)
                    self.statusBar().showMessage(
                        f"Processing page {current_page} of {total_pages}..."
                    )
                    QtWidgets.QApplication.processEvents()

                logger.info("Starting table extraction process")
                success = extract_tables_from_pdf(
                    input_file=self.input_file,
                    output_folder=output_folder,
                    progress_callback=progress_callback,
                    **params,
                )

                if success:
                    self.progressBar.setValue(100)
                    success_msg = "\nTables extracted successfully!"
                    self.outputText.append(success_msg)
                    self.outputText.append(f"\nOutput folder: {output_folder}")

                    logger.info("Table extraction completed successfully")
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Tables have been extracted successfully!\nOutput folder: {output_folder}",
                    )
                    self.statusBar().showMessage("Extraction complete", 3000)
                else:
                    logger.warning("Table extraction failed")
                    QMessageBox.warning(
                        self, "Warning", "Failed to extract tables!"
                    )
                    self.progressBar.setValue(0)
                    self.statusBar().showMessage("Extraction failed", 3000)

            except Exception as e:
                logger.error("Error during extraction: %s", str(e))
                self.outputText.append(f"\nError: {str(e)}")
                QMessageBox.critical(
                    self, "Error", f"Error extracting tables: {str(e)}"
                )
                self.progressBar.setValue(0)
                self.statusBar().showMessage("Extraction failed", 3000)

        except Exception as e:
            logger.error("Error in extract operation: %s", str(e))
            QMessageBox.critical(self, "Error", f"Unexpected error: {str(e)}")
            self.progressBar.setValue(0)
            self.statusBar().showMessage("Error occurred", 3000)

        finally:
            self.progressBar.hide()


def main():
    try:
        app = QApplication(sys.argv)
        window = TableExtractorWindow()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        QMessageBox.critical(
            None, "Fatal Error", f"Application failed to start: %str(e)"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
