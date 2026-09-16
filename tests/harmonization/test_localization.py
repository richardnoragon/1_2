import json

import pytest
from PyQt5.QtWidgets import QLabel

from src.rfu.localization import LocaleService


def test_live_locale_and_english_fallback(qapp, tmp_path):
    service = LocaleService()
    path = tmp_path / "locale.json"
    path.write_text(json.dumps({"schema_version": 1, "locale": "de", "strings": {"Menu.FILE": "&Datei"}}))
    locale, missing = service.load(path)
    assert "Menu.EDIT" in missing
    label = QLabel()
    service.bind(label, "setText", "Menu.FILE")
    service.switch(locale)
    assert label.text() == "&Datei"
    assert service.text("Menu.EDIT") == "&Edit"
    service.switch("en")
    assert label.text() == "&File"


def test_invalid_placeholders_are_atomic(tmp_path):
    service = LocaleService()
    path = tmp_path / "locale.json"
    path.write_text(json.dumps({"schema_version": 1, "locale": "de", "strings": {"Menu.REOPEN": "Öffnen {wrong}"}}))
    with pytest.raises(ValueError, match="placeholders"):
        service.load(path)
    assert not service.packs
