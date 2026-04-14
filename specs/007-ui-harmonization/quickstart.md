# Quickstart: UI Harmonization Developer Setup

**Feature**: `007-ui-harmonization`
**Date**: 2026-03-11

---

## Prerequisites

1. Python 3.12 virtual environment active:
   ```powershell
   # Windows PowerShell
   .\.venv312\Scripts\Activate.ps1
   ```
2. All dependencies installed:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Offscreen Qt platform available (set by pytest-qt automatically via `conftest.py`).

---

## Running the Contract Tests

```powershell
# Menu contract + UAP contract tests only
python -m pytest tests/contract/gui/tests/unit/preferences/test_uap_service.py -v

# All contract tests
python -m pytest tests/contract/ -v
```

Expected output: all tests FAIL until Phase 3.3 implementation is complete (TDD gate).

---

## Running the Dependency Audit

```powershell
python scripts/check_dependencies.py
```

Exit code 0 = all installed packages match `requirements.txt`.
Exit code 1 = mismatch found; details printed to stdout.

---

## Verifying UAP Manually

After Phase 3 implementation:

```python
from src.core.preferences.uap.service import UAPService

svc = UAPService()
settings = svc.load()
print(settings.last_used_font_family, settings.last_used_width)
```

---

## Development Workflow for This Feature

1. **Write failing tests** — see Phase 3.2 tasks in `tasks.md`
2. **Implement** — see Phase 3.3 tasks
3. **Run full suite** to confirm ≥ 85% coverage:
   ```powershell
   python -m pytest tests/ --cov=src --cov-report=term-missing -v
   ```
4. **Launch the hub** and verify UAP visually:
   ```powershell
   python src/rfu/main.py
   ```
5. **Open two different tools** and confirm font/size/directory are identical.
6. **Change font in one tool** (View → Font…) and open a third tool to confirm propagation.
