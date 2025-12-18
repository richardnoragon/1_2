#!/usr/bin/env python3
"""
Test File Structure Generator for RFU Test Suite.
Generates all required directories and placeholder files based on the
outline_of_user_test_documents.md specification.

Usage: python generate_test_structure.py
"""

import os
from pathlib import Path

# Base directory for test files
BASE_DIR = Path(__file__).parent.parent


def create_placeholder_file(filepath: Path, content: str = None):
    """Create a placeholder file with optional content."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if content is None:
        # Generate default content based on file extension
        ext = filepath.suffix.lower()
        if ext in [".txt", ".md"]:
            content = (
                f"# Placeholder file: {filepath.name}\n# Generated for RFU test suite\n"
            )
        elif ext in [".bin", ".dat"]:
            content = b"\x00" * 10  # Binary placeholder
        elif ext in [".py"]:
            content = (
                f'# Placeholder: {filepath.name}\n"""Test placeholder file."""\npass\n'
            )
        elif ext in [".bat"]:
            content = f"REM Placeholder: {filepath.name}\n@echo off\n"
        elif ext in [".ps1"]:
            content = f'# Placeholder: {filepath.name}\nWrite-Host "Placeholder"\n'
        else:
            content = f"Placeholder file: {filepath.name}\n"

    # Write content
    if isinstance(content, bytes):
        with open(filepath, "wb") as f:
            f.write(content)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"  Created: {filepath.relative_to(BASE_DIR)}")


def create_directory(dirpath: Path):
    """Create a directory if it doesn't exist."""
    dirpath.mkdir(parents=True, exist_ok=True)
    print(f"  Created dir: {dirpath.relative_to(BASE_DIR)}")


def generate_structure():
    """Generate the complete test file structure."""
    print("=" * 60)
    print("RFU Test File Structure Generator")
    print("=" * 60)
    print(f"\nBase directory: {BASE_DIR}\n")

    # =========================================================================
    # TEXT FILES
    # =========================================================================
    print("\n[1/15] Creating text_files/ structure...")

    # Encodings
    encodings_dir = BASE_DIR / "text_files" / "encodings"
    encoding_files = [
        ("enc_utf8_bom.txt", "\ufeffUTF-8 with BOM content\nLine 2\n"),
        ("enc_utf8_nobom.txt", "UTF-8 without BOM content\nLine 2\n"),
        ("enc_utf16_le.txt", "UTF-16 LE content"),  # Will need special handling
        ("enc_utf16_be.txt", "UTF-16 BE content"),
        ("enc_ascii.txt", "ASCII only content 123\n"),
        ("enc_latin1.txt", "Latin-1: café résumé\n"),
        ("enc_windows1252.txt", "Windows-1252: smart quotes\n"),
        ("enc_mixed_invalid.txt", "Mixed with invalid bytes\n"),
    ]
    for fname, content in encoding_files:
        create_placeholder_file(encodings_dir / fname, content)

    # Line endings
    line_endings_dir = BASE_DIR / "text_files" / "line_endings"
    create_placeholder_file(
        line_endings_dir / "le_unix_lf.txt", "Line 1\nLine 2\nLine 3\n"
    )
    create_placeholder_file(
        line_endings_dir / "le_windows_crlf.txt", "Line 1\r\nLine 2\r\nLine 3\r\n"
    )
    create_placeholder_file(
        line_endings_dir / "le_mac_cr.txt", "Line 1\rLine 2\rLine 3\r"
    )
    create_placeholder_file(
        line_endings_dir / "le_mixed.txt", "Line 1\nLine 2\r\nLine 3\rLine 4\n"
    )

    # Content
    content_dir = BASE_DIR / "text_files" / "content"
    create_placeholder_file(
        content_dir / "pos_read_basic_small.txt", "Basic read test content.\n"
    )
    create_placeholder_file(
        content_dir / "pos_read_unicode_medium.txt",
        "Unicode: 日本語 中文 한국어 العربية\n" * 100,
    )
    create_placeholder_file(
        content_dir / "pos_read_multilang_medium.txt",
        "Multi: English Español Français Deutsch\n" * 100,
    )
    create_placeholder_file(
        content_dir / "edge_whitespace_only.txt", "   \t\n   \t\n   "
    )
    create_placeholder_file(content_dir / "edge_single_char.txt", "a")
    create_placeholder_file(
        content_dir / "edge_no_newline_eof.txt", "No newline at end"
    )
    create_placeholder_file(
        content_dir / "edge_binary_in_text.txt", "Text with binary: \x00\x01\x02"
    )

    # Sizes (placeholder - actual large files would be generated separately)
    sizes_dir = BASE_DIR / "text_files" / "sizes"
    create_placeholder_file(sizes_dir / "bound_0b_empty.txt", "")
    create_placeholder_file(sizes_dir / "bound_1b_minimal.txt", "a")
    create_placeholder_file(
        sizes_dir / "perf_1mb_large.txt",
        "Large file placeholder - generate actual 1MB content\n",
    )
    create_placeholder_file(
        sizes_dir / "perf_10mb_huge.txt",
        "Huge file placeholder - generate actual 10MB content\n",
    )
    create_placeholder_file(
        sizes_dir / "perf_100mb_extreme.txt",
        "Extreme file placeholder - generate actual 100MB content\n",
    )

    # =========================================================================
    # BINARY FILES
    # =========================================================================
    print("\n[2/15] Creating binary_files/ structure...")

    # Images
    images_dir = BASE_DIR / "binary_files" / "images"
    image_files = [
        "img_jpeg_standard.jpg",
        "img_jpeg_progressive.jpg",
        "img_png_standard.png",
        "img_png_interlaced.png",
        "img_gif_static.gif",
        "img_gif_animated.gif",
        "img_bmp_24bit.bmp",
        "img_tiff_uncompressed.tiff",
        "img_webp_lossy.webp",
        "img_webp_lossless.webp",
        "img_ico_multi.ico",
        "img_svg_vector.svg",
        "edge_img_corrupted.jpg",
        "edge_img_truncated.png",
        "edge_img_wrong_extension.txt",
    ]
    for fname in image_files:
        create_placeholder_file(
            images_dir / fname,
            (
                f"Binary placeholder: {fname}\n".encode()
                if fname.endswith(".txt")
                else b"\x00" * 10
            ),
        )

    # Documents
    docs_dir = BASE_DIR / "binary_files" / "documents"
    doc_files = [
        "doc_word_docx.docx",
        "doc_word_doc.doc",
        "doc_excel_xlsx.xlsx",
        "doc_excel_xls.xls",
        "doc_powerpoint_pptx.pptx",
        "doc_powerpoint_ppt.ppt",
        "doc_odt_openoffice.odt",
        "doc_ods_openoffice.ods",
        "doc_rtf_richtext.rtf",
        "edge_doc_corrupted.docx",
        "edge_doc_password_protected.xlsx",
    ]
    for fname in doc_files:
        create_placeholder_file(docs_dir / fname, b"\x00" * 10)

    # Archives
    archives_dir = BASE_DIR / "binary_files" / "archives"
    archive_files = [
        "arch_zip_standard.zip",
        "arch_zip_encrypted.zip",
        "arch_7z_standard.7z",
        "arch_7z_encrypted.7z",
        "arch_tar_uncompressed.tar",
        "arch_tar_gzip.tar.gz",
        "arch_tar_bzip2.tar.bz2",
        "arch_tar_xz.tar.xz",
        "arch_rar_standard.rar",
        "arch_nested_archives.zip",
        "edge_arch_corrupted.zip",
        "edge_arch_zip_bomb.zip",
    ]
    for fname in archive_files:
        create_placeholder_file(archives_dir / fname, b"\x00" * 10)

    # Executables
    exe_dir = BASE_DIR / "binary_files" / "executables"
    create_placeholder_file(
        exe_dir / "exe_windows_pe.exe", b"MZ" + b"\x00" * 8
    )  # PE header start
    create_placeholder_file(exe_dir / "exe_dll_library.dll", b"MZ" + b"\x00" * 8)
    create_placeholder_file(
        exe_dir / "exe_batch_script.bat", "@echo off\nREM Test batch file\n"
    )
    create_placeholder_file(
        exe_dir / "exe_powershell.ps1", "# Test PowerShell script\nWrite-Host 'Test'\n"
    )
    create_placeholder_file(
        exe_dir / "exe_python_script.py",
        "#!/usr/bin/env python3\n# Test Python script\nprint('Test')\n",
    )
    create_placeholder_file(
        exe_dir / "edge_exe_fake_extension.txt", b"MZ" + b"\x00" * 8
    )

    # Media
    media_dir = BASE_DIR / "binary_files" / "media"
    media_files = [
        "media_mp3_audio.mp3",
        "media_wav_audio.wav",
        "media_flac_audio.flac",
        "media_mp4_video.mp4",
        "media_avi_video.avi",
        "media_mkv_video.mkv",
        "edge_media_corrupted.mp4",
    ]
    for fname in media_files:
        create_placeholder_file(media_dir / fname, b"\x00" * 10)

    # =========================================================================
    # PDF FILES
    # =========================================================================
    print("\n[3/15] Creating pdf_files/ structure...")

    # Standard PDFs
    pdf_standard_dir = BASE_DIR / "pdf_files" / "standard"
    pdf_standard = [
        "pdf_text_only.pdf",
        "pdf_images_embedded.pdf",
        "pdf_forms_interactive.pdf",
        "pdf_annotations.pdf",
        "pdf_bookmarks.pdf",
        "pdf_layers.pdf",
        "pdf_attachments.pdf",
    ]
    for fname in pdf_standard:
        create_placeholder_file(pdf_standard_dir / fname, b"%PDF-1.7\n% Placeholder\n")

    # PDF versions
    pdf_versions_dir = BASE_DIR / "pdf_files" / "versions"
    for ver in ["1_4", "1_5", "1_6", "1_7", "2_0"]:
        create_placeholder_file(
            pdf_versions_dir / f"pdf_v{ver}.pdf",
            f"%PDF-{ver.replace('_', '.')}\n% Placeholder\n".encode(),
        )

    # PDF security
    pdf_security_dir = BASE_DIR / "pdf_files" / "security"
    pdf_security = [
        "pdf_password_user.pdf",
        "pdf_password_owner.pdf",
        "pdf_encrypted_aes128.pdf",
        "pdf_encrypted_aes256.pdf",
        "pdf_signed_digital.pdf",
        "pdf_permissions_restricted.pdf",
    ]
    for fname in pdf_security:
        create_placeholder_file(pdf_security_dir / fname, b"%PDF-1.7\n% Placeholder\n")

    # PDF edge cases
    pdf_edge_dir = BASE_DIR / "pdf_files" / "edge_cases"
    pdf_edge = [
        "edge_pdf_corrupted.pdf",
        "edge_pdf_truncated.pdf",
        "edge_pdf_linearized.pdf",
        "edge_pdf_incremental.pdf",
        "edge_pdf_cross_ref_stream.pdf",
        "edge_pdf_object_streams.pdf",
    ]
    for fname in pdf_edge:
        create_placeholder_file(pdf_edge_dir / fname, b"%PDF-1.7\n% Placeholder\n")

    # PDF sizes
    pdf_sizes_dir = BASE_DIR / "pdf_files" / "sizes"
    create_placeholder_file(
        pdf_sizes_dir / "pdf_tiny_1page.pdf", b"%PDF-1.7\n% Placeholder\n"
    )
    create_placeholder_file(
        pdf_sizes_dir / "pdf_medium_100pages.pdf", b"%PDF-1.7\n% Placeholder\n"
    )
    create_placeholder_file(
        pdf_sizes_dir / "pdf_large_1000pages.pdf", b"%PDF-1.7\n% Placeholder\n"
    )

    # =========================================================================
    # SPECIAL NAMES
    # =========================================================================
    print("\n[4/15] Creating special_names/ structure...")

    # Unicode names
    unicode_dir = BASE_DIR / "special_names" / "unicode_names"
    unicode_files = [
        "日本語ファイル.txt",
        "файл_кириллица.txt",
        "αρχείο_ελληνικά.txt",
        "文件_中文.txt",
        "ملف_عربي.txt",
        "קובץ_עברית.txt",
        "🎉emoji_file🎊.txt",
        "mixed_Miš€d_名前.txt",
    ]
    for fname in unicode_files:
        try:
            create_placeholder_file(
                unicode_dir / fname, f"Unicode test file: {fname}\n"
            )
        except Exception as e:
            print(f"  Warning: Could not create {fname}: {e}")

    # Special characters
    special_chars_dir = BASE_DIR / "special_names" / "special_chars"
    special_char_files = [
        "spaces in name.txt",
        "multiple   spaces.txt",
        "leading_space .txt",
        "trailing_space .txt",
        "file.multiple.dots.txt",
        "file-with-dashes.txt",
        "file_with_underscores.txt",
        "file(with)parentheses.txt",
        "file[with]brackets.txt",
        "file{with}braces.txt",
        "file'with'quotes.txt",
        "file`with`backticks.txt",
        "file~with~tildes.txt",
        "file@with@at.txt",
        "file#with#hash.txt",
        "file$with$dollar.txt",
        "file%with%percent.txt",
        "file^with^caret.txt",
        "file&with&ampersand.txt",
        "file+with+plus.txt",
        "file=with=equals.txt",
        "file;with;semicolon.txt",
    ]
    for fname in special_char_files:
        try:
            create_placeholder_file(
                special_chars_dir / fname, f"Special char test: {fname}\n"
            )
        except Exception as e:
            print(f"  Warning: Could not create {fname}: {e}")

    # Edge names
    edge_names_dir = BASE_DIR / "special_names" / "edge_names"
    create_placeholder_file(
        edge_names_dir / ".hidden_file.txt", "Hidden file content\n"
    )
    create_placeholder_file(
        edge_names_dir / ".hidden_no_ext", "Hidden file no extension\n"
    )
    create_placeholder_file(edge_names_dir / "no_extension", "File without extension\n")
    create_placeholder_file(edge_names_dir / ".dotfile", "Dotfile content\n")
    create_placeholder_file(
        edge_names_dir / "..double_dot_start.txt", "Double dot start\n"
    )
    create_placeholder_file(edge_names_dir / "UPPERCASE.TXT", "UPPERCASE filename\n")
    create_placeholder_file(edge_names_dir / "lowercase.txt", "lowercase filename\n")
    create_placeholder_file(edge_names_dir / "MixedCase.Txt", "MixedCase filename\n")
    create_placeholder_file(edge_names_dir / "a.txt", "Single char name\n")
    create_placeholder_file(edge_names_dir / "ab.txt", "Two char name\n")
    # Long filename (truncated for safety)
    long_name = "verylongfilename" + "a" * 200 + ".txt"
    try:
        create_placeholder_file(
            edge_names_dir / long_name[:250], "Long filename test\n"
        )
    except Exception as e:
        create_placeholder_file(
            edge_names_dir / "verylongfilename_placeholder.txt",
            "Long filename placeholder\n",
        )

    # Reserved names (Windows safe versions)
    reserved_dir = BASE_DIR / "special_names" / "reserved_names"
    reserved_files = [
        "CON_.txt",
        "PRN_.txt",
        "AUX_.txt",
        "NUL_.txt",
        "COM1_.txt",
        "LPT1_.txt",
    ]
    for fname in reserved_files:
        create_placeholder_file(reserved_dir / fname, f"Reserved name test: {fname}\n")
    create_placeholder_file(
        reserved_dir / "reserved_name_test_note.md",
        "# Reserved Names Test\n\nThese files use escaped versions of Windows reserved names.\n",
    )

    # =========================================================================
    # DIRECTORY STRUCTURES
    # =========================================================================
    print("\n[5/15] Creating directory_structures/ structure...")

    # Empty directories
    empty_dirs = [
        "directory_structures/empty_dirs/empty_single",
        "directory_structures/empty_dirs/empty_nested/level2/level3",
        "directory_structures/empty_dirs/empty_with_hidden/.hidden_empty",
    ]
    for d in empty_dirs:
        create_directory(BASE_DIR / d)

    # Deep nesting (create 20 levels for practicality, not 50)
    deep_path = BASE_DIR / "directory_structures" / "deep_nesting"
    for i in range(1, 21):
        deep_path = deep_path / f"level{i:02d}"
    create_directory(deep_path)
    create_placeholder_file(deep_path / "deepest_file.txt", "File at deepest level\n")

    # Wide directories placeholder
    wide_dir = BASE_DIR / "directory_structures" / "wide_dirs" / "many_files"
    create_directory(wide_dir)
    create_placeholder_file(
        wide_dir / "README.md",
        "# Wide Directory\n\nThis directory should contain 10,000+ files for testing.\nUse generate_test_files.py to populate.\n",
    )
    # Create a few sample files
    for i in range(10):
        create_placeholder_file(wide_dir / f"file_{i:05d}.txt", f"File {i}\n")

    # Symlinks directory (create targets, actual symlinks need admin on Windows)
    symlinks_dir = BASE_DIR / "directory_structures" / "symlinks"
    create_placeholder_file(symlinks_dir / "target.txt", "Symlink target file\n")
    create_directory(symlinks_dir / "target_dir")
    create_placeholder_file(
        symlinks_dir / "target_dir" / "file_in_target.txt", "File in target directory\n"
    )
    create_placeholder_file(
        symlinks_dir / "SYMLINKS_NOTE.md",
        "# Symlinks\n\nActual symlinks must be created manually or with admin rights on Windows.\n"
        "Target files are provided for link creation.\n",
    )

    # Junction points
    junction_dir = (
        BASE_DIR / "directory_structures" / "junction_points" / "junction_test"
    )
    create_directory(junction_dir)
    create_placeholder_file(
        junction_dir / "JUNCTION_NOTE.md",
        "# Junction Point\n\nCreate actual junction with mklink /J\n",
    )

    # Hard links
    hardlinks_dir = BASE_DIR / "directory_structures" / "hardlinks"
    create_placeholder_file(
        hardlinks_dir / "original.txt", "Original file for hard link test\n"
    )
    create_placeholder_file(
        hardlinks_dir / "HARDLINK_NOTE.md",
        "# Hard Links\n\nCreate hardlink.txt as hard link to original.txt:\nmklink /H hardlink.txt original.txt\n",
    )

    # =========================================================================
    # PERMISSIONS
    # =========================================================================
    print("\n[6/15] Creating permissions/ structure...")

    # Read-only
    readonly_dir = BASE_DIR / "permissions" / "readonly"
    create_placeholder_file(
        readonly_dir / "perm_readonly.txt", "Read-only file content\n"
    )
    create_directory(readonly_dir / "perm_readonly_dir")

    # Hidden
    hidden_dir = BASE_DIR / "permissions" / "hidden"
    create_placeholder_file(hidden_dir / "perm_hidden.txt", "Hidden file content\n")
    create_directory(hidden_dir / "perm_hidden_dir")

    # System
    system_dir = BASE_DIR / "permissions" / "system"
    create_placeholder_file(
        system_dir / "perm_system.txt", "System attribute file content\n"
    )

    # Locked
    locked_dir = BASE_DIR / "permissions" / "locked"
    create_placeholder_file(
        locked_dir / "perm_locked_simulation.txt", "Locked file simulation\n"
    )

    # ACL tests
    acl_dir = BASE_DIR / "permissions" / "acl_tests"
    create_placeholder_file(
        acl_dir / "perm_inherited.txt", "Inherited permissions test\n"
    )
    create_placeholder_file(acl_dir / "perm_explicit_deny.txt", "Explicit deny test\n")
    create_placeholder_file(acl_dir / "perm_complex_acl.txt", "Complex ACL test\n")

    # =========================================================================
    # METADATA
    # =========================================================================
    print("\n[7/15] Creating metadata/ structure...")

    # Image metadata
    meta_images_dir = BASE_DIR / "metadata" / "images"
    image_meta_files = [
        "meta_exif_full.jpg",
        "meta_exif_gps.jpg",
        "meta_exif_camera.jpg",
        "meta_iptc_keywords.jpg",
        "meta_xmp_data.jpg",
        "meta_no_metadata.jpg",
        "meta_stripped.jpg",
        "meta_corrupt_exif.jpg",
    ]
    for fname in image_meta_files:
        create_placeholder_file(
            meta_images_dir / fname, b"\xff\xd8\xff\xe0" + b"\x00" * 10
        )

    # Document metadata
    meta_docs_dir = BASE_DIR / "metadata" / "documents"
    doc_meta_files = [
        "meta_office_full.docx",
        "meta_office_author.docx",
        "meta_office_custom.xlsx",
        "meta_pdf_full.pdf",
        "meta_pdf_xmp.pdf",
    ]
    for fname in doc_meta_files:
        if fname.endswith(".pdf"):
            create_placeholder_file(meta_docs_dir / fname, b"%PDF-1.7\n% Placeholder\n")
        else:
            create_placeholder_file(meta_docs_dir / fname, b"\x00" * 10)

    # Audio metadata
    meta_audio_dir = BASE_DIR / "metadata" / "audio"
    audio_meta_files = [
        "meta_mp3_id3v1.mp3",
        "meta_mp3_id3v2.mp3",
        "meta_flac_vorbis.flac",
        "meta_mp3_no_tags.mp3",
    ]
    for fname in audio_meta_files:
        create_placeholder_file(meta_audio_dir / fname, b"\x00" * 10)

    # =========================================================================
    # DUPLICATES
    # =========================================================================
    print("\n[8/15] Creating duplicates/ structure...")

    # Exact duplicates
    exact_dup_dir = BASE_DIR / "duplicates" / "exact_duplicates"
    dup_content = "This is duplicate content for testing.\nLine 2 of duplicate.\n"
    create_placeholder_file(exact_dup_dir / "dup_original.txt", dup_content)
    create_placeholder_file(exact_dup_dir / "dup_copy1.txt", dup_content)
    create_placeholder_file(exact_dup_dir / "dup_copy2.txt", dup_content)

    # Near duplicates
    near_dup_dir = BASE_DIR / "duplicates" / "near_duplicates"
    create_placeholder_file(
        near_dup_dir / "near_dup_v1.txt",
        "Near duplicate version 1\nSame base content\n",
    )
    create_placeholder_file(
        near_dup_dir / "near_dup_v2.txt",
        "Near duplicate version 2\nSame base content\n",
    )
    create_placeholder_file(
        near_dup_dir / "near_dup_v3.txt",
        "Near duplicate version 3\nSame base content\n",
    )

    # Same name different content
    same_name_dir = BASE_DIR / "duplicates" / "same_name_diff_content"
    create_placeholder_file(
        same_name_dir / "folder_a" / "document.txt", "Content version A\n"
    )
    create_placeholder_file(
        same_name_dir / "folder_b" / "document.txt", "Content version B - different\n"
    )

    # Same content different name
    same_content_dir = BASE_DIR / "duplicates" / "same_content_diff_name"
    identical_content = "Identical content across different filenames\n"
    create_placeholder_file(same_content_dir / "file_alpha.txt", identical_content)
    create_placeholder_file(same_content_dir / "file_beta.txt", identical_content)
    create_placeholder_file(same_content_dir / "file_gamma.txt", identical_content)

    # Hash collision test
    hash_collision_dir = BASE_DIR / "duplicates" / "hash_collision_test"
    create_placeholder_file(hash_collision_dir / "collision_a.bin", b"\x00" * 100)
    create_placeholder_file(hash_collision_dir / "collision_b.bin", b"\x01" * 100)

    # =========================================================================
    # SYNC TEST DATA
    # =========================================================================
    print("\n[9/15] Creating sync_test_data/ structure...")

    # Source
    sync_source = BASE_DIR / "sync_test_data" / "source"
    create_placeholder_file(
        sync_source / "unchanged" / "stable.txt", "Stable unchanged content\n"
    )
    create_placeholder_file(
        sync_source / "modified" / "changed.txt", "Source version - newer\n"
    )
    create_placeholder_file(
        sync_source / "new_files" / "added.txt", "New file in source\n"
    )
    create_placeholder_file(
        sync_source / "nested" / "level1" / "nested_file.txt", "Nested file content\n"
    )
    create_placeholder_file(
        sync_source / "deleted_from_dest" / "removed.txt",
        "File removed from destination\n",
    )

    # Destination
    sync_dest = BASE_DIR / "sync_test_data" / "destination"
    create_placeholder_file(
        sync_dest / "unchanged" / "stable.txt", "Stable unchanged content\n"
    )
    create_placeholder_file(
        sync_dest / "modified" / "changed.txt", "Destination version - older\n"
    )
    create_placeholder_file(
        sync_dest / "deleted_from_source" / "orphaned.txt",
        "Orphaned file in destination\n",
    )
    create_placeholder_file(
        sync_dest / "nested" / "level1" / "nested_file.txt", "Nested file content\n"
    )

    # Conflicts
    sync_conflicts = BASE_DIR / "sync_test_data" / "conflicts"
    create_directory(sync_conflicts / "both_modified")
    create_directory(sync_conflicts / "name_conflicts")

    # =========================================================================
    # CHECKSUM TEST DATA
    # =========================================================================
    print("\n[10/15] Creating checksum_test_data/ structure...")

    # Known hashes
    known_hashes_dir = BASE_DIR / "checksum_test_data" / "known_hashes"
    create_placeholder_file(known_hashes_dir / "md5_test.txt", "test content for MD5")
    create_placeholder_file(known_hashes_dir / "sha1_test.txt", "test content for SHA1")
    create_placeholder_file(
        known_hashes_dir / "sha256_test.txt", "test content for SHA256"
    )
    create_placeholder_file(
        known_hashes_dir / "sha512_test.txt", "test content for SHA512"
    )
    create_placeholder_file(
        known_hashes_dir / "checksums.txt",
        "# Known checksums for test files\n"
        "md5_test.txt: MD5=9a0364b9e99bb480dd25e1f0284c8555\n"
        "sha1_test.txt: SHA1=placeholder\n"
        "sha256_test.txt: SHA256=placeholder\n"
        "sha512_test.txt: SHA512=placeholder\n",
    )

    # Integrity
    integrity_dir = BASE_DIR / "checksum_test_data" / "integrity"
    create_placeholder_file(
        integrity_dir / "original_intact.txt", "Original intact content\n"
    )
    create_placeholder_file(
        integrity_dir / "modified_corrupted.txt", "Modified/corrupted content\n"
    )

    # =========================================================================
    # COMPRESSION TEST DATA
    # =========================================================================
    print("\n[11/15] Creating compression_test_data/ structure...")

    # Compressible
    comp_dir = BASE_DIR / "compression_test_data" / "compressible"
    create_placeholder_file(comp_dir / "comp_text_repetitive.txt", "AAAA" * 1000 + "\n")
    create_placeholder_file(comp_dir / "comp_zeros.bin", b"\x00" * 1000)
    create_placeholder_file(comp_dir / "comp_pattern.bin", b"\xab\xcd" * 500)

    # Incompressible
    incomp_dir = BASE_DIR / "compression_test_data" / "incompressible"
    import os as os_module

    create_placeholder_file(incomp_dir / "incomp_random.bin", os_module.urandom(100))
    create_placeholder_file(incomp_dir / "incomp_encrypted.bin", os_module.urandom(100))
    create_placeholder_file(
        incomp_dir / "incomp_jpeg.jpg", b"\xff\xd8\xff" + os_module.urandom(97)
    )

    # Multi-format
    multi_format_dir = BASE_DIR / "compression_test_data" / "multi_format"
    create_placeholder_file(
        multi_format_dir / "archive_contents" / "file1.txt", "Archive content file 1\n"
    )
    create_placeholder_file(
        multi_format_dir / "archive_contents" / "file2.txt", "Archive content file 2\n"
    )
    create_placeholder_file(
        multi_format_dir / "archive_contents" / "subdir" / "file3.txt",
        "Archive subdir file 3\n",
    )
    create_directory(multi_format_dir / "expected_archives")

    # =========================================================================
    # SPLIT/JOIN TEST DATA
    # =========================================================================
    print("\n[12/15] Creating split_join_test_data/ structure...")

    # Split source
    split_source_dir = BASE_DIR / "split_join_test_data" / "split_source"
    create_placeholder_file(
        split_source_dir / "split_small_1mb.bin", b"\x00" * 100
    )  # Placeholder
    create_placeholder_file(split_source_dir / "split_medium_100mb.bin", b"\x00" * 100)
    create_placeholder_file(split_source_dir / "split_large_1gb.bin", b"\x00" * 100)

    # Split results
    create_directory(BASE_DIR / "split_join_test_data" / "split_results")

    # Join source
    join_source_dir = BASE_DIR / "split_join_test_data" / "join_source"
    create_placeholder_file(join_source_dir / "part_001.bin", b"\x01" * 100)
    create_placeholder_file(join_source_dir / "part_002.bin", b"\x02" * 100)
    create_placeholder_file(join_source_dir / "part_003.bin", b"\x03" * 100)

    # =========================================================================
    # ENCRYPTION TEST DATA
    # =========================================================================
    print("\n[13/15] Creating encryption_test_data/ structure...")

    # Plaintext
    plaintext_dir = BASE_DIR / "encryption_test_data" / "plaintext"
    create_placeholder_file(
        plaintext_dir / "enc_text_simple.txt", "Simple text for encryption test\n"
    )
    create_placeholder_file(
        plaintext_dir / "enc_binary_data.bin", b"\x00\x01\x02\x03" * 25
    )
    create_placeholder_file(
        plaintext_dir / "enc_sensitive_data.txt", "Sensitive data placeholder\n"
    )

    # Encrypted
    encrypted_dir = BASE_DIR / "encryption_test_data" / "encrypted"
    create_placeholder_file(encrypted_dir / "enc_aes256_cbc.enc", b"\x00" * 100)
    create_placeholder_file(encrypted_dir / "enc_aes256_gcm.enc", b"\x00" * 100)
    create_placeholder_file(encrypted_dir / "enc_wrong_password.enc", b"\x00" * 100)

    # Keys
    keys_dir = BASE_DIR / "encryption_test_data" / "keys"
    create_placeholder_file(
        keys_dir / "test_keyfile.key",
        "# TEST KEY - NOT FOR PRODUCTION\nkey_placeholder_data\n",
    )

    # =========================================================================
    # SECURE DELETE TEST DATA
    # =========================================================================
    print("\n[14/15] Creating secure_delete_test_data/ structure...")

    secure_del_dir = BASE_DIR / "secure_delete_test_data"
    create_placeholder_file(
        secure_del_dir / "single_pass" / "delete_me_single.txt",
        "Single pass delete test\n",
    )
    create_placeholder_file(
        secure_del_dir / "multi_pass" / "delete_me_multi.txt",
        "Multi pass delete test\n",
    )
    create_placeholder_file(
        secure_del_dir / "recovery_verification" / "verify_deletion.txt",
        "Recovery verification test\n",
    )

    # =========================================================================
    # NETWORK TRANSFER TEST DATA
    # =========================================================================
    print("\n[15/15] Creating remaining test directories...")

    network_dir = BASE_DIR / "network_transfer_test_data"
    create_placeholder_file(
        network_dir / "small_files" / "small_transfer.txt", "Small file for transfer\n"
    )
    create_placeholder_file(
        network_dir / "large_files" / "large_transfer.bin", b"\x00" * 100
    )
    create_placeholder_file(
        network_dir / "resume_test" / "resume_file.bin", b"\x00" * 100
    )

    # Performance benchmarks
    perf_dir = BASE_DIR / "performance_benchmarks"
    for count_dir in ["count_100", "count_1000", "count_10000", "count_100000"]:
        create_directory(perf_dir / "file_count" / count_dir)
        create_placeholder_file(
            perf_dir / "file_count" / count_dir / "README.md",
            f"# {count_dir}\n\nThis directory should contain {count_dir.split('_')[1]} files for benchmarking.\n",
        )

    for size_dir in ["size_1kb", "size_1mb", "size_100mb", "size_1gb"]:
        create_directory(perf_dir / "file_sizes" / size_dir)
        create_placeholder_file(
            perf_dir / "file_sizes" / size_dir / "README.md",
            f"# {size_dir}\n\nThis directory should contain files of {size_dir.split('_')[1]} for benchmarking.\n",
        )

    create_directory(perf_dir / "mixed_workload" / "realistic_directory")
    create_placeholder_file(
        perf_dir / "mixed_workload" / "realistic_directory" / "README.md",
        "# Realistic Directory\n\nThis directory should contain a realistic mix of files for workload testing.\n",
    )

    # =========================================================================
    # SCRIPTS DIRECTORY
    # =========================================================================
    print("\n[Bonus] Creating scripts/ helpers...")

    scripts_dir = BASE_DIR / "scripts"
    create_placeholder_file(
        scripts_dir / "verify_test_files.py",
        '#!/usr/bin/env python3\n"""Verify all test files exist and are valid."""\n\n# TODO: Implement verification\npass\n',
    )
    create_placeholder_file(
        scripts_dir / "cleanup_test_files.py",
        '#!/usr/bin/env python3\n"""Clean up generated test files."""\n\n# TODO: Implement cleanup\npass\n',
    )
    create_placeholder_file(
        scripts_dir / "generate_large_files.py",
        '#!/usr/bin/env python3\n"""Generate large test files for performance testing."""\n\n# TODO: Implement large file generation\npass\n',
    )

    # =========================================================================
    # README
    # =========================================================================
    create_placeholder_file(
        BASE_DIR / "README.md",
        "# RFU Test Files\n\n"
        "This directory contains test files for the Richard's File Utilities test suite.\n\n"
        "## Structure\n\n"
        "See `outline_of_user_test_documents.md` for the complete specification.\n\n"
        "## Generation\n\n"
        "Run `scripts/generate_test_structure.py` to regenerate the structure.\n"
        "Run `scripts/generate_large_files.py` to generate large test files.\n\n"
        "## Note\n\n"
        "Many files are placeholders. Use the generation scripts to create actual test content.\n",
    )

    print("\n" + "=" * 60)
    print("Structure generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    generate_structure()
