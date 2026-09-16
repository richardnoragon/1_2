"""Typed, cancellable cross-tool file inspection workflow.

The discovery and checksum steps never modify inputs. Export is a separate,
explicit operation, so cancelling inspection cannot leave a partial report.
"""

from dataclasses import dataclass
import hashlib
import csv
import os
import tempfile
from pathlib import Path
from threading import Event

from src.core.operations import operation


class WorkflowCancelled(Exception):
    pass


@dataclass(frozen=True)
class FileDigest:
    path: str
    size: int
    sha256: str


def inspect_files(root, *, cancel=None, progress=lambda count: None, emit=None):
    """Find regular files, then calculate SHA-256 with cooperative cancellation.

    Symlinks are excluded; unreadable or changing files abort the run instead
    of silently certifying an incomplete or inconsistent report.
    """
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Choose a directory")
    cancel = cancel or Event()
    records = []

    def check_cancelled():
        if cancel.is_set():
            raise WorkflowCancelled()

    def walk_error(error):
        raise error

    with operation("file-inspection", "discover-and-checksum", emit=emit):
        for directory, folders, files in os.walk(root, followlinks=False, onerror=walk_error):
            check_cancelled()
            folders[:] = sorted(name for name in folders if not (Path(directory) / name).is_symlink())
            for name in sorted(files):
                check_cancelled()
                path = Path(directory) / name
                if path.is_symlink() or not path.is_file():
                    continue
                before = path.stat()
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    opened = os.fstat(stream.fileno())
                    if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                        raise OSError("File changed before inspection")
                    while chunk := stream.read(1024 * 1024):
                        check_cancelled()
                        digest.update(chunk)
                    after = os.fstat(stream.fileno())
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    raise OSError("File changed during inspection")
                records.append(FileDigest(str(path.relative_to(root)), after.st_size, digest.hexdigest()))
                progress(len(records))
        check_cancelled()
    return records


def export_report(records, destination, *, cancel=None):
    """Atomically replace an explicitly selected report destination."""
    cancel = cancel or Event()
    destination = Path(destination)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                         dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            writer = csv.writer(stream)
            writer.writerow(["Path", "Bytes", "SHA-256"])
            for record in records:
                if cancel.is_set():
                    raise WorkflowCancelled()
                # Avoid spreadsheet formula evaluation of attacker-controlled names.
                path = record.path
                if path.startswith(("=", "+", "-", "@", "\t", "\r")):
                    path = "'" + path
                writer.writerow([path, record.size, record.sha256])
            stream.flush()
            os.fsync(stream.fileno())
        if cancel.is_set():
            raise WorkflowCancelled()
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
