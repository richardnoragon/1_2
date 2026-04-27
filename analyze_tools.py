import os, re

tools_dir = 'src/tools'
tool_summary = {}

for root, dirs, files in os.walk(tools_dir):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith('.py') or f == '__init__.py':
            continue
        path = os.path.join(root, f)
        # Get relative path from tools_dir
        rel = os.path.relpath(path, tools_dir)
        parts = rel.replace(os.sep, '/').split('/')
        # Group by top-level dir or file
        if len(parts) == 1:
            tool_key = parts[0]
        elif len(parts) == 2:
            tool_key = parts[0]
        else:
            tool_key = parts[0] + '/' + parts[1]

        with open(path, encoding='utf-8', errors='ignore') as fh:
            content = fh.read()

        if tool_key not in tool_summary:
            tool_summary[tool_key] = {
                'log_manager': False, 'bare_logging': False,
                'emit_telemetry': False, 'config_manager': False,
                'error_handler': False, 'try_except': False
            }
        if re.search(r'get_log_manager|from.*log_manager import', content):
            tool_summary[tool_key]['log_manager'] = True
        if re.search(r'logging\.getLogger', content):
            tool_summary[tool_key]['bare_logging'] = True
        if re.search(r'emit_telemetry', content):
            tool_summary[tool_key]['emit_telemetry'] = True
        if re.search(r'ConfigManager|get_config_manager', content):
            tool_summary[tool_key]['config_manager'] = True
        if re.search(r'get_error_handler|ErrorHandler', content):
            tool_summary[tool_key]['error_handler'] = True
        if re.search(r'try:', content):
            tool_summary[tool_key]['try_except'] = True

print(f"{'Tool':<45} | {'LogMgr':^6} | {'BareLg':^6} | {'Telm':^5} | {'CfgMgr':^6} | {'ErrHdlr':^7} | {'try/exc':^7}")
print('-' * 95)
for tool, flags in sorted(tool_summary.items()):
    print(f"{tool:<45} | {'Y' if flags['log_manager'] else '.':^6} | {'Y' if flags['bare_logging'] else '.':^6} | {'Y' if flags['emit_telemetry'] else '.':^5} | {'Y' if flags['config_manager'] else '.':^6} | {'Y' if flags['error_handler'] else '.':^7} | {'Y' if flags['try_except'] else '.':^7}")
