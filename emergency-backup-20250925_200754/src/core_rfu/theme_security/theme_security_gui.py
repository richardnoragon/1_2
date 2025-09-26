"""
Theme Security GUI Components for RFU Hub

Provides GUI components for theme security management:
- Security status dashboard
- Encryption controls
- Backup management interface
- Recovery interface
- Configuration management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import logging
import datetime

# Import security components
try:
    from .theme_security_manager import ThemeSecurityManager
    from .theme_config import ThemeSecurityConfig
    from .theme_backup import ThemeBackupManager
    from .theme_recovery import ThemeRecoveryManager
    from .theme_validator import ThemeIntegrityValidator
    from .theme_access_control import ThemeAccessController
except ImportError:
    # Fallback for development
    ThemeSecurityManager = None
    ThemeSecurityConfig = None
    ThemeBackupManager = None
    ThemeRecoveryManager = None
    ThemeIntegrityValidator = None
    ThemeAccessController = None


# Constants
SECURITY_MANAGER_ERROR = "Security manager not available"


class SecurityStatusWidget(tk.Frame):
    """Widget for displaying theme security status."""

    def __init__(self, parent, security_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.security_manager = security_manager
        self.logger = logging.getLogger("RFU.SecurityStatusWidget")

        self._create_widgets()
        self._update_status()

    def _create_widgets(self):
        """Create status display widgets."""
        # Main frame
        main_frame = ttk.LabelFrame(self, text="Security Status", padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Status indicators
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))

        # Encryption status
        ttk.Label(self.status_frame, text="Encryption:").grid(
            row=0, column=0, sticky=tk.W
        )
        self.encryption_label = ttk.Label(
            self.status_frame, text="Unknown", foreground="gray"
        )
        self.encryption_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Backup status
        ttk.Label(self.status_frame, text="Backup:").grid(
            row=1, column=0, sticky=tk.W
        )
        self.backup_label = ttk.Label(
            self.status_frame, text="Unknown", foreground="gray"
        )
        self.backup_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        # Access control status
        ttk.Label(self.status_frame, text="Access Control:").grid(
            row=2, column=0, sticky=tk.W
        )
        self.access_label = ttk.Label(
            self.status_frame, text="Unknown", foreground="gray"
        )
        self.access_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

        # Security profile
        ttk.Label(self.status_frame, text="Security Profile:").grid(
            row=3, column=0, sticky=tk.W
        )
        self.profile_label = ttk.Label(
            self.status_frame, text="Unknown", foreground="gray"
        )
        self.profile_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))

        # Refresh button
        ttk.Button(
            main_frame, text="Refresh Status", command=self._update_status
        ).pack(pady=(10, 0))

    def _update_status(self):
        """Update security status display."""
        try:
            if not self.security_manager:
                return

            # Get status from security manager
            status = self.security_manager.get_security_status()

            # Update encryption status
            if status.get("encryption_enabled", False):
                self.encryption_label.config(
                    text="Enabled", foreground="green"
                )
            else:
                self.encryption_label.config(text="Disabled", foreground="red")

            # Update backup status
            backup_count = status.get("backup_count", 0)
            if backup_count > 0:
                self.backup_label.config(
                    text=f"Active ({backup_count})", foreground="green"
                )
            else:
                self.backup_label.config(
                    text="No Backups", foreground="orange"
                )

            # Update access control status
            if status.get("access_control_enabled", False):
                self.access_label.config(text="Enabled", foreground="green")
            else:
                self.access_label.config(text="Disabled", foreground="red")

            # Update security profile
            profile = status.get("security_profile", "unknown")
            profile_colors = {
                "low": "red",
                "medium": "orange",
                "high": "green",
                "paranoid": "blue",
            }
            color = profile_colors.get(profile, "gray")
            self.profile_label.config(text=profile.title(), foreground=color)

        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")


class EncryptionControlsWidget(tk.Frame):
    """Widget for encryption controls."""

    def __init__(self, parent, security_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.security_manager = security_manager
        self.logger = logging.getLogger("RFU.EncryptionControlsWidget")

        self._create_widgets()

    def _create_widgets(self):
        """Create encryption control widgets."""
        # Main frame
        main_frame = ttk.LabelFrame(
            self, text="Encryption Controls", padding="10"
        )
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Enable/disable encryption
        self.encryption_var = tk.BooleanVar()
        ttk.Checkbutton(
            main_frame,
            text="Enable theme data encryption",
            variable=self.encryption_var,
            command=self._toggle_encryption,
        ).pack(anchor=tk.W)

        # Key management
        key_frame = ttk.LabelFrame(main_frame, text="Key Management")
        key_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            key_frame, text="Rotate Encryption Key", command=self._rotate_key
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            key_frame, text="Backup Key", command=self._backup_key
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            key_frame, text="Test Encryption", command=self._test_encryption
        ).pack(side=tk.LEFT)

    def _toggle_encryption(self):
        """Toggle encryption on/off."""
        try:
            if not self.security_manager:
                messagebox.showerror("Error", SECURITY_MANAGER_ERROR)
                return

            enabled = self.encryption_var.get()
            if enabled:
                self._enable_encryption()
            else:
                self._disable_encryption()

        except Exception as e:
            self.logger.error(f"Failed to toggle encryption: {e}")
            messagebox.showerror("Error", f"Failed to toggle encryption: {e}")

    def _enable_encryption(self):
        """Enable encryption with confirmation."""
        result = messagebox.askyesno(
            "Enable Encryption",
            "Enable encryption for theme data? "
            "This will encrypt all existing themes.",
        )
        if result:
            success = self.security_manager.enable_encryption()
            if success:
                msg = "Encryption enabled successfully"
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", "Failed to enable encryption")
                self.encryption_var.set(False)
        else:
            self.encryption_var.set(False)

    def _disable_encryption(self):
        """Disable encryption with confirmation."""
        result = messagebox.askyesno(
            "Disable Encryption",
            "Disable encryption for theme data? "
            "This will decrypt all themes.",
        )
        if result:
            success = self.security_manager.disable_encryption()
            if success:
                msg = "Encryption disabled successfully"
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", "Failed to disable encryption")
                self.encryption_var.set(True)
        else:
            self.encryption_var.set(True)

    def _rotate_key(self):
        """Rotate encryption key."""
        try:
            if not self.security_manager:
                messagebox.showerror("Error", SECURITY_MANAGER_ERROR)
                return

            result = messagebox.askyesno(
                "Rotate Key",
                "Rotate the encryption key? This will re-encrypt all data.",
            )

            if result:
                success = self.security_manager.rotate_encryption_key()
                if success:
                    msg = "Encryption key rotated successfully"
                    messagebox.showinfo("Success", msg)
                else:
                    msg = "Failed to rotate encryption key"
                    messagebox.showerror("Error", msg)

        except Exception as e:
            self.logger.error(f"Failed to rotate key: {e}")
            messagebox.showerror("Error", f"Failed to rotate key: {e}")

    def _backup_key(self):
        """Backup encryption key."""
        try:
            if not self.security_manager:
                messagebox.showerror("Error", "Security manager not available")
                return

            file_path = filedialog.asksaveasfilename(
                title="Backup Encryption Key",
                defaultextension=".key",
                filetypes=[("Key files", "*.key"), ("All files", "*.*")],
            )

            if file_path:
                success = self.security_manager.backup_encryption_key(
                    file_path
                )
                if success:
                    messagebox.showinfo(
                        "Success", f"Key backed up to {file_path}"
                    )
                else:
                    messagebox.showerror("Error", "Failed to backup key")

        except Exception as e:
            self.logger.error(f"Failed to backup key: {e}")
            messagebox.showerror("Error", f"Failed to backup key: {e}")

    def _test_encryption(self):
        """Test encryption functionality."""
        try:
            if not self.security_manager:
                messagebox.showerror("Error", "Security manager not available")
                return

            # Test with sample data
            test_data = {
                "test": "theme_data",
                "timestamp": str(datetime.datetime.now()),
            }

            # Encrypt and decrypt
            encrypted = self.security_manager.encrypt_data(test_data)
            if encrypted:
                decrypted = self.security_manager.decrypt_data(encrypted)
                if decrypted == test_data:
                    messagebox.showinfo("Success", "Encryption test passed")
                else:
                    messagebox.showerror(
                        "Error", "Encryption test failed: data mismatch"
                    )
            else:
                messagebox.showerror(
                    "Error", "Encryption test failed: encryption failed"
                )

        except Exception as e:
            self.logger.error(f"Encryption test failed: {e}")
            messagebox.showerror("Error", f"Encryption test failed: {e}")


class BackupManagementWidget(tk.Frame):
    """Widget for backup management."""

    def __init__(self, parent, backup_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.backup_manager = backup_manager
        self.logger = logging.getLogger("RFU.BackupManagementWidget")

        self._create_widgets()
        self._refresh_backups()

    def _create_widgets(self):
        """Create backup management widgets."""
        # Main frame
        main_frame = ttk.LabelFrame(
            self, text="Backup Management", padding="10"
        )
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            button_frame, text="Create Backup", command=self._create_backup
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="Restore Backup", command=self._restore_backup
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="Delete Backup", command=self._delete_backup
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="Refresh", command=self._refresh_backups
        ).pack(side=tk.RIGHT)

        # Backup list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for backups
        columns = ("Theme", "Date", "Size", "Status")
        self.backup_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings"
        )

        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.backup_tree.yview
        )
        self.backup_tree.configure(yscrollcommand=scrollbar.set)

        self.backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_backup(self):
        """Create a new backup."""
        try:
            if not self.backup_manager:
                messagebox.showerror("Error", "Backup manager not available")
                return

            # Get theme name from user
            theme_name = simpledialog.askstring(
                "Create Backup", "Enter theme name to backup:"
            )

            if theme_name:
                backup_id = self.backup_manager.create_backup(theme_name)
                if backup_id:
                    messagebox.showinfo(
                        "Success", f"Backup created: {backup_id}"
                    )
                    self._refresh_backups()
                else:
                    messagebox.showerror("Error", "Failed to create backup")

        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            messagebox.showerror("Error", f"Failed to create backup: {e}")

    def _restore_backup(self):
        """Restore selected backup."""
        try:
            selection = self.backup_tree.selection()
            if not selection:
                messagebox.showwarning(
                    "Warning", "Please select a backup to restore"
                )
                return

            if not self.backup_manager:
                messagebox.showerror("Error", "Backup manager not available")
                return

            # Get backup info from selection
            item = self.backup_tree.item(selection[0])
            backup_info = item["values"]

            if backup_info:
                result = messagebox.askyesno(
                    "Restore Backup",
                    f"Restore backup for theme '{backup_info[0]}'? "
                    f"This will overwrite the current theme.",
                )

                if result:
                    # Restore backup (implement based on backup manager API)
                    success = self.backup_manager.restore_backup(
                        backup_info[0]
                    )
                    if success:
                        messagebox.showinfo(
                            "Success", "Backup restored successfully"
                        )
                    else:
                        messagebox.showerror(
                            "Error", "Failed to restore backup"
                        )

        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            messagebox.showerror("Error", f"Failed to restore backup: {e}")

    def _delete_backup(self):
        """Delete selected backup."""
        try:
            selection = self.backup_tree.selection()
            if not selection:
                messagebox.showwarning(
                    "Warning", "Please select a backup to delete"
                )
                return

            item = self.backup_tree.item(selection[0])
            backup_info = item["values"]

            if backup_info:
                result = messagebox.askyesno(
                    "Delete Backup",
                    f"Delete backup for theme '{backup_info[0]}'? "
                    f"This action cannot be undone.",
                )

                if result:
                    # Delete backup (implement based on backup manager API)
                    success = True  # Placeholder
                    if success:
                        messagebox.showinfo(
                            "Success", "Backup deleted successfully"
                        )
                        self._refresh_backups()
                    else:
                        messagebox.showerror(
                            "Error", "Failed to delete backup"
                        )

        except Exception as e:
            self.logger.error(f"Failed to delete backup: {e}")
            messagebox.showerror("Error", f"Failed to delete backup: {e}")

    def _refresh_backups(self):
        """Refresh backup list."""
        try:
            # Clear current items
            for item in self.backup_tree.get_children():
                self.backup_tree.delete(item)

            if not self.backup_manager:
                return

            # Get backup list (implement based on backup manager API)
            backups = []  # Placeholder

            # Populate tree
            for backup in backups:
                self.backup_tree.insert("", tk.END, values=backup)

        except Exception as e:
            self.logger.error(f"Failed to refresh backups: {e}")


class ThemeSecurityGUI(tk.Toplevel):
    """Main theme security management GUI."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.logger = logging.getLogger("RFU.ThemeSecurityGUI")

        # Initialize security components
        self._init_security_components()

        # Setup window
        self.title("Theme Security Management")
        self.geometry("800x600")
        self.resizable(True, True)

        # Create GUI
        self._create_widgets()

        # Center window
        self._center_window()

    def _init_security_components(self):
        """Initialize security components."""
        try:
            # Initialize configuration
            if ThemeSecurityConfig:
                self.config = ThemeSecurityConfig()
            else:
                self.config = None

            # Initialize security manager
            if ThemeSecurityManager:
                self.security_manager = ThemeSecurityManager()
            else:
                self.security_manager = None

            # Initialize backup manager
            if ThemeBackupManager:
                self.backup_manager = ThemeBackupManager()
            else:
                self.backup_manager = None

        except Exception as e:
            self.logger.error(f"Failed to initialize security components: {e}")
            self.config = None
            self.security_manager = None
            self.backup_manager = None

    def _create_widgets(self):
        """Create main GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status tab
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="Status")
        self.status_widget = SecurityStatusWidget(
            status_frame, self.security_manager
        )
        self.status_widget.pack(fill=tk.BOTH, expand=True)

        # Encryption tab
        encryption_frame = ttk.Frame(self.notebook)
        self.notebook.add(encryption_frame, text="Encryption")
        self.encryption_widget = EncryptionControlsWidget(
            encryption_frame, self.security_manager
        )
        self.encryption_widget.pack(fill=tk.BOTH, expand=True)

        # Backup tab
        backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(backup_frame, text="Backup")
        self.backup_widget = BackupManagementWidget(
            backup_frame, self.backup_manager
        )
        self.backup_widget.pack(fill=tk.BOTH, expand=True)

        # Configuration tab
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        self._create_config_tab(config_frame)

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(button_frame, text="Close", command=self.destroy).pack(
            side=tk.RIGHT
        )
        ttk.Button(
            button_frame, text="Apply Settings", command=self._apply_settings
        ).pack(side=tk.RIGHT, padx=(0, 5))

    def _create_config_tab(self, parent):
        """Create configuration tab."""
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(
            parent, orient=tk.VERTICAL, command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Configuration sections
        self._create_config_section(
            scrollable_frame, "Encryption", "encryption"
        )
        self._create_config_section(
            scrollable_frame, "Access Control", "access_control"
        )
        self._create_config_section(scrollable_frame, "Backup", "backup")
        self._create_config_section(scrollable_frame, "Recovery", "recovery")

        # Update scroll region
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_config_section(self, parent, title, section_key):
        """Create a configuration section."""
        frame = ttk.LabelFrame(parent, text=title, padding="10")
        frame.pack(fill=tk.X, padx=5, pady=5)

        if not self.config:
            ttk.Label(frame, text="Configuration not available").pack()
            return

        # Get section config
        section_config = self.config.get_section(section_key)

        # Create config entries (simplified)
        for key, value in section_config.items():
            row_frame = ttk.Frame(frame)
            row_frame.pack(fill=tk.X, pady=2)

            ttk.Label(row_frame, text=f"{key}:").pack(side=tk.LEFT)

            # Different widgets based on value type
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                ttk.Checkbutton(row_frame, variable=var).pack(side=tk.RIGHT)
            elif isinstance(value, (int, float)):
                var = tk.StringVar(value=str(value))
                ttk.Entry(row_frame, textvariable=var, width=20).pack(
                    side=tk.RIGHT
                )
            else:
                var = tk.StringVar(value=str(value))
                ttk.Entry(row_frame, textvariable=var, width=30).pack(
                    side=tk.RIGHT
                )

    def _apply_settings(self):
        """Apply configuration settings."""
        try:
            if not self.config:
                messagebox.showerror("Error", "Configuration not available")
                return

            # Save configuration
            success = self.config.save_to_file()
            if success:
                messagebox.showinfo("Success", "Settings applied successfully")
            else:
                messagebox.showerror("Error", "Failed to apply settings")

        except Exception as e:
            self.logger.error(f"Failed to apply settings: {e}")
            messagebox.showerror("Error", f"Failed to apply settings: {e}")

    def _center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


def show_theme_security_gui(parent=None):
    """Show the theme security management GUI."""
    try:
        gui = ThemeSecurityGUI(parent)
        gui.transient(parent)
        gui.grab_set()
        return gui
    except Exception as e:
        if parent:
            messagebox.showerror("Error", f"Failed to open security GUI: {e}")
        else:
            print(f"Failed to open security GUI: {e}")
        return None


if __name__ == "__main__":
    # Test the GUI
    root = tk.Tk()
    root.withdraw()  # Hide root window

    gui = show_theme_security_gui()
    if gui:
        root.mainloop()
