"""Shared locale packs with English fallback and live widget bindings."""

import inspect
import json
import re
import string
import weakref
from pathlib import Path

from src.rfu import ui_strings
from src.core.preferences.contracts import PreferenceContract, PreferenceField

PREFERENCES = PreferenceContract("localization", 1, {
    "locale": PreferenceField(str, "en"), "packs": PreferenceField(dict, {})})


_plugin_strings = {}
_legacy_strings = json.loads(Path(__file__).with_name("legacy_strings.json").read_text(encoding="utf-8"))


def register_plugin_strings(prefix, strings):
    if not re.fullmatch(r'Plugin_[a-z][a-z0-9_]*', prefix):
        raise ValueError('Invalid plugin string namespace')
    for key, value in strings.items():
        if not re.fullmatch(r'[a-z][a-z0-9_]*', key) or not isinstance(value, str):
            raise ValueError('Invalid plugin string')
    _plugin_strings.update({prefix + '.' + key: value for key, value in strings.items()})


def catalogue():
    return {**_legacy_strings, **_plugin_strings, **{f"{name}.{key}": value
            for name, cls in vars(ui_strings).items() if inspect.isclass(cls)
            for key, value in vars(cls).items()
            if key.isupper() and isinstance(value, str)}}


def _fields(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name is not None}


class LocalizedText(str):
    def __new__(cls, value, key):
        instance = super().__new__(cls, value)
        instance.key = key
        return instance


class LocaleService:
    def __init__(self):
        self.locale = "en"
        self.packs = {}
        self._bindings = weakref.WeakKeyDictionary()
        self._listeners = weakref.WeakKeyDictionary()
        self._preferences = None

    def load(self, path, *, require_complete=False):
        """Validate placeholders and unknown keys before installing a pack."""
        pack = json.loads(Path(path).read_text(encoding="utf-8"))
        return self.load_data(pack, require_complete=require_complete)

    def load_data(self, pack, *, require_complete=False):
        if not isinstance(pack, dict) or set(pack) != {"schema_version", "locale", "strings"}:
            raise ValueError("Invalid locale pack fields")
        if type(pack["schema_version"]) is not int or pack["schema_version"] != 1:
            raise ValueError("Unsupported locale schema")
        locale = pack["locale"]
        if not isinstance(locale, str) or not re.fullmatch(r"[a-z]{2,3}(?:-[A-Z]{2})?", locale) or locale == "en":
            raise ValueError("Invalid additional locale identifier")
        strings = pack["strings"]
        base = catalogue()
        if not isinstance(strings, dict) or not strings or strings.keys() - base.keys():
            raise ValueError("Locale pack contains unknown or missing string keys")
        for key, value in strings.items():
            if not isinstance(value, str) or not value.strip() or _fields(value) != _fields(base[key]):
                raise ValueError(f"Invalid translation or placeholders: {key}")
            if "&" in base[key].replace("&&", "") and "&" not in value.replace("&&", ""):
                raise ValueError(f"Menu translation requires a mnemonic: {key}")
        missing = sorted(base.keys() - strings.keys())
        if require_complete and missing:
            raise ValueError(f"Missing {len(missing)} translations")
        self.packs[locale] = dict(strings)
        return locale, missing

    def configure_preferences(self, manager):
        """Restore only fully validated state from the existing preference backend."""
        saved = PREFERENCES.load(manager)
        candidate = LocaleService()
        for locale, strings in saved["packs"].items():
            candidate.load_data({"schema_version": 1, "locale": locale, "strings": strings})
        candidate.switch(saved["locale"])
        self.packs = candidate.packs
        self._preferences = manager
        self.switch(candidate.locale)

    def text(self, key):
        base = catalogue()
        value = self.packs.get(self.locale, {}).get(key, base[key])
        return LocalizedText(value, key)

    def bind(self, obj, setter, key):
        getattr(obj, setter)(self.text(key))
        self._bindings.setdefault(obj, {})[setter] = key

    def subscribe(self, obj, method):
        """Refresh compound views on a locale change without retaining windows."""
        self._listeners[obj] = method

    def switch(self, locale):
        if locale != "en" and locale not in self.packs:
            raise ValueError("Load the locale pack before selecting it")
        if self._preferences is not None:
            PREFERENCES.save(self._preferences, {"locale": locale, "packs": self.packs})
        self.locale = locale
        for obj, bindings in list(self._bindings.items()):
            try:
                for setter, key in bindings.items():
                    getattr(obj, setter)(self.text(key))
            except RuntimeError:
                self._bindings.pop(obj, None)
        for obj, method in list(self._listeners.items()):
            try:
                getattr(obj, method)()
            except RuntimeError:
                self._listeners.pop(obj, None)


service = LocaleService()
tr = service.text


def bind_text(obj, setter, text):
    """Bind translated text passed through existing GUI factory APIs."""
    if isinstance(text, LocalizedText):
        service.bind(obj, setter, text.key)


def bind_literal(obj, setter, key):
    """Apply a fixed UI label and keep it live when locale changes."""
    service.bind(obj, setter, key)


def localized_widget(factory, key, setter, *args, **kwargs):
    """Construct a legacy Qt label/control with a stable catalogue key."""
    widget = factory(tr(key), *args, **kwargs)
    service.bind(widget, setter, key)
    if hasattr(widget, 'setAccessibleName') and not widget.accessibleName():
        service.bind(widget, 'setAccessibleName', key)
    return widget


def bind_designer_strings(window):
    """Bind explicit translation metadata from Designer forms, never user data."""
    from PyQt5.QtCore import QObject
    for obj in [window, *window.findChildren(QObject)]:
        for raw in obj.dynamicPropertyNames():
            name = bytes(raw).decode('utf-8')
            if name.startswith('rfuLocale_'):
                service.bind(obj, name[len('rfuLocale_'):], obj.property(name))
