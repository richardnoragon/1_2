from scripts.quality.check_harmonization import counts, findings


def test_gate_detects_replacement_not_only_increased_count(tmp_path):
    tools = tmp_path / "src/tools"
    tools.mkdir(parents=True)
    source = tools / "example.py"
    source.write_text('font = QFont("Arial", 12)\n')
    before = counts(findings(tmp_path))
    source.write_text('font = QFont("Arial", 14)\n')
    after = counts(findings(tmp_path))
    assert sum(before.values()) == sum(after.values()) == 1
    assert after - before


def test_token_usage_does_not_trigger_font_gate(tmp_path):
    tools = tmp_path / "src/tools"
    tools.mkdir(parents=True)
    (tools / "example.py").write_text('from src.rfu import font_tokens\nfont_tokens.bind(label)\n')
    assert findings(tmp_path) == []


def test_gate_checks_designer_fonts_and_missing_translation_keys(tmp_path):
    tools = tmp_path / 'src/tools'
    tools.mkdir(parents=True)
    (tools / 'example.ui').write_text('''<ui><widget class="QWidget"><property name="font"><font><pointsize>9</pointsize></font></property><property name="rfuLocale_setWindowTitle"><string>Legacy.missing</string></property></widget></ui>''')
    assert {rule for _, rule, _ in findings(tmp_path)} == {'FNT', 'STR'}
