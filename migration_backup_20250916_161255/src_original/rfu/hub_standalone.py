#!/usr/bin/env python3
"""
RFU Hub - Standalone Version
Simple launcher that runs the hub without relative import issues.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("PyQt5 not available. Please install PyQt5 to use the GUI.")
    sys.exit(1)

class SimpleRFUHub(QtWidgets.QMainWindow):
    """Simplified RFU Hub that works standalone."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RFU Hub - Standalone")
        self.setGeometry(200, 200, 800, 600)
        
        # Create central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Welcome label
        welcome_label = QtWidgets.QLabel("<h1>RFU Hub - Standalone Mode</h1>")
        welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Info label
        info_label = QtWidgets.QLabel(
            "<p>This is a simplified version of the RFU Hub running in standalone mode.</p>"
            "<p>For full functionality, please run: <code>python main.py</code> from the workspace root.</p>"
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Create buttons for basic tools
        self.create_tool_buttons(layout)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("RFU Hub Standalone - Ready")
    
    def create_tool_buttons(self, layout):
        """Create basic tool launcher buttons."""
        button_group = QtWidgets.QGroupBox("Available Tools")
        button_layout = QtWidgets.QGridLayout(button_group)
        
        # Main application button
        main_app_btn = QtWidgets.QPushButton("🚀 Launch Main Application")
        main_app_btn.setMinimumHeight(50)
        main_app_btn.clicked.connect(self.launch_main_app)
        button_layout.addWidget(main_app_btn, 0, 0, 1, 2)
        
        # Tool buttons (these will show info messages for now)
        tools = [
            ("📁 File Catalog", "File catalog functionality"),
            ("🌐 Network Tools", "Network utilities"),
            ("🔒 Security Tools", "Security and encryption tools"),
            ("⚙️ System Tools", "System utilities"),
            ("📝 Clipboard Manager", "Enhanced clipboard management"),
            ("🔍 Diagnostics", "System diagnostics")
        ]
        
        row, col = 1, 0
        for tool_name, description in tools:
            btn = QtWidgets.QPushButton(tool_name)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, desc=description: self.show_tool_info(desc))
            button_layout.addWidget(btn, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        layout.addWidget(button_group)
    
    def launch_main_app(self):
        """Launch the main application."""
        import subprocess
        import sys
        
        try:
            # Get the workspace root directory
            workspace_root = Path(__file__).parent.parent
            main_py = workspace_root / "main.py"
            
            if main_py.exists():
                self.status_bar.showMessage("Launching main application...")
                # Launch main.py as a separate process
                subprocess.Popen([sys.executable, str(main_py)], cwd=str(workspace_root))
                self.status_bar.showMessage("Main application launched")
            else:
                self.status_bar.showMessage("main.py not found")
        except Exception as e:
            self.status_bar.showMessage(f"Error launching main app: {str(e)}")
    
    def show_tool_info(self, description):
        """Show information about a tool."""
        QtWidgets.QMessageBox.information(
            self,
            "Tool Information",
            f"{description}\n\nFor full functionality, please run the main application:\n"
            "python main.py"
        )

def main():
    """Main function."""
    if not PYQT5_AVAILABLE:
        print("PyQt5 is required for the GUI. Please install it with:")
        print("pip install PyQt5")
        return 1
    
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    hub = SimpleRFUHub()
    hub.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())