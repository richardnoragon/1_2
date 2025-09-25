#!/usr/bin/env python3
"""
PDF Operation Engine - Core functionality for PDF operations
Implements merge, split, and sign operations with comprehensive error handling
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
try:
    import PyPDF2

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pikepdf

    PIKEPDF_AVAILABLE = True
except ImportError:
    PIKEPDF_AVAILABLE = False

# Set up logger
logger = logging.getLogger(__name__)


class OperationType(Enum):
    """PDF operation types"""

    MERGE = "merge"
    SPLIT = "split"
    SIGN = "sign"


class OperationStatus(Enum):
    """Operation status types"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OperationResult:
    """Result of a PDF operation"""

    success: bool
    operation_type: OperationType
    input_files: List[str]
    output_files: List[str]
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class PDFValidator:
    """PDF file validation utilities"""

    @staticmethod
    def validate_pdf_file(file_path: str) -> Dict[str, Any]:
        """Comprehensive PDF file validation"""
        checks = {
            "exists": False,
            "readable": False,
            "valid_pdf": False,
            "encrypted": False,
            "corrupted": False,
            "page_count": 0,
            "file_size": 0,
            "error": None,
        }

        try:
            # Check file existence and accessibility
            if not os.path.exists(file_path):
                checks["error"] = f"File does not exist: {file_path}"
                return checks

            checks["exists"] = True
            checks["readable"] = os.access(file_path, os.R_OK)
            checks["file_size"] = os.path.getsize(file_path)

            if not checks["readable"]:
                checks["error"] = f"File is not readable: {file_path}"
                return checks

            # Validate PDF structure
            try:
                if PYMUPDF_AVAILABLE:
                    doc = fitz.open(file_path)
                    checks["valid_pdf"] = True
                    checks["encrypted"] = doc.needs_pass
                    checks["page_count"] = len(doc)
                    doc.close()

                    logger.debug(
                        f"PDF validation successful: {file_path} "
                        f"({checks['page_count']} pages)"
                    )
                else:
                    checks["error"] = "PyMuPDF not available for validation"
                    return checks

            except Exception as e:
                checks["corrupted"] = True
                checks["error"] = f"PDF validation failed: {str(e)}"
                logger.error(f"PDF validation failed for {file_path}: {e}")

        except Exception as e:
            checks["error"] = f"Validation error: {str(e)}"
            logger.error(f"File validation error for {file_path}: {e}")

        return checks

    @staticmethod
    def validate_multiple_files(
        file_paths: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """Validate multiple PDF files"""
        results = {}
        for file_path in file_paths:
            results[file_path] = PDFValidator.validate_pdf_file(file_path)
        return results


class PDFFileManager:
    """Handles file operations and output management"""

    def __init__(self):
        self.temp_dir = None
        self.created_files = []

    def create_temp_directory(self) -> str:
        """Create temporary directory for operations"""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix="pdf_ops_")
            logger.debug(f"Created temporary directory: {self.temp_dir}")
        return self.temp_dir

    def cleanup_temp_files(self):
        """Clean up temporary files and directories"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(
                    f"Cleaned up temporary directory: {self.temp_dir}"
                )
                self.temp_dir = None
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")

    def generate_output_filename(
        self,
        base_path: str,
        operation: str,
        suffix: str = "",
        extension: str = ".pdf",
    ) -> str:
        """Generate unique output filename"""
        base_name = os.path.splitext(os.path.basename(base_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if suffix:
            filename = (
                f"{base_name}_{operation}_{suffix}_{timestamp}{extension}"
            )
        else:
            filename = f"{base_name}_{operation}_{timestamp}{extension}"

        output_dir = os.path.dirname(base_path)
        output_path = os.path.join(output_dir, filename)

        # Ensure unique filename
        counter = 1
        while os.path.exists(output_path):
            if suffix:
                filename = f"{base_name}_{operation}_{suffix}_{timestamp}_{counter}{extension}"
            else:
                filename = (
                    f"{base_name}_{operation}_{timestamp}_{counter}{extension}"
                )
            output_path = os.path.join(output_dir, filename)
            counter += 1

        return output_path

    def backup_file(self, file_path: str) -> Optional[str]:
        """Create backup of original file"""
        try:
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return None


class ProgressTracker:
    """Tracks and reports operation progress"""

    def __init__(self, operation_name: str, total_steps: int):
        self.operation_name = operation_name
        self.total_steps = total_steps
        self.current_step = 0
        self.callbacks = []
        self.start_time = datetime.now()
        self.cancelled = False

    def add_callback(self, callback: Callable[[float, str], None]):
        """Add progress callback function"""
        self.callbacks.append(callback)

    def update_progress(self, step: int, message: str = ""):
        """Update progress and notify callbacks"""
        if self.cancelled:
            return

        self.current_step = step
        percentage = min((step / self.total_steps) * 100, 100.0)

        for callback in self.callbacks:
            try:
                callback(percentage, message)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")

    def cancel(self):
        """Cancel the operation"""
        self.cancelled = True
        logger.info(f"Operation cancelled: {self.operation_name}")

    def is_cancelled(self) -> bool:
        """Check if operation is cancelled"""
        return self.cancelled

    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now() - self.start_time).total_seconds()


class PDFMergeOperation:
    """PDF merge operation implementation"""

    def __init__(self, file_manager: PDFFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger(f"{__name__}.PDFMergeOperation")

    def execute(
        self,
        input_files: List[str],
        output_file: str,
        options: Dict[str, Any],
        progress_tracker: ProgressTracker,
    ) -> OperationResult:
        """Execute PDF merge operation"""
        start_time = datetime.now()

        try:
            if not PYMUPDF_AVAILABLE:
                error_msg = "PyMuPDF library is required for PDF operations"
                self.logger.error(error_msg)
                return OperationResult(
                    success=False,
                    operation_type=OperationType.MERGE,
                    input_files=input_files,
                    output_files=[],
                    error_message=error_msg,
                )

            self.logger.info(
                f"Starting merge operation: {len(input_files)} files -> {output_file}"
            )

            # Validate input files
            validation_results = PDFValidator.validate_multiple_files(
                input_files
            )
            invalid_files = [
                f for f, v in validation_results.items() if not v["valid_pdf"]
            ]

            if invalid_files:
                error_msg = f"Invalid PDF files: {', '.join(invalid_files)}"
                self.logger.error(error_msg)
                return OperationResult(
                    success=False,
                    operation_type=OperationType.MERGE,
                    input_files=input_files,
                    output_files=[],
                    error_message=error_msg,
                )

            # Create result document
            result_doc = fitz.open()
            total_files = len(input_files)

            for i, file_path in enumerate(input_files):
                if progress_tracker.is_cancelled():
                    result_doc.close()
                    return OperationResult(
                        success=False,
                        operation_type=OperationType.MERGE,
                        input_files=input_files,
                        output_files=[],
                        error_message="Operation cancelled by user",
                    )

                progress_tracker.update_progress(
                    i, f"Processing {os.path.basename(file_path)}"
                )

                try:
                    source_doc = fitz.open(file_path)

                    # Apply page range if specified
                    page_ranges = options.get("page_ranges", {})
                    if file_path in page_ranges:
                        page_range = page_ranges[file_path]
                        for page_num in page_range:
                            if 0 <= page_num < len(source_doc):
                                result_doc.insert_pdf(
                                    source_doc,
                                    from_page=page_num,
                                    to_page=page_num,
                                )
                    else:
                        # Insert all pages
                        result_doc.insert_pdf(source_doc)

                    source_doc.close()
                    self.logger.debug(f"Merged file: {file_path}")

                except Exception as e:
                    source_doc.close() if "source_doc" in locals() else None
                    error_msg = f"Failed to merge file {file_path}: {str(e)}"
                    self.logger.error(error_msg)
                    result_doc.close()
                    return OperationResult(
                        success=False,
                        operation_type=OperationType.MERGE,
                        input_files=input_files,
                        output_files=[],
                        error_message=error_msg,
                    )

            # Save result
            progress_tracker.update_progress(
                total_files, "Saving merged PDF..."
            )

            # Apply output options
            save_options = {}
            if options.get("optimize_output", False):
                save_options.update({"garbage": 4, "deflate": True})

            result_doc.save(output_file, **save_options)
            result_doc.close()

            processing_time = (datetime.now() - start_time).total_seconds()

            self.logger.info(
                f"Merge completed successfully: {output_file} ({processing_time:.2f}s)"
            )

            return OperationResult(
                success=True,
                operation_type=OperationType.MERGE,
                input_files=input_files,
                output_files=[output_file],
                processing_time=processing_time,
                details={
                    "total_pages": (
                        len(result_doc) if "result_doc" in locals() else 0
                    ),
                    "options_applied": options,
                },
            )

        except Exception as e:
            error_msg = f"Merge operation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            return OperationResult(
                success=False,
                operation_type=OperationType.MERGE,
                input_files=input_files,
                output_files=[],
                error_message=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds(),
            )


class PDFSplitOperation:
    """PDF split operation implementation"""

    def __init__(self, file_manager: PDFFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger(f"{__name__}.PDFSplitOperation")

    def execute(
        self,
        input_file: str,
        output_dir: str,
        options: Dict[str, Any],
        progress_tracker: ProgressTracker,
    ) -> OperationResult:
        """Execute PDF split operation"""
        start_time = datetime.now()
        output_files = []

        try:
            self.logger.info(
                f"Starting split operation: {input_file} -> {output_dir}"
            )

            # Validate input file
            validation = PDFValidator.validate_pdf_file(input_file)
            if not validation["valid_pdf"]:
                error_msg = f"Invalid PDF file: {validation.get('error', 'Unknown error')}"
                self.logger.error(error_msg)
                return OperationResult(
                    success=False,
                    operation_type=OperationType.SPLIT,
                    input_files=[input_file],
                    output_files=[],
                    error_message=error_msg,
                )

            source_doc = fitz.open(input_file)
            total_pages = len(source_doc)
            split_method = options.get("method", "pages")

            if split_method == "pages":
                output_files = self._split_by_pages(
                    source_doc,
                    input_file,
                    output_dir,
                    options,
                    progress_tracker,
                )
            elif split_method == "ranges":
                output_files = self._split_by_ranges(
                    source_doc,
                    input_file,
                    output_dir,
                    options,
                    progress_tracker,
                )
            elif split_method == "bookmarks":
                output_files = self._split_by_bookmarks(
                    source_doc,
                    input_file,
                    output_dir,
                    options,
                    progress_tracker,
                )
            elif split_method == "size":
                output_files = self._split_by_size(
                    source_doc,
                    input_file,
                    output_dir,
                    options,
                    progress_tracker,
                )
            else:
                raise ValueError(f"Unknown split method: {split_method}")

            source_doc.close()
            processing_time = (datetime.now() - start_time).total_seconds()

            self.logger.info(
                f"Split completed: {len(output_files)} files created ({processing_time:.2f}s)"
            )

            return OperationResult(
                success=True,
                operation_type=OperationType.SPLIT,
                input_files=[input_file],
                output_files=output_files,
                processing_time=processing_time,
                details={
                    "split_method": split_method,
                    "total_pages": total_pages,
                    "files_created": len(output_files),
                },
            )

        except Exception as e:
            if "source_doc" in locals():
                source_doc.close()

            error_msg = f"Split operation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            return OperationResult(
                success=False,
                operation_type=OperationType.SPLIT,
                input_files=[input_file],
                output_files=output_files,
                error_message=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds(),
            )

    def _split_by_pages(
        self,
        source_doc,
        input_file: str,
        output_dir: str,
        options: Dict[str, Any],
        progress_tracker: ProgressTracker,
    ) -> List[str]:
        """Split PDF by page count"""
        pages_per_file = options.get("pages_per_file", 1)
        naming_pattern = options.get("naming_pattern", "split_{index}.pdf")
        output_files = []
        total_pages = len(source_doc)

        for i in range(0, total_pages, pages_per_file):
            if progress_tracker.is_cancelled():
                break

            progress_tracker.update_progress(
                i, f"Creating file {len(output_files) + 1}"
            )

            new_doc = fitz.open()
            end_page = min(i + pages_per_file - 1, total_pages - 1)
            new_doc.insert_pdf(source_doc, from_page=i, to_page=end_page)

            output_file = os.path.join(
                output_dir, naming_pattern.format(index=len(output_files) + 1)
            )
            new_doc.save(output_file)
            new_doc.close()
            output_files.append(output_file)

            self.logger.debug(
                f"Created split file: {output_file} (pages {i+1}-{end_page+1})"
            )

        return output_files

    def _split_by_ranges(
        self,
        source_doc,
        input_file: str,
        output_dir: str,
        options: Dict[str, Any],
        progress_tracker: ProgressTracker,
    ) -> List[str]:
        """Split PDF by custom page ranges"""
        custom_ranges = options.get("custom_ranges", [])
        output_files = []

        for i, page_range in enumerate(custom_ranges):
            if progress_tracker.is_cancelled():
                break

            progress_tracker.update_progress(i, f"Creating range file {i + 1}")

            start_page, end_page = page_range
            new_doc = fitz.open()
            new_doc.insert_pdf(
                source_doc, from_page=start_page, to_page=end_page
            )

            output_file = os.path.join(
                output_dir, f"range_{start_page+1}-{end_page+1}.pdf"
            )
            new_doc.save(output_file)
            new_doc.close()
            output_files.append(output_file)

            self.logger.debug(
                f"Created range file: {output_file} (pages {start_page+1}-{end_page+1})"
            )

        return output_files

    def _split_by_bookmarks(
        self,
        source_doc,
        input_file: str,
        output_dir: str,
        options: Dict[str, Any],
        progress_tracker: ProgressTracker,
    ) -> List[str]:
        """Split PDF by bookmarks/table of contents"""
        # This is a placeholder for bookmark-based splitting
        # Would require parsing the document's table of contents
        self.logger.warning("Bookmark-based splitting not yet implemented")
        return []

    def _split_by_size(
        self,
        source_doc,
        input_file: str,
        output_dir: str,
        options: Dict[str, Any],
        progress_tracker: ProgressTracker,
    ) -> List[str]:
        """Split PDF by approximate file size"""
        # This is a placeholder for size-based splitting
        # Would require estimating page sizes and splitting accordingly
        self.logger.warning("Size-based splitting not yet implemented")
        return []


class PDFSignOperation:
    """PDF sign operation implementation"""

    def __init__(self, file_manager: PDFFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger(f"{__name__}.PDFSignOperation")

    def execute(
        self,
        input_file: str,
        signature_file: str,
        output_file: str,
        options: Dict[str, Any],
        progress_tracker: ProgressTracker,
    ) -> OperationResult:
        """Execute PDF sign operation"""
        start_time = datetime.now()

        try:
            self.logger.info(
                f"Starting sign operation: {input_file} -> {output_file}"
            )

            # Validate input files
            pdf_validation = PDFValidator.validate_pdf_file(input_file)
            if not pdf_validation["valid_pdf"]:
                error_msg = f"Invalid PDF file: {pdf_validation.get('error', 'Unknown error')}"
                return OperationResult(
                    success=False,
                    operation_type=OperationType.SIGN,
                    input_files=[input_file],
                    output_files=[],
                    error_message=error_msg,
                )

            if not os.path.exists(signature_file):
                error_msg = f"Signature file not found: {signature_file}"
                return OperationResult(
                    success=False,
                    operation_type=OperationType.SIGN,
                    input_files=[input_file],
                    output_files=[],
                    error_message=error_msg,
                )

            pdf_doc = fitz.open(input_file)
            total_pages = len(pdf_doc)

            # Determine pages to sign
            pages_option = options.get("pages", "all")
            if pages_option == "all":
                pages_to_sign = list(range(total_pages))
            elif pages_option == "first":
                pages_to_sign = [0]
            elif pages_option == "last":
                pages_to_sign = [total_pages - 1]
            elif isinstance(pages_option, list):
                pages_to_sign = [
                    p for p in pages_option if 0 <= p < total_pages
                ]
            else:
                pages_to_sign = [0]  # Default to first page

            # Apply signature to pages
            for i, page_num in enumerate(pages_to_sign):
                if progress_tracker.is_cancelled():
                    pdf_doc.close()
                    return OperationResult(
                        success=False,
                        operation_type=OperationType.SIGN,
                        input_files=[input_file],
                        output_files=[],
                        error_message="Operation cancelled by user",
                    )

                progress_tracker.update_progress(
                    i, f"Signing page {page_num + 1}"
                )

                page = pdf_doc[page_num]

                # Calculate signature position
                position = self._calculate_signature_position(
                    page.rect,
                    options.get("position", "bottom_right"),
                    options.get("size", (100, 50)),
                )

                # Insert signature image
                transparency = int(options.get("transparency", 0.8) * 255)
                page.insert_image(
                    position,
                    filename=signature_file,
                    overlay=True,
                    alpha=transparency,
                )

                self.logger.debug(f"Applied signature to page {page_num + 1}")

            # Save signed PDF
            progress_tracker.update_progress(
                len(pages_to_sign), "Saving signed PDF..."
            )
            pdf_doc.save(output_file)
            pdf_doc.close()

            # Add digital signature if requested
            if options.get("digital_signature", False) and options.get(
                "certificate_file"
            ):
                self._add_digital_signature(
                    output_file, options["certificate_file"]
                )

            processing_time = (datetime.now() - start_time).total_seconds()

            self.logger.info(
                f"Sign completed successfully: {output_file} ({processing_time:.2f}s)"
            )

            return OperationResult(
                success=True,
                operation_type=OperationType.SIGN,
                input_files=[input_file],
                output_files=[output_file],
                processing_time=processing_time,
                details={
                    "pages_signed": len(pages_to_sign),
                    "signature_file": signature_file,
                    "digital_signature": options.get(
                        "digital_signature", False
                    ),
                },
            )

        except Exception as e:
            if "pdf_doc" in locals():
                pdf_doc.close()

            error_msg = f"Sign operation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            return OperationResult(
                success=False,
                operation_type=OperationType.SIGN,
                input_files=[input_file],
                output_files=[],
                error_message=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds(),
            )

    def _calculate_signature_position(
        self, page_rect, position, size
    ) -> fitz.Rect:
        """Calculate signature position on page"""
        width, height = size

        positions = {
            "top_left": (10, 10),
            "top_right": (page_rect.width - width - 10, 10),
            "bottom_left": (10, page_rect.height - height - 10),
            "bottom_right": (
                page_rect.width - width - 10,
                page_rect.height - height - 10,
            ),
            "center": (
                (page_rect.width - width) / 2,
                (page_rect.height - height) / 2,
            ),
        }

        if isinstance(position, str) and position in positions:
            x, y = positions[position]
        elif isinstance(position, (tuple, list)) and len(position) == 2:
            x, y = position  # Custom coordinates
        else:
            x, y = positions["bottom_right"]  # Default

        return fitz.Rect(x, y, x + width, y + height)

    def _add_digital_signature(self, pdf_file: str, certificate_file: str):
        """Add digital signature using certificate (placeholder)"""
        # This would require pikepdf or similar library for cryptographic signatures
        self.logger.warning(
            "Digital signature functionality not yet implemented"
        )


class PDFOperationEngine:
    """Main PDF operation engine"""

    def __init__(self):
        self.file_manager = PDFFileManager()
        self.merge_operation = PDFMergeOperation(self.file_manager)
        self.split_operation = PDFSplitOperation(self.file_manager)
        self.sign_operation = PDFSignOperation(self.file_manager)
        self.logger = logging.getLogger(f"{__name__}.PDFOperationEngine")

    def merge_pdfs(
        self,
        input_files: List[str],
        output_file: str,
        options: Dict[str, Any] = None,
        progress_callback: Callable[[float, str], None] = None,
    ) -> OperationResult:
        """Execute PDF merge operation"""
        options = options or {}
        progress_tracker = ProgressTracker("PDF Merge", len(input_files) + 1)

        if progress_callback:
            progress_tracker.add_callback(progress_callback)

        try:
            return self.merge_operation.execute(
                input_files, output_file, options, progress_tracker
            )
        finally:
            self.file_manager.cleanup_temp_files()

    def split_pdf(
        self,
        input_file: str,
        output_dir: str,
        options: Dict[str, Any] = None,
        progress_callback: Callable[[float, str], None] = None,
    ) -> OperationResult:
        """Execute PDF split operation"""
        options = options or {}

        # Estimate progress steps based on split method
        if options.get("method") == "pages":
            validation = PDFValidator.validate_pdf_file(input_file)
            total_pages = validation.get("page_count", 1)
            pages_per_file = options.get("pages_per_file", 1)
            estimated_files = max(1, total_pages // pages_per_file)
        else:
            estimated_files = len(options.get("custom_ranges", [1]))

        progress_tracker = ProgressTracker("PDF Split", estimated_files)

        if progress_callback:
            progress_tracker.add_callback(progress_callback)

        try:
            return self.split_operation.execute(
                input_file, output_dir, options, progress_tracker
            )
        finally:
            self.file_manager.cleanup_temp_files()

    def sign_pdf(
        self,
        input_file: str,
        signature_file: str,
        output_file: str,
        options: Dict[str, Any] = None,
        progress_callback: Callable[[float, str], None] = None,
    ) -> OperationResult:
        """Execute PDF sign operation"""
        options = options or {}

        # Estimate progress steps based on pages to sign
        pages_option = options.get("pages", "all")
        if pages_option == "all":
            validation = PDFValidator.validate_pdf_file(input_file)
            estimated_pages = validation.get("page_count", 1)
        elif isinstance(pages_option, list):
            estimated_pages = len(pages_option)
        else:
            estimated_pages = 1

        progress_tracker = ProgressTracker("PDF Sign", estimated_pages + 1)

        if progress_callback:
            progress_tracker.add_callback(progress_callback)

        try:
            return self.sign_operation.execute(
                input_file,
                signature_file,
                output_file,
                options,
                progress_tracker,
            )
        finally:
            self.file_manager.cleanup_temp_files()

    def cleanup(self):
        """Clean up resources"""
        self.file_manager.cleanup_temp_files()


if __name__ == "__main__":
    # Test the PDF operation engine
    logging.basicConfig(level=logging.DEBUG)

    engine = PDFOperationEngine()

    # Example usage (would need actual PDF files to test)
    print("PDF Operation Engine initialized successfully!")
    print(f"PyPDF2 available: {PYPDF2_AVAILABLE}")
    print(f"pikepdf available: {PIKEPDF_AVAILABLE}")
