"""
HP-02 Critical Issue Investigation
Debug file type detection failure

AUTHORITY: Enterprise Quality Engineering Gatekeeper
"""

import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import MagicMock

# Mock setup
mock_log_manager = MagicMock()
sys.modules["src.log_manager"] = mock_log_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from file_validator import detect_file_type
from file_validator.models import DetectionResult


def debug_file_detection():
    """Debug file detection issue."""
    print("HP-02 CRITICAL ISSUE INVESTIGATION")
    print("=" * 50)

    temp_dir = Path(tempfile.mkdtemp(prefix="debug_"))

    try:
        # Create test files
        test_files = {
            "pdf": (b"%PDF-1.4\ntest content", ".pdf"),
            "png": (bytes.fromhex("89504E470D0A1A0A"), ".png"),
            "gif": (b"GIF87a", ".gif"),
            "jpg": (bytes.fromhex("FFD8FF"), ".jpg"),
        }

        files = {}
        for ftype, (content, ext) in test_files.items():
            path = temp_dir / f"test_{ftype}{ext}"
            path.write_bytes(content)
            files[ftype] = path

        print(f"Created {len(files)} test files")

        # Test each file individually
        for ftype, path in files.items():
            print(f"\nTesting {ftype}: {path}")

            try:
                result = detect_file_type(path)
                print(f"   Result: {result}")
                print(f"   Type: {result.detected_type}")
                print(f"   Confidence: {result.confidence}")
                print(f"   Evidence: {result.evidence}")

            except Exception as e:
                print(f"   ERROR: {e}")
                print(f"   Traceback: {traceback.format_exc()}")

    finally:
        # Cleanup
        import shutil

        shutil.rmtree(temp_dir)
        print("\nCleanup completed")


if __name__ == "__main__":
    debug_file_detection()
