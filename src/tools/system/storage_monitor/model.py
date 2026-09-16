"""Read-only snapshots and an explicitly invoked temporary-file benchmark."""
import os
from pathlib import Path
import time
import tempfile
import psutil
from src.core.workflows import WorkflowCancelled

NETWORK_TYPES = {'nfs', 'nfs4', 'cifs', 'smbfs', 'smb3', 'sshfs', 'fuse.sshfs', 'afpfs', 'davfs'}
PSEUDO_TYPES = {'proc', 'sysfs', 'devpts', 'cgroup', 'cgroup2', 'securityfs', 'debugfs', 'tracefs', 'mqueue', 'hugetlbfs', 'configfs', 'fusectl', 'autofs', 'binfmt_misc', 'tmpfs', 'devtmpfs', 'squashfs'}


def snapshot(path=None):
    drives = []
    seen = set()
    for p in psutil.disk_partitions(all=True):
        if p.mountpoint in seen or p.fstype in PSEUDO_TYPES or not p.fstype:
            continue
        seen.add(p.mountpoint)
        drives.append({'path': p.mountpoint, 'device': p.device, 'filesystem': p.fstype,
                       'network': p.fstype.lower() in NETWORK_TYPES or p.device.startswith(('//', '\\\\')) or 'remote' in p.opts})
    usage, error = None, None
    if path:
        try:
            u = psutil.disk_usage(path)
            usage = {'total': u.total, 'used': u.used, 'free': u.free, 'percent': u.percent, 'writable': os.path.isdir(path) and os.access(path, os.W_OK)}
        except OSError as exc:
            error = type(exc).__name__
    try:
        counters = {name: {'read': c.read_bytes, 'write': c.write_bytes} for name, c in
                    (psutil.disk_io_counters(perdisk=True, nowrap=False) or {}).items()}
    except (OSError, RuntimeError):
        counters = {}
    return {'time': time.monotonic(), 'drives': drives, 'usage': usage, 'error': error, 'counters': counters}


class Rates:
    """Counter resets and missing samples reset the baseline, not produce spikes."""
    def __init__(self):
        self.previous = {}
        self.peaks = {}

    def update(self, timestamp, counters):
        result = {}
        for name, value in counters.items():
            old = self.previous.get(name)
            current = None
            if old and timestamp > old[0] and all(value[k] >= old[1][k] for k in ('read', 'write')):
                current = tuple((value[k] - old[1][k]) / (timestamp - old[0]) for k in ('read', 'write'))
                peak = self.peaks.get(name, (0, 0))
                self.peaks[name] = tuple(max(a, b) for a, b in zip(current, peak))
            result[name] = current
        self.previous = {name: (timestamp, dict(value)) for name, value in counters.items()}
        return result


def benchmark(directory, size=128 * 1024 * 1024, cancelled=lambda: False):
    """Sequential cached-file measurement, not a hardware maximum or raw-disk test."""
    if not 1024 * 1024 <= size <= 512 * 1024 * 1024:
        raise ValueError('Benchmark size out of range')
    if psutil.disk_usage(os.fspath(directory)).free < size + 64 * 1024 * 1024:
        raise OSError('Insufficient free space for benchmark')
    block = os.urandom(1024 * 1024)
    name = None
    try:
        with tempfile.NamedTemporaryFile(prefix='.rfu-benchmark-', dir=directory, delete=False) as stream:
            name = stream.name
            start = time.monotonic()
            for offset in range(0, size, len(block)):
                if cancelled():
                    raise WorkflowCancelled()
                stream.write(block[:min(len(block), size - offset)])
            stream.flush()
            os.fsync(stream.fileno())
            write_seconds = time.monotonic() - start
        start = time.monotonic()
        with open(name, 'rb', buffering=0) as stream:
            while stream.read(len(block)):
                if cancelled():
                    raise WorkflowCancelled()
        read_seconds = time.monotonic() - start
        return {'read': size / max(read_seconds, 1e-9), 'write': size / max(write_seconds, 1e-9), 'bytes': size}
    finally:
        if name:
            os.unlink(name)
