import re
from pathlib import Path

HEX_RE = re.compile(r'(?<![a-zA-Z0-9_])#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b')

tools = [
    'src/tools/analysis/duplicate_finder',
    'src/tools/analysis/checksum',
    'src/tools/analysis/size_analyzer',
    'src/tools/analysis/empty_folders',
    'src/tools/file_management/finder',
    'src/tools/file_management/organizer',
    'src/tools/file_management/advanced_catalog',
    'src/tools/system/diagnostics_monitoring',
    'src/tools/system/process_monitor',
    'src/tools/system/simple_system_info.py',
    'src/tools/system/software_maintenance',
    'src/tools/network',
    'src/tools/logs',
    'src/tools/metadata',
    'src/tools/preferences',
    'src/tools/file_operations',
    'src/tools/security',
    'src/tools/pdf_tools',
    'src/tools/privacy',
]

total = 0
for t in tools:
    p = Path(t)
    files = [p] if p.is_file() else list(p.rglob('*.py'))
    for f in files:
        if '__pycache__' in str(f): continue
        txt = f.read_text(encoding='utf-8', errors='ignore')
        matches = HEX_RE.findall(txt)
        if matches:
            print(f'  {len(matches):3d}  {f}')
            total += len(matches)
print(f'TOTAL HEX: {total}')
