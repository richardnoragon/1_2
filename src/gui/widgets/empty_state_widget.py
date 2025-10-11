"""
EmptyStateWidget: Reusable component for displaying empty states.

Displays centered icon + title + description + optional action button.
Used by BookmarksWidget and RecentWidget when lists are empty.
"""

from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class EmptyStateWidget(QWidget):
    """
    Reusable empty state widget for displaying helpful messages.

    Features:
    - Centered icon (uses text emoji/unicode for cross-platform support)
    - Title text
    - Description text with word wrap
    - Optional action button
    - Accessible for screen readers
    """

    actionClicked = pyqtSignal()

    def __init__(
        self,
        icon: str = "📂",
        title: str = "No Items",
        description: str = "This section is empty.",
        action_text: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize empty state widget.

        Args:
            icon: Unicode emoji/character for icon (default: folder)
            title: Bold title text
            description: Detailed description with helpful guidance
            action_text: Optional action button text (None = no button)
            parent: Parent widget
        """
        super().__init__(parent)

        self.icon = icon
        self.title_text = title
        self.description_text = description
        self.action_text = action_text

        self._setup_ui()
        self._setup_accessibility()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        # Icon label
        self.icon_label = QLabel(self.icon)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet(
            """
            QLabel {
                font-size: 48px;
                color: #999999;
            }
            """
        )
        layout.addWidget(self.icon_label)

        # Title label
        self.title_label = QLabel(self.title_text)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #666666;
            }
            """
        )
        layout.addWidget(self.title_label)

        # Description label
        self.description_label = QLabel(self.description_text)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setWordWrap(True)
        self.description_label.setMaximumWidth(400)
        self.description_label.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #888888;
                line-height: 1.4;
            }
            """
        )
        layout.addWidget(self.description_label)

        # Action button (optional)
        if self.action_text:
            self.action_button = QPushButton(self.action_text)
            self.action_button.setMinimumWidth(120)
            self.action_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #106EBE;
                }
                QPushButton:pressed {
                    background-color: #005A9E;
                }
                """
            )
            self.action_button.clicked.connect(self.actionClicked.emit)
            layout.addWidget(self.action_button, alignment=Qt.AlignCenter)
        else:
            self.action_button = None

        # Add stretch at bottom for centering
        layout.addStretch()

    def _setup_accessibility(self):
        """Setup accessibility properties for screen readers."""
        accessible_text = f"{self.title_text}. {self.description_text}"
        self.setAccessibleName(self.title_text)
        self.setAccessibleDescription(accessible_text)

    def update_content(
        self,
        icon: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        action_text: Optional[str] = None,
    ):
        """
        Update empty state content dynamically.

        Args:
            icon: New icon (None = keep current)
            title: New title (None = keep current)
            description: New description (None = keep current)
            action_text: New action text (None = keep current)
        """
        if icon is not None:
            self.icon = icon
            self.icon_label.setText(icon)

        if title is not None:
            self.title_text = title
            self.title_label.setText(title)

        if description is not None:
            self.description_text = description
            self.description_label.setText(description)

        if action_text is not None:
            self.action_text = action_text
            if self.action_button:
                self.action_button.setText(action_text)

        self._setup_accessibility()

    def has_action_button(self) -> bool:
        """Check if widget has an action button."""
        return self.action_button is not None

    def get_action_button(self) -> Optional[QPushButton]:
        """Get the action button if it exists."""
        return self.action_button

    def wordWrap(self) -> bool:
        """Check if description has word wrap enabled (for testing)."""
        return self.description_label.wordWrap()
