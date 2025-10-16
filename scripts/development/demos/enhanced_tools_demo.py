#!/usr/bin/env python3
"""
Demo script for Enhanced File Operation Tools Menu Integration.
Shows all three tools with their new File menus and Help dialogs.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox


def run_demo():
    """Run a demo showing the enhanced tools."""
    app = QApplication(sys.argv)

    print("🎯 ENHANCED FILE OPERATION TOOLS DEMO")
    print("=" * 50)
    print("Starting demo of all enhanced tools...")
    print("Each tool will open briefly to show menu integration.")
    print("=" * 50)

    # Demo Compress/Decompress Tool
    try:
        from src.utilities.file_operations.compression.compress_decompress import (
            CompressDecompressWindow as CompressDecompressApp,
        )

        print("1. Opening Compress/Decompress Tool...")
        compress_tool = CompressDecompressApp()
        compress_tool.show()

        # Show help after a moment
        def show_compress_help():
            compress_tool.show_help()
            QTimer.singleShot(3000, compress_tool.close)

        QTimer.singleShot(1000, show_compress_help)

    except Exception as e:
        print(f"Error with Compress/Decompress Tool: {e}")

    # Demo message after tools close
    def show_final_message():
        msg = QMessageBox()
        msg.setWindowTitle("Enhanced Tools Demo Complete")
        msg.setText(
            "✅ Enhanced File Operation Tools Demo Complete!\n\n"
            "All enhanced tools now feature:\n\n"
            "🔹 File menu with Exit (Ctrl+Q) and Help (F1)\n"
            "🔹 Comprehensive help dialogs\n"
            "🔹 Consistent UI styling\n"
            "🔹 Menu-driven functionality\n"
            "🔹 Keyboard shortcuts\n"
            "🔹 StandardWindow integration\n\n"
            "Tools enhanced:\n"
            "• Compress/Decompress\n"
            "• File Splitter/Joiner\n"
            "• Synchronize\n\n"
            "Integration template: File Finder menu structure"
        )
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        app.quit()

    QTimer.singleShot(6000, show_final_message)

    return app.exec_()


if __name__ == "__main__":
    run_demo()
