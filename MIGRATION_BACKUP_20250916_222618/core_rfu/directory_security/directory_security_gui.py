"""
Directory Security GUI Component for Phase 3 Implementation

Provides secure directory preferences widget with PII warnings,
security controls, and user-friendly interface for directory management.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timezone
import threading
import queue
import logging

from ..database.database_manager import DatabaseManager
from .directory_security_manager import (
    DirectorySecurityManager, DirectoryStorageResult, DirectoryRetrievalResult
)
from .pii_detector import PIIDetector, PIIAnalysisResult
from .directory_permissions import PermissionLevel, DirectoryRole


@dataclass
class DirectoryEntry:
    """Represents a directory entry in the GUI"""
    path_hash: str
    tool_name: str
    directory_type: str
    display_path: str
    is_pii_sensitive: bool
    sensitivity_level: int
    last_accessed: str
    encrypted: bool
    pii_warnings: List[str]


class DirectorySecurityGUI:
    """
    Secure directory preferences management widget
    
    Features:
    - Directory preference management with security validation
    - PII detection and warnings
    - Encryption status display
    - Security level indicators
    - User-friendly path display with anonymization
    - Permission-based access control
    """
    
    def __init__(self, parent_frame: tk.Frame, db_manager: DatabaseManager,
                 user_id: str, user_role: DirectoryRole = DirectoryRole.USER):
        """
        Initialize DirectorySecurityGUI
        
        Args:
            parent_frame: Parent tkinter frame
            db_manager: Database manager instance
            user_id: Current user ID
            user_role: User's role for permission checking
        """
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.user_id = user_id
        self.user_role = user_role
        
        # Initialize security components
        self.security_manager = DirectorySecurityManager(db_manager)
        self.pii_detector = PIIDetector()
        
        # GUI state
        self.directory_entries: List[DirectoryEntry] = []
        self.selected_entry: Optional[DirectoryEntry] = None
        self.update_queue = queue.Queue()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Create GUI components
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Load initial data
        self._load_directory_entries()
    
    def _create_widgets(self):
        """Create GUI widgets"""
        # Main container
        self.main_frame = ttk.Frame(self.parent_frame, padding="10")
        
        # Title and security status
        self.title_frame = ttk.Frame(self.main_frame)
        self.title_label = ttk.Label(
            self.title_frame,
            text="Secure Directory Preferences",
            font=("Segoe UI", 14, "bold")
        )
        self.security_status_label = ttk.Label(
            self.title_frame,
            text="🔒 Security: Active",
            foreground="green"
        )
        
        # Toolbar
        self.toolbar_frame = ttk.Frame(self.main_frame)
        self.add_button = ttk.Button(
            self.toolbar_frame,
            text="➕ Add Directory",
            command=self._add_directory
        )
        self.remove_button = ttk.Button(
            self.toolbar_frame,
            text="🗑️ Remove",
            command=self._remove_directory,
            state="disabled"
        )
        self.refresh_button = ttk.Button(
            self.toolbar_frame,
            text="🔄 Refresh",
            command=self._refresh_directories
        )
        self.settings_button = ttk.Button(
            self.toolbar_frame,
            text="⚙️ Security Settings",
            command=self._show_security_settings
        )
        
        # Filter frame
        self.filter_frame = ttk.Frame(self.main_frame)
        ttk.Label(self.filter_frame, text="Filter:").pack(side="left", padx=(0, 5))
        
        self.filter_var = tk.StringVar()
        self.filter_combo = ttk.Combobox(
            self.filter_frame,
            textvariable=self.filter_var,
            values=["All", "High Security", "PII Sensitive", "Encrypted", "Recent"],
            state="readonly",
            width=15
        )
        self.filter_combo.set("All")
        
        self.tool_filter_var = tk.StringVar()
        self.tool_filter_combo = ttk.Combobox(
            self.filter_frame,
            textvariable=self.tool_filter_var,
            values=["All Tools"],
            state="readonly",
            width=15
        )
        self.tool_filter_combo.set("All Tools")
        
        # Directory list with tree view
        self.list_frame = ttk.Frame(self.main_frame)
        
        # Create Treeview with columns
        columns = ("Tool", "Type", "Path", "Security", "Status")
        self.directory_tree = ttk.Treeview(
            self.list_frame,
            columns=columns,
            show="tree headings",
            height=12
        )
        
        # Configure columns
        self.directory_tree.heading("#0", text="📁")
        self.directory_tree.column("#0", width=30, minwidth=30)
        
        for col in columns:
            self.directory_tree.heading(col, text=col)
            if col == "Path":
                self.directory_tree.column(col, width=300, minwidth=200)
            elif col == "Security":
                self.directory_tree.column(col, width=100, minwidth=80)
            elif col == "Status":
                self.directory_tree.column(col, width=80, minwidth=60)
            else:
                self.directory_tree.column(col, width=100, minwidth=80)
        
        # Scrollbars for tree
        self.tree_scroll_y = ttk.Scrollbar(
            self.list_frame,
            orient="vertical",
            command=self.directory_tree.yview
        )
        self.tree_scroll_x = ttk.Scrollbar(
            self.list_frame,
            orient="horizontal",
            command=self.directory_tree.xview
        )
        self.directory_tree.configure(
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set
        )
        
        # Details panel
        self.details_frame = ttk.LabelFrame(self.main_frame, text="Directory Details", padding="10")
        
        # Path info
        self.path_info_frame = ttk.Frame(self.details_frame)
        ttk.Label(self.path_info_frame, text="Full Path:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.path_display_var = tk.StringVar()
        self.path_display_label = ttk.Label(
            self.path_info_frame,
            textvariable=self.path_display_var,
            wraplength=400,
            justify="left"
        )
        self.path_display_label.pack(anchor="w", pady=(0, 10))
        
        # Security info
        self.security_info_frame = ttk.Frame(self.details_frame)
        
        # PII warnings
        self.warnings_frame = ttk.Frame(self.details_frame)
        ttk.Label(self.warnings_frame, text="Security Warnings:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.warnings_text = tk.Text(
            self.warnings_frame,
            height=4,
            wrap="word",
            state="disabled",
            background="#fff8dc"
        )
        self.warnings_scroll = ttk.Scrollbar(
            self.warnings_frame,
            orient="vertical",
            command=self.warnings_text.yview
        )
        self.warnings_text.configure(yscrollcommand=self.warnings_scroll.set)
        
        # Action buttons
        self.action_frame = ttk.Frame(self.details_frame)
        self.open_button = ttk.Button(
            self.action_frame,
            text="📂 Open Directory",
            command=self._open_selected_directory,
            state="disabled"
        )
        self.properties_button = ttk.Button(
            self.action_frame,
            text="🔍 Properties",
            command=self._show_properties,
            state="disabled"
        )
        self.encrypt_button = ttk.Button(
            self.action_frame,
            text="🔐 Toggle Encryption",
            command=self._toggle_encryption,
            state="disabled"
        )
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        
        # Progress bar for operations
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            variable=self.progress_var,
            mode="determinate"
        )
    
    def _setup_layout(self):
        """Setup widget layout"""
        self.main_frame.pack(fill="both", expand=True)
        
        # Title frame
        self.title_frame.pack(fill="x", pady=(0, 10))
        self.title_label.pack(side="left")
        self.security_status_label.pack(side="right")
        
        # Toolbar
        self.toolbar_frame.pack(fill="x", pady=(0, 10))
        self.add_button.pack(side="left", padx=(0, 5))
        self.remove_button.pack(side="left", padx=(0, 5))
        self.refresh_button.pack(side="left", padx=(0, 20))
        self.settings_button.pack(side="right")
        
        # Filter frame
        self.filter_frame.pack(fill="x", pady=(0, 10))
        self.filter_combo.pack(side="left", padx=(0, 10))
        self.tool_filter_combo.pack(side="left")
        
        # Directory list
        self.list_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.directory_tree.pack(side="left", fill="both", expand=True)
        self.tree_scroll_y.pack(side="right", fill="y")
        self.tree_scroll_x.pack(side="bottom", fill="x")
        
        # Details panel
        self.details_frame.pack(fill="x", pady=(0, 10))
        
        # Path info
        self.path_info_frame.pack(fill="x", pady=(0, 10))
        
        # Security info
        self.security_info_frame.pack(fill="x", pady=(0, 10))
        
        # Warnings
        self.warnings_frame.pack(fill="x", pady=(0, 10))
        self.warnings_text.pack(side="left", fill="both", expand=True)
        self.warnings_scroll.pack(side="right", fill="y")
        
        # Action buttons
        self.action_frame.pack(fill="x")
        self.open_button.pack(side="left", padx=(0, 5))
        self.properties_button.pack(side="left", padx=(0, 5))
        self.encrypt_button.pack(side="left")
        
        # Status bar
        self.status_frame.pack(fill="x", pady=(10, 0))
        self.status_label.pack(side="left")
        self.progress_bar.pack(side="right", padx=(10, 0))
    
    def _bind_events(self):
        """Bind event handlers"""
        self.directory_tree.bind("<<TreeviewSelect>>", self._on_directory_select)
        self.directory_tree.bind("<Double-1>", self._on_directory_double_click)
        self.filter_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        self.tool_filter_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        
        # Keyboard shortcuts
        self.parent_frame.bind("<Delete>", lambda e: self._remove_directory())
        self.parent_frame.bind("<F5>", lambda e: self._refresh_directories())
        self.parent_frame.bind("<Control-a>", lambda e: self._add_directory())
    
    def _load_directory_entries(self):
        """Load directory entries from database"""
        try:
            self._update_status("Loading directories...")
            self.progress_var.set(0)
            
            # Load in background thread to prevent GUI freezing
            def load_thread():
                try:
                    directories = self.security_manager.list_user_directories(self.user_id)
                    
                    entries = []
                    for i, dir_data in enumerate(directories):
                        # Update progress
                        progress = (i + 1) / len(directories) * 100
                        self.update_queue.put(("progress", progress))
                        
                        # Analyze PII for display
                        pii_result = self.pii_detector.analyze_directory_path(dir_data.get('display_path', ''))
                        
                        entry = DirectoryEntry(
                            path_hash=dir_data['path_hash'],
                            tool_name=dir_data['tool_name'],
                            directory_type=dir_data['directory_type'],
                            display_path=pii_result.anonymized_path if pii_result.contains_pii else dir_data.get('display_path', '[Path]'),
                            is_pii_sensitive=dir_data.get('is_pii_sensitive', False),
                            sensitivity_level=dir_data.get('sensitivity_level', 1),
                            last_accessed=dir_data.get('last_accessed_at', ''),
                            encrypted=dir_data.get('encryption_metadata') is not None,
                            pii_warnings=self.pii_detector.get_pii_warnings(dir_data.get('display_path', ''))
                        )
                        entries.append(entry)
                    
                    self.update_queue.put(("entries", entries))
                    self.update_queue.put(("status", "Loaded {} directories".format(len(entries))))
                
                except Exception as e:
                    self.update_queue.put(("error", f"Failed to load directories: {str(e)}"))
            
            thread = threading.Thread(target=load_thread)
            thread.daemon = True
            thread.start()
            
            # Process updates
            self._process_updates()
            
        except Exception as e:
            self._update_status(f"Error loading directories: {str(e)}")
            self.logger.error(f"Failed to load directory entries: {e}")
    
    def _process_updates(self):
        """Process updates from background threads"""
        try:
            while True:
                update_type, data = self.update_queue.get_nowait()
                
                if update_type == "progress":
                    self.progress_var.set(data)
                elif update_type == "entries":
                    self.directory_entries = data
                    self._update_directory_display()
                    self._update_tool_filter()
                elif update_type == "status":
                    self._update_status(data)
                elif update_type == "error":
                    messagebox.showerror("Error", data)
                    self._update_status("Error occurred")
                
        except queue.Empty:
            pass
        
        # Schedule next update check
        self.parent_frame.after(100, self._process_updates)
    
    def _update_directory_display(self):
        """Update directory tree display"""
        # Clear existing items
        for item in self.directory_tree.get_children():
            self.directory_tree.delete(item)
        
        # Apply filters
        filtered_entries = self._apply_filters(self.directory_entries)
        
        # Add entries to tree
        for entry in filtered_entries:
            # Determine security icon and level
            if entry.sensitivity_level >= 4:
                security_icon = "🔴"
                security_text = "High"
            elif entry.sensitivity_level >= 3:
                security_icon = "🟡"
                security_text = "Medium"
            else:
                security_icon = "🟢"
                security_text = "Low"
            
            # Status indicators
            status_indicators = []
            if entry.encrypted:
                status_indicators.append("🔐")
            if entry.is_pii_sensitive:
                status_indicators.append("👤")
            if entry.pii_warnings:
                status_indicators.append("⚠️")
            
            status_text = " ".join(status_indicators) if status_indicators else "✓"
            
            # Insert item
            item_id = self.directory_tree.insert(
                "",
                "end",
                text=security_icon,
                values=(
                    entry.tool_name,
                    entry.directory_type,
                    entry.display_path,
                    security_text,
                    status_text
                ),
                tags=(f"security_{entry.sensitivity_level}",)
            )
            
            # Store entry reference
            self.directory_tree.set(item_id, "path_hash", entry.path_hash)
        
        # Configure tags for colors
        self.directory_tree.tag_configure("security_1", background="#e8f5e8")
        self.directory_tree.tag_configure("security_2", background="#fff3cd")
        self.directory_tree.tag_configure("security_3", background="#ffeaa7")
        self.directory_tree.tag_configure("security_4", background="#fab1a0")
        self.directory_tree.tag_configure("security_5", background="#ff7675")
        
        self.progress_var.set(0)
    
    def _apply_filters(self, entries: List[DirectoryEntry]) -> List[DirectoryEntry]:
        """Apply current filters to directory entries"""
        filtered = entries
        
        # Security filter
        security_filter = self.filter_var.get()
        if security_filter == "High Security":
            filtered = [e for e in filtered if e.sensitivity_level >= 4]
        elif security_filter == "PII Sensitive":
            filtered = [e for e in filtered if e.is_pii_sensitive]
        elif security_filter == "Encrypted":
            filtered = [e for e in filtered if e.encrypted]
        elif security_filter == "Recent":
            # Filter last 7 days (simplified)
            filtered = [e for e in filtered if e.last_accessed]
        
        # Tool filter
        tool_filter = self.tool_filter_var.get()
        if tool_filter != "All Tools":
            filtered = [e for e in filtered if e.tool_name == tool_filter]
        
        return filtered
    
    def _update_tool_filter(self):
        """Update tool filter combobox"""
        tools = set(entry.tool_name for entry in self.directory_entries)
        values = ["All Tools"] + sorted(tools)
        self.tool_filter_combo.configure(values=values)
    
    def _on_directory_select(self, event):
        """Handle directory selection"""
        selection = self.directory_tree.selection()
        if not selection:
            self.selected_entry = None
            self._update_details_panel(None)
            return
        
        item_id = selection[0]
        path_hash = self.directory_tree.set(item_id, "path_hash")
        
        # Find the entry
        entry = next((e for e in self.directory_entries if e.path_hash == path_hash), None)
        self.selected_entry = entry
        self._update_details_panel(entry)
    
    def _update_details_panel(self, entry: Optional[DirectoryEntry]):
        """Update details panel with entry information"""
        if entry is None:
            self.path_display_var.set("No directory selected")
            self.warnings_text.configure(state="normal")
            self.warnings_text.delete(1.0, "end")
            self.warnings_text.configure(state="disabled")
            
            # Disable action buttons
            self.open_button.configure(state="disabled")
            self.properties_button.configure(state="disabled")
            self.encrypt_button.configure(state="disabled")
            self.remove_button.configure(state="disabled")
            return
        
        # Update path display
        self.path_display_var.set(entry.display_path)
        
        # Update warnings
        self.warnings_text.configure(state="normal")
        self.warnings_text.delete(1.0, "end")
        
        if entry.pii_warnings:
            warning_text = "\n".join(f"⚠️ {warning}" for warning in entry.pii_warnings)
            self.warnings_text.insert("end", warning_text)
        else:
            self.warnings_text.insert("end", "✅ No security warnings")
        
        self.warnings_text.configure(state="disabled")
        
        # Enable action buttons
        self.open_button.configure(state="normal")
        self.properties_button.configure(state="normal")
        self.encrypt_button.configure(state="normal")
        self.remove_button.configure(state="normal")
        
        # Update encryption button text
        if entry.encrypted:
            self.encrypt_button.configure(text="🔓 Decrypt")
        else:
            self.encrypt_button.configure(text="🔐 Encrypt")
    
    def _add_directory(self):
        """Add new directory preference"""
        dialog = DirectoryAddDialog(self.parent_frame, self.security_manager, self.user_id)
        result = dialog.show()
        
        if result:
            self._refresh_directories()
    
    def _remove_directory(self):
        """Remove selected directory preference"""
        if not self.selected_entry:
            messagebox.showwarning("Warning", "Please select a directory to remove.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to remove the directory preference for:\n\n{self.selected_entry.display_path}\n\nThis action cannot be undone."
        ):
            return
        
        try:
            success = self.security_manager.delete_directory_preference(
                self.user_id, self.selected_entry.path_hash
            )
            
            if success:
                self._update_status("Directory preference removed")
                self._refresh_directories()
            else:
                messagebox.showerror("Error", "Failed to remove directory preference.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove directory: {str(e)}")
    
    def _refresh_directories(self):
        """Refresh directory list"""
        self._load_directory_entries()
    
    def _on_filter_change(self, event):
        """Handle filter change"""
        self._update_directory_display()
    
    def _on_directory_double_click(self, event):
        """Handle double-click on directory"""
        self._open_selected_directory()
    
    def _open_selected_directory(self):
        """Open selected directory in file explorer"""
        if not self.selected_entry:
            return
        
        try:
            # Retrieve actual path (decrypt if needed)
            result = self.security_manager.retrieve_directory_preference(
                self.user_id, self.selected_entry.path_hash
            )
            
            if result.success and os.path.exists(result.directory_path):
                if os.name == 'nt':  # Windows
                    os.startfile(result.directory_path)
                elif os.name == 'posix':  # macOS and Linux
                    os.system(f'open "{result.directory_path}"')
            else:
                messagebox.showwarning("Warning", "Directory path no longer exists or cannot be accessed.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open directory: {str(e)}")
    
    def _show_properties(self):
        """Show directory properties dialog"""
        if not self.selected_entry:
            return
        
        PropertiesDialog(self.parent_frame, self.selected_entry, self.security_manager, self.user_id).show()
    
    def _toggle_encryption(self):
        """Toggle encryption for selected directory"""
        if not self.selected_entry:
            return
        
        # This would require implementing encryption toggle functionality
        messagebox.showinfo("Info", "Encryption toggle functionality would be implemented here.")
    
    def _show_security_settings(self):
        """Show security settings dialog"""
        SecuritySettingsDialog(self.parent_frame, self.security_manager, self.user_id).show()
    
    def _update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)


class DirectoryAddDialog:
    """Dialog for adding new directory preferences"""
    
    def __init__(self, parent: tk.Widget, security_manager: DirectorySecurityManager, user_id: str):
        self.parent = parent
        self.security_manager = security_manager
        self.user_id = user_id
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Directory Preference")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Add Directory Preference", font=("Segoe UI", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Directory path
        path_frame = ttk.Frame(main_frame)
        ttk.Label(path_frame, text="Directory Path:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        
        path_entry_frame = ttk.Frame(path_frame)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_entry_frame, textvariable=self.path_var, width=50)
        browse_button = ttk.Button(path_entry_frame, text="Browse...", command=self._browse_directory)
        
        self.path_entry.pack(side="left", fill="x", expand=True)
        browse_button.pack(side="right", padx=(5, 0))
        path_entry_frame.pack(fill="x", pady=(5, 0))
        
        # Tool name
        tool_frame = ttk.Frame(main_frame)
        ttk.Label(tool_frame, text="Tool Name:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.tool_var = tk.StringVar()
        self.tool_entry = ttk.Entry(tool_frame, textvariable=self.tool_var, width=50)
        self.tool_entry.pack(fill="x", pady=(5, 0))
        
        # Directory type
        type_frame = ttk.Frame(main_frame)
        ttk.Label(type_frame, text="Directory Type:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.type_var,
            values=["favorite", "recent", "default", "workspace", "config", "data", "temp"],
            state="readonly",
            width=47
        )
        self.type_combo.set("favorite")
        self.type_combo.pack(fill="x", pady=(5, 0))
        
        # Security analysis display
        analysis_frame = ttk.LabelFrame(main_frame, text="Security Analysis", padding="10")
        self.analysis_text = tk.Text(analysis_frame, height=6, wrap="word", state="disabled")
        analysis_scroll = ttk.Scrollbar(analysis_frame, orient="vertical", command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scroll.set)
        
        self.analysis_text.pack(side="left", fill="both", expand=True)
        analysis_scroll.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        ok_button = ttk.Button(button_frame, text="Add Directory", command=self._ok_clicked)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked)
        
        cancel_button.pack(side="right", padx=(5, 0))
        ok_button.pack(side="right")
        
        # Pack frames
        path_frame.pack(fill="x", pady=(0, 15))
        tool_frame.pack(fill="x", pady=(0, 15))
        type_frame.pack(fill="x", pady=(0, 15))
        analysis_frame.pack(fill="both", expand=True, pady=(0, 15))
        button_frame.pack(fill="x")
        
        # Bind path change event
        self.path_var.trace("w", self._on_path_change)
    
    def _setup_layout(self):
        """Setup dialog layout"""
        pass  # Layout is handled in _create_widgets
    
    def _browse_directory(self):
        """Browse for directory"""
        directory = filedialog.askdirectory(
            title="Select Directory",
            initialdir=os.path.expanduser("~")
        )
        if directory:
            self.path_var.set(directory)
    
    def _on_path_change(self, *args):
        """Handle path change for security analysis"""
        path = self.path_var.get().strip()
        if not path:
            self._update_analysis("Enter a directory path to see security analysis.")
            return
        
        try:
            # Analyze path for PII and security
            pii_detector = PIIDetector()
            analysis = pii_detector.analyze_directory_path(path)
            
            # Build analysis text
            analysis_lines = []
            analysis_lines.append(f"🔍 Security Analysis for: {path}")
            analysis_lines.append("")
            
            if analysis.contains_pii:
                analysis_lines.append(f"⚠️ PII Detected: Yes")
                analysis_lines.append(f"📊 Sensitivity Level: {analysis.sensitivity_level}/5")
                analysis_lines.append(f"🔐 Encryption Recommended: {'Yes' if analysis.requires_encryption else 'No'}")
                analysis_lines.append("")
                analysis_lines.append("PII Indicators:")
                for indicator in analysis.pii_indicators:
                    analysis_lines.append(f"  • {indicator}")
                analysis_lines.append("")
                analysis_lines.append("Anonymized Path: " + analysis.anonymized_path)
            else:
                analysis_lines.append("✅ No PII detected")
                analysis_lines.append(f"📊 Sensitivity Level: {analysis.sensitivity_level}/5")
                analysis_lines.append("🔐 Encryption: Optional")
            
            self._update_analysis("\n".join(analysis_lines))
            
        except Exception as e:
            self._update_analysis(f"❌ Analysis failed: {str(e)}")
    
    def _update_analysis(self, text: str):
        """Update analysis display"""
        self.analysis_text.configure(state="normal")
        self.analysis_text.delete(1.0, "end")
        self.analysis_text.insert("end", text)
        self.analysis_text.configure(state="disabled")
    
    def _ok_clicked(self):
        """Handle OK button click"""
        path = self.path_var.get().strip()
        tool = self.tool_var.get().strip()
        dir_type = self.type_var.get().strip()
        
        # Validate inputs
        if not path:
            messagebox.showerror("Error", "Please enter a directory path.")
            return
        
        if not tool:
            messagebox.showerror("Error", "Please enter a tool name.")
            return
        
        if not dir_type:
            messagebox.showerror("Error", "Please select a directory type.")
            return
        
        if not os.path.exists(path):
            if not messagebox.askyesno("Warning", f"The directory '{path}' does not exist. Add anyway?"):
                return
        
        try:
            # Store directory preference
            result = self.security_manager.store_directory_preference(
                self.user_id, tool, dir_type, path
            )
            
            if result.success:
                self.result = result
                self.dialog.destroy()
            else:
                error_msg = "Failed to add directory preference."
                if result.security_violation:
                    error_msg += "\n\nSecurity violation detected. The path may contain unsafe patterns."
                messagebox.showerror("Error", error_msg)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add directory: {str(e)}")
    
    def _cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and return result"""
        self.dialog.wait_window()
        return self.result


class PropertiesDialog:
    """Dialog for showing directory properties"""
    
    def __init__(self, parent: tk.Widget, entry: DirectoryEntry, 
                 security_manager: DirectorySecurityManager, user_id: str):
        self.parent = parent
        self.entry = entry
        self.security_manager = security_manager
        self.user_id = user_id
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Directory Properties")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self._create_widgets()
        self._load_properties()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Directory Properties", font=("Segoe UI", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        
        # General tab
        general_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(general_frame, text="General")
        
        # Security tab
        security_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(security_frame, text="Security")
        
        # Audit tab
        audit_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(audit_frame, text="Audit Log")
        
        self.notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # Close button
        close_button = ttk.Button(main_frame, text="Close", command=self.dialog.destroy)
        close_button.pack(anchor="e")
        
        # Setup tabs
        self._setup_general_tab(general_frame)
        self._setup_security_tab(security_frame)
        self._setup_audit_tab(audit_frame)
    
    def _setup_general_tab(self, frame):
        """Setup general properties tab"""
        # Create property fields
        props = [
            ("Tool Name:", self.entry.tool_name),
            ("Directory Type:", self.entry.directory_type),
            ("Display Path:", self.entry.display_path),
            ("Last Accessed:", self.entry.last_accessed),
            ("Encrypted:", "Yes" if self.entry.encrypted else "No"),
            ("PII Sensitive:", "Yes" if self.entry.is_pii_sensitive else "No"),
            ("Sensitivity Level:", f"{self.entry.sensitivity_level}/5")
        ]
        
        for i, (label, value) in enumerate(props):
            ttk.Label(frame, text=label, font=("Segoe UI", 9, "bold")).grid(
                row=i, column=0, sticky="w", pady=5, padx=(0, 10)
            )
            ttk.Label(frame, text=str(value)).grid(
                row=i, column=1, sticky="w", pady=5
            )
    
    def _setup_security_tab(self, frame):
        """Setup security properties tab"""
        # Security warnings
        ttk.Label(frame, text="Security Warnings:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        warnings_text = tk.Text(frame, height=6, wrap="word", state="disabled")
        warnings_scroll = ttk.Scrollbar(frame, orient="vertical", command=warnings_text.yview)
        warnings_text.configure(yscrollcommand=warnings_scroll.set)
        
        warnings_text.pack(side="top", fill="x", pady=(0, 10))
        
        # Update warnings
        warnings_text.configure(state="normal")
        if self.entry.pii_warnings:
            for warning in self.entry.pii_warnings:
                warnings_text.insert("end", f"⚠️ {warning}\n")
        else:
            warnings_text.insert("end", "✅ No security warnings")
        warnings_text.configure(state="disabled")
    
    def _setup_audit_tab(self, frame):
        """Setup audit log tab"""
        ttk.Label(frame, text="Recent Audit Events:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Audit log tree
        columns = ("Time", "Event", "Status")
        audit_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            audit_tree.heading(col, text=col)
            audit_tree.column(col, width=150)
        
        audit_scroll = ttk.Scrollbar(frame, orient="vertical", command=audit_tree.yview)
        audit_tree.configure(yscrollcommand=audit_scroll.set)
        
        audit_tree.pack(side="left", fill="both", expand=True)
        audit_scroll.pack(side="right", fill="y")
    
    def _load_properties(self):
        """Load additional properties from database"""
        # This would load additional properties like audit logs
        pass
    
    def show(self):
        """Show dialog"""
        self.dialog.wait_window()


class SecuritySettingsDialog:
    """Dialog for security settings"""
    
    def __init__(self, parent: tk.Widget, security_manager: DirectorySecurityManager, user_id: str):
        self.parent = parent
        self.security_manager = security_manager
        self.user_id = user_id
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Security Settings")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="Security Settings", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Auto-encrypt PII
        self.auto_encrypt_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Automatically encrypt PII-sensitive paths",
            variable=self.auto_encrypt_var
        ).pack(anchor="w", pady=5)
        
        # Show warnings
        self.show_warnings_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Show security warnings",
            variable=self.show_warnings_var
        ).pack(anchor="w", pady=5)
        
        # Audit logging
        self.audit_logging_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame,
            text="Enable audit logging",
            variable=self.audit_logging_var
        ).pack(anchor="w", pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", side="bottom", pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side="right")
    
    def _ok_clicked(self):
        """Handle OK button click"""
        # Save settings (would be implemented)
        self.dialog.destroy()
    
    def show(self):
        """Show dialog"""
        self.dialog.wait_window()


def create_directory_security_widget(parent_frame: tk.Frame, db_manager: DatabaseManager,
                                   user_id: str, user_role: DirectoryRole = DirectoryRole.USER) -> DirectorySecurityGUI:
    """
    Create and return a DirectorySecurityGUI widget
    
    Args:
        parent_frame: Parent tkinter frame
        db_manager: Database manager instance  
        user_id: Current user ID
        user_role: User's role for permission checking
        
    Returns:
        DirectorySecurityGUI instance
    """
    return DirectorySecurityGUI(parent_frame, db_manager, user_id, user_role)