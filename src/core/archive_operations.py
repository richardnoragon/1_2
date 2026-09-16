"""Read-only archive plans and cancellable execution away from the GUI thread."""
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import os
import shutil
import stat
import tarfile
import tempfile
import zipfile
from src.core.document_export import atomic_export, check_cancel


@dataclass(frozen=True)
class ArchivePlan:
    source: Path
    destination: Path
    mode: str
    members: tuple
    format: str
    level: int = 6


def plan_compression(source, destination, format='ZIP', level=6, password='', cancel=None):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if password:
        raise ValueError('Password-protected archive creation is not supported by this engine.')
    if not source.is_dir() or format not in {'ZIP', 'TAR.GZ', 'TAR.BZ2'}:
        raise ValueError('Choose a folder and a supported archive format.')
    if destination == source or source in destination.parents:
        raise ValueError('Save the archive outside its input folder.')
    members = []
    for folder, directories, files in os.walk(source, followlinks=False):
        check_cancel(cancel)
        for name in sorted(directories + files):
            path = Path(folder) / name
            if path.is_symlink():
                raise ValueError('Archive input contains a symbolic link; choose regular files and folders.')
            info = path.stat()
            members.append((path.relative_to(source).as_posix(), path.is_dir(), info.st_size, info.st_mtime_ns))
    return ArchivePlan(source, destination, 'compress', tuple(members), format, level)


def _validated_name(name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
        raise ValueError('Archive contains an unsafe member path.')
    return path.as_posix().rstrip('/')


def plan_extraction(source, destination, cancel=None):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.exists():
        raise FileExistsError('Choose a new output folder; extraction never overwrites existing files.')
    members, seen = [], set()
    def add(name, directory, size):
        check_cancel(cancel)
        name = _validated_name(name)
        if name == '.':
            if directory:
                return
            raise ValueError('Invalid archive member')
        if name.casefold() in seen:
            raise ValueError('Archive contains duplicate or case-colliding names.')
        seen.add(name.casefold())
        members.append((name, directory, size, 0))
    if zipfile.is_zipfile(source):
        format = 'ZIP'
        with zipfile.ZipFile(source) as archive:
            for member in archive.infolist():
                if stat.S_ISLNK(member.external_attr >> 16):
                    raise ValueError('Archive links are unsupported.')
                add(member.filename, member.is_dir(), member.file_size)
    else:
        format = 'TAR'
        with tarfile.open(source) as archive:
            for member in archive:
                if not (member.isfile() or member.isdir()):
                    raise ValueError('Archive links and special files are unsupported.')
                add(member.name, member.isdir(), member.size)
    return ArchivePlan(source, destination, 'extract', tuple(members), format)


def _copy(source, target, cancel):
    while chunk := source.read(1024 * 1024):
        check_cancel(cancel)
        target.write(chunk)


def execute_compression(plan, cancel=None):
    def write(temporary):
        mode = 'w:gz' if plan.format == 'TAR.GZ' else 'w:bz2'
        archive = zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=plan.level) if plan.format == 'ZIP' else tarfile.open(temporary, mode, compresslevel=plan.level)
        with archive:
            for name, directory, size, modified in plan.members:
                check_cancel(cancel)
                path = plan.source / name
                info = path.stat()
                if path.is_symlink() or (info.st_size, info.st_mtime_ns) != (size, modified):
                    raise OSError('Archive input changed since preview.')
                if plan.format == 'ZIP':
                    if directory:
                        archive.writestr(name.rstrip('/') + '/', b'')
                    else:
                        with path.open('rb') as source, archive.open(name, 'w', force_zip64=True) as target:
                            _copy(source, target, cancel)
                else:
                    metadata = archive.gettarinfo(str(path), arcname=name)
                    if directory:
                        archive.addfile(metadata)
                    else:
                        with path.open('rb') as source:
                            archive.addfile(metadata, source)
                check_cancel(cancel)
    atomic_export(plan.destination, [plan.source], write, cancel)


def execute_extraction(plan, password='', cancel=None):
    # Recheck the archive before creating any output, then only use staged paths.
    current = plan_extraction(plan.source, plan.destination, cancel)
    if current.members != plan.members:
        raise OSError('Archive changed since preview.')
    with tempfile.TemporaryDirectory(prefix='.rfu-extract-', dir=plan.destination.parent) as temporary:
        stage = Path(temporary)
        archive = zipfile.ZipFile(plan.source) if plan.format == 'ZIP' else tarfile.open(plan.source)
        with archive:
            names = archive.namelist() if plan.format == "ZIP" else archive.getnames()
            original_names = {_validated_name(name): name for name in names}
            for name, directory, _, _ in plan.members:
                check_cancel(cancel)
                path = stage / name
                if directory:
                    path.mkdir(parents=True, exist_ok=True)
                    continue
                path.parent.mkdir(parents=True, exist_ok=True)
                source = archive.open(original_names[name], pwd=password.encode() or None) if plan.format == 'ZIP' else archive.extractfile(original_names[name])
                with source, path.open('xb') as target:
                    _copy(source, target, cancel)
        check_cancel(cancel)
        # Never merge into an existing directory. Rename publishes a complete tree.
        if plan.destination.exists():
            raise FileExistsError('Output folder appeared during extraction.')
        os.rename(stage, plan.destination)
