"""One-way migration of declared QSettings fields into PreferenceManager."""
import base64
from PyQt5.QtCore import QByteArray, QSettings
from src.core.preferences.contracts import PreferenceContract, PreferenceField
from src.core.preferences.manager import PreferenceManager


class DeclaredSettings:
    """Small compatibility surface; only explicitly declared keys can be stored.

    Native settings are read on the first canonical load and left intact. Each
    subsequent update is a validated versioned bundle in the user-scoped backend.
    """
    def __init__(self, category, fields, legacy_application, *, manager=None, legacy=None):
        self.fields = fields
        self.manager = manager or PreferenceManager()
        self.names = {key: 'key_' + key.encode('utf-8').hex() for key in fields}
        declarations = {self.names[key]: PreferenceField(str if isinstance(default, QByteArray)
                        else type(default), self.encode(default)) for key, default in fields.items()}
        self.contract = PreferenceContract(category, 1, declarations)
        existing = self.manager.get(category, 'configuration', None)
        if existing is None:
            legacy = legacy if legacy is not None else QSettings('RFU', legacy_application)
            values = {}
            for key, default in fields.items():
                value = legacy.value(key, default, type=bool) if isinstance(default, bool) else legacy.value(key, default)
                if type(default) is list and isinstance(value, str):
                    value = [value]
                if type(default) in (int, float):
                    value = type(default)(value)
                values[self.names[key]] = self.encode(value)
            self.contract.save(self.manager, values)
        self.values = self.contract.load(self.manager)

    @staticmethod
    def encode(value):
        return base64.b64encode(bytes(value)).decode('ascii') if isinstance(value, QByteArray) else value

    def value(self, key, default=None, type=None):
        if key not in self.fields:
            raise KeyError('Undeclared preference key')
        value = self.values[self.names[key]]
        if isinstance(self.fields[key], QByteArray):
            return QByteArray(base64.b64decode(value, validate=True))
        return value

    def setValue(self, key, value):
        if key not in self.fields:
            raise KeyError('Undeclared preference key')
        candidate = dict(self.values)
        candidate[self.names[key]] = self.encode(value)
        self.contract.save(self.manager, candidate)
        self.values = candidate
