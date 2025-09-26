help me to crate a plan to:
i would like to rpolace the dialog based hub with a file explorer based hub.
this will be an imporved version of total commader, but cross platform!
the user will be able to choose between 1, 2, 3 and 4 pane hub, when
the main.py is executed.
all programs will be available from this file explorer ui.
the user can select which view, 1,2,3 or 4 is default.
the user can select which arrangement of views is their favorite, for each view
the user can select which source is their favorite for each view.
the use can select to have different file types color coded
the users selection will be saved in the user prefence db

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QComboBox, QPushButton, QMessageBox
)

class Pane(QWidget):
    def __init__(self, number):
        super().__init__()
        self.number = number
        layout = QVBoxLayout()

        # Drive selector
        self.drive_selector = QComboBox()
        self.drive_selector.addItems(self.get_drives())
        layout.addWidget(QLabel(f"Pane {number} - Select Drive:"))
        layout.addWidget(self.drive_selector)

        # Text editor
        self.editor = QTextEdit()
        layout.addWidget(self.editor)

        self.setLayout(layout)

    def get_drives(self):
        if os.name == 'nt':
            return [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        else:
            return ["/"]

class FileEditorDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Pane File Editor")
        self.panes = {}

        self.main_layout = QVBoxLayout()
        self.control_layout = QHBoxLayout()

        # Dropdown for number of panes
        self.pane_count_dropdown = QComboBox()
        self.pane_count_dropdown.addItems([str(i) for i in range(1, 5)])
        self.control_layout.addWidget(QLabel("Number of Panes:"))
        self.control_layout.addWidget(self.pane_count_dropdown)

        # Apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.update_panes)
        self.control_layout.addWidget(self.apply_button)

        # Dropdown for removing a pane
        self.remove_dropdown = QComboBox()
        self.remove_dropdown.addItems([str(i) for i in range(1, 5)])
        self.control_layout.addWidget(QLabel("Remove Pane #:"))
        self.control_layout.addWidget(self.remove_dropdown)

        # Remove button
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_pane)
        self.control_layout.addWidget(self.remove_button)

        self.main_layout.addLayout(self.control_layout)

        # Pane container
        self.pane_container = QHBoxLayout()
        self.main_layout.addLayout(self.pane_container)

        self.setLayout(self.main_layout)
        self.update_panes()

    def update_panes(self):
        desired_count = int(self.pane_count_dropdown.currentText())
        current_count = len(self.panes)

        # Add panes
        for i in range(current_count + 1, desired_count + 1):
            pane = Pane(i)
            self.panes[i] = pane
            self.pane_container.addWidget(pane)

        # Remove excess panes
        for i in range(desired_count + 1, current_count + 1):
            pane = self.panes.pop(i)
            pane.setParent(None)

        # Update remove dropdown
        self.remove_dropdown.clear()
        self.remove_dropdown.addItems([str(i) for i in sorted(self.panes.keys())])

    def remove_pane(self):
        pane_number = int(self.remove_dropdown.currentText())
        if pane_number in self.panes:
            pane = self.panes.pop(pane_number)
            pane.setParent(None)
            self.update_panes()
        else:
            QMessageBox.warning(self, "Error", f"Pane {pane_number} does not exist.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileEditorDemo()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())
