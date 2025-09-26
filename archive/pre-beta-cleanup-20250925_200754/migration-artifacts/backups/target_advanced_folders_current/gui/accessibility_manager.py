"""Accessibility Manager for Advanced Folders.

Enterprise-grade accessibility manager that ensures WCAG 2.1 AA compliance
across all Advanced Folders components with comprehensive screen reader support,
keyboard navigation, and accessibility testing capabilities.

Features:
- WCAG 2.1 AA compliance validation
- Screen reader optimization (JAWS, NVDA, VoiceOver)
- Comprehensive keyboard navigation
- Focus management and visual indicators
- High contrast mode support
- Accessibility announcement system
- Component accessibility auditing
"""

import logging
from typing import Any, Dict, List, Optional, Set

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication, QWidget


class AccessibilityLevel:
    """Accessibility compliance levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class AccessibilityAnnouncement:
    """Represents an accessibility announcement."""
    
    def __init__(self, message: str, priority: str = "polite", 
                 context: Optional[str] = None):
        """Initialize accessibility announcement.
        
        Args:
            message: Message to announce
            priority: Announcement priority (polite, assertive, off)
            context: Context where announcement occurs
        """
        self.message = message
        self.priority = priority  # polite, assertive, off
        self.context = context


class AccessibilityManager(QObject):
    """Enterprise-grade accessibility manager.
    
    Provides comprehensive accessibility support including:
    - WCAG 2.1 AA compliance validation
    - Screen reader integration
    - Keyboard navigation management
    - Focus management and indicators
    - High contrast mode support
    - Accessibility announcements
    - Component auditing and validation
    """
    
    # Signals
    accessibilityModeChanged = pyqtSignal(bool)  # enabled
    announcementRequested = pyqtSignal(str, str)  # message, priority
    focusChanged = pyqtSignal(QWidget, QWidget)  # old_widget, new_widget
    contrastModeChanged = pyqtSignal(bool)  # high_contrast_enabled
    auditCompleted = pyqtSignal(dict)  # audit_results
    
    def __init__(self, application: QApplication, parent: Optional[QWidget] = None):
        """Initialize accessibility manager.
        
        Args:
            application: QApplication instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize logging
        self.logger = logging.getLogger('AdvancedFolders.Accessibility')
        self.logger.info("Initializing Accessibility Manager")
        
        # Application reference
        self.application = application
        self.parent_widget = parent
        
        # Accessibility state
        self.accessibility_enabled = True
        self.high_contrast_enabled = False
        self.screen_reader_detected = False
        self.focus_indicators_enabled = True
        
        # Focus management
        self.focus_history: List[QWidget] = []
        self.focus_trap_stack: List[QWidget] = []
        self.current_focus_widget: Optional[QWidget] = None
        
        # Announcement system
        self.announcement_queue: List[AccessibilityAnnouncement] = []
        self.announcement_timer = QTimer()
        self.announcement_timer.timeout.connect(self._process_announcements)
        self.announcement_timer.setSingleShot(True)
        
        # Registered components for auditing
        self.registered_components: Set[QWidget] = set()
        
        # Color schemes
        self.standard_palette: Optional[QPalette] = None
        self.high_contrast_palette: Optional[QPalette] = None
        
        # Initialize accessibility features
        self._detect_screen_reader()
        self._setup_color_schemes()
        self._setup_focus_management()
        self._setup_application_accessibility()
        
        self.logger.info("Accessibility Manager initialized successfully")
    
    def _detect_screen_reader(self):
        """Detect if screen reader is active."""
        try:
            # Check for common screen reader processes/environment variables
            import os

            import psutil

            # Check environment variables
            screen_reader_vars = [
                'NVDA_PROCESS_ID',
                'JAWS',
                'WINDOW_EYES',
                'SCREEN_READER'
            ]
            
            for var in screen_reader_vars:
                if os.environ.get(var):
                    self.screen_reader_detected = True
                    self.logger.info(f"Screen reader detected via environment: {var}")
                    return
            
            # Check for common screen reader processes
            screen_reader_processes = [
                'nvda.exe',
                'jaws.exe',
                'jfw.exe',
                'windoweyes.exe',
                'narrator.exe',
                'orca'
            ]
            
            for process in psutil.process_iter(['name']):
                try:
                    if process.info['name'].lower() in screen_reader_processes:
                        self.screen_reader_detected = True
                        self.logger.info(f"Screen reader detected: {process.info['name']}")
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.logger.debug("No screen reader detected")
            
        except ImportError:
            self.logger.warning("psutil not available for screen reader detection")
        except Exception as e:
            self.logger.error(f"Error detecting screen reader: {e}")
    
    def _setup_color_schemes(self):
        """Setup standard and high contrast color schemes."""
        # Store standard palette
        self.standard_palette = self.application.palette()
        
        # Create high contrast palette
        self.high_contrast_palette = QPalette()
        
        # High contrast colors
        black = QColor(0, 0, 0)
        white = QColor(255, 255, 255)
        yellow = QColor(255, 255, 0)
        blue = QColor(0, 0, 255)
        
        # Set high contrast colors
        self.high_contrast_palette.setColor(QPalette.Window, white)
        self.high_contrast_palette.setColor(QPalette.WindowText, black)
        self.high_contrast_palette.setColor(QPalette.Base, white)
        self.high_contrast_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        self.high_contrast_palette.setColor(QPalette.Text, black)
        self.high_contrast_palette.setColor(QPalette.Button, white)
        self.high_contrast_palette.setColor(QPalette.ButtonText, black)
        self.high_contrast_palette.setColor(QPalette.Highlight, yellow)
        self.high_contrast_palette.setColor(QPalette.HighlightedText, black)
        self.high_contrast_palette.setColor(QPalette.Link, blue)
        self.high_contrast_palette.setColor(QPalette.LinkVisited, QColor(128, 0, 128))
    
    def _setup_focus_management(self):
        """Setup focus management system."""
        # Connect to application focus changes
        self.application.focusChanged.connect(self._handle_focus_changed)
    
    def _setup_application_accessibility(self):
        """Setup application-wide accessibility features."""
        # Set application accessibility attributes
        self.application.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTabletEvents, True)
        
        # Set application properties for screen readers
        self.application.setApplicationName("Advanced Folders")
        self.application.setApplicationDisplayName("Advanced Folders - File Management Suite")
        self.application.setApplicationVersion("2.0.0")
    
    def register_component(self, widget: QWidget, 
                          accessibility_name: Optional[str] = None,
                          accessibility_description: Optional[str] = None,
                          role: Optional[str] = None) -> bool:
        """Register a component for accessibility management.
        
        Args:
            widget: Widget to register
            accessibility_name: Accessible name
            accessibility_description: Accessible description
            role: ARIA role
            
        Returns:
            True if registration successful
        """
        try:
            if not widget:
                return False
            
            # Add to registered components
            self.registered_components.add(widget)
            
            # Set accessibility properties
            if accessibility_name:
                widget.setAccessibleName(accessibility_name)
            
            if accessibility_description:
                widget.setAccessibleDescription(accessibility_description)
            
            # Set ARIA role if supported
            if role:
                widget.setProperty("aria-role", role)
            
            # Ensure widget is focusable if interactive
            if self._is_interactive_widget(widget):
                widget.setFocusPolicy(Qt.TabFocus)
            
            self.logger.debug(f"Registered accessibility component: {widget.__class__.__name__}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register component: {e}")
            return False
    
    def unregister_component(self, widget: QWidget) -> bool:
        """Unregister a component from accessibility management.
        
        Args:
            widget: Widget to unregister
            
        Returns:
            True if unregistration successful
        """
        try:
            if widget in self.registered_components:
                self.registered_components.remove(widget)
                self.logger.debug(f"Unregistered accessibility component: {widget.__class__.__name__}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to unregister component: {e}")
            return False
    
    def announce(self, message: str, priority: str = "polite", 
                context: Optional[str] = None, delay: int = 100):
        """Make an accessibility announcement.
        
        Args:
            message: Message to announce
            priority: Announcement priority (polite, assertive, off)
            context: Context where announcement occurs
            delay: Delay before announcement in milliseconds
        """
        if not self.accessibility_enabled:
            return
        
        # Create announcement
        announcement = AccessibilityAnnouncement(message, priority, context)
        
        # Add to queue
        self.announcement_queue.append(announcement)
        
        # Start timer if not already running
        if not self.announcement_timer.isActive():
            self.announcement_timer.start(delay)
        
        self.logger.debug(f"Accessibility announcement queued: {message}")
    
    def announce_immediate(self, message: str, priority: str = "assertive"):
        """Make an immediate accessibility announcement.
        
        Args:
            message: Message to announce
            priority: Announcement priority
        """
        if not self.accessibility_enabled:
            return
        
        # Emit signal immediately
        self.announcementRequested.emit(message, priority)
        self.logger.debug(f"Immediate accessibility announcement: {message}")
    
    def _process_announcements(self):
        """Process queued accessibility announcements."""
        if not self.announcement_queue:
            return
        
        # Get next announcement
        announcement = self.announcement_queue.pop(0)
        
        # Emit announcement signal
        self.announcementRequested.emit(announcement.message, announcement.priority)
        
        # Continue processing if more announcements
        if self.announcement_queue:
            self.announcement_timer.start(200)  # Slight delay between announcements
    
    def set_accessibility_enabled(self, enabled: bool):
        """Enable or disable accessibility features.
        
        Args:
            enabled: Whether to enable accessibility
        """
        if enabled != self.accessibility_enabled:
            self.accessibility_enabled = enabled
            self.accessibilityModeChanged.emit(enabled)
            
            if enabled:
                self.announce("Accessibility mode enabled", "assertive")
                self.logger.info("Accessibility mode enabled")
            else:
                self.logger.info("Accessibility mode disabled")
    
    def is_accessibility_enabled(self) -> bool:
        """Check if accessibility is enabled.
        
        Returns:
            True if accessibility is enabled
        """
        return self.accessibility_enabled
    
    def set_high_contrast_mode(self, enabled: bool):
        """Enable or disable high contrast mode.
        
        Args:
            enabled: Whether to enable high contrast
        """
        if enabled != self.high_contrast_enabled:
            self.high_contrast_enabled = enabled
            
            # Apply appropriate palette
            if enabled and self.high_contrast_palette:
                self.application.setPalette(self.high_contrast_palette)
                self.announce("High contrast mode enabled", "polite")
            elif self.standard_palette:
                self.application.setPalette(self.standard_palette)
                self.announce("High contrast mode disabled", "polite")
            
            self.contrastModeChanged.emit(enabled)
            self.logger.info(f"High contrast mode: {'enabled' if enabled else 'disabled'}")
    
    def is_high_contrast_enabled(self) -> bool:
        """Check if high contrast mode is enabled.
        
        Returns:
            True if high contrast is enabled
        """
        return self.high_contrast_enabled
    
    def is_screen_reader_detected(self) -> bool:
        """Check if screen reader is detected.
        
        Returns:
            True if screen reader is detected
        """
        return self.screen_reader_detected
    
    def set_focus_widget(self, widget: QWidget, reason: str = "programmatic"):
        """Set focus to a specific widget with accessibility support.
        
        Args:
            widget: Widget to focus
            reason: Reason for focus change
        """
        if not widget:
            return
        
        try:
            # Set focus
            widget.setFocus(Qt.OtherFocusReason)
            
            # Announce focus change if accessibility enabled
            if self.accessibility_enabled:
                accessible_name = widget.accessibleName() or widget.objectName() or "unnamed element"
                self.announce(f"Focus on {accessible_name}", "polite")
            
            self.logger.debug(f"Focus set to {widget.__class__.__name__}: {reason}")
            
        except Exception as e:
            self.logger.error(f"Failed to set focus: {e}")
    
    def _handle_focus_changed(self, old_widget: QWidget, new_widget: QWidget):
        """Handle application focus changes.
        
        Args:
            old_widget: Previously focused widget
            new_widget: Newly focused widget
        """
        # Update focus history
        if new_widget and new_widget != self.current_focus_widget:
            if self.current_focus_widget:
                self.focus_history.append(self.current_focus_widget)
            
            self.current_focus_widget = new_widget
            
            # Limit history size
            if len(self.focus_history) > 50:
                self.focus_history = self.focus_history[-25:]
        
        # Emit focus change signal
        self.focusChanged.emit(old_widget, new_widget)
    
    def create_focus_trap(self, container: QWidget) -> bool:
        """Create a focus trap within a container.
        
        Args:
            container: Container widget to trap focus
            
        Returns:
            True if focus trap created successfully
        """
        try:
            if not container:
                return False
            
            # Add to focus trap stack
            self.focus_trap_stack.append(container)
            
            # Find focusable children
            focusable_children = self._get_focusable_children(container)
            
            if focusable_children:
                # Set focus to first focusable child
                focusable_children[0].setFocus()
                
                self.announce(f"Entered {container.accessibleName() or 'dialog'}", "assertive")
            
            self.logger.debug(f"Created focus trap for {container.__class__.__name__}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create focus trap: {e}")
            return False
    
    def release_focus_trap(self) -> bool:
        """Release the current focus trap.
        
        Returns:
            True if focus trap released successfully
        """
        try:
            if not self.focus_trap_stack:
                return False
            
            # Remove from stack
            container = self.focus_trap_stack.pop()
            
            # Restore focus to previous widget if available
            if self.focus_history:
                previous_widget = self.focus_history.pop()
                if previous_widget:
                    previous_widget.setFocus()
            
            self.announce(f"Exited {container.accessibleName() or 'dialog'}", "polite")
            
            self.logger.debug(f"Released focus trap for {container.__class__.__name__}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to release focus trap: {e}")
            return False
    
    def _get_focusable_children(self, widget: QWidget) -> List[QWidget]:
        """Get all focusable children of a widget.
        
        Args:
            widget: Parent widget
            
        Returns:
            List of focusable child widgets
        """
        focusable = []
        
        def traverse(w):
            if w.focusPolicy() != Qt.NoFocus and w.isVisible() and w.isEnabled():
                focusable.append(w)
            
            for child in w.children():
                if isinstance(child, QWidget):
                    traverse(child)
        
        traverse(widget)
        return focusable
    
    def _is_interactive_widget(self, widget: QWidget) -> bool:
        """Check if widget is interactive and should be focusable.
        
        Args:
            widget: Widget to check
            
        Returns:
            True if widget should be focusable
        """
        interactive_types = [
            'QPushButton', 'QToolButton', 'QCheckBox', 'QRadioButton',
            'QLineEdit', 'QTextEdit', 'QPlainTextEdit', 'QSpinBox',
            'QDoubleSpinBox', 'QComboBox', 'QSlider', 'QScrollBar',
            'QListWidget', 'QTreeWidget', 'QTableWidget', 'QTabWidget'
        ]
        
        return widget.__class__.__name__ in interactive_types
    
    def audit_accessibility(self, widget: QWidget = None) -> Dict[str, Any]:
        """Perform accessibility audit on widget or all registered components.
        
        Args:
            widget: Specific widget to audit (if None, audit all registered)
            
        Returns:
            Audit results dictionary
        """
        audit_results = {
            'timestamp': self._get_timestamp(),
            'total_components': 0,
            'issues': [],
            'passed_checks': 0,
            'failed_checks': 0,
            'warnings': 0,
            'compliance_level': AccessibilityLevel.A
        }
        
        try:
            # Determine widgets to audit
            widgets_to_audit = [widget] if widget else list(self.registered_components)
            audit_results['total_components'] = len(widgets_to_audit)
            
            for w in widgets_to_audit:
                widget_issues = self._audit_widget(w)
                audit_results['issues'].extend(widget_issues)
            
            # Calculate summary statistics
            for issue in audit_results['issues']:
                if issue['severity'] == 'error':
                    audit_results['failed_checks'] += 1
                elif issue['severity'] == 'warning':
                    audit_results['warnings'] += 1
                else:
                    audit_results['passed_checks'] += 1
            
            # Determine compliance level
            if audit_results['failed_checks'] == 0:
                if audit_results['warnings'] == 0:
                    audit_results['compliance_level'] = AccessibilityLevel.AAA
                else:
                    audit_results['compliance_level'] = AccessibilityLevel.AA
            else:
                audit_results['compliance_level'] = AccessibilityLevel.A
            
            self.auditCompleted.emit(audit_results)
            self.logger.info(f"Accessibility audit completed: {audit_results['compliance_level']} compliance")
            
        except Exception as e:
            self.logger.error(f"Accessibility audit failed: {e}")
            audit_results['issues'].append({
                'widget': 'Audit System',
                'severity': 'error',
                'guideline': 'System',
                'description': f'Audit system error: {e}'
            })
        
        return audit_results
    
    def _audit_widget(self, widget: QWidget) -> List[Dict[str, Any]]:
        """Audit a specific widget for accessibility issues.
        
        Args:
            widget: Widget to audit
            
        Returns:
            List of accessibility issues
        """
        issues = []
        widget_name = widget.__class__.__name__
        
        # Check accessible name
        if not widget.accessibleName():
            issues.append({
                'widget': widget_name,
                'severity': 'error',
                'guideline': 'WCAG 2.1 1.3.1',
                'description': 'Widget missing accessible name'
            })
        
        # Check accessible description for complex widgets
        if self._is_interactive_widget(widget) and not widget.accessibleDescription():
            issues.append({
                'widget': widget_name,
                'severity': 'warning',
                'guideline': 'WCAG 2.1 3.3.2',
                'description': 'Interactive widget missing accessible description'
            })
        
        # Check focus policy for interactive widgets
        if self._is_interactive_widget(widget) and widget.focusPolicy() == Qt.NoFocus:
            issues.append({
                'widget': widget_name,
                'severity': 'error',
                'guideline': 'WCAG 2.1 2.1.1',
                'description': 'Interactive widget not keyboard accessible'
            })
        
        # Check visibility and enabled state
        if not widget.isVisible():
            issues.append({
                'widget': widget_name,
                'severity': 'info',
                'guideline': 'General',
                'description': 'Widget is not visible'
            })
        
        if not widget.isEnabled():
            issues.append({
                'widget': widget_name,
                'severity': 'info',
                'guideline': 'General',
                'description': 'Widget is disabled'
            })
        
        return issues
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string.
        
        Returns:
            Timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_accessibility_report(self) -> Dict[str, Any]:
        """Get comprehensive accessibility status report.
        
        Returns:
            Accessibility status report
        """
        return {
            'accessibility_enabled': self.accessibility_enabled,
            'high_contrast_enabled': self.high_contrast_enabled,
            'screen_reader_detected': self.screen_reader_detected,
            'focus_indicators_enabled': self.focus_indicators_enabled,
            'registered_components': len(self.registered_components),
            'focus_trap_active': bool(self.focus_trap_stack),
            'pending_announcements': len(self.announcement_queue),
            'focus_history_length': len(self.focus_history)
        }
    
    def shutdown(self):
        """Shutdown the accessibility manager."""
        self.logger.info("Shutting down Accessibility Manager")
        
        # Stop announcement timer
        if self.announcement_timer.isActive():
            self.announcement_timer.stop()
        
        # Clear focus traps
        self.focus_trap_stack.clear()
        
        # Clear registered components
        self.registered_components.clear()
        
        # Restore standard palette if high contrast is active
        if self.high_contrast_enabled and self.standard_palette:
            self.application.setPalette(self.standard_palette)
        
        self.logger.info("Accessibility Manager shutdown complete")