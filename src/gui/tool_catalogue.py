"""Canonical lazy tool catalogue shared by hub layouts."""
import inspect
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QTreeWidget,
                            QTreeWidgetItem, QHBoxLayout, QMainWindow)
from PyQt5.QtCore import Qt
from src.core.tool_manifest import ToolManifestRegistry
from src.core.tool_lifecycle import resolve_tool_class
from src.core.operations import operation
from src.gui.components import PrimaryButton
from src.rfu import font_tokens
from src.rfu.localization import service, tr


class ToolCatalogue(QWidget):
    def __init__(self, hub):
        super().__init__(hub)
        self.hub = hub
        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        service.bind(self.search, 'setPlaceholderText', 'ToolCatalogue.SEARCH')
        service.bind(self.search, 'setAccessibleName', 'ToolCatalogue.SEARCH')
        font_tokens.bind(self.search)
        layout.addWidget(self.search)
        self.tree = QTreeWidget()
        service.bind(self.tree, 'setAccessibleName', 'ToolCatalogue.TITLE')
        self.tree.setHeaderLabels(tr('ToolCatalogue.HEADERS').split('|'))
        font_tokens.bind(self.tree)
        layout.addWidget(self.tree)
        self.search.textChanged.connect(self.filter)
        self.tree.itemActivated.connect(lambda *_: self.open_selected())
        row = QHBoxLayout()
        row.addStretch()
        self.open_button = PrimaryButton(tr('ToolCatalogue.OPEN'))
        service.bind(self.open_button, 'setText', 'ToolCatalogue.OPEN')
        service.bind(self.open_button, 'setAccessibleName', 'ToolCatalogue.OPEN')
        self.open_button.clicked.connect(self.open_selected)
        row.addWidget(self.open_button)
        layout.addLayout(row)
        for entry in ToolManifestRegistry.builtins():
            item = QTreeWidgetItem([entry.display_name, entry.category.replace('-', ' ').title()])
            item.setData(0, Qt.UserRole, entry.tool_id)
            self.tree.addTopLevelItem(item)
        self.tree.resizeColumnToContents(0)
        self.tree.setCurrentItem(self.tree.topLevelItem(0))
        service.subscribe(self, 'retranslate')

    def retranslate(self):
        self.tree.setHeaderLabels(tr('ToolCatalogue.HEADERS').split('|'))

    def filter(self, query):
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            item.setHidden(query.casefold() not in (item.text(0) + ' ' + item.text(1)).casefold())

    def open_selected(self):
        item = self.tree.currentItem()
        if item is not None and not item.isHidden():
            self.hub.launch_tool(item.data(0, Qt.UserRole))


def launch_registered_tool(hub, tool_name):
    entry = ToolManifestRegistry.lookup(tool_name)
    if entry is None:
        return False
    windows = getattr(hub, '_catalogue_windows', {})
    hub._catalogue_windows = windows
    window = windows.get(entry.tool_id)
    if window is not None:
        window.show()
        window.raise_()
        window.activateWindow()
        return True
    with operation(entry.tool_id, 'launch'):
        cls = resolve_tool_class(entry.module_path, entry.class_name)
        if cls is None:
            raise ImportError('Tool entry point could not be loaded')
        parameters = inspect.signature(cls).parameters
        widget = cls(**({'hub_instance': hub} if 'hub_instance' in parameters else {}))
        if not isinstance(widget, QWidget):
            raise TypeError('Tool entry point must construct a QWidget')
        from src.gui.document_tool import DocumentToolWindow
        if isinstance(widget, DocumentToolWindow):
            window = widget
            window.parent_hub = hub
            from src.simple_menu_manager import SimpleMenuManager
            window.menu_manager = SimpleMenuManager(window)
            window.menu_manager.create_menubar()
            window.menu_manager.register_callback('save_as', window.save_as)
            window.menu_manager.register_callback('open_file', window.choose_file)
            if window.undo_supported:
                from src.gui.undo_history import install_undo_history
                window.undo_actions = install_undo_history(window, window.undo_stack, tool_id=entry.tool_id)
        elif isinstance(widget, QMainWindow):
            window = widget
            window.parent_hub = hub
            if not hasattr(window, 'menu_registry'):
                from src.gui.menu_registry import MenuRegistry
                window.menu_registry = MenuRegistry(window)
        else:
            from src.tabbed_hub import UtilityWindow
            window = UtilityWindow(hub, widget, entry.display_name)
        font_tokens.bind(window)
        font_tokens.bind(widget)
        font_tokens.apply_profile(window, window.font().family(), max(14, window.font().pointSizeF()))
        window.tool_id = entry.tool_id
        window.setMinimumSize(entry.min_window_width, entry.min_window_height)
        if hasattr(hub, 'register_tool'):
            hub.register_tool(entry.display_name, widget)
        from src.rfu.localization import bind_designer_strings
        bind_designer_strings(window)
        from src.gui.tool_runtime import ToolRuntime
        window.tool_runtime = ToolRuntime(window, widget, entry, hub)
        windows[entry.tool_id] = window
        window.show()
    return True
