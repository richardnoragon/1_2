# RFU Test Files

This directory contains test files for the Richard's File Utilities test suite.

## Current Status

**Last Updated:** 2025-12-13
**Overall Status:** ✅ ALL PHASES COMPLETE (Including Optional Files)

### Phase 1: Directory Structure ✅ COMPLETE

| Directory                  | Status | Subdirectories                                  |
| -------------------------- | ------ | ----------------------------------------------- |
| text_files                 | ✅     | encodings, line_endings, content, sizes         |
| binary_files               | ✅     | images, documents, archives, executables, media |
| pdf_files                  | ✅     | standard, versions, security, edge_cases, sizes |
| special_names              | ✅     | unicode_names, special_chars, edge_names        |
| directory_structures       | ✅     | deep_nesting, empty_dirs, hardlinks, junctions  |
| permissions                | ✅     | readonly, hidden, system, acl_tests, locked     |
| metadata                   | ✅     | images, documents, audio                        |
| duplicates                 | ✅     | exact_duplicates, near_duplicates, etc.         |
| sync_test_data             | ✅     | source, destination, conflicts                  |
| checksum_test_data         | ✅     | integrity, known_hashes                         |
| compression_test_data      | ✅     | compressible, incompressible, multi_format      |
| split_join_test_data       | ✅     | split_source, split_results, join_source        |
| encryption_test_data       | ✅     | plaintext, encrypted, keys                      |
| secure_delete_test_data    | ✅     | single_pass, multi_pass, recovery_verification  |
| network_transfer_test_data | ✅     | small_files, large_files, resume_test           |
| performance_benchmarks     | ✅     | file_count, file_sizes, mixed_workload          |
| scripts                    | ✅     | Generation and verification scripts             |

**Total: 17/17 top-level directories verified**

### Phase 2: File Creation ✅ COMPLETE

| Section | Description                    | Status  | Files | Notes                           |
| ------- | ------------------------------ | ------- | ----- | ------------------------------- |
| 2.1     | Duplicate Detection Test Files | ✅ DONE | 13    | + checksums.md                  |
| 2.2     | Synchronization Test Data      | ✅ DONE | 13    | timestamps verified             |
| 2.3     | Checksum Verification Data     | ✅ DONE | 7     | hashes verified                 |
| 2.4     | Compression Test Data          | ✅ DONE | 8     | ratios verified                 |
| 2.5     | Large File Generation          | ✅ DONE | 15+   | 1.2GB total (including optional)  |
| 2.6     | Line Ending Test Files         | ✅ DONE | 4     | Created via structure gen       |
| 2.7     | Content Test Files             | ✅ DONE | 7     | Created via structure gen       |
| 2.8     | Binary Test Files (Images)     | ✅ DONE | 15    | BMP, PNG, GIF, JPEG, SVG, etc   |
| 2.9     | Binary Test Files (Docs)       | ✅ DONE | 11    | DOCX, XLSX, PPTX, ODT, ODS, RTF |
| 2.10    | Binary Test Files (Archives)   | ✅ DONE | 12    | ZIP, TAR, 7z, RAR formats       |

**Phase 2.5 Details (Large Files):**

- Text: 1MB, 10MB, 100MB files ✅
- Binary: 1MB, 100MB, 1GB files ✅
- Join parts: 3 x 350KB parts ✅
- Benchmarks: count_100, count_1000, count_10000, count_100000 directories ✅
- Total disk usage: ~1.4 GB

### Phase 3: Permission Configuration ✅ COMPLETE (2025-12-11)

| Item                    | Status | Verified   |
| ----------------------- | ------ | ---------- |
| ReadOnly files          | ✅     | 2025-12-11 |
| Hidden files            | ✅     | 2025-12-11 |
| System files            | ✅     | 2025-12-11 |
| ACL test placeholders   | ✅     | 2025-12-11 |
| Locked file placeholder | ✅     | 2025-12-11 |
| set_permissions.ps1     | ✅     | 2025-12-11 |

**Verified Attributes:**

- `perm_readonly.txt`: ReadOnly, Archive
- `perm_readonly_dir`: ReadOnly, Directory
- `perm_hidden.txt`: Hidden, Archive
- `perm_hidden_dir`: Hidden, Directory
- `perm_system.txt`: System, Archive

### Phase 4: Validation and Verification ✅ COMPLETE (2025-12-11)

| Phase Verified         | Checks  | Passed  | Status   |
| ---------------------- | ------- | ------- | -------- |
| Phase 1: Directory     | 26      | 26      | ✅       |
| Phase 2.1: Duplicates  | 16      | 16      | ✅       |
| Phase 2.2: Sync Data   | 27      | 27      | ✅       |
| Phase 2.3: Checksums   | 16      | 16      | ✅       |
| Phase 2.4: Compression | 23      | 23      | ✅       |
| Phase 2.5: Large Files | 8       | 8       | ✅       |
| Phase 3.1: Permissions | 14      | 14      | ✅       |
| **TOTAL**              | **130** | **130** | **100%** |

### Phase 5: Execution Sequence ✅ COMPLETE (2025-12-11)

| Step | Script                       | Status | Notes                         |
| ---- | ---------------------------- | ------ | ----------------------------- |
| 1    | Navigate to directory        | ✅     | `cd tests\user_test_files`    |
| 2    | `generate_test_structure.py` | ✅     | Main structure generator      |
| 9    | `generate_large_files.py`    | ✅     | 1MB, 10MB, 100MB files        |
| 10   | `set_permissions.ps1`        | ✅     | Windows attributes configured |
| 11   | `verify_test_files.py`       | ✅     | 130/130 checks passed (100%)  |

**Note:** Steps 3-8 (individual creation scripts) were consolidated into `generate_test_structure.py`.

## Structure

See `outline_of_user_test_documents.md` for the complete specification.

## Generation

Run `scripts/generate_test_structure.py` to regenerate the structure.
Run `scripts/generate_large_files.py` to generate large test files.
Run `scripts/generate_binary_test_files.py` to regenerate binary test files.
Run `scripts/generate_optional_files.py --all` to generate optional large-scale files (1GB, 10K, 100K).
Run `scripts/set_permissions.ps1` to configure Windows file attributes.
Run `scripts/verify_test_files.py --verbose` to verify the test structure.

## Quick Commands

```powershell
# Navigate to test files directory
cd C:\Users\HP1\1_2\tests\user_test_files

# Run verification (recommended first step)
python scripts/verify_test_files.py --verbose

# Regenerate structure if needed
python scripts/generate_test_structure.py

# Configure Windows file attributes (may require admin)
powershell -ExecutionPolicy Bypass -File scripts/set_permissions.ps1
```

## Note

Binary test files (images, documents, archives) have been generated with valid file headers and content structures.
Some formats (7z, RAR, encrypted archives) are placeholders with correct magic bytes - use external tools to create fully functional versions if needed for specific testing scenarios.

## Optional Large-Scale Files (2025-12-13)

The following optional files have been generated for stress/performance testing:

| Item             | Location                           | Size/Count    | Status |
| ---------------- | ---------------------------------- | ------------- | ------ |
| 1GB Binary       | split_join_test_data/split_source/ | 1 GB          | ✅     |
| 10K File Count   | performance_benchmarks/count_10000/  | 10,000 files  | ✅     |
| 100K File Count  | performance_benchmarks/count_100000/ | 100,000 files | ✅     |

To regenerate optional files:
```powershell
python scripts/generate_optional_files.py --all
```
