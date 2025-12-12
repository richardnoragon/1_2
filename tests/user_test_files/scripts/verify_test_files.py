#!/usr/bin/env python3
"""
Verify all test files and directories exist and are valid.

This script validates the test file structure as defined in:
outline_of_user_test_documents.md

Usage:
    python verify_test_files.py [--verbose] [--phase PHASE]

Author: RFU Test Suite
Last Updated: 2025-12-10
"""

import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Get the base directory (parent of scripts)
BASE_DIR = Path(__file__).parent.parent


def verify_phase1_directories() -> Dict[str, any]:
    """Verify Phase 1: Directory Structure Creation."""
    results = {
        "phase": "Phase 1: Directory Structure",
        "timestamp": datetime.now().isoformat(),
        "sections": {},
        "summary": {"passed": 0, "failed": 0, "total": 0},
    }

    # Section 1.1: Root Directory Hierarchy
    expected_top_level = [
        "text_files",
        "binary_files",
        "pdf_files",
        "special_names",
        "directory_structures",
        "permissions",
        "metadata",
        "duplicates",
        "sync_test_data",
        "checksum_test_data",
        "compression_test_data",
        "split_join_test_data",
        "encryption_test_data",
        "secure_delete_test_data",
        "network_transfer_test_data",
        "performance_benchmarks",
        "scripts",
    ]

    section_1_1 = {
        "name": "1.1 Root Directory Hierarchy",
        "checks": [],
        "status": "PASS",
    }
    for dir_name in expected_top_level:
        dir_path = BASE_DIR / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        section_1_1["checks"].append(
            {
                "item": dir_name,
                "expected": "Directory exists",
                "result": "PASS" if exists else "FAIL",
                "path": str(dir_path),
            }
        )
        if not exists:
            section_1_1["status"] = "FAIL"

    results["sections"]["1.1"] = section_1_1

    # Section 1.2: Text Files Subdirectories
    text_subdirs = ["encodings", "line_endings", "content", "sizes"]
    section_1_2 = {
        "name": "1.2 Text Files Subdirectories",
        "checks": [],
        "status": "PASS",
    }
    for subdir in text_subdirs:
        dir_path = BASE_DIR / "text_files" / subdir
        exists = dir_path.exists() and dir_path.is_dir()
        section_1_2["checks"].append(
            {
                "item": f"text_files/{subdir}",
                "expected": "Subdirectory exists",
                "result": "PASS" if exists else "FAIL",
                "path": str(dir_path),
            }
        )
        if not exists:
            section_1_2["status"] = "FAIL"

    results["sections"]["1.2"] = section_1_2

    # Section 1.3: Binary Files Subdirectories
    binary_subdirs = ["images", "documents", "archives", "executables", "media"]
    section_1_3 = {
        "name": "1.3 Binary Files Subdirectories",
        "checks": [],
        "status": "PASS",
    }
    for subdir in binary_subdirs:
        dir_path = BASE_DIR / "binary_files" / subdir
        exists = dir_path.exists() and dir_path.is_dir()
        section_1_3["checks"].append(
            {
                "item": f"binary_files/{subdir}",
                "expected": "Subdirectory exists",
                "result": "PASS" if exists else "FAIL",
                "path": str(dir_path),
            }
        )
        if not exists:
            section_1_3["status"] = "FAIL"

    results["sections"]["1.3"] = section_1_3

    # Calculate summary
    for section in results["sections"].values():
        for check in section["checks"]:
            results["summary"]["total"] += 1
            if check["result"] == "PASS":
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1

    return results


def verify_phase2_duplicates() -> Dict[str, any]:
    """Verify Phase 2.1: Duplicate Detection Test Files."""
    results = {
        "phase": "Phase 2.1: Duplicate Detection Test Files",
        "timestamp": datetime.now().isoformat(),
        "sections": {},
        "summary": {"passed": 0, "failed": 0, "total": 0},
    }

    dup_base = BASE_DIR / "duplicates"

    # Section 2.1.1: Exact Duplicates
    section_2_1_1 = {
        "name": "2.1.1 Exact Duplicates",
        "checks": [],
        "status": "PASS",
    }

    exact_dir = dup_base / "exact_duplicates"
    expected_exact = ["dup_original.txt", "dup_copy1.txt", "dup_copy2.txt"]
    hashes = []

    for fname in expected_exact:
        fpath = exact_dir / fname
        exists = fpath.exists() and fpath.is_file()
        if exists:
            file_hash = hashlib.sha256(fpath.read_bytes()).hexdigest()
            hashes.append(file_hash)
        section_2_1_1["checks"].append(
            {
                "item": fname,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_1_1["status"] = "FAIL"

    # Check all hashes are identical
    if hashes and len(set(hashes)) == 1:
        section_2_1_1["checks"].append(
            {
                "item": "Hash comparison",
                "expected": "All hashes identical",
                "result": "PASS",
            }
        )
    else:
        section_2_1_1["checks"].append(
            {
                "item": "Hash comparison",
                "expected": "All hashes identical",
                "result": "FAIL",
            }
        )
        section_2_1_1["status"] = "FAIL"

    results["sections"]["2.1.1"] = section_2_1_1

    # Section 2.1.2: Near Duplicates
    section_2_1_2 = {
        "name": "2.1.2 Near Duplicates",
        "checks": [],
        "status": "PASS",
    }

    near_dir = dup_base / "near_duplicates"
    expected_near = ["near_dup_v1.txt", "near_dup_v2.txt", "near_dup_v3.txt"]
    near_hashes = []

    for fname in expected_near:
        fpath = near_dir / fname
        exists = fpath.exists() and fpath.is_file()
        if exists:
            file_hash = hashlib.sha256(fpath.read_bytes()).hexdigest()
            near_hashes.append(file_hash)
        section_2_1_2["checks"].append(
            {
                "item": fname,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_1_2["status"] = "FAIL"

    # Check all hashes are different
    if near_hashes and len(set(near_hashes)) == len(near_hashes):
        section_2_1_2["checks"].append(
            {
                "item": "Hash comparison",
                "expected": "All hashes different",
                "result": "PASS",
            }
        )
    else:
        section_2_1_2["checks"].append(
            {
                "item": "Hash comparison",
                "expected": "All hashes different",
                "result": "FAIL",
            }
        )
        section_2_1_2["status"] = "FAIL"

    results["sections"]["2.1.2"] = section_2_1_2

    # Section 2.1.3: Same Content Different Name
    section_2_1_3 = {
        "name": "2.1.3 Same Content Different Name",
        "checks": [],
        "status": "PASS",
    }

    same_content_dir = dup_base / "same_content_diff_name"
    expected_same_content = ["file_alpha.txt", "file_beta.txt", "file_gamma.txt"]
    same_hashes = []

    for fname in expected_same_content:
        fpath = same_content_dir / fname
        exists = fpath.exists() and fpath.is_file()
        if exists:
            file_hash = hashlib.sha256(fpath.read_bytes()).hexdigest()
            same_hashes.append(file_hash)
        section_2_1_3["checks"].append(
            {
                "item": fname,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_1_3["status"] = "FAIL"

    # Check all hashes are identical
    if same_hashes and len(set(same_hashes)) == 1:
        section_2_1_3["checks"].append(
            {
                "item": "Hash comparison",
                "expected": "All hashes identical",
                "result": "PASS",
            }
        )
    else:
        section_2_1_3["checks"].append(
            {
                "item": "Hash comparison",
                "expected": "All hashes identical",
                "result": "FAIL",
            }
        )
        section_2_1_3["status"] = "FAIL"

    results["sections"]["2.1.3"] = section_2_1_3

    # Section 2.1.4: Same Name Different Content
    section_2_1_4 = {
        "name": "2.1.4 Same Name Different Content",
        "checks": [],
        "status": "PASS",
    }

    same_name_dir = dup_base / "same_name_diff_content"
    diff_hashes = []

    for folder in ["folder_a", "folder_b"]:
        fpath = same_name_dir / folder / "document.txt"
        exists = fpath.exists() and fpath.is_file()
        if exists:
            file_hash = hashlib.sha256(fpath.read_bytes()).hexdigest()
            diff_hashes.append(file_hash)
        section_2_1_4["checks"].append(
            {
                "item": f"{folder}/document.txt",
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_1_4["status"] = "FAIL"

    # Check hashes are different
    if diff_hashes and len(set(diff_hashes)) == len(diff_hashes):
        section_2_1_4["checks"].append(
            {
                "item": "Hash comparison",
                "expected": "Hashes different",
                "result": "PASS",
            }
        )
    else:
        section_2_1_4["checks"].append(
            {
                "item": "Hash comparison",
                "expected": "Hashes different",
                "result": "FAIL",
            }
        )
        section_2_1_4["status"] = "FAIL"

    results["sections"]["2.1.4"] = section_2_1_4

    # Section 2.1.5: Checksums file
    section_2_1_5 = {
        "name": "2.1.5 Checksums Documentation",
        "checks": [],
        "status": "PASS",
    }

    checksums_file = dup_base / "checksums.md"
    exists = checksums_file.exists() and checksums_file.is_file()
    section_2_1_5["checks"].append(
        {
            "item": "checksums.md",
            "expected": "File exists",
            "result": "PASS" if exists else "FAIL",
        }
    )
    if not exists:
        section_2_1_5["status"] = "FAIL"

    results["sections"]["2.1.5"] = section_2_1_5

    # Calculate summary
    for section in results["sections"].values():
        for check in section["checks"]:
            results["summary"]["total"] += 1
            if check["result"] == "PASS":
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1

    return results


def verify_phase2_sync_data() -> Dict[str, any]:
    """Verify Phase 2.2: Synchronization Test Data."""
    results = {
        "phase": "Phase 2.2: Synchronization Test Data",
        "timestamp": datetime.now().isoformat(),
        "sections": {},
        "summary": {"passed": 0, "failed": 0, "total": 0},
    }

    sync_base = BASE_DIR / "sync_test_data"

    # Section 2.2.1: Directory Structure
    section_2_2_1 = {
        "name": "2.2.1 Directory Structure",
        "checks": [],
        "status": "PASS",
    }

    expected_dirs = [
        "source",
        "destination",
        "conflicts",
        "source/unchanged",
        "source/modified",
        "source/new_files",
        "source/deleted_from_dest",
        "source/nested/level1",
        "destination/unchanged",
        "destination/modified",
        "destination/deleted_from_source",
        "destination/nested/level1",
        "conflicts/both_modified",
        "conflicts/name_conflicts",
    ]

    for dir_name in expected_dirs:
        dir_path = sync_base / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        section_2_2_1["checks"].append(
            {
                "item": dir_name,
                "expected": "Directory exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_2_1["status"] = "FAIL"

    results["sections"]["2.2.1"] = section_2_2_1

    # Section 2.2.2: Unchanged Files (identical hash)
    section_2_2_2 = {
        "name": "2.2.2 Unchanged Files",
        "checks": [],
        "status": "PASS",
    }

    src_unchanged = sync_base / "source" / "unchanged" / "stable.txt"
    dst_unchanged = sync_base / "destination" / "unchanged" / "stable.txt"

    src_exists = src_unchanged.exists()
    dst_exists = dst_unchanged.exists()

    section_2_2_2["checks"].append(
        {
            "item": "source/unchanged/stable.txt",
            "expected": "File exists",
            "result": "PASS" if src_exists else "FAIL",
        }
    )
    section_2_2_2["checks"].append(
        {
            "item": "destination/unchanged/stable.txt",
            "expected": "File exists",
            "result": "PASS" if dst_exists else "FAIL",
        }
    )

    if src_exists and dst_exists:
        src_hash = hashlib.sha256(src_unchanged.read_bytes()).hexdigest()
        dst_hash = hashlib.sha256(dst_unchanged.read_bytes()).hexdigest()
        hashes_match = src_hash == dst_hash
        section_2_2_2["checks"].append(
            {
                "item": "Hash comparison",
                "expected": "Hashes identical",
                "result": "PASS" if hashes_match else "FAIL",
            }
        )
        if not hashes_match:
            section_2_2_2["status"] = "FAIL"
    else:
        section_2_2_2["status"] = "FAIL"

    results["sections"]["2.2.2"] = section_2_2_2

    # Section 2.2.3: Modified Files (source newer)
    section_2_2_3 = {
        "name": "2.2.3 Modified Files (Timestamp)",
        "checks": [],
        "status": "PASS",
    }

    src_modified = sync_base / "source" / "modified" / "changed.txt"
    dst_modified = sync_base / "destination" / "modified" / "changed.txt"

    src_mod_exists = src_modified.exists()
    dst_mod_exists = dst_modified.exists()

    section_2_2_3["checks"].append(
        {
            "item": "source/modified/changed.txt",
            "expected": "File exists",
            "result": "PASS" if src_mod_exists else "FAIL",
        }
    )
    section_2_2_3["checks"].append(
        {
            "item": "destination/modified/changed.txt",
            "expected": "File exists",
            "result": "PASS" if dst_mod_exists else "FAIL",
        }
    )

    if src_mod_exists and dst_mod_exists:
        src_mtime = src_modified.stat().st_mtime
        dst_mtime = dst_modified.stat().st_mtime
        src_newer = src_mtime > dst_mtime
        section_2_2_3["checks"].append(
            {
                "item": "Timestamp comparison",
                "expected": "Source newer than destination",
                "result": "PASS" if src_newer else "FAIL",
            }
        )
        if not src_newer:
            section_2_2_3["status"] = "FAIL"
    else:
        section_2_2_3["status"] = "FAIL"

    results["sections"]["2.2.3"] = section_2_2_3

    # Section 2.2.4: New Files (only in source)
    section_2_2_4 = {
        "name": "2.2.4 New Files (Source Only)",
        "checks": [],
        "status": "PASS",
    }

    src_new = sync_base / "source" / "new_files" / "added.txt"
    src_removed = sync_base / "source" / "deleted_from_dest" / "removed.txt"

    section_2_2_4["checks"].append(
        {
            "item": "source/new_files/added.txt",
            "expected": "File exists",
            "result": "PASS" if src_new.exists() else "FAIL",
        }
    )
    section_2_2_4["checks"].append(
        {
            "item": "source/deleted_from_dest/removed.txt",
            "expected": "File exists",
            "result": "PASS" if src_removed.exists() else "FAIL",
        }
    )

    if not src_new.exists() or not src_removed.exists():
        section_2_2_4["status"] = "FAIL"

    results["sections"]["2.2.4"] = section_2_2_4

    # Section 2.2.5: Orphaned Files (only in dest)
    section_2_2_5 = {
        "name": "2.2.5 Orphaned Files (Dest Only)",
        "checks": [],
        "status": "PASS",
    }

    dst_orphaned = sync_base / "destination" / "deleted_from_source" / "orphaned.txt"

    section_2_2_5["checks"].append(
        {
            "item": "destination/deleted_from_source/orphaned.txt",
            "expected": "File exists",
            "result": "PASS" if dst_orphaned.exists() else "FAIL",
        }
    )

    if not dst_orphaned.exists():
        section_2_2_5["status"] = "FAIL"

    results["sections"]["2.2.5"] = section_2_2_5

    # Section 2.2.6: Conflict Files
    section_2_2_6 = {
        "name": "2.2.6 Conflict Test Files",
        "checks": [],
        "status": "PASS",
    }

    conflict_files = [
        "conflicts/both_modified/conflict_file_source.txt",
        "conflicts/both_modified/conflict_file_dest.txt",
        "conflicts/name_conflicts/CaseSensitive.txt",
        "conflicts/name_conflicts/casesensitive_lower.txt",
    ]

    for file_path in conflict_files:
        full_path = sync_base / file_path
        exists = full_path.exists() and full_path.is_file()
        section_2_2_6["checks"].append(
            {
                "item": file_path,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_2_6["status"] = "FAIL"

    results["sections"]["2.2.6"] = section_2_2_6

    # Calculate summary
    for section in results["sections"].values():
        for check in section["checks"]:
            results["summary"]["total"] += 1
            if check["result"] == "PASS":
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1

    return results


def verify_phase2_checksum_data() -> Dict[str, any]:
    """Verify Phase 2.3: Checksum Verification Test Data."""
    results = {
        "phase": "Phase 2.3: Checksum Verification Test Data",
        "timestamp": datetime.now().isoformat(),
        "sections": {},
        "summary": {"passed": 0, "failed": 0, "total": 0},
    }

    checksum_base = BASE_DIR / "checksum_test_data"

    # Section 2.3.1: Directory Structure
    section_2_3_1 = {
        "name": "2.3.1 Directory Structure",
        "checks": [],
        "status": "PASS",
    }

    expected_dirs = ["known_hashes", "integrity"]
    for dir_name in expected_dirs:
        dir_path = checksum_base / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        section_2_3_1["checks"].append(
            {
                "item": dir_name,
                "expected": "Directory exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_3_1["status"] = "FAIL"

    results["sections"]["2.3.1"] = section_2_3_1

    # Section 2.3.2: Known Hash Files
    section_2_3_2 = {
        "name": "2.3.2 Known Hash Files",
        "checks": [],
        "status": "PASS",
    }

    known_hashes_dir = checksum_base / "known_hashes"
    expected_files = {
        "md5_test.txt": "test content for MD5",
        "sha1_test.txt": "test",
        "sha256_test.txt": "test",
        "sha512_test.txt": "test content for SHA512",
        "bound_0b_empty.txt": "",
    }

    for fname, expected_content in expected_files.items():
        fpath = known_hashes_dir / fname
        exists = fpath.exists() and fpath.is_file()
        section_2_3_2["checks"].append(
            {
                "item": fname,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_3_2["status"] = "FAIL"
        elif fpath.read_text() != expected_content:
            section_2_3_2["checks"].append(
                {
                    "item": f"{fname} content",
                    "expected": "Content matches",
                    "result": "FAIL",
                }
            )
            section_2_3_2["status"] = "FAIL"

    results["sections"]["2.3.2"] = section_2_3_2

    # Section 2.3.3: Hash Value Verification
    section_2_3_3 = {
        "name": "2.3.3 Hash Value Verification",
        "checks": [],
        "status": "PASS",
    }

    # Verify specific known hashes from spec
    hash_checks = [
        ("sha1_test.txt", "sha1", "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"),
        (
            "sha256_test.txt",
            "sha256",
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
        ),
        ("bound_0b_empty.txt", "md5", "d41d8cd98f00b204e9800998ecf8427e"),
        ("bound_0b_empty.txt", "sha1", "da39a3ee5e6b4b0d3255bfef95601890afd80709"),
        (
            "bound_0b_empty.txt",
            "sha256",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        ),
    ]

    for fname, hash_type, expected_hash in hash_checks:
        fpath = known_hashes_dir / fname
        if fpath.exists():
            content = fpath.read_bytes()
            if hash_type == "md5":
                actual_hash = hashlib.md5(content).hexdigest()
            elif hash_type == "sha1":
                actual_hash = hashlib.sha1(content).hexdigest()
            elif hash_type == "sha256":
                actual_hash = hashlib.sha256(content).hexdigest()

            match = actual_hash == expected_hash
            section_2_3_3["checks"].append(
                {
                    "item": f"{fname} {hash_type.upper()}",
                    "expected": expected_hash[:16] + "...",
                    "result": "PASS" if match else "FAIL",
                }
            )
            if not match:
                section_2_3_3["status"] = "FAIL"

    results["sections"]["2.3.3"] = section_2_3_3

    # Section 2.3.4: Integrity Test Files
    section_2_3_4 = {
        "name": "2.3.4 Integrity Test Files",
        "checks": [],
        "status": "PASS",
    }

    integrity_dir = checksum_base / "integrity"
    integrity_files = ["original_intact.txt", "modified_corrupted.txt"]

    for fname in integrity_files:
        fpath = integrity_dir / fname
        exists = fpath.exists() and fpath.is_file()
        section_2_3_4["checks"].append(
            {
                "item": fname,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_3_4["status"] = "FAIL"

    # Verify they have different hashes
    if (integrity_dir / "original_intact.txt").exists() and (
        integrity_dir / "modified_corrupted.txt"
    ).exists():
        hash1 = hashlib.sha256(
            (integrity_dir / "original_intact.txt").read_bytes()
        ).hexdigest()
        hash2 = hashlib.sha256(
            (integrity_dir / "modified_corrupted.txt").read_bytes()
        ).hexdigest()
        different = hash1 != hash2
        section_2_3_4["checks"].append(
            {
                "item": "Integrity files have different hashes",
                "expected": "Different",
                "result": "PASS" if different else "FAIL",
            }
        )
        if not different:
            section_2_3_4["status"] = "FAIL"

    results["sections"]["2.3.4"] = section_2_3_4

    # Section 2.3.5: Checksums Documentation
    section_2_3_5 = {
        "name": "2.3.5 Checksums Documentation",
        "checks": [],
        "status": "PASS",
    }

    checksums_file = known_hashes_dir / "checksums.txt"
    exists = checksums_file.exists() and checksums_file.is_file()
    section_2_3_5["checks"].append(
        {
            "item": "checksums.txt",
            "expected": "File exists",
            "result": "PASS" if exists else "FAIL",
        }
    )
    if not exists:
        section_2_3_5["status"] = "FAIL"

    results["sections"]["2.3.5"] = section_2_3_5

    # Calculate summary
    for section in results["sections"].values():
        for check in section["checks"]:
            results["summary"]["total"] += 1
            if check["result"] == "PASS":
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1

    return results


def verify_phase2_compression_data() -> Dict[str, any]:
    """Verify Phase 2.4: Compression Test Data."""
    import gzip

    results = {
        "phase": "Phase 2.4: Compression Test Data",
        "timestamp": datetime.now().isoformat(),
        "sections": {},
        "summary": {"passed": 0, "failed": 0, "total": 0},
    }

    compression_base = BASE_DIR / "compression_test_data"

    # Section 2.4.1: Directory Structure
    section_2_4_1 = {
        "name": "2.4.1 Directory Structure",
        "checks": [],
        "status": "PASS",
    }

    expected_dirs = [
        "compressible",
        "incompressible",
        "multi_format",
        "multi_format/archive_contents",
        "multi_format/archive_contents/subdir",
    ]

    for dir_name in expected_dirs:
        dir_path = compression_base / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        section_2_4_1["checks"].append(
            {
                "item": dir_name,
                "expected": "Directory exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_4_1["status"] = "FAIL"

    results["sections"]["2.4.1"] = section_2_4_1

    # Section 2.4.2: Compressible Files
    section_2_4_2 = {
        "name": "2.4.2 Compressible Files",
        "checks": [],
        "status": "PASS",
    }

    compressible_dir = compression_base / "compressible"
    compressible_files = {
        "comp_text_repetitive.txt": {"min_size": 40000, "max_ratio": 0.10},
        "comp_zeros.bin": {"min_size": 100000, "max_ratio": 0.05},
        "comp_pattern.bin": {"min_size": 99000, "max_ratio": 0.05},
    }

    for fname, criteria in compressible_files.items():
        fpath = compressible_dir / fname
        exists = fpath.exists() and fpath.is_file()
        section_2_4_2["checks"].append(
            {
                "item": fname,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_4_2["status"] = "FAIL"
            continue

        # Check file size
        file_size = fpath.stat().st_size
        size_ok = file_size >= criteria["min_size"]
        section_2_4_2["checks"].append(
            {
                "item": f"{fname} size",
                "expected": f">= {criteria['min_size']} bytes",
                "result": "PASS" if size_ok else f"FAIL ({file_size} bytes)",
            }
        )
        if not size_ok:
            section_2_4_2["status"] = "FAIL"

        # Check compression ratio
        original_data = fpath.read_bytes()
        compressed_data = gzip.compress(original_data)
        ratio = len(compressed_data) / len(original_data)
        ratio_ok = ratio < criteria["max_ratio"]
        section_2_4_2["checks"].append(
            {
                "item": f"{fname} compression ratio",
                "expected": f"< {criteria['max_ratio']*100:.0f}%",
                "result": "PASS" if ratio_ok else f"FAIL ({ratio*100:.2f}%)",
            }
        )
        if not ratio_ok:
            section_2_4_2["status"] = "FAIL"

    results["sections"]["2.4.2"] = section_2_4_2

    # Section 2.4.3: Incompressible Files
    section_2_4_3 = {
        "name": "2.4.3 Incompressible Files",
        "checks": [],
        "status": "PASS",
    }

    incompressible_dir = compression_base / "incompressible"
    incompressible_files = ["incomp_random.bin", "incomp_encrypted.bin"]

    for fname in incompressible_files:
        fpath = incompressible_dir / fname
        exists = fpath.exists() and fpath.is_file()
        section_2_4_3["checks"].append(
            {
                "item": fname,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_4_3["status"] = "FAIL"
            continue

        # Check file size (should be 10000 bytes)
        file_size = fpath.stat().st_size
        size_ok = file_size == 10000
        section_2_4_3["checks"].append(
            {
                "item": f"{fname} size",
                "expected": "10000 bytes",
                "result": "PASS" if size_ok else f"FAIL ({file_size} bytes)",
            }
        )
        if not size_ok:
            section_2_4_3["status"] = "FAIL"

        # Check compression ratio (should be >= 100%, i.e., no compression)
        original_data = fpath.read_bytes()
        compressed_data = gzip.compress(original_data)
        ratio = len(compressed_data) / len(original_data)
        ratio_ok = ratio >= 1.0  # Should not compress well
        section_2_4_3["checks"].append(
            {
                "item": f"{fname} compression ratio",
                "expected": ">= 100% (incompressible)",
                "result": "PASS" if ratio_ok else f"FAIL ({ratio*100:.2f}%)",
            }
        )
        if not ratio_ok:
            section_2_4_3["status"] = "FAIL"

    results["sections"]["2.4.3"] = section_2_4_3

    # Section 2.4.4: Multi-Format Archive Contents
    section_2_4_4 = {
        "name": "2.4.4 Multi-Format Archive Contents",
        "checks": [],
        "status": "PASS",
    }

    archive_contents = compression_base / "multi_format" / "archive_contents"
    expected_archive_files = [
        "file1.txt",
        "file2.txt",
        "subdir/file3.txt",
    ]

    for fname in expected_archive_files:
        fpath = archive_contents / fname
        exists = fpath.exists() and fpath.is_file()
        section_2_4_4["checks"].append(
            {
                "item": f"archive_contents/{fname}",
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_4_4["status"] = "FAIL"

    results["sections"]["2.4.4"] = section_2_4_4

    # Calculate summary
    for section in results["sections"].values():
        for check in section["checks"]:
            results["summary"]["total"] += 1
            if check["result"] == "PASS" or check["result"].startswith("PASS"):
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1

    return results


def verify_phase2_large_files() -> Dict[str, any]:
    """Verify Phase 2.5: Large File Generation."""
    results = {
        "phase": "Phase 2.5: Large File Generation",
        "timestamp": datetime.now().isoformat(),
        "sections": {},
        "summary": {"passed": 0, "failed": 0, "total": 0},
    }

    # Section 2.5.1: Directory Structure
    section_2_5_1 = {
        "name": "2.5.1 Directory Structure",
        "checks": [],
        "status": "PASS",
    }

    sizes_dir = BASE_DIR / "text_files" / "sizes"
    split_dir = BASE_DIR / "split_join_test_data" / "split_source"

    for dir_path, desc in [
        (sizes_dir, "text_files/sizes"),
        (split_dir, "split_join_test_data/split_source"),
    ]:
        exists = dir_path.exists() and dir_path.is_dir()
        section_2_5_1["checks"].append(
            {
                "item": desc,
                "expected": "Directory exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_2_5_1["status"] = "FAIL"

    results["sections"]["2.5.1"] = section_2_5_1

    # Section 2.5.2: Text Size Variants
    section_2_5_2 = {
        "name": "2.5.2 Text Size Variants",
        "checks": [],
        "status": "PASS",
    }

    # Core files (required)
    text_files = {
        "perf_1mb_large.txt": (1 * 1024 * 1024, 1.2 * 1024 * 1024),  # 1MB - 1.2MB
        "perf_10mb_huge.txt": (10 * 1024 * 1024, 11 * 1024 * 1024),  # 10MB - 11MB
    }

    for fname, (min_size, max_size) in text_files.items():
        fpath = sizes_dir / fname
        exists = fpath.exists() and fpath.is_file()
        section_2_5_2["checks"].append(
            {
                "item": fname,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if exists:
            actual_size = fpath.stat().st_size
            size_ok = min_size <= actual_size <= max_size
            size_mb = actual_size / (1024 * 1024)
            section_2_5_2["checks"].append(
                {
                    "item": f"{fname} size",
                    "expected": f"{min_size//(1024*1024)}-{max_size//(1024*1024)} MB",
                    "result": (
                        f"PASS ({size_mb:.2f} MB)"
                        if size_ok
                        else f"FAIL ({size_mb:.2f} MB)"
                    ),
                }
            )
            if not size_ok:
                section_2_5_2["status"] = "FAIL"
        else:
            section_2_5_2["status"] = "FAIL"

    results["sections"]["2.5.2"] = section_2_5_2

    # Section 2.5.3: Binary Split Source Files
    section_2_5_3 = {
        "name": "2.5.3 Binary Split Source Files",
        "checks": [],
        "status": "PASS",
    }

    # Core binary file (required)
    split_1mb = split_dir / "split_small_1mb.bin"
    exists = split_1mb.exists() and split_1mb.is_file()
    section_2_5_3["checks"].append(
        {
            "item": "split_small_1mb.bin",
            "expected": "File exists",
            "result": "PASS" if exists else "FAIL",
        }
    )
    if exists:
        actual_size = split_1mb.stat().st_size
        expected_size = 1 * 1024 * 1024  # Exactly 1MB
        size_ok = actual_size == expected_size
        section_2_5_3["checks"].append(
            {
                "item": "split_small_1mb.bin size",
                "expected": "1,048,576 bytes (1 MB)",
                "result": (
                    f"PASS ({actual_size:,} bytes)"
                    if size_ok
                    else f"FAIL ({actual_size:,} bytes)"
                ),
            }
        )
        if not size_ok:
            section_2_5_3["status"] = "FAIL"
    else:
        section_2_5_3["status"] = "FAIL"

    results["sections"]["2.5.3"] = section_2_5_3

    # Calculate summary
    for section in results["sections"].values():
        for check in section["checks"]:
            results["summary"]["total"] += 1
            if check["result"] == "PASS" or check["result"].startswith("PASS"):
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1

    return results


def verify_phase3_permissions() -> Dict[str, any]:
    """Verify Phase 3.1: Windows File Attributes."""
    results = {
        "phase": "Phase 3.1: Windows File Attributes",
        "timestamp": datetime.now().isoformat(),
        "sections": {},
        "summary": {"passed": 0, "failed": 0, "total": 0},
    }

    perm_base = BASE_DIR / "permissions"

    # Section 3.1.1: Directory Structure
    section_3_1_1 = {
        "name": "3.1.1 Directory Structure",
        "checks": [],
        "status": "PASS",
    }

    expected_dirs = ["readonly", "hidden", "system", "acl_tests", "locked"]
    for dir_name in expected_dirs:
        dir_path = perm_base / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        section_3_1_1["checks"].append(
            {
                "item": f"permissions/{dir_name}",
                "expected": "Directory exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_3_1_1["status"] = "FAIL"

    results["sections"]["3.1.1"] = section_3_1_1

    # Section 3.1.2: Read-Only Files
    section_3_1_2 = {
        "name": "3.1.2 Read-Only Attribute Files",
        "checks": [],
        "status": "PASS",
    }

    readonly_file = perm_base / "readonly" / "perm_readonly.txt"
    readonly_dir = perm_base / "readonly" / "perm_readonly_dir"

    # Check file exists and has ReadOnly attribute
    if readonly_file.exists():
        import stat

        is_readonly = not os.access(readonly_file, os.W_OK)
        section_3_1_2["checks"].append(
            {
                "item": "perm_readonly.txt",
                "expected": "ReadOnly attribute",
                "result": "PASS" if is_readonly else "FAIL (not read-only)",
            }
        )
        if not is_readonly:
            section_3_1_2["status"] = "FAIL"
    else:
        section_3_1_2["checks"].append(
            {
                "item": "perm_readonly.txt",
                "expected": "File exists",
                "result": "FAIL",
            }
        )
        section_3_1_2["status"] = "FAIL"

    # Check directory exists and has ReadOnly attribute
    if readonly_dir.exists():
        section_3_1_2["checks"].append(
            {
                "item": "perm_readonly_dir/",
                "expected": "Directory exists",
                "result": "PASS",
            }
        )
    else:
        section_3_1_2["checks"].append(
            {
                "item": "perm_readonly_dir/",
                "expected": "Directory exists",
                "result": "FAIL",
            }
        )
        section_3_1_2["status"] = "FAIL"

    results["sections"]["3.1.2"] = section_3_1_2

    # Section 3.1.3: Hidden Files
    section_3_1_3 = {
        "name": "3.1.3 Hidden Attribute Files",
        "checks": [],
        "status": "PASS",
    }

    hidden_file = perm_base / "hidden" / "perm_hidden.txt"
    hidden_dir = perm_base / "hidden" / "perm_hidden_dir"

    # Check hidden file
    if hidden_file.exists():
        import ctypes

        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(hidden_file))
            is_hidden = bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN = 2
        except Exception:
            is_hidden = False
        section_3_1_3["checks"].append(
            {
                "item": "perm_hidden.txt",
                "expected": "Hidden attribute",
                "result": "PASS" if is_hidden else "FAIL (not hidden)",
            }
        )
        if not is_hidden:
            section_3_1_3["status"] = "FAIL"
    else:
        section_3_1_3["checks"].append(
            {
                "item": "perm_hidden.txt",
                "expected": "File exists",
                "result": "FAIL",
            }
        )
        section_3_1_3["status"] = "FAIL"

    # Check hidden directory
    if hidden_dir.exists():
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(hidden_dir))
            is_hidden = bool(attrs & 2)
        except Exception:
            is_hidden = False
        section_3_1_3["checks"].append(
            {
                "item": "perm_hidden_dir/",
                "expected": "Hidden attribute",
                "result": "PASS" if is_hidden else "FAIL (not hidden)",
            }
        )
        if not is_hidden:
            section_3_1_3["status"] = "FAIL"
    else:
        section_3_1_3["checks"].append(
            {
                "item": "perm_hidden_dir/",
                "expected": "Directory exists",
                "result": "FAIL",
            }
        )
        section_3_1_3["status"] = "FAIL"

    results["sections"]["3.1.3"] = section_3_1_3

    # Section 3.1.4: System Files
    section_3_1_4 = {
        "name": "3.1.4 System Attribute Files",
        "checks": [],
        "status": "PASS",
    }

    system_file = perm_base / "system" / "perm_system.txt"

    if system_file.exists():
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(system_file))
            is_system = bool(attrs & 4)  # FILE_ATTRIBUTE_SYSTEM = 4
        except Exception:
            is_system = False
        section_3_1_4["checks"].append(
            {
                "item": "perm_system.txt",
                "expected": "System attribute",
                "result": "PASS" if is_system else "FAIL (not system)",
            }
        )
        if not is_system:
            section_3_1_4["status"] = "FAIL"
    else:
        section_3_1_4["checks"].append(
            {
                "item": "perm_system.txt",
                "expected": "File exists",
                "result": "FAIL",
            }
        )
        section_3_1_4["status"] = "FAIL"

    results["sections"]["3.1.4"] = section_3_1_4

    # Section 3.1.5: ACL and Other Test Files
    section_3_1_5 = {
        "name": "3.1.5 ACL and Other Test Files",
        "checks": [],
        "status": "PASS",
    }

    other_files = [
        ("acl_tests/perm_inherited.txt", "ACL inherited test"),
        ("acl_tests/perm_explicit_deny.txt", "ACL explicit deny test"),
        ("acl_tests/perm_complex_acl.txt", "ACL complex test"),
        ("locked/perm_locked_simulation.txt", "Locked file simulation"),
    ]

    for rel_path, desc in other_files:
        fpath = perm_base / rel_path
        exists = fpath.exists() and fpath.is_file()
        section_3_1_5["checks"].append(
            {
                "item": rel_path,
                "expected": "File exists",
                "result": "PASS" if exists else "FAIL",
            }
        )
        if not exists:
            section_3_1_5["status"] = "FAIL"

    results["sections"]["3.1.5"] = section_3_1_5

    # Calculate summary
    for section in results["sections"].values():
        for check in section["checks"]:
            results["summary"]["total"] += 1
            if check["result"] == "PASS" or check["result"].startswith("PASS"):
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1

    return results


def print_results(results: Dict, verbose: bool = False):
    """Print verification results."""
    print(f"\n{'='*60}")
    print(f"  {results['phase']}")
    print(f"  Timestamp: {results['timestamp']}")
    print(f"{'='*60}\n")

    for section_id, section in results["sections"].items():
        status_icon = "✅" if section["status"] == "PASS" else "❌"
        print(f"{status_icon} {section['name']}: {section['status']}")

        if verbose:
            for check in section["checks"]:
                icon = "  ✓" if check["result"] == "PASS" else "  ✗"
                print(f"   {icon} {check['item']}: {check['result']}")
        print()

    # Summary
    print(f"{'='*60}")
    summary = results["summary"]
    pass_rate = (
        (summary["passed"] / summary["total"] * 100) if summary["total"] > 0 else 0
    )
    print(
        f"  Summary: {summary['passed']}/{summary['total']} checks passed ({pass_rate:.1f}%)"
    )
    print(f"{'='*60}\n")

    return summary["failed"] == 0


def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print("\n🔍 RFU Test Files Verification Script")
    print("=" * 60)

    all_passed = True

    # Run Phase 1 verification
    phase1_results = verify_phase1_directories()
    phase1_passed = print_results(phase1_results, verbose)
    all_passed = all_passed and phase1_passed

    # Run Phase 2.1 verification
    phase2_1_results = verify_phase2_duplicates()
    phase2_1_passed = print_results(phase2_1_results, verbose)
    all_passed = all_passed and phase2_1_passed

    # Run Phase 2.2 verification
    phase2_2_results = verify_phase2_sync_data()
    phase2_2_passed = print_results(phase2_2_results, verbose)
    all_passed = all_passed and phase2_2_passed

    # Run Phase 2.3 verification
    phase2_3_results = verify_phase2_checksum_data()
    phase2_3_passed = print_results(phase2_3_results, verbose)
    all_passed = all_passed and phase2_3_passed

    # Run Phase 2.4 verification
    phase2_4_results = verify_phase2_compression_data()
    phase2_4_passed = print_results(phase2_4_results, verbose)
    all_passed = all_passed and phase2_4_passed

    # Run Phase 2.5 verification
    phase2_5_results = verify_phase2_large_files()
    phase2_5_passed = print_results(phase2_5_results, verbose)
    all_passed = all_passed and phase2_5_passed

    # Run Phase 3.1 verification
    phase3_1_results = verify_phase3_permissions()
    phase3_1_passed = print_results(phase3_1_results, verbose)
    all_passed = all_passed and phase3_1_passed

    if all_passed:
        print("✅ All verification checks PASSED!")
        return 0
    else:
        print("❌ Some checks FAILED. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
