"""Declarative commands, typed preferences and telemetry for local plugins."""
import re
from src.core.preferences.contracts import PreferenceContract, PreferenceField
from src.core.operations import operation

TYPES = {'string': str, 'integer': int, 'number': float, 'boolean': bool}
NAME = re.compile(r'[a-z][a-z0-9_]*\Z')


def validate_contracts(row):
    """Validate all metadata before registration; never import plugin code."""
    commands = row.get('commands', [])
    if not isinstance(commands, list):
        raise ValueError('Plugin commands must be a list')
    seen, shortcuts, mnemonics = set(), set(), set()
    for command in commands:
        if not isinstance(command, dict) or set(command) != {'id', 'label', 'menu', 'shortcut', 'method'}:
            raise ValueError('Invalid plugin command declaration')
        if any(not isinstance(value, str) or not value for value in command.values()):
            raise ValueError('Plugin command fields must be nonempty strings')
        if not NAME.fullmatch(command['id']) or not NAME.fullmatch(command['method']):
            raise ValueError('Plugin commands need public snake_case identifiers')
        if command['menu'] not in {'Tools', 'View', 'Reports'}:
            raise ValueError('Plugin commands belong to Tools, View or Reports')
        mnemonic = re.search(r'&(.)', command['label'].replace('&&', ''))
        if mnemonic is None:
            raise ValueError('Plugin commands require a mnemonic')
        key = command['menu'], mnemonic.group(1).casefold()
        if command['id'] in seen or command['shortcut'] in shortcuts or key in mnemonics:
            raise ValueError('Duplicate plugin command, shortcut or mnemonic')
        seen.add(command['id'])
        shortcuts.add(command['shortcut'])
        mnemonics.add(key)
    preferences = row.get('preferences', {})
    if not isinstance(preferences, dict):
        raise ValueError('Plugin preferences must be an object')
    if preferences:
        if set(preferences) != {'schema_version', 'fields'} or preferences['schema_version'] != 1 or type(preferences['schema_version']) is not int:
            raise ValueError('Unsupported plugin preference schema')
        if not isinstance(preferences['fields'], dict):
            raise ValueError('Invalid plugin preference fields')
        for key, field in preferences['fields'].items():
            if not NAME.fullmatch(key) or not isinstance(field, dict) or set(field) != {'type', 'default'}:
                raise ValueError('Invalid plugin preference declaration')
            if not isinstance(field['type'], str) or field['type'] not in TYPES or type(field['default']) is not TYPES[field['type']]:
                raise ValueError('Invalid plugin preference type')
        preference_contract(row['tool_id'], preferences)
    events = row.get('telemetry', {})
    if not isinstance(events, dict):
        raise ValueError('Plugin telemetry must be an object')
    for event, fields in events.items():
        if not NAME.fullmatch(event) or not isinstance(fields, dict):
            raise ValueError('Invalid plugin telemetry event')
        if any(not NAME.fullmatch(key) or not isinstance(kind, str) or kind not in TYPES for key, kind in fields.items()):
            raise ValueError('Invalid plugin telemetry field')


def preference_contract(tool_id, declaration):
    fields = {key: PreferenceField(TYPES[field['type']], field['default'])
              for key, field in declaration.get('fields', {}).items()}
    return PreferenceContract('plugin-' + tool_id, 1, fields)


class PluginServices:
    """A namespaced preference store and schema-checked event emitter."""
    def __init__(self, entry, manager):
        self.entry, self.manager = entry, manager
        self.contract = preference_contract(entry.tool_id, entry.preferences)

    def load_preferences(self):
        return self.contract.load(self.manager)

    def save_preferences(self, values):
        self.contract.save(self.manager, values)

    def emit_event(self, name, **values):
        schema = self.entry.telemetry.get(name)
        if schema is None or values.keys() != schema.keys() or any(
                type(values[key]) is not TYPES[kind] for key, kind in schema.items()):
            raise ValueError('Plugin telemetry does not match its declaration')
        import json
        json.dumps(values, allow_nan=False)
        from src.gui.telemetry import emit_telemetry
        emit_telemetry('ui_user_action', tool_id=self.entry.tool_id,
                       action='plugin_event', plugin_event=name, plugin_fields=values,
                       schema_version=1)


def install_contracts(window, widget, entry):
    from src.core.preferences.manager import PreferenceManager
    from src.rfu.localization import register_plugin_strings
    widget.plugin_services = PluginServices(entry, PreferenceManager())
    prefix = 'Plugin_' + entry.tool_id.replace('-', '_')
    register_plugin_strings(prefix, {command['id']: command['label'] for command in entry.commands})
    for command in entry.commands:
        callback = getattr(widget, command['method'], None)
        if not callable(callback):
            raise ValueError('Plugin command method is unavailable')
        def activate(callback=callback, command=command):
            with operation(entry.tool_id, command['id']):
                callback()
        window.menu_registry.register(tool_id=entry.tool_id, menu=command['menu'],
            label=prefix + '.' + command['id'], accelerator=command['shortcut'], callback=activate)
