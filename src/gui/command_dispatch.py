"""Dispatch shared menu commands to the active tool and its focused editor."""
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication, QAction, QUndoStack, QLineEdit, QTextEdit, QPlainTextEdit
from src.core.operations import operation
from src.core.error_codes import resolve_error

ALIASES = {'save_as_file': 'save_as', 'show_preferences': 'preferences', 'show_options': 'options',
           'find_action': 'find', 'replace_action': 'replace', 'show_user_guide': 'user_guide'}
# Legacy callback names are explicit aliases, never routed to hub editing state.
for canonical, legacy in {
    'open_file': ('open_files', 'open_office_file', 'open_catalog', 'load_operation'),
    'save_file': ('save_metadata', 'save_catalog', 'save_operation'),
    'export_data': ('export_metadata', 'export_catalog', 'export_results'),
    'user_guide': ('show_help', 'help_compression', 'help_encrypt_decrypt', 'help_metadata',
                   'help_office_metadata', 'help_permissions', 'help_secure_delete', 'help_sync'),
    'new_project': ('new_analysis', 'new_catalog', 'new_checksum', 'new_compression',
                    'new_deletion', 'new_file', 'new_metadata_session', 'new_operation',
                    'new_organize', 'new_permissions', 'new_rename', 'new_scan', 'new_sync'),
}.items():
    ALIASES.update({name: canonical for name in legacy})

METHODS = {
    'open_file': ('choose_file', 'open_document', 'open_file'),
    'save_file': ('save_document', 'save_file'), 'save_as': ('save_as', 'save_document_as', 'save_as_file'),
    'new_project': ('new_document', 'new_project'), 'undo': ('undo', '_undo_last_organization'),
    'redo': ('redo',), 'cut': ('cut', 'cut_text'), 'copy': ('copy', 'copy_text'),
    'paste': ('paste', 'paste_text'), 'select_all': ('select_all', 'select_all_text'),
    'find': ('show_search_dialog', 'find', 'find_in_paths'),
    'replace': ('show_replace_dialog', 'replace'), 'refresh': ('refresh_view', 'refresh_data'),
    'preferences': ('show_preferences',), 'user_guide': ('show_help',),
    'export_data': ('export_data', 'export_report', 'export_metadata', 'export_rename_results'),
    'import_data': ('import_data',), 'zoom_in': ('zoom_in',), 'zoom_out': ('zoom_out',),
    'zoom_reset': ('zoom_reset',), 'close': ('close',),
}
EDITOR = {'cut': 'cut', 'copy': 'copy', 'paste': 'paste', 'undo': 'undo', 'redo': 'redo', 'select_all': 'selectAll'}


class CommandDispatcher(QObject):
    def __init__(self, window, owner, tool_id):
        super().__init__(window)
        self.window, self.owner, self.tool_id = window, owner, tool_id
        window.command_dispatcher = self
        QApplication.instance().focusChanged.connect(self.refresh)
        registry = getattr(window, 'menu_registry', None)
        if registry:
            for menu in registry.menus.values():
                menu.aboutToShow.connect(self.refresh)
        self.refresh()

    def busy(self):
        if getattr(self.owner, '_job', None) is not None:
            return True
        for name in ('worker', '_worker', 'scan_worker', 'thread'):
            worker = getattr(self.owner, name, None)
            if worker is not None and callable(getattr(worker, 'isRunning', None)) and worker.isRunning():
                return True
        return False

    def resolve(self, command):
        command = ALIASES.get(command, command)
        if (self.busy() or self.window.property('toolDegraded')) and command not in {'user_guide', 'close'}:
            return None
        focus = QApplication.focusWidget()
        if command in EDITOR and isinstance(focus, (QLineEdit, QTextEdit, QPlainTextEdit)) and (
                focus is self.owner or self.owner.isAncestorOf(focus)):
            if command in {'cut', 'paste', 'undo', 'redo'} and focus.isReadOnly():
                return None
            return getattr(focus, EDITOR[command])
        availability = getattr(self.owner, 'can_' + command, None)
        if callable(availability) and not availability():
            return None
        stack = getattr(self.owner, 'undo_stack', None)
        if command in {'undo', 'redo'} and isinstance(stack, QUndoStack):
            possible = stack.canUndo() if command == 'undo' else stack.canRedo()
            return getattr(stack, command) if possible else None
        manager = getattr(self.owner, 'menu_manager', None)
        for name, callback in getattr(manager, 'callbacks', {}).items():
            if ALIASES.get(name, name) == command and callable(callback):
                return callback
        for name in METHODS.get(command, (command,)):
            callback = getattr(self.owner, name, None)
            if callable(callback):
                return callback
        return None

    def invoke(self, command):
        callback = self.resolve(command)
        if callback is None:
            return False
        from src.gui.telemetry import emit_telemetry
        emit_telemetry('ui_user_action', tool_id=self.tool_id, action=command)
        try:
            with operation(self.tool_id, 'command-' + command):
                callback()
            return True
        except Exception as exc:
            emit_telemetry('ui_error_event', tool_id=self.tool_id, action=command, error_code=resolve_error(exc).code)
            self.window.statusBar().showMessage(resolve_error(exc).message, 8000)
            return False
        finally:
            self.refresh()

    def refresh(self, *_):
        for action in self.window.findChildren(QAction):
            command = action.property('toolCommand')
            if command:
                action.setEnabled(self.resolve(command) is not None)
