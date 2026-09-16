"""Shared atomic Save As semantics for document tools."""
import os
from pathlib import Path
import tempfile
from src.core.workflows import WorkflowCancelled


def check_cancel(cancel):
    if cancel is not None and cancel.is_set():
        raise WorkflowCancelled()


def atomic_export(destination, sources, write, cancel=None):
    destination = Path(destination).resolve()
    for source in sources:
        source = Path(source).resolve()
        if destination == source or (destination.exists() and source.exists()
                                     and os.path.samefile(destination, source)):
            raise ValueError('Choose a separate output file; source files are preserved.')
    check_cancel(cancel)
    fd, name = tempfile.mkstemp(suffix=destination.suffix, dir=destination.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        write(temporary)
        check_cancel(cancel)
        # Windows FlushFileBuffers requires a writable descriptor.
        with temporary.open('r+b') as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
