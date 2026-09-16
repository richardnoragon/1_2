"""Preview and compare-before-apply permission changes without following links."""
from dataclasses import dataclass, replace
from pathlib import Path
import os
import stat


@dataclass(frozen=True)
class PermissionPlan:
    path: Path
    device: int
    inode: int
    before: int
    after: int


def plan_permissions(path, owner_mode):
    path = Path(path).absolute()
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode):
        raise ValueError('Select the target itself; symbolic links are not supported.')
    before = stat.S_IMODE(info.st_mode)
    # Only the owner controls are editable. Preserve group, other and special bits.
    after = (before & ~stat.S_IRWXU) | (owner_mode & stat.S_IRWXU)
    return PermissionPlan(path, info.st_dev, info.st_ino, before, after)


def apply_permissions(plan):
    info = plan.path.lstat()
    if (stat.S_ISLNK(info.st_mode) or (info.st_dev, info.st_ino, stat.S_IMODE(info.st_mode))
            != (plan.device, plan.inode, plan.before)):
        raise OSError('The target or its permissions changed after preview. Preview again.')
    if os.name == 'nt':
        # Windows chmod exposes the read-only flag, not POSIX ACL editing.
        os.chmod(plan.path, plan.after)
    else:
        try:
            fd = os.open(plan.path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, 'O_NOFOLLOW', 0))
        except PermissionError:
            # An owner may restore permissions even after removing read access.
            # Do not follow a substituted symlink; unsupported platforms fail closed.
            os.chmod(plan.path, plan.after, follow_symlinks=False)
            return replace(plan, before=plan.after, after=plan.before)
        try:
            current = os.fstat(fd)
            if (current.st_dev, current.st_ino, stat.S_IMODE(current.st_mode)) != (plan.device, plan.inode, plan.before):
                raise OSError('The target changed after preview.')
            os.fchmod(fd, plan.after)
        finally:
            os.close(fd)
    return replace(plan, before=plan.after, after=plan.before)
