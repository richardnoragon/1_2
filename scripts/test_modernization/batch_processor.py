#!/usr/bin/env python3
"""
FR-01.6: Batch Processing Framework for Test Modernization

Implements batch processing for multiple test files with:
- Progress tracking and reporting
- Error recovery and continuation
- Resume capability for interrupted processing
- Parallel and sequential processing modes

Generated: 2025-12-19T06:45:00Z
Task Reference: FR-01.6 Manual Test Modernization
Authority: System Integration Engineer
"""

import concurrent.futures
import json
import logging
import os
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Status of batch processing."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class FileProcessingResult:
    """Result of processing a single file."""

    file_path: str
    status: ProcessingStatus
    changes_made: int = 0
    error_message: Optional[str] = None
    processing_time_ms: float = 0
    imports_updated: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "status": (
                self.status.value
                if isinstance(self.status, ProcessingStatus)
                else self.status
            ),
            "changes_made": self.changes_made,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "imports_updated": self.imports_updated,
        }


@dataclass
class BatchState:
    """State of a batch processing session for resume capability."""

    session_id: str
    total_files: int
    processed_files: int
    successful: int
    failed: int
    skipped: int
    current_index: int
    file_list: List[str]
    results: List[Dict]
    started_at: str
    last_updated: str
    status: str  # 'running', 'completed', 'interrupted'

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "BatchState":
        """Create from dictionary."""
        return cls(**data)


class BatchProcessor:
    """
    Batch processor for test modernization with resume capability.

    Features:
    - Progress tracking with percentage completion
    - Error handling with continue-on-error option
    - Resume capability for interrupted sessions
    - Parallel processing with configurable workers
    - Comprehensive reporting
    """

    def __init__(
        self,
        project_root: str,
        modernizer_class: type,
        state_dir: Optional[str] = None,
        max_workers: int = 1,
        continue_on_error: bool = True,
    ):
        """
        Initialize the batch processor.

        Args:
            project_root: Root directory of the project
            modernizer_class: Class to use for modernization (TestModernizer)
            state_dir: Directory to store batch state files
            max_workers: Number of parallel workers (1 = sequential)
            continue_on_error: Whether to continue processing after errors
        """
        self.project_root = Path(project_root)
        self.modernizer_class = modernizer_class
        self.state_dir = (
            Path(state_dir) if state_dir else self.project_root / "temp" / "batch_state"
        )
        self.max_workers = max_workers
        self.continue_on_error = continue_on_error

        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state: Optional[BatchState] = None
        self.results: List[FileProcessingResult] = []
        self._stop_requested = False
        self._lock = threading.Lock()

        # Progress callback
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None

    def _ensure_state_dir(self):
        """Ensure state directory exists."""
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _save_state(self):
        """Save current batch state to disk."""
        if self.state is None:
            return

        self._ensure_state_dir()
        state_file = self.state_dir / f"batch_state_{self.session_id}.json"

        with self._lock:
            self.state.last_updated = datetime.now().isoformat()
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, indent=2)

    def _load_state(self, session_id: str) -> Optional[BatchState]:
        """Load batch state from disk."""
        state_file = self.state_dir / f"batch_state_{session_id}.json"

        if not state_file.exists():
            return None

        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return BatchState.from_dict(data)

    def _list_resumable_sessions(self) -> List[Dict]:
        """List all resumable batch sessions."""
        sessions = []

        if not self.state_dir.exists():
            return sessions

        for state_file in self.state_dir.glob("batch_state_*.json"):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("status") == "interrupted":
                        sessions.append(
                            {
                                "session_id": data["session_id"],
                                "started_at": data["started_at"],
                                "progress": f"{data['processed_files']}/{data['total_files']}",
                                "state_file": str(state_file),
                            }
                        )
            except Exception:
                continue

        return sorted(sessions, key=lambda x: x["started_at"], reverse=True)

    def _process_file(
        self, file_path: Path, dry_run: bool = True
    ) -> FileProcessingResult:
        """
        Process a single file.

        Args:
            file_path: Path to the file
            dry_run: If True, don't modify files

        Returns:
            FileProcessingResult
        """
        start_time = time.time()

        try:
            modernizer = self.modernizer_class(str(self.project_root), dry_run=dry_run)

            result = modernizer.modernize_file(file_path)

            processing_time = (time.time() - start_time) * 1000

            if result.success:
                status = (
                    ProcessingStatus.COMPLETED
                    if result.changes_made > 0
                    else ProcessingStatus.SKIPPED
                )
                return FileProcessingResult(
                    file_path=str(file_path),
                    status=status,
                    changes_made=result.changes_made,
                    processing_time_ms=processing_time,
                    imports_updated=result.imports_updated,
                )
            else:
                return FileProcessingResult(
                    file_path=str(file_path),
                    status=ProcessingStatus.FAILED,
                    error_message=result.error_message,
                    processing_time_ms=processing_time,
                )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return FileProcessingResult(
                file_path=str(file_path),
                status=ProcessingStatus.FAILED,
                error_message=str(e),
                processing_time_ms=processing_time,
            )

    def process_batch(
        self,
        file_paths: List[Path],
        dry_run: bool = True,
        resume_session: Optional[str] = None,
    ) -> Dict:
        """
        Process a batch of files.

        Args:
            file_paths: List of file paths to process
            dry_run: If True, don't modify files
            resume_session: Session ID to resume from

        Returns:
            Batch processing report
        """
        # Initialize or resume state
        start_index = 0
        if resume_session:
            self.state = self._load_state(resume_session)
            if self.state:
                self.session_id = self.state.session_id
                start_index = self.state.current_index
                file_paths = [Path(f) for f in self.state.file_list]
                self.results = [
                    (
                        FileProcessingResult(**r)
                        if isinstance(r, dict)
                        else FileProcessingResult(
                            file_path=r.get("file_path", ""),
                            status=ProcessingStatus(r.get("status", "pending")),
                            changes_made=r.get("changes_made", 0),
                        )
                    )
                    for r in self.state.results
                ]
                logger.info(
                    f"Resuming session {resume_session} from file {start_index}"
                )

        if self.state is None:
            self.state = BatchState(
                session_id=self.session_id,
                total_files=len(file_paths),
                processed_files=0,
                successful=0,
                failed=0,
                skipped=0,
                current_index=0,
                file_list=[str(f) for f in file_paths],
                results=[],
                started_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                status="running",
            )

        logger.info(f"Processing {len(file_paths)} files (starting from {start_index})")

        # Process files
        try:
            if self.max_workers > 1:
                # Parallel processing
                self._process_parallel(file_paths, start_index, dry_run)
            else:
                # Sequential processing
                self._process_sequential(file_paths, start_index, dry_run)

            self.state.status = "completed"

        except KeyboardInterrupt:
            logger.warning("Batch processing interrupted")
            self.state.status = "interrupted"
            self._save_state()
            raise
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            self.state.status = "interrupted"
            self._save_state()
            raise

        # Save final state
        self._save_state()

        # Generate report
        return self.generate_report()

    def _process_sequential(
        self, file_paths: List[Path], start_index: int, dry_run: bool
    ):
        """Process files sequentially."""
        for i, file_path in enumerate(file_paths[start_index:], start=start_index):
            if self._stop_requested:
                break

            # Update progress
            if self.progress_callback:
                self.progress_callback(i + 1, len(file_paths), str(file_path))

            logger.info(f"Processing [{i+1}/{len(file_paths)}]: {file_path.name}")

            result = self._process_file(file_path, dry_run)
            self.results.append(result)

            # Update state
            with self._lock:
                self.state.current_index = i + 1
                self.state.processed_files = i + 1

                if result.status == ProcessingStatus.COMPLETED:
                    self.state.successful += 1
                elif result.status == ProcessingStatus.FAILED:
                    self.state.failed += 1
                    if not self.continue_on_error:
                        raise RuntimeError(
                            f"Processing failed for {file_path}: {result.error_message}"
                        )
                else:
                    self.state.skipped += 1

                self.state.results.append(result.to_dict())

            # Periodic state save
            if (i + 1) % 10 == 0:
                self._save_state()

    def _process_parallel(
        self, file_paths: List[Path], start_index: int, dry_run: bool
    ):
        """Process files in parallel."""
        files_to_process = file_paths[start_index:]

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._process_file, fp, dry_run): fp
                for fp in files_to_process
            }

            # Process results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(future_to_file)):
                if self._stop_requested:
                    executor.shutdown(wait=False)
                    break

                file_path = future_to_file[future]

                try:
                    result = future.result()
                except Exception as e:
                    result = FileProcessingResult(
                        file_path=str(file_path),
                        status=ProcessingStatus.FAILED,
                        error_message=str(e),
                    )

                self.results.append(result)

                # Update state
                with self._lock:
                    self.state.processed_files += 1

                    if result.status == ProcessingStatus.COMPLETED:
                        self.state.successful += 1
                    elif result.status == ProcessingStatus.FAILED:
                        self.state.failed += 1
                    else:
                        self.state.skipped += 1

                    self.state.results.append(result.to_dict())

                if self.progress_callback:
                    self.progress_callback(
                        start_index + i + 1, len(file_paths), str(file_path)
                    )

    def stop(self):
        """Request stop of batch processing."""
        self._stop_requested = True
        logger.info("Stop requested")

    def generate_report(self) -> Dict:
        """Generate comprehensive batch processing report."""
        completed = [r for r in self.results if r.status == ProcessingStatus.COMPLETED]
        failed = [r for r in self.results if r.status == ProcessingStatus.FAILED]
        skipped = [r for r in self.results if r.status == ProcessingStatus.SKIPPED]

        total_time = sum(r.processing_time_ms for r in self.results)
        total_changes = sum(r.changes_made for r in self.results)

        return {
            "session_id": self.session_id,
            "status": self.state.status if self.state else "unknown",
            "summary": {
                "total_files": len(self.results),
                "completed": len(completed),
                "failed": len(failed),
                "skipped": len(skipped),
                "total_changes": total_changes,
                "total_time_ms": total_time,
                "avg_time_per_file_ms": (
                    total_time / len(self.results) if self.results else 0
                ),
            },
            "completed_files": [
                {
                    "file": r.file_path,
                    "changes": r.changes_made,
                    "updates": r.imports_updated,
                    "time_ms": r.processing_time_ms,
                }
                for r in completed
            ],
            "failed_files": [
                {"file": r.file_path, "error": r.error_message} for r in failed
            ],
            "skipped_files": [r.file_path for r in skipped],
            "timestamp": datetime.now().isoformat(),
            "resumable": self.state.status == "interrupted" if self.state else False,
        }

    def save_report(self, report_path: Optional[Path] = None) -> Path:
        """Save batch processing report."""
        report = self.generate_report()

        if report_path is None:
            reports_dir = self.project_root / "reports" / "test_modernization"
            reports_dir.mkdir(parents=True, exist_ok=True)
            report_path = reports_dir / f"batch_report_{self.session_id}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report_path


def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """Create a text-based progress bar."""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {current}/{total} ({percent*100:.1f}%)"


def main():
    """Main entry point for batch processing."""
    import argparse

    # Import the TestModernizer from the main script
    from import_modernization_script import TestModernizer

    parser = argparse.ArgumentParser(
        description="Batch process test file modernization"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Test files to modernize (default: all deprecated tests)",
    )
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show changes without modifying files (default: True)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually modify files (disables dry-run)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parallel workers (default: 1 = sequential)",
    )
    parser.add_argument(
        "--resume", metavar="SESSION_ID", help="Resume from an interrupted session"
    )
    parser.add_argument(
        "--list-resumable", action="store_true", help="List all resumable sessions"
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop batch processing on first error",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    dry_run = not args.execute

    processor = BatchProcessor(
        str(project_root),
        TestModernizer,
        max_workers=args.workers,
        continue_on_error=not args.stop_on_error,
    )

    # List resumable sessions
    if args.list_resumable:
        sessions = processor._list_resumable_sessions()
        if sessions:
            print("\nResumable sessions:")
            for s in sessions:
                print(f"  {s['session_id']}: {s['progress']} files ({s['started_at']})")
        else:
            print("No resumable sessions found")
        return 0

    # Determine files to process
    if args.files:
        file_paths = [Path(f) for f in args.files]
    else:
        # Default: process all deprecated tests from FR-01.2 high-priority list
        tests_dir = project_root / "tests"
        deprecated_patterns = [
            "test_empty_folders.py",
            "test_compression_logic.py",
            "test_secure_delete.py",
            "test_file_touch.py",
            "test_encryption.py",
            "test_checksum.py",
            "test_size_analyzer_core.py",
            "test_size_analyzer_config.py",
            "test_image_metadata.py",
            "test_file_operations.py",
        ]
        file_paths = [
            tests_dir / p for p in deprecated_patterns if (tests_dir / p).exists()
        ]

    if not file_paths:
        print("No files to process")
        return 0

    # Set up progress callback
    def progress_callback(current, total, file_name):
        bar = create_progress_bar(current, total)
        print(f"\r{bar} - {Path(file_name).name}", end="", flush=True)

    processor.progress_callback = progress_callback

    print(
        f"{'[DRY RUN] ' if dry_run else ''}Batch processing {len(file_paths)} files..."
    )
    print()

    try:
        report = processor.process_batch(
            file_paths, dry_run=dry_run, resume_session=args.resume
        )

        print("\n")
        print("=" * 60)
        print("BATCH PROCESSING COMPLETE")
        print("=" * 60)
        print(f"Session ID: {report['session_id']}")
        print(f"Status: {report['status']}")
        print(f"Total files: {report['summary']['total_files']}")
        print(f"Completed: {report['summary']['completed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Skipped: {report['summary']['skipped']}")
        print(f"Total changes: {report['summary']['total_changes']}")
        print(f"Total time: {report['summary']['total_time_ms']:.2f}ms")

        if report["failed_files"]:
            print("\nFailed files:")
            for item in report["failed_files"]:
                print(f"  - {item['file']}: {item['error']}")

        # Save report
        report_path = processor.save_report()
        print(f"\nReport saved to: {report_path}")

        return 0 if report["summary"]["failed"] == 0 else 1

    except KeyboardInterrupt:
        print("\n\nBatch processing interrupted. Use --resume to continue.")
        return 1


if __name__ == "__main__":
    exit(main())
