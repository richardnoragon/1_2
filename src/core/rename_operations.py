"""Validated file renames with exclusive destinations and reversible results."""
from dataclasses import dataclass
from pathlib import Path
import os
import stat


@dataclass(frozen=True)
class RenameItem:
    source: Path
    target: Path
    identity: tuple


def identity(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('Only regular files can be renamed in this workflow.')
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def plan_renames(directory, pairs):
    directory = Path(directory).resolve(strict=True)
    plan, destinations = [], set()
    for old, new in pairs:
        for name in (old, new):
            if not name or name in {'.', '..'} or any(c in name for c in '/\\\x00<>:"|?*'):
                raise ValueError('Use a file name without path separators or reserved characters.')
        source, target = directory / old, directory / new
        snapshot = identity(source)
        if source == target:
            continue
        if target.name.casefold() in destinations or os.path.lexists(target):
            raise FileExistsError('A destination already exists or is selected more than once.')
        destinations.add(target.name.casefold())
        plan.append(RenameItem(source, target, snapshot))
    return tuple(plan)


def execute_renames(plan, cancel=None):
    """Return completed reverse steps even after cancellation or partial failure."""
    reverse, errors = [], []
    for item in plan:
        if cancel is not None and cancel.is_set():
            break
        try:
            if identity(item.source) != item.identity:
                raise OSError('Source changed after preview.')
            # link creation is exclusive; unlike POSIX rename it cannot overwrite
            # an unrelated destination that appears after preview.
            os.link(item.source, item.target, follow_symlinks=False)
            try:
                if identity(item.source) != item.identity or identity(item.target) != item.identity:
                    raise OSError('Source changed during rename.')
                item.source.unlink()
            except Exception:
                if item.target.exists() and identity(item.target) == item.identity:
                    item.target.unlink()
                raise
            reverse.insert(0, RenameItem(item.target, item.source, identity(item.target)))
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            break
    return tuple(reverse), tuple(errors)
