"""Benchmark export/import latency for preference portability."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Tuple

from src.core.preferences.portability import export_preferences, import_preferences
from src.core.preferences.store import PreferencesStore
from src.database.database_manager import DatabaseManager


@dataclass
class BenchmarkResult:
    """Captures timing and artifact metrics for a single benchmark run."""

    entry_count: int
    seed_seconds: float
    export_seconds: float
    import_seconds: float
    export_size_bytes: int
    export_path: Path

    @property
    def export_throughput(self) -> float:
        return self.entry_count / self.export_seconds if self.export_seconds else 0.0

    @property
    def import_throughput(self) -> float:
        return self.entry_count / self.import_seconds if self.import_seconds else 0.0


def seed_preferences(
    store: PreferencesStore,
    user_id: str,
    entry_target: int,
    category_count: int,
) -> int:
    """Populate the store with synthetic preferences matching the target size."""

    if entry_target <= 0:
        raise ValueError("entry_target must be greater than zero")
    if category_count <= 0:
        raise ValueError("category_count must be greater than zero")

    base = entry_target // category_count
    remainder = entry_target % category_count
    total = 0

    for category_index in range(category_count):
        count = base + (1 if category_index < remainder else 0)
        if count == 0:
            continue

        category_name = f"benchmark.category_{category_index:03d}"
        values = {}
        for entry_index in range(count):
            key = f"setting_{category_index:03d}_{entry_index:04d}"
            pattern = (entry_index + category_index) % 5
            if pattern == 0:
                values[key] = {
                    "index": entry_index,
                    "category": category_name,
                    "enabled": (entry_index % 2) == 0,
                }
            elif pattern == 1:
                values[key] = f"value-{category_index}-{entry_index}"
            elif pattern == 2:
                values[key] = entry_index
            elif pattern == 3:
                values[key] = entry_index / 10.0
            else:
                values[key] = (entry_index % 3) == 0

        store.set_category(user_id, category_name, values)
        total += len(values)

    return total


def run_benchmark(
    entry_target: int,
    category_count: int,
    export_dir: Path,
) -> BenchmarkResult:
    """Execute the benchmark using a temporary database instance."""

    previous_instance = DatabaseManager._instance
    manager = None

    try:
        if previous_instance is not None:
            previous_instance.close_all_connections()
        DatabaseManager._instance = None

        manager = DatabaseManager(export_dir.parent / "preferences_perf.db")
        store = PreferencesStore(manager)

        user_id = "benchmark-source"
        import_user = "benchmark-import"

        start_seed = perf_counter()
        entry_count = seed_preferences(store, user_id, entry_target, category_count)
        seed_seconds = perf_counter() - start_seed

        export_dir.mkdir(parents=True, exist_ok=True)

        start_export = perf_counter()
        export_path = export_preferences(
            user_id,
            destination=export_dir,
            store=store,
        )
        export_seconds = perf_counter() - start_export

        start_import = perf_counter()
        result = import_preferences(
            export_path,
            target_user_id=import_user,
            allow_overwrite=True,
            store=store,
        )
        import_seconds = perf_counter() - start_import

        applied = int(result.get("applied", 0))
        if applied != entry_count:
            raise RuntimeError(
                "Import applied count does not match exported entry count",
            )

        export_size_bytes = export_path.stat().st_size

        return BenchmarkResult(
            entry_count=entry_count,
            seed_seconds=seed_seconds,
            export_seconds=export_seconds,
            import_seconds=import_seconds,
            export_size_bytes=export_size_bytes,
            export_path=export_path,
        )
    finally:
        if manager is not None:
            manager.close_all_connections()
        DatabaseManager._instance = previous_instance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark preference export/import latency using a synthetic dataset"
        ),
    )
    parser.add_argument(
        "--entries",
        type=int,
        default=10_000,
        help="Total preference entries to seed (default: 10,000)",
    )
    parser.add_argument(
        "--categories",
        type=int,
        default=50,
        help="Number of distinct categories to populate (default: 50)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional directory to persist the export artifact",
    )
    return parser.parse_args()


def choose_export_dir(output: Path | None) -> Tuple[Path, TemporaryDirectory | None]:
    """Resolve the export directory while honoring optional user overrides."""

    if output is not None:
        output.mkdir(parents=True, exist_ok=True)
        return output, None

    temp_dir = TemporaryDirectory()
    return Path(temp_dir.name) / "exports", temp_dir


def main() -> None:
    args = parse_args()

    export_dir, temp_handle = choose_export_dir(args.output)

    try:
        result = run_benchmark(
            entry_target=args.entries,
            category_count=args.categories,
            export_dir=export_dir,
        )
    finally:
        if temp_handle is not None:
            temp_handle.cleanup()

    print(f"Entries: {result.entry_count}")
    print(f"Seed seconds: {result.seed_seconds:.3f}")
    print(f"Export seconds: {result.export_seconds:.3f}")
    print(f"Import seconds: {result.import_seconds:.3f}")
    print(f"Export throughput (entries/sec): {result.export_throughput:.1f}")
    print(f"Import throughput (entries/sec): {result.import_throughput:.1f}")
    print(f"Export size (bytes): {result.export_size_bytes}")
    print(f"Export path: {result.export_path}")


if __name__ == "__main__":
    main()
