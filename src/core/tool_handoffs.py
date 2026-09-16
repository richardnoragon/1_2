"""Typed, explicit handoffs of saved artifacts between governed tools."""
from dataclasses import dataclass
from pathlib import Path
from src.core.operations import operation


@dataclass(frozen=True)
class DocumentArtifact:
    path: Path
    media_type: str
    producer: str

    def validate(self):
        expected = {'application/pdf': '.pdf', 'text/csv': '.csv', 'application/json': '.json'}
        path = self.path.resolve()
        if self.media_type not in expected or path.suffix.lower() != expected[self.media_type]:
            raise ValueError('Unsupported document artifact type')
        if not path.is_file():
            raise FileNotFoundError('The exported document is no longer available')
        return path


ACCEPTS = {
    'pdf-extract-links': {'application/pdf'},
    'pdf-page-administration': {'application/pdf'},
    'data-anonymizer': {'text/csv', 'application/json'},
}


def handoff(hub, artifact, target):
    path = artifact.validate()
    if artifact.media_type not in ACCEPTS.get(target, set()):
        raise ValueError('This tool does not accept that document type')
    with operation(artifact.producer, 'handoff-' + target):
        if not hub.launch_tool(target):
            raise RuntimeError('The destination tool could not start')
        window = hub._catalogue_windows[target]
        if window._job is not None:
            raise RuntimeError('The destination tool is busy')
        window.load_file(path)
    return window
