# 1GB Split Test File

## Current Status
The split_large_1gb.bin file is a placeholder (100 bytes).

## Generate on Demand
To generate the actual 1GB file:

`python
from pathlib import Path
import os

def generate_binary_file(path: Path, size_mb: int):
    target_bytes = size_mb * 1024 * 1024
    chunk_size = 1024 * 1024  # 1MB chunks
    
    with open(path, 'wb') as f:
        written = 0
        while written < target_bytes:
            chunk = os.urandom(min(chunk_size, target_bytes - written))
            f.write(chunk)
            written += len(chunk)
            if written % (100 * 1024 * 1024) == 0:
                print(f'Progress: {written // (1024*1024)} MB / {size_mb} MB')
    
    print(f'Created: {path} ({path.stat().st_size:,} bytes)')

# Generate 1GB file
generate_binary_file(Path('split_large_1gb.bin'), 1024)
`

## Time Estimate
- Generation time: ~30-60 seconds depending on disk speed
- Disk space required: ~1 GB

## Alternative
For most split/join testing, use split_medium_100mb.bin (100 MB).
