#!/usr/bin/env python3
"""
Generate large test files for performance testing.

This script creates large files for:
- Performance benchmarking
- Split/join testing
- Stress testing

Usage:
    python generate_large_files.py [--all] [--text] [--binary] [--benchmarks]
    
Options:
    --all         Generate all large files (default)
    --text        Generate text size variant files only
    --binary      Generate binary split/join files only
    --benchmarks  Generate performance benchmark files only
    --force       Overwrite existing files
"""

from pathlib import Path
import os
import sys
import argparse


def get_base_dir() -> Path:
    """Get the base test files directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent


def generate_text_file(path: Path, size_mb: int, force: bool = False) -> bool:
    """Generate a text file of specified size in MB."""
    if path.exists() and not force:
        existing_size = path.stat().st_size
        expected_size = size_mb * 1024 * 1024
        if existing_size >= expected_size * 0.95:  # Within 5% of target
            print(f"  SKIP: {path.name} already exists ({existing_size:,} bytes)")
            return False
    
    target_bytes = size_mb * 1024 * 1024
    chunk = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
             "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n") * 10
    chunk_bytes = len(chunk.encode('utf-8'))
    
    print(f"  Generating: {path.name} ({size_mb} MB)...")
    with open(path, 'w', encoding='utf-8') as f:
        written = 0
        while written < target_bytes:
            f.write(chunk)
            written += chunk_bytes
            if written % (10 * 1024 * 1024) == 0:
                print(f"    Progress: {written // (1024*1024)} MB / {size_mb} MB", 
                      end='\r', file=sys.stderr)
    
    actual_size = path.stat().st_size
    print(f"  CREATED: {path.name} ({actual_size:,} bytes)")
    return True


def generate_binary_file(path: Path, size_mb: int, force: bool = False) -> bool:
    """Generate a binary file of specified size in MB."""
    if path.exists() and not force:
        existing_size = path.stat().st_size
        expected_size = size_mb * 1024 * 1024
        if existing_size >= expected_size * 0.95:  # Within 5% of target
            print(f"  SKIP: {path.name} already exists ({existing_size:,} bytes)")
            return False
    
    target_bytes = size_mb * 1024 * 1024
    chunk_size = 1024 * 1024  # Write in 1MB chunks
    
    print(f"  Generating: {path.name} ({size_mb} MB)...")
    with open(path, 'wb') as f:
        written = 0
        while written < target_bytes:
            chunk = os.urandom(min(chunk_size, target_bytes - written))
            f.write(chunk)
            written += len(chunk)
            if written % (10 * 1024 * 1024) == 0:
                print(f"    Progress: {written // (1024*1024)} MB / {size_mb} MB",
                      end='\r', file=sys.stderr)
    
    actual_size = path.stat().st_size
    print(f"  CREATED: {path.name} ({actual_size:,} bytes)")
    return True


def generate_text_size_variants(base: Path, force: bool = False) -> int:
    """Generate text files of various sizes."""
    print("\n=== Text Size Variants ===")
    sizes_dir = base / "text_files" / "sizes"
    sizes_dir.mkdir(parents=True, exist_ok=True)
    
    created = 0
    
    # Boundary files (always quick)
    empty = sizes_dir / "bound_0b_empty.txt"
    if not empty.exists() or force:
        empty.write_text("")
        print(f"  CREATED: bound_0b_empty.txt (0 bytes)")
        created += 1
    
    minimal = sizes_dir / "bound_1b_minimal.txt"
    if not minimal.exists() or force:
        minimal.write_text("a")
        print(f"  CREATED: bound_1b_minimal.txt (1 byte)")
        created += 1
    
    # Size variants
    size_files = [
        ("perf_1mb_large.txt", 1),
        ("perf_10mb_huge.txt", 10),
        ("perf_100mb_extreme.txt", 100),
    ]
    
    for filename, size_mb in size_files:
        if generate_text_file(sizes_dir / filename, size_mb, force):
            created += 1
    
    return created


def generate_binary_split_files(base: Path, force: bool = False) -> int:
    """Generate binary files for split/join testing."""
    print("\n=== Binary Split/Join Files ===")
    split_dir = base / "split_join_test_data" / "split_source"
    split_dir.mkdir(parents=True, exist_ok=True)
    
    created = 0
    
    # Split source files
    split_files = [
        ("split_small_1mb.bin", 1),
        ("split_medium_100mb.bin", 100),
        # ("split_large_1gb.bin", 1024),  # Uncomment for 1GB
    ]
    
    for filename, size_mb in split_files:
        if generate_binary_file(split_dir / filename, size_mb, force):
            created += 1
    
    # Join source parts
    print("\n=== Join Source Parts ===")
    join_dir = base / "split_join_test_data" / "join_source"
    join_dir.mkdir(parents=True, exist_ok=True)
    
    part_size = 350 * 1024  # ~350KB each
    for i in range(1, 4):
        part_file = join_dir / f"part_{i:03d}.bin"
        if not part_file.exists() or force:
            part_file.write_bytes(os.urandom(part_size))
            print(f"  CREATED: {part_file.name} ({part_size:,} bytes)")
            created += 1
    
    return created


def generate_benchmark_files(base: Path, force: bool = False) -> int:
    """Generate performance benchmark files."""
    print("\n=== Performance Benchmark Files ===")
    perf_base = base / "performance_benchmarks"
    created = 0
    
    # Size benchmarks
    print("\n-- Size Benchmarks --")
    size_benchmarks = [
        ("size_1kb", 1, "benchmark_1kb.bin"),
        ("size_1mb", 1024, "benchmark_1mb.bin"),
    ]
    
    for dirname, size_kb, filename in size_benchmarks:
        bench_dir = perf_base / "file_sizes" / dirname
        bench_dir.mkdir(parents=True, exist_ok=True)
        bench_file = bench_dir / filename
        if not bench_file.exists() or force:
            bench_file.write_bytes(os.urandom(size_kb * 1024))
            print(f"  CREATED: {dirname}/{filename} ({size_kb} KB)")
            created += 1
    
    # File count benchmarks
    print("\n-- File Count Benchmarks --")
    count_benchmarks = [
        ("count_100", 100),
        ("count_1000", 1000),
    ]
    
    for dirname, count in count_benchmarks:
        count_dir = perf_base / "file_count" / dirname
        count_dir.mkdir(parents=True, exist_ok=True)
        existing = len(list(count_dir.glob("*.txt")))
        if existing < count or force:
            for i in range(count):
                (count_dir / f"file_{i:05d}.txt").write_text(f"File {i} content\n")
            print(f"  CREATED: {dirname}/ with {count:,} files")
            created += 1
        else:
            print(f"  SKIP: {dirname}/ already has {existing:,} files")
    
    return created


def main():
    parser = argparse.ArgumentParser(description="Generate large test files")
    parser.add_argument("--all", action="store_true", 
                        help="Generate all large files (default)")
    parser.add_argument("--text", action="store_true",
                        help="Generate text size variant files only")
    parser.add_argument("--binary", action="store_true",
                        help="Generate binary split/join files only")
    parser.add_argument("--benchmarks", action="store_true",
                        help="Generate performance benchmark files only")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing files")
    args = parser.parse_args()
    
    # Default to --all if no specific option given
    if not (args.text or args.binary or args.benchmarks):
        args.all = True
    
    base = get_base_dir()
    print(f"Base directory: {base}")
    print(f"Force overwrite: {args.force}")
    
    total_created = 0
    
    if args.all or args.text:
        total_created += generate_text_size_variants(base, args.force)
    
    if args.all or args.binary:
        total_created += generate_binary_split_files(base, args.force)
    
    if args.all or args.benchmarks:
        total_created += generate_benchmark_files(base, args.force)
    
    print(f"\n{'='*50}")
    print(f"Total files created/updated: {total_created}")
    print(f"{'='*50}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
