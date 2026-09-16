"""Versioned preference bundles on the canonical, user-scoped manager.

Bundles are validated completely and saved as one JSON value. Import cannot
change the signed-in user, category or schema, and never partially applies keys.
"""

from dataclasses import dataclass
import copy
import json
import re


@dataclass(frozen=True)
class PreferenceField:
    value_type: type
    default: object


class PreferenceContract:
    def __init__(self, category, version, fields, *, migrations=None):
        if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", category):
            raise ValueError("Preference category must use kebab-case")
        if type(version) is not int or version < 1:
            raise ValueError("Preference version must be a positive integer")
        if any(not re.fullmatch(r"[a-z][a-z0-9_]*", key) for key in fields):
            raise ValueError("Preference keys must use snake_case")
        self.category, self.version = category, version
        self.fields = dict(fields)
        self.migrations = dict(migrations or {})
        self.validate({key: field.default for key, field in self.fields.items()})

    def validate(self, values):
        if not isinstance(values, dict) or values.keys() - self.fields.keys():
            raise ValueError("Unknown preference keys")
        result = {key: copy.deepcopy(values.get(key, field.default)) for key, field in self.fields.items()}
        for key, value in result.items():
            if type(value) is not self.fields[key].value_type:
                raise ValueError(f"Invalid preference type: {key}")
        json.dumps(result, allow_nan=False)
        return result

    def bundle(self, values):
        return {"category": self.category, "schema_version": self.version, "values": self.validate(values)}

    def decode(self, bundle):
        if not isinstance(bundle, dict) or set(bundle) != {"category", "schema_version", "values"}:
            raise ValueError("Invalid preference bundle")
        if bundle["category"] != self.category:
            raise ValueError("Preference category mismatch")
        version = bundle["schema_version"]
        if type(version) is not int or not 1 <= version <= self.version:
            raise ValueError("Unsupported preference version")
        values = copy.deepcopy(bundle["values"])
        while version < self.version:
            if version not in self.migrations:
                raise ValueError("No preference migration is registered")
            values = self.migrations[version](values)
            version += 1
        return self.validate(values)

    def load(self, manager):
        bundle = manager.get(self.category, "configuration", None)
        return self.validate({}) if bundle is None else self.decode(bundle)

    def save(self, manager, values):
        manager.set(self.category, "configuration", self.bundle(values))

    def import_bundle(self, manager, bundle):
        self.save(manager, self.decode(bundle))
