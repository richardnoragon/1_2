#!/usr/bin/env python3
"""
Richard's File Utilities - Minimal Test Version

A minimal version to test if the basic application can start.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt5.QtCore import Qt

    class MinimalApp(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Richard's File Utilities - Test")
            self.setGeometry(300, 300, 400, 200)

            label = QLabel(
                "Richard's File Utilities is running!\n\nPyQt5 is working correctly.",
                self,
            )
            label.setAlignment(Qt.AlignCenter)
            self.setCentralWidget(label)

    def main():
        app = QApplication(sys.argv)
        window = MinimalApp()
        window.show()
        return app.exec_()

    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure PyQt5 is properly installed.")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
