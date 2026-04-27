import os, re

tools_dir = 'src/tools'
results = {}
for root, dirs, files in os.walk(tools_dir):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        with open(path, encoding='utf-8', errors='ignore') as fh:
            content = fh.read()
        has_log_manager = bool(re.search(r'get_log_manager|from.*log_manager import', content))
        has_bare_logging = bool(re.search(r'logging\.getLogger', content))
        has_emit_telemetry = bool(re.search(r'emit_telemetry', content))
        if has_bare_logging or has_log_manager or has_emit_telemetry:
            rel = os.path.relpath(path, tools_dir).replace(chr(92), '/')
            if rel not in results:
                results[rel] = {'log_manager': False, 'bare_logging': False, 'telemetry': False}
            if has_log_manager:
                results[rel]['log_manager'] = True
            if has_bare_logging:
                results[rel]['bare_logging'] = True
            if has_emit_telemetry:
                results[rel]['telemetry'] = True

# Files using BARE logging (logging.getLogger) but NOT log_manager
print('=== Files using BARE logging.getLogger (NOT log_manager) ===')
bare_only = [t for t, f in results.items() if f['bare_logging'] and not f['log_manager']]
for t in sorted(bare_only):
    print(t)
print(f'\nTotal: {len(bare_only)} files')

print('\n=== Files using log_manager ===')
log_mgr = [t for t, f in results.items() if f['log_manager']]
for t in sorted(log_mgr):
    print(t)
print(f'\nTotal: {len(log_mgr)} files')
