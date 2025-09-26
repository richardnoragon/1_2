#!/usr/bin/env python3
"""
Data Anonymizer - Simple alias for privacy tools.
"""

from .privacy_tools import PrivacyCleanerGUI as DataAnonymizerGUI


def main():
    """Main function for standalone execution."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = DataAnonymizerGUI()
    window.setWindowTitle("Data Anonymizer - Richard's File Utilities")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
