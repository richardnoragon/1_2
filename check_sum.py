import hashlib
import os
from PyQt5.QtCore import QObject, pyqtSignal

from core.error_handler import error_handler


VALID_ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha512']
CHUNK_SIZE = 8192  # Read file in chunks


class ChecksumLogic(QObject):
    """Handles checksum calculation and verification logic."""
    progress_updated = pyqtSignal(int, int)  # current, total
    result_ready = pyqtSignal(dict)  # Results dictionary
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, target_path, algorithm, expected_checksum=None,
                 checksum_file_path=None, mode='calculate'):
        super().__init__()
        if algorithm.lower() not in VALID_ALGORITHMS:
            raise ValueError(
                f"Invalid algorithm: {algorithm}. "
                f"Choose from {VALID_ALGORITHMS}"
            )

        self.target_path = target_path
        self.algorithm = algorithm.lower()
        self.expected_checksum = expected_checksum
        self.checksum_file_path = checksum_file_path
        # Modes: calculate_file, calculate_dir, verify_file, verify_dir
        self.mode = mode
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        """Main execution method to be run in a thread."""
        try:
            self._is_running = True
            results = {}

            if self.mode == 'calculate_file':
                checksum = self._calculate_file_checksum(self.target_path)
                if checksum:
                    results[self.target_path] = checksum
            elif self.mode == 'calculate_dir':
                results = self._calculate_directory_checksums(self.target_path)
            elif self.mode == 'verify_file':
                status = self._verify_file_checksum(self.target_path, self.expected_checksum)
                results[self.target_path] = status
            elif self.mode == 'verify_dir':
                results = self._verify_directory_checksums(self.target_path, self.checksum_file_path)
            else:
                raise ValueError(f"Invalid mode: {self.mode}")

            if self._is_running:
                self.result_ready.emit(results)

        except Exception as e:
            if self._is_running:  # Don't emit error if stopped manually
                self.error_occurred.emit(f"Error: {e}")
        finally:
            if self._is_running:
                self.finished.emit()

    def _calculate_file_checksum(self, file_path):
        """Calculates the checksum for a single file."""
        if not self._is_running:
            return None
        hasher = hashlib.new(self.algorithm)
        try:
            with open(file_path, 'rb') as f:
                total_size = os.path.getsize(file_path)
                bytes_read = 0

                while self._is_running:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    hasher.update(chunk)
                    bytes_read += len(chunk)

                    # Emit progress infrequently to avoid overwhelming GUI thread
                    if bytes_read % (CHUNK_SIZE * 50) == 0 or bytes_read == total_size:
                        self.progress_updated.emit(bytes_read, total_size)

                if not self._is_running:
                    return None
                return hasher.hexdigest()

        except FileNotFoundError:
            self.error_occurred.emit(f"File not found: {file_path}")
            return None
        except PermissionError:
            self.error_occurred.emit(f"Permission denied: {file_path}")
            return None
        except Exception as e:
            self.error_occurred.emit(f"Error reading {file_path}: {e}")
            return None

    def _calculate_directory_checksums(self, dir_path):
        """Calculates checksums for all files in a directory recursively."""
        results = {}
        files_to_process = []

        for root, _, files in os.walk(dir_path):
            if not self._is_running:
                break
            for filename in files:
                if not self._is_running:
                    break
                file_path = os.path.join(root, filename)
                files_to_process.append(file_path)

        total_files = len(files_to_process)
        processed_files = 0

        for file_path in files_to_process:
            if not self._is_running:
                break
            checksum = self._calculate_file_checksum(file_path)
            if checksum:
                relative_path = os.path.relpath(file_path, dir_path)
                results[relative_path] = checksum
            processed_files += 1

        return results

    def _verify_file_checksum(self, file_path, expected_checksum):
        """Verifies a single file against an expected checksum."""
        if not expected_checksum:
            return "ERROR: No expected checksum provided."
        calculated_checksum = self._calculate_file_checksum(file_path)
        if calculated_checksum is None:
            return "ERROR: Could not calculate checksum."
        if calculated_checksum.lower() == expected_checksum.lower():
            return "OK"
        return (f"MISMATCH (Expected: {expected_checksum}, "
                f"Got: {calculated_checksum})")

    def _parse_checksum_file(self, checksum_file_path):
        """Parses a checksum file (e.g., sha256sum output format)."""
        expected_checksums = {}
        try:
            with open(checksum_file_path, 'r') as f:
                for line in f:
                    if not self._is_running:
                        break
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split(None, 1)  # Split on first whitespace
                    if len(parts) == 2:
                        checksum, filename = parts
                        filename = filename.lstrip('*').strip()
                        expected_checksums[filename] = checksum
                    else:
                        msg = (f"Skipping malformed line in "
                               f"{checksum_file_path}: {line}")
                        self.error_occurred.emit(msg)
        except FileNotFoundError:
            msg = f"Checksum file not found: {checksum_file_path}"
            self.error_occurred.emit(msg)
            return None
        except Exception as e:
            msg = f"Error reading checksum file {checksum_file_path}: {e}"
            self.error_occurred.emit(msg)
            return None

        return expected_checksums

    def _verify_directory_checksums(self, dir_path, checksum_file_path):
        """Verifies files in a directory against a checksum file."""
        results = {}
        expected_checksums = self._parse_checksum_file(checksum_file_path)

        if expected_checksums is None:
            err = "ERROR: Failed to parse checksum file."
            return {checksum_file_path: err}

        processed_files = set()
        files_in_dir = []

        for root, _, files in os.walk(dir_path):
            if not self._is_running:
                break
            for filename in files:
                if not self._is_running:
                    break
                full_path = os.path.join(root, filename)
                relative_path = os.path.relpath(full_path, dir_path)
                relative_path = relative_path.replace('\\', '/')
                files_in_dir.append((full_path, relative_path))

        for full_path, relative_path in files_in_dir:
            if not self._is_running:
                break
            processed_files.add(relative_path)
            expected_checksum = expected_checksums.get(relative_path)

            if expected_checksum:
                status = self._verify_file_checksum(
                    full_path, 
                    expected_checksum
                )
                results[relative_path] = status
            else:
                results[relative_path] = "WARNING: Not found in checksum file."

        for relative_path in expected_checksums:
            if relative_path not in processed_files:
                msg = "ERROR: File listed in checksum file but not found"
                results[relative_path] = f"{msg} in directory."

        return results