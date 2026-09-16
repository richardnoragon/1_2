"""Validated, one-time import of legacy JSON into canonical preferences."""
import copy
import json
from pathlib import Path
from src.core.preferences.contracts import PreferenceContract, PreferenceField
from src.core.preferences.manager import PreferenceManager


class LegacyJSONPreferences:
    def __init__(self, category, defaults, *, manager=None):
        self.defaults = json.loads(json.dumps(defaults, allow_nan=False))
        self.manager = manager or PreferenceManager()
        self.contract = PreferenceContract(category, 1, {'settings': PreferenceField(dict, self.defaults)})

    def validate(self, values):
        def check(value, default, path):
            if isinstance(default, dict):
                if not isinstance(value, dict) or value.keys() - default.keys():
                    raise ValueError('Unknown or invalid preference fields: ' + path)
                return {key: check(value.get(key, copy.deepcopy(item)), item, path + '.' + key)
                        for key, item in default.items()}
            if isinstance(default, list) and isinstance(value, tuple):
                value = list(value)
            if default is not None and type(value) is not type(default):
                raise ValueError('Invalid preference type: ' + path)
            return copy.deepcopy(value)
        result = check(values, self.defaults, self.contract.category)
        json.dumps(result, allow_nan=False)
        return result

    def load(self, legacy_path=None, *, extract=lambda value: value):
        saved = self.manager.get(self.contract.category, 'configuration', None)
        if saved is not None:
            return self.validate(self.contract.decode(saved)['settings'])
        values = self.defaults
        if legacy_path is not None and Path(legacy_path).is_file():
            values = extract(json.loads(Path(legacy_path).read_text(encoding='utf-8-sig')))
        result = self.validate(values)
        self.save(result)
        return result

    def save(self, values):
        self.contract.save(self.manager, {'settings': self.validate(values)})
