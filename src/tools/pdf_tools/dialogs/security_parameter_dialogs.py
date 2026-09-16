"""
PDF Security Parameter Dialogs - Phase 2.3 Implementation
User interface dialogs for PDF security operations including encryption,
digital signatures, and access controls.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

from src.rfu import font_tokens
import os
from typing import Optional, Tuple

from pdf_security_engine import (
    DigitalSignature,
    EncryptionLevel,
    SecuritySettings,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)

from src.gui.components.buttons import PrimaryButton, SecondaryButton
from src.gui.components.inputs import TextInput
from src.gui.themes import Typography, token

# Constants
INVALID_INPUT_TITLE = "Invalid Input"


class BaseSecurityDialog(QDialog):
    """Base class for security dialogs with common styling"""

    def __init__(self, parent=None, title="PDF Security"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self.setup_ui()
        self.apply_styling()

    def setup_ui(self):
        """Setup base UI elements"""
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Title label
        self.title_label = QLabel(self.windowTitle())
        self.title_label.setAlignment(Qt.AlignCenter)
        font_tokens.bind(self.title_label, "font.title")
        self.layout.addWidget(self.title_label)

        # Main content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.layout.addWidget(self.content_widget)

        # Button area
        self.setup_buttons()

    def setup_buttons(self):
        """Setup dialog buttons"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = _ui_widget(PrimaryButton, 'Legacy.s565339bc4d33d728', 'setText')
        _ui_bind(self.ok_button, 'setAccessibleName', 'Legacy.s2475563598ab6aef')
        self.ok_button.clicked.connect(self.accept)

        self.cancel_button = _ui_widget(SecondaryButton, 'Legacy.s19766ed6ccb2f4a3', 'setText')
        _ui_bind(self.cancel_button, 'setAccessibleName', 'Legacy.s2a65de1f6fd6cb3d')
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)

    def apply_styling(self):
        """Apply consistent styling"""
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {token('surface')};


            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {token('border')};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {token('text_primary')};
            }}
            QPushButton {{
                background-color: {token('button_primary')};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {token('color_action_blue')};
            }}
            QPushButton:pressed {{
                background-color: {token('button_primary')};
            }}
            QLineEdit, QTextEdit, QComboBox, QSpinBox {{
                border: 1px solid {token('border')};
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border-color: {token('button_primary')};
            }}
            QCheckBox {{
                spacing: 8px;
            }}
            QLabel {{
                color: {token('text_primary')};
            }}
        """
        )
        font_tokens.bind(self, "font.body")


class PDFEncryptionDialog(BaseSecurityDialog):
    """Dialog for PDF encryption settings"""

    def __init__(self, parent=None):
        super().__init__(parent, "PDF Encryption Settings")
        self.resize(600, 500)
        self.setup_encryption_ui()

    def setup_encryption_ui(self):
        """Setup encryption-specific UI"""
        # Password settings group
        password_group = _ui_widget(QGroupBox, 'Legacy.s4fa2cd1f0799c7cd', 'setTitle')
        password_layout = QFormLayout(password_group)

        self.user_password_edit = TextInput(
            "User Password",
            "Enter user password",
            accessible_name="User password",
        )
        self.user_password_edit.setReadOnly(False)
        self.user_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow(self.user_password_edit)

        self.owner_password_edit = TextInput(
            "Owner Password",
            "Enter owner password",
            accessible_name="Owner password",
        )
        self.owner_password_edit.setReadOnly(False)
        self.owner_password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow(self.owner_password_edit)

        self.show_passwords_cb = _ui_widget(QCheckBox, 'Legacy.s0ab984b46165bf53', 'setText')
        _ui_bind(self.show_passwords_cb, 'setAccessibleName', 'Legacy.s0ab984b46165bf53')
        self.show_passwords_cb.setMinimumHeight(44)
        self.show_passwords_cb.toggled.connect(self.toggle_password_visibility)
        password_layout.addRow("", self.show_passwords_cb)

        self.content_layout.addWidget(password_group)

        # Encryption level group
        encryption_group = _ui_widget(QGroupBox, 'Legacy.s302de2d12163fc51', 'setTitle')
        encryption_layout = QVBoxLayout(encryption_group)

        self.encryption_combo = QComboBox()
        _ui_bind(self.encryption_combo, 'setAccessibleName', 'Legacy.sc39b5e13b3e25a92')
        self.encryption_combo.setMinimumHeight(44)
        self.encryption_combo.addItems(
            [
                "AES 256-bit (Recommended)",
                "AES 128-bit",
                "RC4 128-bit",
                "RC4 40-bit (Legacy)",
            ]
        )
        encryption_layout.addWidget(self.encryption_combo)

        encryption_info = _ui_widget(QLabel, 'Legacy.s9b717209e86e86e2', 'setText')
        encryption_info.setWordWrap(True)
        encryption_info.setStyleSheet(
            f"color: {token('text_muted')}; "
        )
        font_tokens.bind(encryption_info, "font.body")
        encryption_layout.addWidget(encryption_info)

        self.content_layout.addWidget(encryption_group)

        # Permissions group
        permissions_group = _ui_widget(QGroupBox, 'Legacy.s698f69b4ba1ecc91', 'setTitle')
        permissions_layout = QGridLayout(permissions_group)

        self.allow_printing_cb = _ui_widget(QCheckBox, 'Legacy.s9b5a25cfbfc95847', 'setText')
        _ui_bind(self.allow_printing_cb, 'setAccessibleName', 'Legacy.s9b5a25cfbfc95847')
        self.allow_printing_cb.setMinimumHeight(44)
        self.allow_printing_cb.setChecked(True)
        permissions_layout.addWidget(self.allow_printing_cb, 0, 0)

        self.allow_modification_cb = _ui_widget(QCheckBox, 'Legacy.s47c895ed46219387', 'setText')
        _ui_bind(self.allow_modification_cb, 'setAccessibleName', 'Legacy.s47c895ed46219387')
        self.allow_modification_cb.setMinimumHeight(44)
        permissions_layout.addWidget(self.allow_modification_cb, 0, 1)

        self.allow_copying_cb = _ui_widget(QCheckBox, 'Legacy.se9813cc8ef2530a2', 'setText')
        _ui_bind(self.allow_copying_cb, 'setAccessibleName', 'Legacy.se9813cc8ef2530a2')
        self.allow_copying_cb.setMinimumHeight(44)
        permissions_layout.addWidget(self.allow_copying_cb, 1, 0)

        self.allow_annotation_cb = _ui_widget(QCheckBox, 'Legacy.s3d29a40c9a4847e7', 'setText')
        _ui_bind(self.allow_annotation_cb, 'setAccessibleName', 'Legacy.s3d29a40c9a4847e7')
        self.allow_annotation_cb.setMinimumHeight(44)
        self.allow_annotation_cb.setChecked(True)
        permissions_layout.addWidget(self.allow_annotation_cb, 1, 1)

        self.allow_form_filling_cb = _ui_widget(QCheckBox, 'Legacy.sfd4e8aca6090ab55', 'setText')
        _ui_bind(self.allow_form_filling_cb, 'setAccessibleName', 'Legacy.sfd4e8aca6090ab55')
        self.allow_form_filling_cb.setMinimumHeight(44)
        self.allow_form_filling_cb.setChecked(True)
        permissions_layout.addWidget(self.allow_form_filling_cb, 2, 0)

        self.allow_text_extraction_cb = _ui_widget(QCheckBox, 'Legacy.s561ecbd6340d8b8e', 'setText')
        _ui_bind(self.allow_text_extraction_cb, 'setAccessibleName', 'Legacy.s561ecbd6340d8b8e')
        self.allow_text_extraction_cb.setMinimumHeight(44)
        self.allow_text_extraction_cb.setChecked(True)
        permissions_layout.addWidget(self.allow_text_extraction_cb, 2, 1)

        self.allow_assembly_cb = _ui_widget(QCheckBox, 'Legacy.s557d1912a19ff85d', 'setText')
        _ui_bind(self.allow_assembly_cb, 'setAccessibleName', 'Legacy.s557d1912a19ff85d')
        self.allow_assembly_cb.setMinimumHeight(44)
        permissions_layout.addWidget(self.allow_assembly_cb, 3, 0)

        self.allow_hq_print_cb = _ui_widget(QCheckBox, 'Legacy.s19da39cacc322496', 'setText')
        _ui_bind(self.allow_hq_print_cb, 'setAccessibleName', 'Legacy.s19da39cacc322496')
        self.allow_hq_print_cb.setMinimumHeight(44)
        self.allow_hq_print_cb.setChecked(True)
        permissions_layout.addWidget(self.allow_hq_print_cb, 3, 1)

        self.content_layout.addWidget(permissions_group)

    def toggle_password_visibility(self, show):
        """Toggle password field visibility"""
        mode = QLineEdit.Normal if show else QLineEdit.Password
        self.user_password_edit.setEchoMode(mode)
        self.owner_password_edit.setEchoMode(mode)

    def get_security_settings(self) -> SecuritySettings:
        """Get security settings from dialog"""
        # Map encryption combo selection to enum
        encryption_map = {
            0: EncryptionLevel.AES_256,
            1: EncryptionLevel.AES_128,
            2: EncryptionLevel.RC4_128,
            3: EncryptionLevel.RC4_40,
        }

        settings = SecuritySettings(
            user_password=self.user_password_edit.text(),
            owner_password=self.owner_password_edit.text(),
            encryption_level=(
                encryption_map[self.encryption_combo.currentIndex()]
            ),
            allow_printing=self.allow_printing_cb.isChecked(),
            allow_modification=self.allow_modification_cb.isChecked(),
            allow_copying=self.allow_copying_cb.isChecked(),
            allow_annotation=self.allow_annotation_cb.isChecked(),
            allow_form_filling=self.allow_form_filling_cb.isChecked(),
            allow_text_extraction=self.allow_text_extraction_cb.isChecked(),
            allow_assembly=self.allow_assembly_cb.isChecked(),
            allow_high_quality_print=self.allow_hq_print_cb.isChecked(),
        )

        return settings

    def validate_input(self) -> Tuple[bool, str]:
        """Validate dialog input"""
        user_pw = self.user_password_edit.text()
        owner_pw = self.owner_password_edit.text()

        if not user_pw and not owner_pw:
            return False, "At least one password must be provided"

        if len(user_pw) > 127:
            return False, "User password too long (max 127 characters)"

        if len(owner_pw) > 127:
            return False, "Owner password too long (max 127 characters)"

        return True, ""


class PDFDecryptionDialog(BaseSecurityDialog):
    """Dialog for PDF decryption"""

    def __init__(self, parent=None):
        super().__init__(parent, "PDF Decryption")
        self.resize(450, 300)
        self.setup_decryption_ui()

    def setup_decryption_ui(self):
        """Setup decryption-specific UI"""
        info_label = _ui_widget(QLabel, 'Legacy.s21db81c0ee6e1b33', 'setText')
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            f"color: {token('text_muted')}; margin-bottom: 15px;"
        )
        self.content_layout.addWidget(info_label)

        # Password input
        password_group = _ui_widget(QGroupBox, 'Legacy.se7cf3ef4f17c3999', 'setTitle')
        password_layout = QFormLayout(password_group)

        self.password_edit = TextInput(
            "Password",
            "Enter document password",
            accessible_name="Document password",
        )
        self.password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addRow(self.password_edit)

        self.show_password_cb = _ui_widget(QCheckBox, 'Legacy.s6aeaa6a53d09dcad', 'setText')
        _ui_bind(self.show_password_cb, 'setAccessibleName', 'Legacy.s6aeaa6a53d09dcad')
        self.show_password_cb.setMinimumHeight(44)
        self.show_password_cb.toggled.connect(self.toggle_password_visibility)
        password_layout.addRow("", self.show_password_cb)

        self.content_layout.addWidget(password_group)

        # Password type hint
        hint_group = _ui_widget(QGroupBox, 'Legacy.s1d330336b8f29485', 'setTitle')
        hint_layout = QVBoxLayout(hint_group)

        user_hint = _ui_widget(QLabel, 'Legacy.s1d8247b6dc78cee2', 'setText')
        owner_hint = _ui_widget(QLabel, 'Legacy.s3e1f7c7438a933d4', 'setText')

        hint_layout.addWidget(user_hint)
        hint_layout.addWidget(owner_hint)

        self.content_layout.addWidget(hint_group)

    def toggle_password_visibility(self, show):
        """Toggle password field visibility"""
        mode = QLineEdit.Normal if show else QLineEdit.Password
        self.password_edit.setEchoMode(mode)

    def get_password(self) -> str:
        """Get password from dialog"""
        return self.password_edit.text()

    def validate_input(self) -> Tuple[bool, str]:
        """Validate dialog input"""
        if not self.password_edit.text():
            return False, "Password is required"
        return True, ""


class PDFDigitalSignatureDialog(BaseSecurityDialog):
    """Dialog for digital signature settings"""

    def __init__(self, parent=None):
        super().__init__(parent, "Digital Signature Settings")
        self.resize(700, 600)
        self.setup_signature_ui()

    def setup_signature_ui(self):
        """Setup digital signature UI"""
        # Create tab widget for organization
        tab_widget = QTabWidget()
        _ui_bind(tab_widget, 'setAccessibleName', 'Legacy.s24f52582ca8824bf')

        # Certificate tab
        cert_tab = QWidget()
        cert_layout = QVBoxLayout(cert_tab)

        cert_group = _ui_widget(QGroupBox, 'Legacy.s654c7576f226693b', 'setTitle')
        cert_form = QFormLayout(cert_group)

        self.cert_path_edit = TextInput(
            "Certificate File",
            "Select certificate file",
            accessible_name="Certificate file path",
        )
        cert_browse_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(cert_browse_btn, 'setAccessibleName', 'Legacy.s0782eb8dbd434fda')
        cert_browse_btn.clicked.connect(self.browse_certificate)

        cert_row = QHBoxLayout()
        cert_row.addWidget(self.cert_path_edit)
        cert_row.addWidget(cert_browse_btn)
        cert_form.addRow(cert_row)

        self.private_key_edit = TextInput(
            "Private Key File",
            "Select private key file",
            accessible_name="Private key file path",
        )
        key_browse_btn = _ui_widget(SecondaryButton, 'Legacy.sc58a6bd402efb06c', 'setText')
        _ui_bind(key_browse_btn, 'setAccessibleName', 'Legacy.sb4d3c1faee0958fb')
        key_browse_btn.clicked.connect(self.browse_private_key)

        key_row = QHBoxLayout()
        key_row.addWidget(self.private_key_edit)
        key_row.addWidget(key_browse_btn)
        cert_form.addRow(key_row)

        self.cert_password_edit = TextInput(
            "Certificate Password",
            "Certificate password",
            accessible_name="Certificate password",
        )
        self.cert_password_edit.setEchoMode(QLineEdit.Password)
        cert_form.addRow(self.cert_password_edit)

        cert_layout.addWidget(cert_group)
        tab_widget.addTab(cert_tab, "Certificate")

        # Signature details tab
        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)

        details_group = _ui_widget(QGroupBox, 'Legacy.s90121e5b4a8c520c', 'setTitle')
        details_form = QFormLayout(details_group)

        self.reason_edit = TextInput(
            "Reason",
            "Document verification",
            accessible_name="Signature reason",
        )
        details_form.addRow(self.reason_edit)

        self.location_edit = TextInput(
            "Location",
            "Location (optional)",
            accessible_name="Signature location",
        )
        details_form.addRow(self.location_edit)

        self.contact_edit = TextInput(
            "Contact Info",
            "Contact information",
            accessible_name="Signature contact information",
        )
        details_form.addRow(self.contact_edit)

        self.field_name_edit = TextInput(
            "Signature Field",
            "Signature1",
            accessible_name="Signature field name",
        )
        details_form.addRow(self.field_name_edit)

        details_layout.addWidget(details_group)

        # Appearance group
        appearance_group = _ui_widget(QGroupBox, 'Legacy.s3ace16f61deb82ed', 'setTitle')
        appearance_layout = QVBoxLayout(appearance_group)

        self.visible_cb = _ui_widget(QCheckBox, 'Legacy.s305e83a149c656e5', 'setText')
        _ui_bind(self.visible_cb, 'setAccessibleName', 'Legacy.s305e83a149c656e5')
        self.visible_cb.setMinimumHeight(44)
        self.visible_cb.setChecked(True)
        appearance_layout.addWidget(self.visible_cb)

        position_layout = QFormLayout()

        self.x_spin = QSpinBox()
        _ui_bind(self.x_spin, 'setAccessibleName', 'Legacy.s9ce2f9237161bde8')
        self.x_spin.setMinimumHeight(44)
        self.x_spin.setRange(0, 1000)
        self.x_spin.setValue(100)
        position_layout.addRow("X Position:", self.x_spin)

        self.y_spin = QSpinBox()
        _ui_bind(self.y_spin, 'setAccessibleName', 'Legacy.s261b7e87dfd15211')
        self.y_spin.setMinimumHeight(44)
        self.y_spin.setRange(0, 1000)
        self.y_spin.setValue(100)
        position_layout.addRow("Y Position:", self.y_spin)

        self.width_spin = QSpinBox()
        _ui_bind(self.width_spin, 'setAccessibleName', 'Legacy.sd53c9c874144f37c')
        self.width_spin.setMinimumHeight(44)
        self.width_spin.setRange(50, 500)
        self.width_spin.setValue(100)
        position_layout.addRow("Width:", self.width_spin)

        self.height_spin = QSpinBox()
        _ui_bind(self.height_spin, 'setAccessibleName', 'Legacy.sa847d4babec4bde5')
        self.height_spin.setMinimumHeight(44)
        self.height_spin.setRange(25, 200)
        self.height_spin.setValue(50)
        position_layout.addRow("Height:", self.height_spin)

        appearance_layout.addLayout(position_layout)
        details_layout.addWidget(appearance_group)

        tab_widget.addTab(details_tab, "Details")

        self.content_layout.addWidget(tab_widget)

    def browse_certificate(self):
        """Browse for certificate file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Certificate File",
            "",
            "Certificate Files (*.p12 *.pfx *.crt *.cer);;All Files (*)",
        )
        if file_path:
            self.cert_path_edit.setText(file_path)

    def browse_private_key(self):
        """Browse for private key file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Private Key File",
            "",
            "Key Files (*.key *.pem);;All Files (*)",
        )
        if file_path:
            self.private_key_edit.setText(file_path)

    def get_signature_config(self) -> DigitalSignature:
        """Get signature configuration from dialog"""
        signature = DigitalSignature(
            certificate_path=self.cert_path_edit.text(),
            private_key_path=self.private_key_edit.text(),
            password=self.cert_password_edit.text(),
            reason=self.reason_edit.text(),
            location=self.location_edit.text(),
            contact_info=self.contact_edit.text(),
            signature_field_name=self.field_name_edit.text(),
            visible=self.visible_cb.isChecked(),
            signature_rect=(
                self.x_spin.value(),
                self.y_spin.value(),
                self.x_spin.value() + self.width_spin.value(),
                self.y_spin.value() + self.height_spin.value(),
            ),
        )

        return signature

    def validate_input(self) -> Tuple[bool, str]:
        """Validate dialog input"""
        if not self.cert_path_edit.text():
            return False, "Certificate file is required"

        if not os.path.exists(self.cert_path_edit.text()):
            return False, "Certificate file not found"

        if self.private_key_edit.text() and not os.path.exists(
            self.private_key_edit.text()
        ):
            return False, "Private key file not found"

        if not self.reason_edit.text():
            return False, "Signature reason is required"

        return True, ""


class PDFSecurityInfoDialog(BaseSecurityDialog):
    """Dialog for displaying PDF security information"""

    def __init__(self, parent=None, security_info=None):
        self.security_info = security_info or {}
        super().__init__(parent, "PDF Security Information")
        self.resize(600, 500)
        self.setup_info_ui()
        self.populate_info()

        # Remove OK button, only show Close
        self.ok_button.setText("Close")
        self.cancel_button.hide()

    def setup_info_ui(self):
        """Setup security info display UI"""
        # Create scroll area for large content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.NoFrame)

        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)

        # Encryption status
        self.encryption_group = _ui_widget(QGroupBox, 'Legacy.s518e0ffb1cde0eee', 'setTitle')
        self.encryption_layout = QFormLayout(self.encryption_group)
        info_layout.addWidget(self.encryption_group)

        # Permissions
        self.permissions_group = _ui_widget(QGroupBox, 'Legacy.s698f69b4ba1ecc91', 'setTitle')
        self.permissions_layout = QGridLayout(self.permissions_group)
        info_layout.addWidget(self.permissions_group)

        # Signature information
        self.signature_group = _ui_widget(QGroupBox, 'Legacy.s35c21f97ac038fb4', 'setTitle')
        self.signature_layout = QVBoxLayout(self.signature_group)
        info_layout.addWidget(self.signature_group)

        scroll.setWidget(info_widget)
        self.content_layout.addWidget(scroll)

    def populate_info(self):
        """Populate dialog with security information"""
        if not self.security_info:
            return

        # Encryption status
        encrypted = self.security_info.get("encrypted", False)
        self.encryption_layout.addRow(
            "Encrypted:", QLabel("Yes" if encrypted else "No")
        )

        if encrypted:
            needs_password = self.security_info.get("needs_password", False)
            self.encryption_layout.addRow(
                "Password Required:", QLabel("Yes" if needs_password else "No")
            )

        # Permissions
        permissions = self.security_info.get("permissions", {})
        if permissions:
            row = 0
            for perm, allowed in permissions.items():
                label = QLabel(perm.replace("_", " ").title() + ":")
                status = QLabel("Allowed" if allowed else "Restricted")
                status.setStyleSheet(
                    "color: green;" if allowed else "color: red;"
                )

                self.permissions_layout.addWidget(label, row, 0)
                self.permissions_layout.addWidget(status, row, 1)
                row += 1
        else:
            self.permissions_layout.addWidget(
                _ui_widget(QLabel, 'Legacy.scca525ccebb42438', 'setText'), 0, 0, 1, 2
            )

        # Signature information (placeholder)
        self.signature_layout.addWidget(
            _ui_widget(QLabel, 'Legacy.sa3eaa5abaa85fdf3', 'setText')
        )


# Convenience functions for dialog creation
def show_encryption_dialog(parent=None) -> Optional[SecuritySettings]:
    """Show encryption dialog and return settings"""
    dialog = PDFEncryptionDialog(parent)
    if dialog.exec_() == QDialog.Accepted:
        valid, msg = dialog.validate_input()
        if valid:
            return dialog.get_security_settings()
        else:
            QMessageBox.warning(parent, INVALID_INPUT_TITLE, msg)
    return None


def show_decryption_dialog(parent=None) -> Optional[str]:
    """Show decryption dialog and return password"""
    dialog = PDFDecryptionDialog(parent)
    if dialog.exec_() == QDialog.Accepted:
        valid, msg = dialog.validate_input()
        if valid:
            return dialog.get_password()
        else:
            QMessageBox.warning(parent, INVALID_INPUT_TITLE, msg)
    return None


def show_signature_dialog(parent=None) -> Optional[DigitalSignature]:
    """Show digital signature dialog and return configuration"""
    dialog = PDFDigitalSignatureDialog(parent)
    if dialog.exec_() == QDialog.Accepted:
        valid, msg = dialog.validate_input()
        if valid:
            return dialog.get_signature_config()
        else:
            QMessageBox.warning(parent, INVALID_INPUT_TITLE, msg)
    return None


def show_security_info_dialog(parent=None, security_info=None):
    """Show security information dialog"""
    dialog = PDFSecurityInfoDialog(parent, security_info)
    dialog.exec_()
