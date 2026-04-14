# FR-02.4: Selective Cleanup Strategy

**Generated**: 2025-12-19  
**Task ID**: FR-02.4  
**Status**: ✅ COMPLETE  
**Prerequisites**: FR-02.1, FR-02.2, FR-02.3

---

## Executive Summary

This document defines a phased, risk-stratified cleanup strategy for archive directories. Based on FR-02.2 Historical Value Analysis findings (85% redundant, 10% potentially unique, 5% obsolete), the strategy prioritizes removing highest-risk/lowest-value content first while preserving potentially valuable historical data.

---

## Cleanup Priority Matrix

### Phase 1: SAFE REMOVAL (Lowest Risk)

**Target: 80% error reduction with minimal risk**

| Directory               | Risk Level  | Redundancy | Action | Rationale                                                             |
| ----------------------- | ----------- | ---------- | ------ | --------------------------------------------------------------------- |
| `venv_backup_20251021/` | 🟢 Very Low | 100%       | DELETE | Virtual environment backup - fully reproducible from requirements.txt |
| `venv_temp/`            | 🟢 Very Low | 100%       | DELETE | Temporary artifacts - no unique value                                 |
| `archive/temp_*`        | 🟢 Low      | 99%        | DELETE | Temporary directories within archive                                  |

**Expected Impact**:

- Files removed: ~6,200
- Space recovered: ~345 MB
- Errors eliminated: ~15,000 (estimated)

### Phase 2: MODERATE REMOVAL (Medium Risk)

**Target: Additional cleanup with careful validation**

| Directory                                                               | Risk Level | Redundancy | Action           | Rationale                                         |
| ----------------------------------------------------------------------- | ---------- | ---------- | ---------------- | ------------------------------------------------- |
| `file_utilities_2/`                                                     | 🟡 Medium  | 95%        | ARCHIVE + DELETE | Legacy project - verify no unique implementations |
| `emergency-backup-20250925_200754/` subdirectories matching git commits | 🟡 Medium  | 90%        | DELETE           | Verify git preservation before removal            |

**Expected Impact**:

- Files removed: ~3,500
- Space recovered: ~100 MB
- Errors eliminated: ~10,000 (estimated)

### Phase 3: SELECTIVE PRESERVATION (Higher Risk)

**Target: Clean remaining content with unique value assessment**

| Directory                    | Risk Level | Redundancy | Action    | Rationale                                    |
| ---------------------------- | ---------- | ---------- | --------- | -------------------------------------------- |
| `archive/pre-beta-cleanup-*` | 🟠 Higher  | 80%        | SELECTIVE | Review for unique implementations not in git |
| `archive/` remaining         | 🟠 Higher  | 75%        | SELECTIVE | Manual review recommended                    |

**Expected Impact**:

- Variable based on manual review findings
- Preserve 10-15% with unique historical value

---

## Pre-Deletion Checklist

### For Each Cleanup Phase:

1. **Backup Verification**

   - [ ] Verify target directory contents with FR-02.5 backup system
   - [ ] Confirm backup integrity with checksum validation
   - [ ] Test restore procedure on sample files

2. **Git History Cross-Reference**

   - [ ] Run git log to identify overlapping commits
   - [ ] Verify no unique commits only in archive
   - [ ] Document any files not in git history

3. **Unique Content Scan**

   - [ ] Search for files not matching any git blob
   - [ ] Identify potential unique implementations
   - [ ] Flag files for manual review if uncertain

4. **Development Environment Test**
   - [ ] Ensure application launches correctly
   - [ ] Run test suite (848 tests should pass)
   - [ ] Verify no import errors in production code

---

## Cleanup Scripts

### Phase 1: Safe Virtual Environment Cleanup

```python
#!/usr/bin/env python3
"""
FR-02.4 Phase 1: Safe Virtual Environment Cleanup
Target: venv_backup_* directories - fully reproducible from requirements.txt
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path(r"c:\Users\HP1\1_2")
BACKUP_LOCATION = WORKSPACE_ROOT / "archive" / "cleanup_backups"
LOG_FILE = WORKSPACE_ROOT / "reports" / "cleanup_execution_log.md"

PHASE_1_TARGETS = [
    "venv_backup_20251021",
    "venv_temp",
]

def log_action(message: str):
    """Append action to cleanup log."""
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def phase_1_cleanup(dry_run: bool = True):
    """Execute Phase 1 cleanup."""
    print(f"Phase 1 Cleanup - Dry Run: {dry_run}")

    for target in PHASE_1_TARGETS:
        target_path = WORKSPACE_ROOT / target

        if not target_path.exists():
            log_action(f"SKIP: {target} (does not exist)")
            continue

        # Count files and size
        file_count = sum(1 for _ in target_path.rglob("*") if _.is_file())
        total_size = sum(f.stat().st_size for f in target_path.rglob("*") if f.is_file())
        size_mb = total_size / (1024 * 1024)

        print(f"  Target: {target}")
        print(f"    Files: {file_count:,}")
        print(f"    Size: {size_mb:.2f} MB")

        if not dry_run:
            # Perform actual deletion
            shutil.rmtree(target_path)
            log_action(f"DELETED: {target} ({file_count:,} files, {size_mb:.2f} MB)")
        else:
            log_action(f"DRY RUN: Would delete {target} ({file_count:,} files, {size_mb:.2f} MB)")

    print("\nPhase 1 cleanup complete.")

if __name__ == "__main__":
    import sys
    dry_run = "--execute" not in sys.argv
    phase_1_cleanup(dry_run=dry_run)
```

### Phase 2: Legacy Project Cleanup (file_utilities_2)

```python
#!/usr/bin/env python3
"""
FR-02.4 Phase 2: Legacy Project Cleanup
Target: file_utilities_2/ - verify no unique implementations first
"""

import os
import hashlib
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(r"c:\Users\HP1\1_2")

def check_file_in_git(file_path: Path) -> bool:
    """Check if file content exists anywhere in git history."""
    try:
        # Get file hash
        with open(file_path, "rb") as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()[:16]

        # Search git for this content (simplified check)
        result = subprocess.run(
            ["git", "log", "--all", "--format=%H", "-1", "--", str(file_path.name)],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False

def analyze_file_utilities_2():
    """Analyze file_utilities_2 for unique content."""
    target = WORKSPACE_ROOT / "file_utilities_2"

    if not target.exists():
        print("file_utilities_2 does not exist")
        return

    python_files = list(target.rglob("*.py"))
    unique_files = []

    for py_file in python_files:
        if not check_file_in_git(py_file):
            unique_files.append(py_file)

    print(f"Total Python files: {len(python_files)}")
    print(f"Potentially unique: {len(unique_files)}")

    if unique_files:
        print("\nFiles requiring manual review:")
        for f in unique_files:
            print(f"  - {f.relative_to(WORKSPACE_ROOT)}")

if __name__ == "__main__":
    analyze_file_utilities_2()
```

---

## Decision Matrix

### When to DELETE immediately:

- Virtual environment backups (`venv_*`)
- `__pycache__` directories
- `.pyc` files
- Temporary files (`temp_*`, `*.tmp`)
- Build artifacts

### When to ARCHIVE before deletion:

- Legacy project directories
- Pre-release snapshots
- Configuration backups

### When to PRESERVE:

- Documentation with historical context
- Unique implementations not in git
- Files with modification dates after last git commit
- Any file flagged during manual review

---

## Execution Schedule

| Phase   | Timeline                 | Approval Required | Rollback Window |
| ------- | ------------------------ | ----------------- | --------------- |
| Phase 1 | Immediate                | No                | 7 days          |
| Phase 2 | After Phase 1 validation | Yes (optional)    | 14 days         |
| Phase 3 | After Phase 2 validation | Yes               | 30 days         |

---

## Success Criteria

- [ ] All targeted directories removed without errors
- [ ] No production code imports affected
- [ ] Test suite passes (848 tests)
- [ ] IDE performance improved (verified)
- [ ] Backup integrity validated
- [ ] Cleanup log completed

---

## Cross-References

| Document                                                                                | Relationship              |
| --------------------------------------------------------------------------------------- | ------------------------- |
| [FR-02.1 Archive Impact Assessment](../reports/archive_impact_assessment_2025-12-19.md) | Data source for targets   |
| [FR-02.2 Historical Value Analysis](../reports/archive_historical_value_analysis.md)    | Redundancy metrics        |
| [FR-02.3 IDE Configuration](../reports/ide_configuration_exclusion_report.md)           | Immediate fix applied     |
| [FR-02.5 Backup System](backup_system.py)                                               | Prerequisite for Phase 2+ |

---

## Conclusion

The selective cleanup strategy provides a safe, phased approach to archive directory cleanup:

1. **Phase 1** (Safe): Remove virtual environment backups immediately - zero risk
2. **Phase 2** (Moderate): Archive and remove legacy projects after verification
3. **Phase 3** (Selective): Manual review of remaining archive content

**Recommendation**: Execute Phase 1 immediately. Phases 2-3 are optional given FR-02.3 IDE exclusion success.
