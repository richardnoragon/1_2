"""
PDF Enhancement Engine - Phase 2.4 Implementation
Provides PDF optimization, compression, metadata management,
and quality improvements.
"""

import os
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime

try:
    import fitz  # PyMuPDF

    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import pikepdf

    HAS_PIKEPDF = True
except ImportError:
    HAS_PIKEPDF = False

try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class EnhancementOperation(Enum):
    """Types of PDF enhancement operations"""

    OPTIMIZE = "optimize"
    COMPRESS = "compress"
    COMPRESS_IMAGES = "compress_images"
    REMOVE_DUPLICATES = "remove_duplicates"
    CLEAN_METADATA = "clean_metadata"
    UPDATE_METADATA = "update_metadata"
    REPAIR = "repair"
    LINEARIZE = "linearize"
    REDUCE_FILE_SIZE = "reduce_file_size"
    ENHANCE_QUALITY = "enhance_quality"


class CompressionLevel(Enum):
    """PDF compression levels"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class ImageQuality(Enum):
    """Image quality levels for compression"""

    VERY_LOW = 30
    LOW = 50
    MEDIUM = 70
    HIGH = 85
    VERY_HIGH = 95


class OptimizationLevel(Enum):
    """PDF optimization levels"""

    BASIC = "basic"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    WEB_OPTIMIZED = "web_optimized"


@dataclass
class EnhancementResult:
    """Result of an enhancement operation"""

    success: bool
    operation: EnhancementOperation
    message: str
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    original_size: int = 0
    optimized_size: int = 0
    compression_ratio: float = 0.0
    processing_time: float = 0.0
    improvements: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class EnhancementSettings:
    """PDF enhancement configuration"""

    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    compression_level: CompressionLevel = CompressionLevel.MEDIUM
    image_quality: ImageQuality = ImageQuality.MEDIUM
    compress_images: bool = True
    remove_unused_objects: bool = True
    remove_duplicate_objects: bool = True
    optimize_content_streams: bool = True
    linearize_pdf: bool = False
    remove_metadata: bool = False
    preserve_quality: bool = True
    target_file_size_mb: Optional[float] = None
    max_image_width: int = 1200
    max_image_height: int = 1600
    grayscale_conversion: bool = False


@dataclass
class MetadataSettings:
    """PDF metadata configuration"""

    title: str = ""
    author: str = ""
    subject: str = ""
    keywords: str = ""
    creator: str = ""
    producer: str = ""
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    custom_properties: Dict[str, str] = field(default_factory=dict)
    remove_all_metadata: bool = False
    preserve_creation_date: bool = True


class PDFEnhancementValidator:
    """Validates PDF files and enhancement operations"""

    @staticmethod
    def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
        """Validate if file is a valid PDF"""
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        if not file_path.lower().endswith(".pdf"):
            return False, "File must have .pdf extension"

        try:
            if HAS_PYMUPDF:
                doc = fitz.open(file_path)
                doc.close()
                return True, "Valid PDF file"
            elif HAS_PIKEPDF:
                pikepdf.open(file_path).close()
                return True, "Valid PDF file"
            else:
                return False, "No PDF processing library available"
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"

    @staticmethod
    def validate_enhancement_settings(
        settings: EnhancementSettings,
    ) -> Tuple[bool, str]:
        """Validate enhancement settings"""
        if settings.target_file_size_mb and settings.target_file_size_mb <= 0:
            return False, "Target file size must be positive"

        if settings.max_image_width <= 0 or settings.max_image_height <= 0:
            return False, "Image dimensions must be positive"

        return True, "Valid enhancement settings"

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0


class PDFOptimizer:
    """Handles PDF optimization and compression"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def optimize_pdf(
        self, input_path: str, output_path: str, settings: EnhancementSettings
    ) -> EnhancementResult:
        """Optimize PDF with specified settings"""
        try:
            start_time = datetime.now()

            # Validate inputs
            valid, msg = PDFEnhancementValidator.validate_pdf_file(input_path)
            if not valid:
                return EnhancementResult(
                    False, EnhancementOperation.OPTIMIZE, msg
                )

            valid, msg = PDFEnhancementValidator.validate_enhancement_settings(
                settings
            )
            if not valid:
                return EnhancementResult(
                    False, EnhancementOperation.OPTIMIZE, msg
                )

            original_size = PDFEnhancementValidator.get_file_size(input_path)

            # Use pikepdf for optimization (preferred)
            if HAS_PIKEPDF:
                result = self._optimize_with_pikepdf(
                    input_path, output_path, settings
                )
            elif HAS_PYMUPDF:
                result = self._optimize_with_pymupdf(
                    input_path, output_path, settings
                )
            else:
                return EnhancementResult(
                    False,
                    EnhancementOperation.OPTIMIZE,
                    "No optimization library available (pikepdf or PyMuPDF required)",
                )

            # Calculate metrics
            if result.success:
                optimized_size = PDFEnhancementValidator.get_file_size(
                    output_path
                )
                processing_time = (datetime.now() - start_time).total_seconds()

                result.original_size = original_size
                result.optimized_size = optimized_size
                result.compression_ratio = (
                    (1 - optimized_size / original_size) * 100
                    if original_size > 0
                    else 0
                )
                result.processing_time = processing_time

                result.improvements = {
                    "size_reduction_bytes": original_size - optimized_size,
                    "size_reduction_percent": result.compression_ratio,
                    "processing_time_seconds": processing_time,
                }

            return result

        except Exception as e:
            self.logger.error(f"PDF optimization failed: {str(e)}")
            return EnhancementResult(
                False,
                EnhancementOperation.OPTIMIZE,
                f"Optimization failed: {str(e)}",
            )

    def _optimize_with_pikepdf(
        self, input_path: str, output_path: str, settings: EnhancementSettings
    ) -> EnhancementResult:
        """Optimize PDF using pikepdf"""
        try:
            with pikepdf.open(input_path) as pdf:
                # Remove unused objects
                if settings.remove_unused_objects:
                    pdf.remove_unreferenced_resources()

                # Optimize content streams
                if settings.optimize_content_streams:
                    for page in pdf.pages:
                        page.compress_content_streams()

                # Save with optimization
                save_params = {
                    "compress_streams": True,
                    "stream_decode_level": pikepdf.StreamDecodeLevel.generalized,
                    "object_stream_mode": pikepdf.ObjectStreamMode.generate,
                    "normalize_content": True,
                    "linearize": settings.linearize_pdf,
                }

                pdf.save(output_path, **save_params)

            return EnhancementResult(
                True,
                EnhancementOperation.OPTIMIZE,
                f"PDF optimized successfully using pikepdf",
                input_path=input_path,
                output_path=output_path,
            )

        except Exception as e:
            return EnhancementResult(
                False,
                EnhancementOperation.OPTIMIZE,
                f"pikepdf optimization failed: {str(e)}",
            )

    def _optimize_with_pymupdf(
        self, input_path: str, output_path: str, settings: EnhancementSettings
    ) -> EnhancementResult:
        """Optimize PDF using PyMuPDF"""
        try:
            doc = fitz.open(input_path)

            # Apply optimization based on level
            if settings.optimization_level == OptimizationLevel.AGGRESSIVE:
                # Aggressive optimization
                doc.scrub()  # Remove sensitive information

            # Compress images if requested
            if settings.compress_images and HAS_PIL:
                self._compress_images_pymupdf(doc, settings)

            # Save with optimization flags
            save_flags = 0
            if settings.remove_unused_objects:
                save_flags |= fitz.PDF_OPT_GARBAGE_COMPACT
            if settings.optimize_content_streams:
                save_flags |= fitz.PDF_OPT_CONTENT_STREAMS
            if settings.linearize_pdf:
                save_flags |= fitz.PDF_OPT_LINEARIZE

            doc.save(output_path, deflate=True, garbage=4, clean=True)
            doc.close()

            return EnhancementResult(
                True,
                EnhancementOperation.OPTIMIZE,
                f"PDF optimized successfully using PyMuPDF",
                input_path=input_path,
                output_path=output_path,
            )

        except Exception as e:
            return EnhancementResult(
                False,
                EnhancementOperation.OPTIMIZE,
                f"PyMuPDF optimization failed: {str(e)}",
            )

    def _compress_images_pymupdf(self, doc, settings: EnhancementSettings):
        """Compress images in PDF using PyMuPDF"""
        try:
            for page_num in range(doc.page_count):
                page = doc[page_num]
                image_list = page.get_images()

                for img_index, img in enumerate(image_list):
                    xref = img[0]

                    # Get image data
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    if HAS_PIL and image_ext in ["png", "jpg", "jpeg"]:
                        # Process with PIL
                        import io

                        pil_image = Image.open(io.BytesIO(image_bytes))

                        # Resize if too large
                        if (
                            pil_image.width > settings.max_image_width
                            or pil_image.height > settings.max_image_height
                        ):
                            pil_image.thumbnail(
                                (
                                    settings.max_image_width,
                                    settings.max_image_height,
                                ),
                                Image.Resampling.LANCZOS,
                            )

                        # Convert to grayscale if requested
                        if (
                            settings.grayscale_conversion
                            and pil_image.mode != "L"
                        ):
                            pil_image = pil_image.convert("L")

                        # Compress
                        output_buffer = io.BytesIO()
                        if pil_image.mode == "RGBA":
                            pil_image = pil_image.convert("RGB")

                        pil_image.save(
                            output_buffer,
                            format="JPEG",
                            quality=settings.image_quality.value,
                            optimize=True,
                        )

                        # Replace image in PDF
                        compressed_bytes = output_buffer.getvalue()
                        if len(compressed_bytes) < len(image_bytes):
                            doc._replace_image(xref, compressed_bytes)

        except Exception as e:
            self.logger.warning(f"Image compression failed: {e}")

    def compress_pdf(
        self,
        input_path: str,
        output_path: str,
        compression_level: CompressionLevel,
    ) -> EnhancementResult:
        """Compress PDF file"""
        settings = EnhancementSettings(compression_level=compression_level)
        return self.optimize_pdf(input_path, output_path, settings)

    def repair_pdf(
        self, input_path: str, output_path: str
    ) -> EnhancementResult:
        """Attempt to repair a corrupted PDF"""
        try:
            if HAS_PIKEPDF:
                return self._repair_with_pikepdf(input_path, output_path)
            elif HAS_PYMUPDF:
                return self._repair_with_pymupdf(input_path, output_path)
            else:
                return EnhancementResult(
                    False,
                    EnhancementOperation.REPAIR,
                    "No repair library available",
                )

        except Exception as e:
            return EnhancementResult(
                False,
                EnhancementOperation.REPAIR,
                f"PDF repair failed: {str(e)}",
            )

    def _repair_with_pikepdf(
        self, input_path: str, output_path: str
    ) -> EnhancementResult:
        """Repair PDF using pikepdf"""
        try:
            with pikepdf.open(input_path, allow_overwriting_input=True) as pdf:
                # pikepdf automatically repairs many issues during opening
                pdf.save(output_path)

            return EnhancementResult(
                True,
                EnhancementOperation.REPAIR,
                "PDF repaired successfully using pikepdf",
                input_path=input_path,
                output_path=output_path,
            )

        except Exception as e:
            return EnhancementResult(
                False,
                EnhancementOperation.REPAIR,
                f"pikepdf repair failed: {str(e)}",
            )

    def _repair_with_pymupdf(
        self, input_path: str, output_path: str
    ) -> EnhancementResult:
        """Repair PDF using PyMuPDF"""
        try:
            doc = fitz.open(input_path)

            # PyMuPDF automatically repairs many issues
            # Save with repair options
            doc.save(output_path, garbage=4, clean=True)
            doc.close()

            return EnhancementResult(
                True,
                EnhancementOperation.REPAIR,
                "PDF repaired successfully using PyMuPDF",
                input_path=input_path,
                output_path=output_path,
            )

        except Exception as e:
            return EnhancementResult(
                False,
                EnhancementOperation.REPAIR,
                f"PyMuPDF repair failed: {str(e)}",
            )


class PDFMetadataManager:
    """Handles PDF metadata operations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def update_metadata(
        self, input_path: str, output_path: str, metadata: MetadataSettings
    ) -> EnhancementResult:
        """Update PDF metadata"""
        try:
            valid, msg = PDFEnhancementValidator.validate_pdf_file(input_path)
            if not valid:
                return EnhancementResult(
                    False, EnhancementOperation.UPDATE_METADATA, msg
                )

            if HAS_PIKEPDF:
                return self._update_metadata_pikepdf(
                    input_path, output_path, metadata
                )
            elif HAS_PYMUPDF:
                return self._update_metadata_pymupdf(
                    input_path, output_path, metadata
                )
            else:
                return EnhancementResult(
                    False,
                    EnhancementOperation.UPDATE_METADATA,
                    "No metadata library available",
                )

        except Exception as e:
            return EnhancementResult(
                False,
                EnhancementOperation.UPDATE_METADATA,
                f"Metadata update failed: {str(e)}",
            )

    def _update_metadata_pikepdf(
        self, input_path: str, output_path: str, metadata: MetadataSettings
    ) -> EnhancementResult:
        """Update metadata using pikepdf"""
        try:
            with pikepdf.open(input_path) as pdf:
                if metadata.remove_all_metadata:
                    # Remove all metadata
                    if "/Info" in pdf.Root:
                        del pdf.Root["/Info"]
                    pdf.remove_unreferenced_resources()
                else:
                    # Update metadata
                    with pdf.open_metadata() as meta:
                        if metadata.title:
                            meta["dc:title"] = metadata.title
                        if metadata.author:
                            meta["dc:creator"] = metadata.author
                        if metadata.subject:
                            meta["dc:subject"] = metadata.subject
                        if metadata.keywords:
                            meta["pdf:Keywords"] = metadata.keywords
                        if metadata.creator:
                            meta["xmp:CreatorTool"] = metadata.creator
                        if metadata.producer:
                            meta["pdf:Producer"] = metadata.producer

                        # Set dates
                        if metadata.creation_date:
                            meta["xmp:CreateDate"] = metadata.creation_date
                        if metadata.modification_date:
                            meta["xmp:ModifyDate"] = metadata.modification_date
                        else:
                            meta["xmp:ModifyDate"] = datetime.now()

                pdf.save(output_path)

            return EnhancementResult(
                True,
                EnhancementOperation.UPDATE_METADATA,
                "Metadata updated successfully using pikepdf",
                input_path=input_path,
                output_path=output_path,
            )

        except Exception as e:
            return EnhancementResult(
                False,
                EnhancementOperation.UPDATE_METADATA,
                f"pikepdf metadata update failed: {str(e)}",
            )

    def _update_metadata_pymupdf(
        self, input_path: str, output_path: str, metadata: MetadataSettings
    ) -> EnhancementResult:
        """Update metadata using PyMuPDF"""
        try:
            doc = fitz.open(input_path)

            if metadata.remove_all_metadata:
                # Clear all metadata
                doc.set_metadata({})
            else:
                # Update metadata
                meta_dict = {}
                if metadata.title:
                    meta_dict["title"] = metadata.title
                if metadata.author:
                    meta_dict["author"] = metadata.author
                if metadata.subject:
                    meta_dict["subject"] = metadata.subject
                if metadata.keywords:
                    meta_dict["keywords"] = metadata.keywords
                if metadata.creator:
                    meta_dict["creator"] = metadata.creator
                if metadata.producer:
                    meta_dict["producer"] = metadata.producer

                # Preserve creation date if requested
                if metadata.preserve_creation_date:
                    current_meta = doc.metadata
                    if "creationDate" in current_meta:
                        meta_dict["creationDate"] = current_meta[
                            "creationDate"
                        ]

                # Set modification date
                meta_dict["modDate"] = datetime.now().strftime(
                    "D:%Y%m%d%H%M%S"
                )

                doc.set_metadata(meta_dict)

            doc.save(output_path)
            doc.close()

            return EnhancementResult(
                True,
                EnhancementOperation.UPDATE_METADATA,
                "Metadata updated successfully using PyMuPDF",
                input_path=input_path,
                output_path=output_path,
            )

        except Exception as e:
            return EnhancementResult(
                False,
                EnhancementOperation.UPDATE_METADATA,
                f"PyMuPDF metadata update failed: {str(e)}",
            )

    def clean_metadata(
        self, input_path: str, output_path: str
    ) -> EnhancementResult:
        """Remove all metadata from PDF"""
        metadata = MetadataSettings(remove_all_metadata=True)
        return self.update_metadata(input_path, output_path, metadata)

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get PDF metadata information"""
        try:
            if HAS_PYMUPDF:
                doc = fitz.open(file_path)
                metadata = doc.metadata
                doc.close()
                return metadata
            elif HAS_PIKEPDF:
                with pikepdf.open(file_path) as pdf:
                    try:
                        with pdf.open_metadata() as meta:
                            return dict(meta)
                    except Exception:
                        return {}
            else:
                return {}

        except Exception as e:
            self.logger.error(f"Failed to get metadata: {e}")
            return {}


class PDFEnhancementEngine:
    """Main PDF enhancement operations engine"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimizer = PDFOptimizer()
        self.metadata_manager = PDFMetadataManager()

    def check_dependencies(self) -> Dict[str, bool]:
        """Check available enhancement libraries"""
        return {"pymupdf": HAS_PYMUPDF, "pikepdf": HAS_PIKEPDF, "pil": HAS_PIL}

    def optimize_pdf(
        self, input_path: str, output_path: str, settings: EnhancementSettings
    ) -> EnhancementResult:
        """Optimize PDF with specified settings"""
        return self.optimizer.optimize_pdf(input_path, output_path, settings)

    def compress_pdf(
        self,
        input_path: str,
        output_path: str,
        compression_level: CompressionLevel = CompressionLevel.MEDIUM,
    ) -> EnhancementResult:
        """Compress PDF file"""
        return self.optimizer.compress_pdf(
            input_path, output_path, compression_level
        )

    def repair_pdf(
        self, input_path: str, output_path: str
    ) -> EnhancementResult:
        """Repair corrupted PDF"""
        return self.optimizer.repair_pdf(input_path, output_path)

    def update_metadata(
        self, input_path: str, output_path: str, metadata: MetadataSettings
    ) -> EnhancementResult:
        """Update PDF metadata"""
        return self.metadata_manager.update_metadata(
            input_path, output_path, metadata
        )

    def clean_metadata(
        self, input_path: str, output_path: str
    ) -> EnhancementResult:
        """Remove all metadata from PDF"""
        return self.metadata_manager.clean_metadata(input_path, output_path)

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get PDF metadata"""
        return self.metadata_manager.get_metadata(file_path)

    def batch_optimize(
        self,
        file_paths: List[str],
        output_dir: str,
        settings: EnhancementSettings,
    ) -> List[EnhancementResult]:
        """Optimize multiple PDF files"""
        results = []

        for file_path in file_paths:
            try:
                filename = os.path.basename(file_path)
                output_path = os.path.join(output_dir, f"optimized_{filename}")

                result = self.optimize_pdf(file_path, output_path, settings)
                results.append(result)

            except Exception as e:
                results.append(
                    EnhancementResult(
                        False,
                        EnhancementOperation.OPTIMIZE,
                        f"Batch optimization failed for {file_path}: {str(e)}",
                    )
                )

        return results

    def analyze_pdf(self, file_path: str) -> Dict[str, Any]:
        """Analyze PDF file for optimization opportunities"""
        try:
            analysis = {
                "file_size": PDFEnhancementValidator.get_file_size(file_path),
                "metadata": self.get_metadata(file_path),
                "optimization_suggestions": [],
            }

            if HAS_PYMUPDF:
                doc = fitz.open(file_path)
                analysis.update(
                    {
                        "page_count": doc.page_count,
                        "has_images": False,
                        "image_count": 0,
                        "has_forms": doc.is_form_pdf,
                        "is_encrypted": doc.needs_pass,
                    }
                )

                # Count images
                total_images = 0
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    images = page.get_images()
                    total_images += len(images)

                analysis["image_count"] = total_images
                analysis["has_images"] = total_images > 0

                # Generate suggestions
                if total_images > 0:
                    analysis["optimization_suggestions"].append(
                        "Consider image compression"
                    )

                if analysis["file_size"] > 10 * 1024 * 1024:  # 10MB
                    analysis["optimization_suggestions"].append(
                        "Large file - consider aggressive optimization"
                    )

                doc.close()

            return analysis

        except Exception as e:
            self.logger.error(f"PDF analysis failed: {e}")
            return {"error": str(e)}


# Convenience functions for external access
def create_enhancement_engine() -> PDFEnhancementEngine:
    """Create a new PDF enhancement engine instance"""
    return PDFEnhancementEngine()


def create_enhancement_settings(
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
    compression_level: CompressionLevel = CompressionLevel.MEDIUM,
    **kwargs,
) -> EnhancementSettings:
    """Create enhancement settings with convenience parameters"""
    settings = EnhancementSettings(
        optimization_level=optimization_level,
        compression_level=compression_level,
    )

    # Apply optional parameters
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

    return settings


def create_metadata_settings(
    title: str = "", author: str = "", subject: str = "", **kwargs
) -> MetadataSettings:
    """Create metadata settings with convenience parameters"""
    settings = MetadataSettings(title=title, author=author, subject=subject)

    # Apply optional parameters
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

    return settings
