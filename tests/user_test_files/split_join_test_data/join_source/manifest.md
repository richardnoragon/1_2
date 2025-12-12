# Join Test Parts Manifest

## Parts Description
- part_001.bin: First chunk (~350KB)
- part_002.bin: Second chunk (~350KB)
- part_003.bin: Third chunk (~350KB)

## Expected Joined Size
Approximately 1,050,000 bytes (1 MB)

## Join Command Example
`python
parts = sorted(Path('.').glob('part_*.bin'))
with open('joined_output.bin', 'wb') as out:
    for part in parts:
        out.write(part.read_bytes())
`
