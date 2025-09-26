#!/usr/bin/env python3
"""
Data Anonymizer - Robust alias for privacy tools with fallback support.
"""

import sys

# Try to import privacy tools with fallback mechanism
try:
    from .privacy_tools import PrivacyCleanerGUI as DataAnonymizerGUI
except ImportError:
    # Fallback to simplified version
    try:
        from .privacy_tools_simple import SimplePrivacyHub as DataAnonymizerGUI
    except ImportError:
        # Final fallback - show error message
        print("Error: Privacy tools are not available.")
        print("Please check your installation and dependencies.")

        # Create a minimal error dialog
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox

            class DataAnonymizerGUI:
                def __init__(self):
                    self.show_error()

                def show_error(self):
                    app = QApplication.instance() or QApplication(sys.argv)
                    QMessageBox.critical(
                        None,
                        "Data Anonymizer Error",
                        "The Data Anonymizer tool is currently unavailable.\n\n"
                        "This may be due to missing dependencies or "
                        "configuration issues.\n\n"
                        "Please check the installation and try again.",
                    )

                def show(self):
                    pass  # No-op for compatibility

        except ImportError:
            # If even PyQt5 is not available
            class DataAnonymizerGUI:
                def __init__(self):
                    print("Data Anonymizer: PyQt5 not available")

                def show(self):
                    print("Data Anonymizer: Cannot display GUI without PyQt5")


def main():
    """Main function for standalone execution."""
    try:
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        window = DataAnonymizerGUI()
        if hasattr(window, "setWindowTitle"):
            window.setWindowTitle("Data Anonymizer - Richard's File Utilities")
        window.show()
        sys.exit(app.exec_())
    except ImportError:
        print("Error: PyQt5 is required to run the Data Anonymizer.")
        print("Please install PyQt5: pip install PyQt5")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting Data Anonymizer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
