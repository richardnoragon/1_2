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
        has_config_manager = bool(re.search(r'ConfigManager|get_config_manager', content))
        has_error_handler = bool(re.search(r'get_error_handler|error_handler', content))
        if has_bare_logging or has_log_manager or has_emit_telemetry:
            # Normalize path
            rel = os.path.relpath(path, tools_dir).replace(chr(92), '/')
            # Use path as key
            if rel not in results:
                results[rel] = {'log_manager': False, 'bare_logging': False, 'telemetry': False, 'config_manager': False, 'error_handler': False}
            if has_log_manager:
                results[rel]['log_manager'] = True
            if has_bare_logging:
                results[rel]['bare_logging'] = True
            if has_emit_telemetry:
                results[rel]['telemetry'] = True
            if has_config_manager:
                results[rel]['config_manager'] = True
            if has_error_handler:
                results[rel]['error_handler'] = True

print('Tool                                          | LogMgr | BareLog | Telem | CfgMgr | ErrHdlr')
print('-' * 95)
for tool, flags in sorted(results.items()):
    lm = 'Y' if flags['log_manager'] else 'N'
    bl = 'Y' if flags['bare_logging'] else 'N'
    te = 'Y' if flags['telemetry'] else 'N'
    cm = 'Y' if flags['config_manager'] else 'N'
    eh = 'Y' if flags['error_handler'] else 'N'
    print(f'{tool:45} | {lm:^6} | {bl:^7} | {te:^5} | {cm:^6} | {eh:^7}')
