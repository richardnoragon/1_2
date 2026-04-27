import os, re

tools_dir = 'src/tools'
no_logging = []
for root, dirs, files in os.walk(tools_dir):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if not f.endswith('.py') or f.startswith('__'):
            continue
        path = os.path.join(root, f)
        with open(path, encoding='utf-8', errors='ignore') as fh:
            content = fh.read()
        if not re.search(r'logging|log_manager', content):
            no_logging.append(os.path.relpath(path, tools_dir).replace(chr(92), '/'))

print('Files with NO logging at all:')
for p in sorted(no_logging):
    print(' ', p)
print(f'\nTotal: {len(no_logging)} files')
