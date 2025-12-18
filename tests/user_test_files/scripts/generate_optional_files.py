"""
Generate Optional Large Test Files for RFU Test Suite

This script creates the optional large-scale test files:
- 1GB binary file for stress testing
- 10,000 file directory for file count benchmarks
- 100,000 file directory for extreme file count benchmarks

WARNING: This script creates significant disk usage:
- 1GB file: ~1 GB
- 10K files: ~10 MB
- 100K files: ~100 MB
Total: ~1.1 GB

Run only when stress/performance testing is required.
"""

from pathlib import Path
import os
import sys
import time


def generate_1gb_file(path: Path):
    """Generate a 1GB binary file."""
    print(f"\n📦 Generating 1GB binary file...")
    print(f"   Target: {path}")
    
    target_bytes = 1024 * 1024 * 1024  # 1 GB
    chunk_size = 1024 * 1024  # 1 MB chunks
    
    start_time = time.time()
    
    with open(path, 'wb') as f:
        written = 0
        while written < target_bytes:
            # Generate random bytes for each chunk
            chunk = os.urandom(min(chunk_size, target_bytes - written))
            f.write(chunk)
            written += len(chunk)
            
            # Progress indicator
            mb_written = written // (1024 * 1024)
            if mb_written % 100 == 0 or written >= target_bytes:
                elapsed = time.time() - start_time
                rate = mb_written / elapsed if elapsed > 0 else 0
                print(f"   Progress: {mb_written} MB / 1024 MB ({rate:.1f} MB/s)", end='\r')
    
    elapsed = time.time() - start_time
    print(f"\n   ✅ Complete: {path.stat().st_size:,} bytes in {elapsed:.1f}s")
    return path.stat().st_size


def generate_file_count_directory(path: Path, count: int):
    """Generate a directory with specified number of files."""
    print(f"\n📂 Generating {count:,} files directory...")
    print(f"   Target: {path}")
    
    # Remove README.md if it exists (it's the placeholder)
    readme_path = path / "README.md"
    if readme_path.exists():
        readme_path.unlink()
    
    path.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    
    for i in range(count):
        file_path = path / f"file_{i:06d}.txt"
        file_path.write_text(f"Benchmark file {i} for file count testing\n")
        
        # Progress indicator every 1000 files
        if (i + 1) % 1000 == 0 or (i + 1) == count:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(f"   Progress: {i + 1:,} / {count:,} files ({rate:.1f} files/s)", end='\r')
    
    elapsed = time.time() - start_time
    actual_count = len(list(path.iterdir()))
    print(f"\n   ✅ Complete: {actual_count:,} files in {elapsed:.1f}s")
    return actual_count


def main():
    print("=" * 60)
    print("RFU Optional Large Test File Generator")
    print("=" * 60)
    
    BASE = Path(__file__).parent.parent
    print(f"\nBase path: {BASE}")
    
    # Parse command line arguments
    generate_1gb = '--1gb' in sys.argv or '--all' in sys.argv
    generate_10k = '--10k' in sys.argv or '--all' in sys.argv
    generate_100k = '--100k' in sys.argv or '--all' in sys.argv
    
    if not any([generate_1gb, generate_10k, generate_100k]):
        print("\nUsage: python generate_optional_files.py [OPTIONS]")
        print("\nOptions:")
        print("  --1gb    Generate 1GB binary file (~1 GB disk usage)")
        print("  --10k    Generate 10,000 file directory (~10 MB disk usage)")
        print("  --100k   Generate 100,000 file directory (~100 MB disk usage)")
        print("  --all    Generate all optional files (~1.1 GB disk usage)")
        print("\nExample:")
        print("  python generate_optional_files.py --1gb")
        print("  python generate_optional_files.py --10k --100k")
        print("  python generate_optional_files.py --all")
        return 0
    
    results = []
    
    # Generate 1GB file
    if generate_1gb:
        gb_path = BASE / "split_join_test_data" / "split_source" / "split_large_1gb.bin"
        
        # Check if already exists with correct size
        if gb_path.exists() and gb_path.stat().st_size >= 1024 * 1024 * 1024:
            print(f"\n⚠️ 1GB file already exists with correct size, skipping...")
        else:
            size = generate_1gb_file(gb_path)
            results.append(("split_large_1gb.bin", size, "1GB binary"))
    
    # Generate 10K files
    if generate_10k:
        dir_10k = BASE / "performance_benchmarks" / "file_count" / "count_10000"
        
        # Check if already populated
        existing_files = len(list(dir_10k.glob("file_*.txt")))
        if existing_files >= 10000:
            print(f"\n⚠️ 10K directory already has {existing_files:,} files, skipping...")
        else:
            count = generate_file_count_directory(dir_10k, 10000)
            results.append(("count_10000/", count, "10K files"))
    
    # Generate 100K files
    if generate_100k:
        dir_100k = BASE / "performance_benchmarks" / "file_count" / "count_100000"
        
        # Check if already populated
        existing_files = len(list(dir_100k.glob("file_*.txt")))
        if existing_files >= 100000:
            print(f"\n⚠️ 100K directory already has {existing_files:,} files, skipping...")
        else:
            count = generate_file_count_directory(dir_100k, 100000)
            results.append(("count_100000/", count, "100K files"))
    
    # Summary
    print("\n" + "=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)
    
    if results:
        print("\nGenerated:")
        for name, size_or_count, desc in results:
            if isinstance(size_or_count, int) and size_or_count > 1000000:
                print(f"  ✅ {name}: {size_or_count / (1024*1024*1024):.2f} GB ({desc})")
            else:
                print(f"  ✅ {name}: {size_or_count:,} ({desc})")
    else:
        print("\nNo new files generated (all requested files already exist).")
    
    print("\n✅ Optional file generation complete!")
    return 0


if __name__ == "__main__":
    exit(main())
