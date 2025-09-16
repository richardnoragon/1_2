#!/usr/bin/env python3
"""
Test script to verify PDF security dialog is working
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from pdf_security_parameter_dialogs import PDFEncryptionDialog


def test_encryption_dialog():
    app = QApplication(sys.argv)
    
    # Create a simple test window
    window = QMainWindow()
    window.setWindowTitle("Test Encryption Dialog")
    
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    test_button = QPushButton("Test Encryption Dialog")
    layout.addWidget(test_button)
    
    window.setCentralWidget(central_widget)
    
    def show_encryption_dialog():
        try:
            dialog = PDFEncryptionDialog(window)
            result = dialog.exec_()
            if result == dialog.Accepted:
                settings = dialog.get_security_settings()
                print(f"Encryption settings: {settings}")
            else:
                print("Dialog cancelled")
        except Exception as e:
            print(f"Error showing dialog: {e}")
            import traceback
            traceback.print_exc()
    
    test_button.clicked.connect(show_encryption_dialog)
    
    window.show()
    return app.exec_()


if __name__ == "__main__":
    test_encryption_dialog()
