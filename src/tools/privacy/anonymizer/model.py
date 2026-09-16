"""Explicit field transformations; pseudonyms are scoped to one loaded document."""
import copy
import csv
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from pathlib import Path

from src.core.document_export import atomic_export, check_cancel


@dataclass
class Dataset:
    source: Path
    records: list
    fields: list
    format: str
    object_root: bool = False


def load_dataset(path, cancel=None):
    source = Path(path).resolve()
    check_cancel(cancel)
    if source.suffix.lower() == '.csv':
        with source.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            if not fields or len(fields) != len(set(fields)) or any(not f for f in fields):
                raise ValueError('CSV needs unique, nonempty column names.')
            records = []
            for row in reader:
                check_cancel(cancel)
                if None in row or None in row.values():
                    raise ValueError('CSV rows must match the column count.')
                records.append(row)
        return Dataset(source, records, fields, 'csv')
    if source.suffix.lower() != '.json':
        raise ValueError('Choose a CSV or JSON file.')
    data = json.loads(source.read_text(encoding='utf-8-sig'))
    object_root = isinstance(data, dict)
    records = [data] if object_root else data
    if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
        raise ValueError('JSON must be an object or an array of objects.')
    fields = list(dict.fromkeys(key for row in records for key in row))
    check_cancel(cancel)
    return Dataset(source, records, fields, 'json', object_root)


def transform(dataset, rules, key, cancel=None):
    if not rules or any(field not in dataset.fields or mode not in ('redact', 'pseudonym')
                        for field, mode in rules.items()):
        raise ValueError('Select at least one field and a valid transformation.')
    result = []
    for record in dataset.records:
        check_cancel(cancel)
        row = copy.deepcopy(record)
        for field, mode in rules.items():
            if field not in row:
                continue
            if mode == 'redact':
                row[field] = '[REDACTED]'
            else:
                value = json.dumps([field, row[field]], sort_keys=True, ensure_ascii=False,
                                   separators=(',', ':')).encode('utf-8')
                row[field] = 'person_' + hmac.new(key, value, hashlib.sha256).hexdigest()[:24]
        result.append(row)
    return result


def new_key():
    return secrets.token_bytes(32)


def export_dataset(dataset, records, destination, cancel=None):
    destination = Path(destination)
    if destination.suffix.lower() != '.' + dataset.format:
        raise ValueError('Use the same file format as the source.')
    def write(path):
        with path.open('w', encoding='utf-8', newline='') as stream:
            if dataset.format == 'csv':
                writer = csv.DictWriter(stream, fieldnames=dataset.fields)
                writer.writeheader()
                for row in records:
                    check_cancel(cancel)
                    # Export remains data, never an executable spreadsheet formula.
                    writer.writerow({k: "'" + v if isinstance(v, str) and v.startswith(
                        ('=', '+', '-', '@', '\t', '\r')) else v for k, v in row.items()})
            else:
                json.dump(records[0] if dataset.object_root else records, stream,
                          ensure_ascii=False, indent=2)
    atomic_export(destination, [dataset.source], write, cancel)
