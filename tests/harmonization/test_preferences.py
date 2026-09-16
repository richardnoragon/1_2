import pytest

from src.core.preferences.contracts import PreferenceContract, PreferenceField


def test_preference_import_is_atomic_and_cannot_change_user():
    contract = PreferenceContract("localization", 1, {"locale": PreferenceField(str, "en")})
    class Manager:
        writes = []
        def set(self, *args):
            self.writes.append(args)
    manager = Manager()
    with pytest.raises(ValueError):
        contract.import_bundle(manager, {"category": "localization", "schema_version": 1,
                                        "values": {"locale": 1}})
    assert manager.writes == []
    contract.import_bundle(manager, contract.bundle({"locale": "de"}))
    assert manager.writes[0][:2] == ("localization", "configuration")


def test_migration_and_future_version_rejection():
    contract = PreferenceContract("localization", 2, {"locale": PreferenceField(str, "en")},
                                  migrations={1: lambda old: {"locale": old["language"]}})
    assert contract.decode({"category": "localization", "schema_version": 1,
                            "values": {"language": "de"}}) == {"locale": "de"}
    with pytest.raises(ValueError, match="version"):
        contract.decode({"category": "localization", "schema_version": 3, "values": {}})


def test_declared_qt_settings_migrate_once_and_preserve_native_data(tmp_path):
    from PyQt5.QtCore import QByteArray, QSettings
    from src.core.preferences.qt_adapter import DeclaredSettings
    class Manager:
        data = {}
        def get(self, category, key, default=None):
            return self.data.get((category, key), default)
        def set(self, category, key, value):
            self.data[category, key] = value
    native = QSettings(str(tmp_path / 'legacy.ini'), QSettings.IniFormat)
    native.setValue('enabled', False)
    native.setValue('geometry', QByteArray(b'\x00\xffgeometry'))
    native.setValue('recent_files', '/example.txt')
    manager = Manager()
    fields = {'enabled': True, 'geometry': QByteArray(), 'recent_files': []}
    settings = DeclaredSettings('test-tool', fields, 'Test', manager=manager, legacy=native)
    assert settings.value('enabled', type=bool) is False
    assert settings.value('recent_files') == ['/example.txt']
    assert bytes(settings.value('geometry')) == b'\x00\xffgeometry'
    settings.setValue('enabled', True)
    assert native.value('enabled', type=bool) is False
    reloaded = DeclaredSettings('test-tool', fields, 'Test', manager=manager, legacy=native)
    assert reloaded.value('enabled') is True
    with pytest.raises(ValueError):
        reloaded.setValue('enabled', 'false')
    assert reloaded.value('enabled') is True
