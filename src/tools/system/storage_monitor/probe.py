"""Isolate potentially blocking mount queries from the Qt event loop."""
import json
import sys
from src.tools.system.storage_monitor.model import snapshot

if __name__ == '__main__':
    try:
        print(json.dumps(snapshot(sys.argv[1] if len(sys.argv) > 1 else None)))
    except Exception as exc:
        print(json.dumps({'error': type(exc).__name__}))
        sys.exit(1)
