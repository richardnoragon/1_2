#!/usr/bin/env python3
"""
PDF Extraction Engine - Phase 2.2 Implementation
Core functionality for PDF content extraction operations following
established patterns. Implements text, image, metadata, table, and
link extraction with comprehensive error handling
"""

import os
import logging
import shutil
import json
import csv
from typing import List, Dict, Any, Optional, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import io

# PDF processing libraries
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pikepdf
    PIKEPDF_AVAILABLE = True
except ImportError:
    PIKEPDF_AVAILABLE = False

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Set up logger
logger = logging.getLogger(__name__)


class ExtractionType(Enum):
    """PDF extraction operation types"""
    TEXT = "text"
    IMAGES = "images"
    METADATA = "metadata"
    TABLES = "tables"
    LINKS = "links"


class ExtractionStatus(Enum):
    """Extraction operation status types"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExtractionResult:
    """Result of a PDF extraction operation"""
    success: bool
    extraction_type: ExtractionType
    input_file: str
    output_files: List[str]
    extracted_data: Optional[Any] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class PDFExtractionValidator:
    """PDF file validation utilities for extraction operations"""
    
    @staticmethod
    def validate_extraction_file(file_path: str, 
                               extraction_type: ExtractionType) -> Dict[str, Any]:
        """Comprehensive PDF file validation for extraction"""
        checks = {
            'exists': False,
            'readable': False,
            'valid_pdf': False,
            'encrypted': False,
            'corrupted': False,
            'page_count': 0,
            'file_size': 0,
            'extraction_compatible': False,
            'error': None
        }
        
        try:
            # Basic file checks
            if not os.path.exists(file_path):
                checks['error'] = f"File does not exist: {file_path}"
                return checks
            
            checks['exists'] = True
            checks['readable'] = os.access(file_path, os.R_OK)
            checks['file_size'] = os.path.getsize(file_path)
            
            if not checks['readable']:
                checks['error'] = f"File is not readable: {file_path}"
                return checks
            
            # Validate PDF structure
            if PYMUPDF_AVAILABLE:
                try:
                    doc = fitz.open(file_path)
                    checks['valid_pdf'] = True
                    checks['encrypted'] = doc.needs_pass
                    checks['page_count'] = len(doc)
                    
                    # Check extraction-specific compatibility
                    checks['extraction_compatible'] = (
                        PDFExtractionValidator._check_extraction_compatibility(
                            doc, extraction_type
                        )
                    )
                    
                    doc.close()
                    logger.debug(
                        f"PDF validation successful for {extraction_type.value}: "
                        f"{file_path}"
                    )
                    
                except Exception as e:
                    checks['corrupted'] = True
                    checks['error'] = f"PDF validation failed: {str(e)}"
                    logger.error(f"PDF validation failed for {file_path}: {e}")
            else:
                checks['error'] = "PyMuPDF not available for validation"
                
        except Exception as e:
            checks['error'] = f"Validation error: {str(e)}"
            logger.error(f"File validation error for {file_path}: {e}")
        
        return checks
    
    @staticmethod
    def _check_extraction_compatibility(doc, extraction_type: ExtractionType) -> bool:
        """Check if PDF is compatible with specific extraction type"""
        try:
            if extraction_type == ExtractionType.TEXT:
                # Check if PDF has extractable text
                for page_num in range(min(3, len(doc))):  # Check first 3 pages
                    page = doc[page_num]
                    if page.get_text().strip():
                        return True
                return False
                
            elif extraction_type == ExtractionType.IMAGES:
                # Check if PDF has images
                for page_num in range(min(3, len(doc))):
                    page = doc[page_num]
                    if page.get_images():
                        return True
                return False
                
            elif extraction_type == ExtractionType.LINKS:
                # Check if PDF has links
                for page_num in range(min(3, len(doc))):
                    page = doc[page_num]
                    if page.get_links():
                        return True
                return False
                
            elif extraction_type in [ExtractionType.METADATA, ExtractionType.TABLES]:
                # These operations are generally possible on most PDFs
                return True
                
        except Exception as e:
            logger.warning(f"Compatibility check failed for {extraction_type.value}: {e}")
            
        return True  # Default to compatible


class PDFExtractionFileManager:
    """Handles file operations and output management for extractions"""
    
    def __init__(self):
        self.temp_dir = None
        self.created_files = []
        self.extraction_outputs = {}
    
    def create_extraction_directory(self, base_path: str, extraction_type: ExtractionType) -> str:
        """Create directory for extraction outputs"""
        base_name = os.path.splitext(os.path.basename(base_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_dir = os.path.join(
            os.path.dirname(base_path),
            f"{base_name}_{extraction_type.value}_extracted_{timestamp}"
        )
        
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Created extraction directory: {output_dir}")
        return output_dir
    
    def generate_output_filename(self, base_path: str, extraction_type: ExtractionType, 
                                suffix: str = "", extension: Optional[str] = None) -> str:
        """Generate output filename for extraction"""
        base_name = os.path.splitext(os.path.basename(base_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if extension is None:
            # Default extensions based on extraction type
            extensions = {
                ExtractionType.TEXT: ".txt",
                ExtractionType.METADATA: ".json",
                ExtractionType.LINKS: ".json",
                ExtractionType.TABLES: ".csv",
                ExtractionType.IMAGES: ""  # Will be handled per image
            }
            extension = extensions.get(extraction_type, ".txt")
        
        if suffix:
            filename = f"{base_name}_{extraction_type.value}_{suffix}_{timestamp}{extension}"
        else:
            filename = f"{base_name}_{extraction_type.value}_{timestamp}{extension}"
        
        output_dir = os.path.dirname(base_path)
        output_path = os.path.join(output_dir, filename)
        
        # Ensure unique filename
        counter = 1
        while os.path.exists(output_path):
            if suffix:
                filename = f"{base_name}_{extraction_type.value}_{suffix}_{timestamp}_{counter}{extension}"
            else:
                filename = f"{base_name}_{extraction_type.value}_{timestamp}_{counter}{extension}"
            output_path = os.path.join(output_dir, filename)
            counter += 1
        
        return output_path
    
    def save_extraction_data(self, data: Any, output_path: str, data_format: str = "auto") -> bool:
        """Save extracted data in appropriate format"""
        try:
            if data_format == "auto":
                # Determine format from extension
                ext = os.path.splitext(output_path)[1].lower()
                if ext == ".json":
                    data_format = "json"
                elif ext == ".csv":
                    data_format = "csv"
                elif ext == ".txt":
                    data_format = "text"
                else:
                    data_format = "text"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if data_format == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            elif data_format == "csv":
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    # List of dictionaries to CSV
                    with open(output_path, 'w', newline='', encoding='utf-8') as f:
                        if data:
                            writer = csv.DictWriter(f, fieldnames=data[0].keys())
                            writer.writeheader()
                            writer.writerows(data)
                elif hasattr(data, 'to_csv'):
                    # DataFrame or similar
                    data.to_csv(output_path, index=False)
                else:
                    # Fallback to string representation
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(str(data))
            else:  # text format
                with open(output_path, 'w', encoding='utf-8') as f:
                    if isinstance(data, (list, tuple)):
                        f.write('\n'.join(str(item) for item in data))
                    else:
                        f.write(str(data))
            
            self.created_files.append(output_path)
            logger.debug(f"Saved extraction data to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save extraction data to {output_path}: {e}")
            return False
    
    def cleanup_temp_files(self):
        """Clean up temporary files and directories"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
                self.temp_dir = None
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")


class PDFTextExtraction:
    """PDF text extraction operation implementation"""
    
    def __init__(self, file_manager: PDFExtractionFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger(f"{__name__}.PDFTextExtraction")
    
    def execute(self, input_file: str, output_path: Optional[str] = None,
                options: Optional[Dict[str, Any]] = None, progress_tracker=None) -> ExtractionResult:
        """Execute PDF text extraction operation"""
        start_time = datetime.now()
        options = options or {}
        
        try:
            self.logger.info(f"Starting text extraction: {input_file}")
            
            # Validate input file
            validation = PDFExtractionValidator.validate_extraction_file(input_file, ExtractionType.TEXT)
            if not validation['valid_pdf']:
                error_msg = f"Invalid PDF file: {validation.get('error', 'Unknown error')}"
                return ExtractionResult(
                    success=False,
                    extraction_type=ExtractionType.TEXT,
                    input_file=input_file,
                    output_files=[],
                    error_message=error_msg
                )
            
            # Determine output path
            if not output_path:
                output_path = self.file_manager.generate_output_filename(
                    input_file, ExtractionType.TEXT
                )
            
            # Extract text based on preferred method
            extraction_method = options.get('method', 'pdfplumber')
            page_range = options.get('page_range')
            include_formatting = options.get('include_formatting', False)
            
            if extraction_method == 'pdfplumber' and PDFPLUMBER_AVAILABLE:
                extracted_text = self._extract_with_pdfplumber(
                    input_file, page_range, include_formatting, progress_tracker
                )
            elif extraction_method == 'pymupdf' and PYMUPDF_AVAILABLE:
                extracted_text = self._extract_with_pymupdf(
                    input_file, page_range, include_formatting, progress_tracker
                )
            else:
                # Fallback to available method
                if PDFPLUMBER_AVAILABLE:
                    extracted_text = self._extract_with_pdfplumber(
                        input_file, page_range, include_formatting, progress_tracker
                    )
                elif PYMUPDF_AVAILABLE:
                    extracted_text = self._extract_with_pymupdf(
                        input_file, page_range, include_formatting, progress_tracker
                    )
                else:
                    raise ImportError("No PDF text extraction library available")
            
            # Save extracted text
            if self.file_manager.save_extraction_data(extracted_text, output_path, "text"):
                processing_time = (datetime.now() - start_time).total_seconds()
                
                self.logger.info(f"Text extraction completed: {output_path} ({processing_time:.2f}s)")
                
                return ExtractionResult(
                    success=True,
                    extraction_type=ExtractionType.TEXT,
                    input_file=input_file,
                    output_files=[output_path],
                    extracted_data=extracted_text,
                    processing_time=processing_time,
                    details={
                        'method': extraction_method,
                        'character_count': len(extracted_text),
                        'word_count': len(extracted_text.split()),
                        'page_range': page_range,
                        'include_formatting': include_formatting
                    }
                )
            else:
                raise Exception("Failed to save extracted text")
                
        except Exception as e:
            error_msg = f"Text extraction failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return ExtractionResult(
                success=False,
                extraction_type=ExtractionType.TEXT,
                input_file=input_file,
                output_files=[],
                error_message=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _extract_with_pdfplumber(self, input_file: str, page_range: Optional[Tuple[int, int]], 
                                include_formatting: bool, progress_tracker) -> str:
        """Extract text using pdfplumber"""
        text_parts = []
        
        with pdfplumber.open(input_file) as pdf:
            total_pages = len(pdf.pages)
            
            # Determine pages to process
            if page_range:
                start_page, end_page = page_range
                pages_to_process = range(max(0, start_page), min(end_page + 1, total_pages))
            else:
                pages_to_process = range(total_pages)
            
            for i, page_num in enumerate(pages_to_process):
                if progress_tracker and progress_tracker.is_cancelled():
                    break
                
                if progress_tracker:
                    progress_tracker.update_progress(
                        i, f"Extracting text from page {page_num + 1}"
                    )
                
                page = pdf.pages[page_num]
                
                if include_formatting:
                    # Extract with layout information
                    page_text = self._extract_formatted_text(page)
                else:
                    # Simple text extraction
                    page_text = page.extract_text()
                
                if page_text:
                    text_parts.append(f"\n=== Page {page_num + 1} ===\n{page_text}\n")
        
        return '\n'.join(text_parts)
    
    def _extract_with_pymupdf(self, input_file: str, page_range: Optional[Tuple[int, int]], 
                             include_formatting: bool, progress_tracker) -> str:
        """Extract text using PyMuPDF"""
        text_parts = []
        
        doc = fitz.open(input_file)
        total_pages = len(doc)
        
        try:
            # Determine pages to process
            if page_range:
                start_page, end_page = page_range
                pages_to_process = range(max(0, start_page), min(end_page + 1, total_pages))
            else:
                pages_to_process = range(total_pages)
            
            for i, page_num in enumerate(pages_to_process):
                if progress_tracker and progress_tracker.is_cancelled():
                    break
                
                if progress_tracker:
                    progress_tracker.update_progress(
                        i, f"Extracting text from page {page_num + 1}"
                    )
                
                page = doc[page_num]
                
                if include_formatting:
                    # Extract with formatting information
                    blocks = page.get_text("dict")
                    page_text = self._format_pymupdf_blocks(blocks)
                else:
                    # Simple text extraction
                    page_text = page.get_text()
                
                if page_text:
                    text_parts.append(f"\n=== Page {page_num + 1} ===\n{page_text}\n")
                    
        finally:
            doc.close()
        
        return '\n'.join(text_parts)
    
    def _extract_formatted_text(self, page) -> str:
        """Extract text with formatting information using pdfplumber"""
        try:
            # Extract text with bounding boxes
            chars = page.chars
            if not chars:
                return page.extract_text() or ""
            
            # Group characters by lines and format
            lines = {}
            for char in chars:
                y = round(char['top'], 1)
                if y not in lines:
                    lines[y] = []
                lines[y].append(char)
            
            # Sort lines by y-coordinate and reconstruct text
            formatted_text = []
            for y in sorted(lines.keys()):
                line_chars = sorted(lines[y], key=lambda x: x['x0'])
                line_text = ''.join(char['text'] for char in line_chars)
                if line_text.strip():
                    formatted_text.append(line_text)
            
            return '\n'.join(formatted_text)
        except:
            # Fallback to simple extraction
            return page.extract_text() or ""
    
    def _format_pymupdf_blocks(self, blocks_dict: Dict) -> str:
        """Format PyMuPDF text blocks with structure"""
        try:
            formatted_lines = []
            
            for block in blocks_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        if line_text.strip():
                            formatted_lines.append(line_text)
            
            return '\n'.join(formatted_lines)
        except:
            # Fallback to dict representation
            return str(blocks_dict)


class PDFImageExtraction:
    """PDF image extraction operation implementation"""
    
    def __init__(self, file_manager: PDFExtractionFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger(f"{__name__}.PDFImageExtraction")
    
    def execute(self, input_file: str, output_dir: str = None, 
                options: Dict[str, Any] = None, progress_tracker=None) -> ExtractionResult:
        """Execute PDF image extraction operation"""
        start_time = datetime.now()
        options = options or {}
        
        try:
            self.logger.info(f"Starting image extraction: {input_file}")
            
            # Validate input file
            validation = PDFExtractionValidator.validate_extraction_file(input_file, ExtractionType.IMAGES)
            if not validation['valid_pdf']:
                error_msg = f"Invalid PDF file: {validation.get('error', 'Unknown error')}"
                return ExtractionResult(
                    success=False,
                    extraction_type=ExtractionType.IMAGES,
                    input_file=input_file,
                    output_files=[],
                    error_message=error_msg
                )
            
            # Determine output directory
            if not output_dir:
                output_dir = self.file_manager.create_extraction_directory(
                    input_file, ExtractionType.IMAGES
                )
            
            # Extract images
            min_width = options.get('min_width', 100)
            min_height = options.get('min_height', 100)
            image_format = options.get('format', 'png')
            page_range = options.get('page_range')
            
            if not PYMUPDF_AVAILABLE:
                raise ImportError("PyMuPDF is required for image extraction")
            
            extracted_images = self._extract_images_pymupdf(
                input_file, output_dir, min_width, min_height, 
                image_format, page_range, progress_tracker
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Image extraction completed: {len(extracted_images)} images ({processing_time:.2f}s)")
            
            return ExtractionResult(
                success=True,
                extraction_type=ExtractionType.IMAGES,
                input_file=input_file,
                output_files=extracted_images,
                processing_time=processing_time,
                details={
                    'images_extracted': len(extracted_images),
                    'output_directory': output_dir,
                    'min_size': f"{min_width}x{min_height}",
                    'format': image_format,
                    'page_range': page_range
                }
            )
            
        except Exception as e:
            error_msg = f"Image extraction failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return ExtractionResult(
                success=False,
                extraction_type=ExtractionType.IMAGES,
                input_file=input_file,
                output_files=[],
                error_message=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _extract_images_pymupdf(self, input_file: str, output_dir: str, 
                               min_width: int, min_height: int, image_format: str,
                               page_range: Optional[Tuple[int, int]], progress_tracker) -> List[str]:
        """Extract images using PyMuPDF"""
        extracted_images = []
        
        doc = fitz.open(input_file)
        total_pages = len(doc)
        
        try:
            # Determine pages to process
            if page_range:
                start_page, end_page = page_range
                pages_to_process = range(max(0, start_page), min(end_page + 1, total_pages))
            else:
                pages_to_process = range(total_pages)
            
            image_count = 0
            
            for i, page_num in enumerate(pages_to_process):
                if progress_tracker and progress_tracker.is_cancelled():
                    break
                
                if progress_tracker:
                    progress_tracker.update_progress(
                        i, f"Processing page {page_num + 1}"
                    )
                
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Load as PIL Image for processing
                        if PIL_AVAILABLE:
                            image = Image.open(io.BytesIO(image_bytes))
                            
                            # Check image dimensions
                            if image.width >= min_width and image.height >= min_height:
                                image_count += 1
                                output_file = os.path.join(
                                    output_dir, 
                                    f"image_page{page_num + 1}_{img_index + 1}.{image_format}"
                                )
                                
                                # Save image
                                image.save(output_file, format=image_format.upper())
                                extracted_images.append(output_file)
                                
                                self.logger.debug(f"Extracted image: {output_file}")
                            else:
                                self.logger.debug(f"Skipped small image: {image.width}x{image.height}")
                        else:
                            # Save without size filtering if PIL not available
                            image_count += 1
                            output_file = os.path.join(
                                output_dir, 
                                f"image_page{page_num + 1}_{img_index + 1}.{base_image.get('ext', 'png')}"
                            )
                            
                            with open(output_file, 'wb') as f:
                                f.write(image_bytes)
                            extracted_images.append(output_file)
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image {img_index + 1} from page {page_num + 1}: {e}")
                        continue
                        
        finally:
            doc.close()
        
        return extracted_images


class PDFMetadataExtraction:
    """PDF metadata extraction operation implementation"""
    
    def __init__(self, file_manager: PDFExtractionFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger(f"{__name__}.PDFMetadataExtraction")
    
    def execute(self, input_file: str, output_path: str = None, 
                options: Dict[str, Any] = None, progress_tracker=None) -> ExtractionResult:
        """Execute PDF metadata extraction operation"""
        start_time = datetime.now()
        options = options or {}
        
        try:
            self.logger.info(f"Starting metadata extraction: {input_file}")
            
            # Validate input file
            validation = PDFExtractionValidator.validate_extraction_file(input_file, ExtractionType.METADATA)
            if not validation['valid_pdf']:
                error_msg = f"Invalid PDF file: {validation.get('error', 'Unknown error')}"
                return ExtractionResult(
                    success=False,
                    extraction_type=ExtractionType.METADATA,
                    input_file=input_file,
                    output_files=[],
                    error_message=error_msg
                )
            
            # Determine output path
            if not output_path:
                output_path = self.file_manager.generate_output_filename(
                    input_file, ExtractionType.METADATA, extension=".json"
                )
            
            # Extract metadata
            include_extended = options.get('include_extended', True)
            
            metadata = self._extract_metadata(input_file, include_extended, progress_tracker)
            
            # Save metadata
            if self.file_manager.save_extraction_data(metadata, output_path, "json"):
                processing_time = (datetime.now() - start_time).total_seconds()
                
                self.logger.info(f"Metadata extraction completed: {output_path} ({processing_time:.2f}s)")
                
                return ExtractionResult(
                    success=True,
                    extraction_type=ExtractionType.METADATA,
                    input_file=input_file,
                    output_files=[output_path],
                    extracted_data=metadata,
                    processing_time=processing_time,
                    details={
                        'metadata_fields': len(metadata),
                        'include_extended': include_extended
                    }
                )
            else:
                raise Exception("Failed to save extracted metadata")
                
        except Exception as e:
            error_msg = f"Metadata extraction failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return ExtractionResult(
                success=False,
                extraction_type=ExtractionType.METADATA,
                input_file=input_file,
                output_files=[],
                error_message=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _extract_metadata(self, input_file: str, include_extended: bool, progress_tracker) -> Dict[str, Any]:
        """Extract PDF metadata"""
        metadata = {
            'extraction_info': {
                'extracted_at': datetime.now().isoformat(),
                'file_path': input_file,
                'file_size': os.path.getsize(input_file)
            }
        }
        
        if progress_tracker:
            progress_tracker.update_progress(0, "Opening PDF file")
        
        # Try pikepdf first for comprehensive metadata
        if PIKEPDF_AVAILABLE:
            try:
                with pikepdf.Pdf.open(input_file) as pdf:
                    if progress_tracker:
                        progress_tracker.update_progress(25, "Extracting document info")
                    
                    # Basic document info
                    if pdf.docinfo:
                        doc_info = {}
                        for key, value in pdf.docinfo.items():
                            key_str = str(key).lstrip('/')
                            
                            # Handle date strings
                            if 'Date' in key_str and isinstance(value, str) and value.startswith('D:'):
                                try:
                                    doc_info[key_str] = self._transform_pdf_date(value)
                                except:
                                    doc_info[key_str] = str(value)
                            else:
                                doc_info[key_str] = str(value)
                        
                        metadata['document_info'] = doc_info
                    
                    if progress_tracker:
                        progress_tracker.update_progress(50, "Extracting XMP metadata")
                    
                    # XMP metadata if available
                    if include_extended and hasattr(pdf, 'open_metadata'):
                        try:
                            xmp_meta = pdf.open_metadata()
                            if xmp_meta:
                                metadata['xmp_metadata'] = str(xmp_meta)
                        except:
                            pass
                    
                    if progress_tracker:
                        progress_tracker.update_progress(75, "Extracting page information")
                    
                    # Page information
                    metadata['page_info'] = {
                        'page_count': len(pdf.pages),
                        'pages': []
                    }
                    
                    for i, page in enumerate(pdf.pages[:10]):  # First 10 pages
                        try:
                            page_info = {
                                'page_number': i + 1,
                                'mediabox': [float(x) for x in page.mediabox],
                                'rotation': int(page.get('/Rotate', 0))
                            }
                            metadata['page_info']['pages'].append(page_info)
                        except:
                            pass
                            
            except Exception as e:
                self.logger.warning(f"pikepdf metadata extraction failed: {e}")
        
        # Fallback to PyMuPDF
        if PYMUPDF_AVAILABLE and 'document_info' not in metadata:
            try:
                doc = fitz.open(input_file)
                
                if progress_tracker:
                    progress_tracker.update_progress(50, "Extracting basic metadata")
                
                # Basic metadata
                doc_metadata = doc.metadata
                if doc_metadata:
                    metadata['document_info'] = doc_metadata
                
                # Page count and basic info
                metadata['page_info'] = {
                    'page_count': len(doc),
                    'pages': []
                }
                
                doc.close()
                
            except Exception as e:
                self.logger.warning(f"PyMuPDF metadata extraction failed: {e}")
        
        if progress_tracker:
            progress_tracker.update_progress(100, "Metadata extraction complete")
        
        return metadata
    
    def _transform_pdf_date(self, date_str: str) -> str:
        """Transform PDF date format to ISO format"""
        try:
            # Remove 'D:' prefix
            date_str = date_str.replace('D:', '')
            
            # Parse components
            if len(date_str) >= 14:
                year = int(date_str[0:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                hour = int(date_str[8:10])
                minute = int(date_str[10:12])
                second = int(date_str[12:14])
                
                dt = datetime(year, month, day, hour, minute, second)
                return dt.isoformat()
        except:
            pass
        
        return date_str


class PDFTableExtraction:
    """PDF table extraction operation implementation"""
    
    def __init__(self, file_manager: PDFExtractionFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger(f"{__name__}.PDFTableExtraction")
    
    def execute(self, input_file: str, output_dir: str = None, 
                options: Dict[str, Any] = None, progress_tracker=None) -> ExtractionResult:
        """Execute PDF table extraction operation"""
        start_time = datetime.now()
        options = options or {}
        
        try:
            self.logger.info(f"Starting table extraction: {input_file}")
            
            # Validate input file
            validation = PDFExtractionValidator.validate_extraction_file(input_file, ExtractionType.TABLES)
            if not validation['valid_pdf']:
                error_msg = f"Invalid PDF file: {validation.get('error', 'Unknown error')}"
                return ExtractionResult(
                    success=False,
                    extraction_type=ExtractionType.TABLES,
                    input_file=input_file,
                    output_files=[],
                    error_message=error_msg
                )
            
            # Determine output directory
            if not output_dir:
                output_dir = self.file_manager.create_extraction_directory(
                    input_file, ExtractionType.TABLES
                )
            
            # Extract tables
            extraction_method = options.get('method', 'camelot')
            page_range = options.get('page_range')
            camelot_options = options.get('camelot_options', {})
            
            if extraction_method == 'camelot' and CAMELOT_AVAILABLE:
                extracted_tables = self._extract_tables_camelot(
                    input_file, output_dir, page_range, camelot_options, progress_tracker
                )
            else:
                # Fallback to pdfplumber if available
                if PDFPLUMBER_AVAILABLE:
                    extracted_tables = self._extract_tables_pdfplumber(
                        input_file, output_dir, page_range, progress_tracker
                    )
                else:
                    raise ImportError("No table extraction library available")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"Table extraction completed: {len(extracted_tables)} tables ({processing_time:.2f}s)")
            
            return ExtractionResult(
                success=True,
                extraction_type=ExtractionType.TABLES,
                input_file=input_file,
                output_files=extracted_tables,
                processing_time=processing_time,
                details={
                    'tables_extracted': len(extracted_tables),
                    'output_directory': output_dir,
                    'method': extraction_method,
                    'page_range': page_range
                }
            )
            
        except Exception as e:
            error_msg = f"Table extraction failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return ExtractionResult(
                success=False,
                extraction_type=ExtractionType.TABLES,
                input_file=input_file,
                output_files=[],
                error_message=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _extract_tables_camelot(self, input_file: str, output_dir: str, 
                               page_range: Optional[Tuple[int, int]], 
                               camelot_options: Dict, progress_tracker) -> List[str]:
        """Extract tables using Camelot"""
        extracted_files = []
        
        # Prepare page specification for Camelot
        if page_range:
            start_page, end_page = page_range
            pages = f"{start_page + 1}-{end_page + 1}"  # Camelot uses 1-based indexing
        else:
            pages = 'all'
        
        if progress_tracker:
            progress_tracker.update_progress(0, "Initializing table extraction")
        
        # Default Camelot options
        default_options = {
            'flavor': 'lattice',
            'pages': pages
        }
        default_options.update(camelot_options)
        
        try:
            if progress_tracker:
                progress_tracker.update_progress(25, "Reading tables from PDF")
            
            # Extract tables using Camelot
            tables = camelot.read_pdf(input_file, **default_options)
            
            if not tables:
                self.logger.warning("No tables found in the document")
                return extracted_files
            
            if progress_tracker:
                progress_tracker.update_progress(50, f"Processing {len(tables)} tables")
            
            # Save each table
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            
            for i, table in enumerate(tables):
                if progress_tracker and progress_tracker.is_cancelled():
                    break
                
                output_file = os.path.join(output_dir, f"{base_name}_table_{i + 1}.csv")
                
                try:
                    table.to_csv(output_file)
                    extracted_files.append(output_file)
                    
                    self.logger.debug(f"Saved table {i + 1}: {output_file}")
                    
                    if progress_tracker:
                        progress = 50 + int((i + 1) / len(tables) * 50)
                        progress_tracker.update_progress(progress, f"Saved table {i + 1}")
                        
                except Exception as e:
                    self.logger.warning(f"Failed to save table {i + 1}: {e}")
                    continue
            
            return extracted_files
            
        except Exception as e:
            self.logger.error(f"Camelot table extraction failed: {e}")
            raise
    
    def _extract_tables_pdfplumber(self, input_file: str, output_dir: str, 
                                  page_range: Optional[Tuple[int, int]], progress_tracker) -> List[str]:
        """Extract tables using pdfplumber"""
        extracted_files = []
        
        with pdfplumber.open(input_file) as pdf:
            total_pages = len(pdf.pages)
            
            # Determine pages to process
            if page_range:
                start_page, end_page = page_range
                pages_to_process = range(max(0, start_page), min(end_page + 1, total_pages))
            else:
                pages_to_process = range(total_pages)
            
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            table_count = 0
            
            for i, page_num in enumerate(pages_to_process):
                if progress_tracker and progress_tracker.is_cancelled():
                    break
                
                if progress_tracker:
                    progress_tracker.update_progress(
                        int(i / len(pages_to_process) * 100),
                        f"Processing page {page_num + 1}"
                    )
                
                page = pdf.pages[page_num]
                
                try:
                    # Extract tables from page
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if table:  # Skip empty tables
                            table_count += 1
                            output_file = os.path.join(
                                output_dir, 
                                f"{base_name}_page{page_num + 1}_table{table_count}.csv"
                            )
                            
                            # Save table as CSV
                            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerows(table)
                            
                            extracted_files.append(output_file)
                            self.logger.debug(f"Saved table: {output_file}")
                            
                except Exception as e:
                    self.logger.warning(f"Failed to extract tables from page {page_num + 1}: {e}")
                    continue
        
        return extracted_files


class PDFLinkExtraction:
    """PDF link extraction operation implementation"""
    
    def __init__(self, file_manager: PDFExtractionFileManager):
        self.file_manager = file_manager
        self.logger = logging.getLogger(f"{__name__}.PDFLinkExtraction")
    
    def execute(self, input_file: str, output_path: str = None, 
                options: Dict[str, Any] = None, progress_tracker=None) -> ExtractionResult:
        """Execute PDF link extraction operation"""
        start_time = datetime.now()
        options = options or {}
        
        try:
            self.logger.info(f"Starting link extraction: {input_file}")
            
            # Validate input file
            validation = PDFExtractionValidator.validate_extraction_file(input_file, ExtractionType.LINKS)
            if not validation['valid_pdf']:
                error_msg = f"Invalid PDF file: {validation.get('error', 'Unknown error')}"
                return ExtractionResult(
                    success=False,
                    extraction_type=ExtractionType.LINKS,
                    input_file=input_file,
                    output_files=[],
                    error_message=error_msg
                )
            
            # Determine output path
            if not output_path:
                output_path = self.file_manager.generate_output_filename(
                    input_file, ExtractionType.LINKS, extension=".json"
                )
            
            # Extract links
            page_range = options.get('page_range')
            include_internal_links = options.get('include_internal_links', True)
            
            links = self._extract_links(input_file, page_range, include_internal_links, progress_tracker)
            
            # Save links
            if self.file_manager.save_extraction_data(links, output_path, "json"):
                processing_time = (datetime.now() - start_time).total_seconds()
                
                self.logger.info(f"Link extraction completed: {len(links['links'])} links ({processing_time:.2f}s)")
                
                return ExtractionResult(
                    success=True,
                    extraction_type=ExtractionType.LINKS,
                    input_file=input_file,
                    output_files=[output_path],
                    extracted_data=links,
                    processing_time=processing_time,
                    details={
                        'links_extracted': len(links['links']),
                        'external_links': len([l for l in links['links'] if l['type'] == 'external']),
                        'internal_links': len([l for l in links['links'] if l['type'] == 'internal']),
                        'page_range': page_range
                    }
                )
            else:
                raise Exception("Failed to save extracted links")
                
        except Exception as e:
            error_msg = f"Link extraction failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return ExtractionResult(
                success=False,
                extraction_type=ExtractionType.LINKS,
                input_file=input_file,
                output_files=[],
                error_message=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def _extract_links(self, input_file: str, page_range: Optional[Tuple[int, int]], 
                      include_internal_links: bool, progress_tracker) -> Dict[str, Any]:
        """Extract links from PDF"""
        links_data = {
            'extraction_info': {
                'extracted_at': datetime.now().isoformat(),
                'file_path': input_file,
                'include_internal_links': include_internal_links
            },
            'links': []
        }
        
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is required for link extraction")
        
        doc = fitz.open(input_file)
        total_pages = len(doc)
        
        try:
            # Determine pages to process
            if page_range:
                start_page, end_page = page_range
                pages_to_process = range(max(0, start_page), min(end_page + 1, total_pages))
            else:
                pages_to_process = range(total_pages)
            
            for i, page_num in enumerate(pages_to_process):
                if progress_tracker and progress_tracker.is_cancelled():
                    break
                
                if progress_tracker:
                    progress_tracker.update_progress(
                        int(i / len(pages_to_process) * 100),
                        f"Processing page {page_num + 1}"
                    )
                
                page = doc[page_num]
                
                # Get all links from the page
                page_links = page.get_links()
                
                for link in page_links:
                    link_info = {
                        'page': page_num + 1,
                        'type': 'unknown',
                        'destination': None,
                        'rect': [link['from'].x0, link['from'].y0, link['from'].x1, link['from'].y1]
                    }
                    
                    # Determine link type and destination
                    if link['kind'] == fitz.LINK_URI:
                        # External URL
                        link_info['type'] = 'external'
                        link_info['destination'] = link['uri']
                    elif link['kind'] == fitz.LINK_GOTO:
                        # Internal link to page
                        if include_internal_links:
                            link_info['type'] = 'internal'
                            link_info['destination'] = f"Page {link['page'] + 1}"
                    elif link['kind'] == fitz.LINK_GOTOR:
                        # Link to another document
                        link_info['type'] = 'external_document'
                        link_info['destination'] = link.get('file', 'Unknown document')
                    elif link['kind'] == fitz.LINK_NAMED:
                        # Named destination
                        if include_internal_links:
                            link_info['type'] = 'named'
                            link_info['destination'] = link.get('name', 'Unknown destination')
                    
                    # Only add if we have a destination
                    if link_info['destination']:
                        links_data['links'].append(link_info)
                        
        finally:
            doc.close()
        
        # Sort links by page and position
        links_data['links'].sort(key=lambda x: (x['page'], x['rect'][1]))
        
        return links_data


class PDFExtractionEngine:
    """Main PDF extraction engine"""
    
    def __init__(self):
        self.file_manager = PDFExtractionFileManager()
        self.text_extraction = PDFTextExtraction(self.file_manager)
        self.image_extraction = PDFImageExtraction(self.file_manager)
        self.metadata_extraction = PDFMetadataExtraction(self.file_manager)
        self.table_extraction = PDFTableExtraction(self.file_manager)
        self.link_extraction = PDFLinkExtraction(self.file_manager)
        self.logger = logging.getLogger(f"{__name__}.PDFExtractionEngine")
    
    def extract_text(self, input_file: str, output_path: str = None, 
                     options: Dict[str, Any] = None, 
                     progress_callback: Callable[[float, str], None] = None) -> ExtractionResult:
        """Execute PDF text extraction"""
        from pdf_operation_engine import ProgressTracker
        
        progress_tracker = ProgressTracker("PDF Text Extraction", 100)
        if progress_callback:
            progress_tracker.add_callback(progress_callback)
        
        try:
            return self.text_extraction.execute(input_file, output_path, options, progress_tracker)
        finally:
            self.file_manager.cleanup_temp_files()
    
    def extract_images(self, input_file: str, output_dir: str = None, 
                       options: Dict[str, Any] = None,
                       progress_callback: Callable[[float, str], None] = None) -> ExtractionResult:
        """Execute PDF image extraction"""
        from pdf_operation_engine import ProgressTracker
        
        progress_tracker = ProgressTracker("PDF Image Extraction", 100)
        if progress_callback:
            progress_tracker.add_callback(progress_callback)
        
        try:
            return self.image_extraction.execute(input_file, output_dir, options, progress_tracker)
        finally:
            self.file_manager.cleanup_temp_files()
    
    def extract_metadata(self, input_file: str, output_path: str = None, 
                         options: Dict[str, Any] = None,
                         progress_callback: Callable[[float, str], None] = None) -> ExtractionResult:
        """Execute PDF metadata extraction"""
        from pdf_operation_engine import ProgressTracker
        
        progress_tracker = ProgressTracker("PDF Metadata Extraction", 100)
        if progress_callback:
            progress_tracker.add_callback(progress_callback)
        
        try:
            return self.metadata_extraction.execute(input_file, output_path, options, progress_tracker)
        finally:
            self.file_manager.cleanup_temp_files()
    
    def extract_tables(self, input_file: str, output_dir: str = None, 
                       options: Dict[str, Any] = None,
                       progress_callback: Callable[[float, str], None] = None) -> ExtractionResult:
        """Execute PDF table extraction"""
        from pdf_operation_engine import ProgressTracker
        
        progress_tracker = ProgressTracker("PDF Table Extraction", 100)
        if progress_callback:
            progress_tracker.add_callback(progress_callback)
        
        try:
            return self.table_extraction.execute(input_file, output_dir, options, progress_tracker)
        finally:
            self.file_manager.cleanup_temp_files()
    
    def extract_links(self, input_file: str, output_path: str = None, 
                      options: Dict[str, Any] = None,
                      progress_callback: Callable[[float, str], None] = None) -> ExtractionResult:
        """Execute PDF link extraction"""
        from pdf_operation_engine import ProgressTracker
        
        progress_tracker = ProgressTracker("PDF Link Extraction", 100)
        if progress_callback:
            progress_callback.add_callback(progress_callback)
        
        try:
            return self.link_extraction.execute(input_file, output_path, options, progress_tracker)
        finally:
            self.file_manager.cleanup_temp_files()
    
    def cleanup(self):
        """Clean up resources"""
        self.file_manager.cleanup_temp_files()


if __name__ == "__main__":
    # Test the PDF extraction engine
    logging.basicConfig(level=logging.DEBUG)
    
    engine = PDFExtractionEngine()
    
    print("PDF Extraction Engine initialized successfully!")
    print(f"PyMuPDF available: {PYMUPDF_AVAILABLE}")
    print(f"pdfplumber available: {PDFPLUMBER_AVAILABLE}")
    print(f"pikepdf available: {PIKEPDF_AVAILABLE}")
    print(f"camelot available: {CAMELOT_AVAILABLE}")
    print(f"PIL available: {PIL_AVAILABLE}")
