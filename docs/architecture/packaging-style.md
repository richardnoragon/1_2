# RFU — Packaging Style Guide

**Version**: 1.0.0
**Date**: 2026-03-11
**Spec**: [specs/007-ui-harmonization](../../specs/007-ui-harmonization/spec.md)
**Maintained by**: update this file when virtual environment conventions or
dependency management rules change.

---

## 1. Python Version

| Item | Value |
|---|---|
| Required runtime | Python **3.12** |
| Minimum acceptable | Python 3.11 (3.10 is EOL) |
| Version pinning | `.venv312` directory name encodes the minor version |

Do not use Python 3.13 until all binary wheels are available (PyQt5, PyMuPDF,
opencv-python-headless).

---

## 2. Virtual Environment Conventions

### Directory name

The virtual environment lives at the **repository root** and is named `.venv312`:

```
<repo-root>/
└── .venv312/          ← always here; always this name
    ├── Scripts/       ← Windows
    └── bin/           ← Linux / macOS
```

Do not create additional virtual environments (e.g. `venv/`, `.venv/`, `env/`).
The `.gitignore` excludes `.venv312/`, `venv/`, and `__pycache__/`.

### Activation scripts (provided at repo root)

| File | Platform | Usage |
|---|---|---|
| `activate_env.bat` | Windows CMD | `activate_env.bat` |
| `activate_env.ps1` | Windows PowerShell | `. .\activate_env.ps1` |
| `activate_env.sh` | Linux / macOS bash | `source activate_env.sh` |
| `activate_env.py` | Cross-platform Python launcher | `python activate_env.py` |

All scripts activate `.venv312` and print the active Python path for confirmation.

### Creating the environment from scratch

```powershell
# Windows PowerShell
python -m venv .venv312
.\.venv312\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

```bash
# Linux / macOS
python3.12 -m venv .venv312
source .venv312/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. `requirements.txt` Format Rules

### Location

One canonical `requirements.txt` at the **repository root**.
Do not create `requirements-dev.txt`, `requirements-test.txt`, etc.
All dependencies — runtime, testing, tooling, type stubs — live in this single file.

### Line format

Every non-comment, non-conditional line MUST follow this pattern:

```
<package-name>==<exact-version>          # <purpose-category>: <brief description>
```

Rules:
- Use `==` (exact pin). Never `>=`, `~=`, `^`, or unpinned.
- The comment is **mandatory**. It must state the purpose category (see §3.1) and
  a brief human-readable description.
- Align the `#` comments to the same column within a logical group for readability.
- Use the canonical PyPI package name (case-sensitive match to the package index).

**Good example:**
```
PyQt5==5.15.11                  # GUI framework: primary widget toolkit
pytest==8.3.5                   # Testing: primary test runner
cryptography==44.0.2            # Security: secret handling + token signing
```

**Bad examples (never do these):**
```
PyQt5>=5.15                     # ❌ range pin
pytest                          # ❌ unpinned, no comment
cryptography==44.0.2            # encryption  ← ❌ missing category colon
```

### Platform-conditional lines

Use `;` markers for platform-only packages:

```
pywin32==308; sys_platform=="win32"          # System: Windows API access
netifaces==0.11.0; sys_platform!="win32"     # Network: interface info (skip Windows build issues)
pyobjc-framework-Cocoa==10.3.1; sys_platform=="darwin"  # System: macOS AppKit integration
```

### Grouping order

1. GUI framework (`PyQt5`, `PyQt5-Qt5`, `PyQt5-sip`)
2. Security / identity
3. Testing (all `pytest-*` and test utilities)
4. Data processing
5. PDF tools
6. File & archive
7. System & network
8. Code quality & tooling
9. CLI utilities
10. Documentation
11. Type stubs
12. Platform-conditional packages (last, clearly separated by a comment header)

---

### 3.1 Purpose Category Vocabulary

Use these exact category labels in comments to keep `scripts/check_dependencies.py`
parseable and the inventory consistent:

| Label | Use for |
|---|---|
| `GUI framework` | PyQt5 and its components |
| `Security` | Cryptography, password hashing, TLS |
| `Testing` | pytest and all plugins; Faker, factory-boy |
| `Data processing` | pandas, numpy, openpyxl, document libraries |
| `PDF` | PyMuPDF, PyPDF2, pikepdf, etc. |
| `File & archive` | Pillow, py7zr, python-magic, Send2Trash, etc. |
| `System` | psutil, watchdog, pywin32, wmi, pyobjc |
| `Network` | requests, urllib3, paramiko, netifaces |
| `Code quality` | black, isort, flake8, mypy, pre-commit |
| `CLI` | fire, click, termcolor, colorama |
| `Documentation` | sphinx, sphinx themes |
| `Type stubs` | types-* packages |

---

## 4. Adding a New Dependency — Checklist

Before adding any new package to `requirements.txt`:

1. **Confirm necessity**: Is there an existing package in `requirements.txt` that
   already covers the need? Check [frameworks-and-dependencies.md](frameworks-and-dependencies.md) first.

2. **Find the exact version**: Identify the latest stable release on PyPI.
   ```powershell
   pip index versions <package-name>   # shows available versions
   ```

3. **Install and test locally**:
   ```powershell
   pip install <package-name>==<version>
   python -m pytest tests/ -v          # ensure no new failures
   ```

4. **Add to `requirements.txt`** with the mandatory comment:
   ```
   <package>==<version>    # <Category>: <brief description>
   ```
   Place it in the correct group (see §3 Grouping order).

5. **Update `docs/architecture/frameworks-and-dependencies.md`**: add a row to
   the appropriate section table.

6. **Run the dependency audit**:
   ```powershell
   python scripts/check_dependencies.py   # must exit 0
   ```

7. **Include both file changes** (`requirements.txt` and `frameworks-and-dependencies.md`)
   in the same commit / PR as the code that uses the new package.

---

## 5. Removing a Dependency

1. Search the codebase for all imports of the package:
   ```powershell
   grep -r "import <package>" src/ tests/
   ```
2. Confirm no code remains that uses it.
3. Remove from `requirements.txt` and from `frameworks-and-dependencies.md`.
4. Run full test suite to confirm nothing breaks.
5. Include all changes in one commit.

---

## 6. Upgrading a Dependency

1. Review the package's changelog for breaking changes.
2. Update the pinned version in `requirements.txt`.
3. Update the version in `frameworks-and-dependencies.md`.
4. Run `python scripts/check_dependencies.py` to verify the new version is installed.
5. Run `python -m pytest tests/ -v` to confirm no regressions.
6. If the upgrade changes the minimum acceptable version, update the
   "Minimum Acceptable Versions" table in `frameworks-and-dependencies.md`.

---

## 7. CI / Automated Checks

### Dependency audit

```powershell
python scripts/check_dependencies.py
```

- Parses `requirements.txt` (respects conditional markers, skips comment-only lines)
- Compares against `pip list --format=json` in the active environment
- Prints each mismatch: `REQUIRED <pkg>==<pinned>  INSTALLED <pkg>==<actual>`
- Exits **0** if all match; exits **1** on any mismatch
- Must pass in CI before the test suite runs

### Full test suite with coverage

```powershell
python -m pytest tests/ --cov=src --cov-report=term-missing -v
```

Coverage gate: **≥ 85% line coverage** (enforced by `pytest-cov` `--cov-fail-under=85`
in `setup.cfg`).

### Pre-commit hooks

```powershell
pre-commit run --all-files
```

Runs: `black` (format), `isort` (import order), `flake8` (lint).
Configure in `.pre-commit-config.yaml` at the repo root.

---

## 8. What NOT to Do

| Anti-pattern | Why |
|---|---|
| `pip install <package>` without updating `requirements.txt` | Creates invisible version drift; fails audit |
| Range pins (`>=`, `~=`) | Silent upgrades break reproducibility |
| Multiple `requirements*.txt` files | Fragments the source of truth; confuses new developers |
| Committing `.venv312/` | Binary artifacts bloat git history |
| Creating a second venv under `src/` or `tools/` | Leads to import confusion and duplicate packages |
| Importing a package not in `requirements.txt` | Will fail in clean environments (CI, other developers) |
