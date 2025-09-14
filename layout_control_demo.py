#!/usr/bin/env python3
"""
Layout Control Demonstration

This script demonstrates the conditional layout control feature that
disables layout selection when only one pane is active.

Features demonstrated:
- Layout controls disabled when pane count = 1
- Layout controls enabled when pane count > 1  
- Visual feedback (grayed out appearance)
- Descriptive tooltips explaining the state
- Automatic reset to horizontal layout when going to single pane
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (QApplication, QComboBox, QLabel, QPushButton,
                                 QVBoxLayout, QWidget)
    
    class LayoutControlDemo(QWidget):
        def __init__(self):
            super().__init__()
            self.pane_count = 2
            self.layout_mode = 'horizontal'
            self.init_ui()
            
        def init_ui(self):
            self.setWindowTitle("Layout Control Conditional Logic Demo")
            self.setGeometry(100, 100, 400, 300)
            
            layout = QVBoxLayout()
            
            # Title
            title = QLabel("Multi-Pane Explorer Layout Control Demo")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(title)
            
            # Description
            description = QLabel(
                "This demonstrates how layout controls are disabled when only one pane is active.\n"
                "Layout arrangements (horizontal, vertical, grid) are only meaningful with multiple panes."
            )
            description.setWordWrap(True)
            description.setAlignment(Qt.AlignCenter)
            description.setStyleSheet("margin: 10px; color: #666;")
            layout.addWidget(description)
            
            # Pane count selector
            pane_label = QLabel("Number of Panes:")
            pane_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
            layout.addWidget(pane_label)
            
            self.pane_combo = QComboBox()
            self.pane_combo.addItems(['1', '2', '3', '4'])
            self.pane_combo.setCurrentText(str(self.pane_count))
            self.pane_combo.currentTextChanged.connect(self.on_pane_count_changed)
            layout.addWidget(self.pane_combo)
            
            # Layout selector (this will be conditionally enabled/disabled)
            self.layout_label = QLabel("Layout Arrangement:")
            self.layout_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
            layout.addWidget(self.layout_label)
            
            self.layout_combo = QComboBox()
            self.layout_combo.addItems(['Horizontal', 'Vertical', 'Grid'])
            self.layout_combo.setCurrentText(self.layout_mode.title())
            layout.addWidget(self.layout_combo)
            
            # Status display
            self.status_label = QLabel("")
            self.status_label.setStyleSheet("margin: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px;")
            self.status_label.setWordWrap(True)
            layout.addWidget(self.status_label)
            
            self.setLayout(layout)
            
            # Initialize the layout control state
            self.update_layout_control_state()
            
        def on_pane_count_changed(self, text):
            """Handle pane count change."""
            try:
                self.pane_count = int(text)
                self.update_layout_control_state()
            except ValueError:
                pass
                
        def update_layout_control_state(self):
            """Update layout control enabled/disabled state based on pane count.
            
            Single-pane configurations don't require layout choices since there's
            only one pane to display. Layout arrangements (horizontal, vertical, grid)
            are only meaningful when multiple panes need to be arranged relative to each other.
            """
            # Layout controls are only meaningful with multiple panes
            layout_enabled = self.pane_count > 1
            
            # Update the layout combo box
            self.layout_combo.setEnabled(layout_enabled)
            
            # Update tooltip to explain why it might be disabled
            if layout_enabled:
                self.layout_combo.setToolTip("Choose how multiple panes are arranged")
                tooltip_text = "Layout controls enabled - multiple panes active"
            else:
                self.layout_combo.setToolTip("Layout selection disabled - only one pane active")
                tooltip_text = "Layout controls disabled - single pane active"
                # Reset to default layout when transitioning to single pane
                if self.pane_count == 1 and self.layout_mode != 'horizontal':
                    self.layout_mode = 'horizontal'
                    self.layout_combo.setCurrentText('Horizontal')
            
            # Apply visual styling to indicate disabled state
            if layout_enabled:
                self.layout_combo.setStyleSheet("")
                self.layout_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
            else:
                self.layout_combo.setStyleSheet(
                    "QComboBox { color: gray; background-color: #f0f0f0; }"
                    "QComboBox::drop-down { border: none; }"
                    "QComboBox::down-arrow { image: none; }"
                )
                self.layout_label.setStyleSheet("color: gray; font-weight: bold; margin-top: 20px;")
            
            # Update status display
            status_msg = (
                f"Pane Count: {self.pane_count}\\n"
                f"Layout Enabled: {layout_enabled}\\n"
                f"Current Layout: {self.layout_mode.title()}\\n\\n"
                f"Explanation: {tooltip_text}\\n\\n"
                f"Note: {'Layout arrangements are only applicable when multiple panes need to be organized relative to each other.' if not layout_enabled else 'You can choose how the multiple panes are arranged on screen.'}"
            )
            self.status_label.setText(status_msg)
    
    def main():
        app = QApplication(sys.argv)
        demo = LayoutControlDemo()
        demo.show()
        return app.exec_()
        
    if __name__ == '__main__':
        sys.exit(main())
        
except ImportError as e:
    print(f"PyQt5 not available for demo: {e}")
    print("\\nLayout Control Logic Summary:")
    print("=" * 50)
    print("✓ Layout controls disabled when pane_count == 1")
    print("✓ Layout controls enabled when pane_count > 1") 
    print("✓ Visual feedback: grayed out when disabled")
    print("✓ Descriptive tooltips explain the state")
    print("✓ Auto-reset to horizontal layout for single pane")
    print("\\nImplementation successfully added to multi_pane_explorer.py")