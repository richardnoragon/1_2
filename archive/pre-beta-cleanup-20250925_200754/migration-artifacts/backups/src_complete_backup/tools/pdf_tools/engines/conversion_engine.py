"""
PDF Conversion Engine - Phase 2.5 Implementation
Provides PDF conversion capabilities supporting multiple file formats including
Word, Excel, PowerPoint, images, and other document types.
"""

import os
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple, Union
from datetime import datetime
from pathlib import Path

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import docx
    from docx.shared import Inches
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import openpyxl
    from openpyxl.drawing.image import Image as ExcelImage
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    from pptx import Presentation
    from pptx.util import Inches as PptInches
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False


class ConversionFormat(Enum):
    """Supported conversion formats"""
    # Document formats
    DOCX = "docx"
    DOC = "doc"
    RTF = "rtf"
    TXT = "txt"
    
    # Spreadsheet formats
    XLSX = "xlsx"
    XLS = "xls"
    CSV = "csv"
    
    # Presentation formats
    PPTX = "pptx"
    PPT = "ppt"
    
    # Image formats
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    TIFF = "tiff"
    BMP = "bmp"
    GIF = "gif"
    
    # Other formats
    HTML = "html"
    XML = "xml"
    JSON = "json"
    EPUB = "epub"


class ConversionOperation(Enum):
    """Types of conversion operations"""
    PDF_TO_DOCX = "pdf_to_docx"
    PDF_TO_XLSX = "pdf_to_xlsx"
    PDF_TO_PPTX = "pdf_to_pptx"
    PDF_TO_IMAGES = "pdf_to_images"
    PDF_TO_TEXT = "pdf_to_text"
    PDF_TO_HTML = "pdf_to_html"
    IMAGES_TO_PDF = "images_to_pdf"
    DOCX_TO_PDF = "docx_to_pdf"
    AUTO_DETECT = "auto_detect"


class ConversionQuality(Enum):
    """Conversion quality levels"""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PRINT = "print"


@dataclass
class ConversionResult:
    """Result of a conversion operation"""
    success: bool
    operation: ConversionOperation
    message: str
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    source_format: Optional[str] = None
    target_format: Optional[str] = None
    processing_time: float = 0.0
    page_count: int = 0
    file_size: int = 0
    quality_info: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ConversionSettings:
    """Conversion configuration"""
    quality: ConversionQuality = ConversionQuality.STANDARD
    preserve_formatting: bool = True
    preserve_images: bool = True
    preserve_tables: bool = True
    preserve_hyperlinks: bool = True
    extract_pages: Optional[List[int]] = None
    image_dpi: int = 150
    image_format: str = "PNG"
    text_encoding: str = "utf-8"
    include_metadata: bool = True
    custom_options: Dict[str, Any] = field(default_factory=dict)


class PDFConversionValidator:
    """Validates conversion operations and parameters"""
    
    @staticmethod
    def validate_input_file(file_path: str) -> Tuple[bool, str]:
        """Validate input file exists and is readable"""
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        if not os.path.isfile(file_path):
            return False, f"Not a file: {file_path}"
        
        return True, "Valid input file"
    
    @staticmethod
    def detect_format(file_path: str) -> Optional[ConversionFormat]:
        """Auto-detect file format from extension"""
        try:
            suffix = Path(file_path).suffix.lower().lstrip('.')
            for fmt in ConversionFormat:
                if fmt.value == suffix:
                    return fmt
            return None
        except Exception:
            return None
    
    @staticmethod
    def validate_conversion_settings(settings: ConversionSettings) -> Tuple[bool, str]:
        """Validate conversion settings"""
        if settings.image_dpi <= 0:
            return False, "Image DPI must be positive"
        
        if settings.extract_pages:
            if any(p <= 0 for p in settings.extract_pages):
                return False, "Page numbers must be positive"
        
        return True, "Valid conversion settings"


class PDFToDocumentConverter:
    """Converts PDF to document formats (DOCX, XLSX, PPTX)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def pdf_to_docx(self, input_path: str, output_path: str,
                   settings: ConversionSettings) -> ConversionResult:
        """Convert PDF to DOCX format"""
        try:
            if not HAS_DOCX or not HAS_PYMUPDF:
                return ConversionResult(
                    False, ConversionOperation.PDF_TO_DOCX,
                    "Required libraries not available (python-docx, PyMuPDF)"
                )
            
            start_time = datetime.now()
            
            # Open PDF
            doc = fitz.open(input_path)
            
            # Create DOCX document
            docx_doc = docx.Document()
            
            # Process pages
            pages_to_process = settings.extract_pages or list(range(doc.page_count))
            
            for page_num in pages_to_process:
                if page_num >= doc.page_count:
                    continue
                
                page = doc[page_num]
                
                # Extract text
                if settings.preserve_formatting:
                    text_blocks = page.get_text("dict")
                    self._process_text_blocks_to_docx(text_blocks, docx_doc, settings)
                else:
                    text = page.get_text()
                    docx_doc.add_paragraph(text)
                
                # Extract images
                if settings.preserve_images:
                    self._extract_images_to_docx(page, docx_doc, settings)
                
                # Add page break
                if page_num < len(pages_to_process) - 1:
                    docx_doc.add_page_break()
            
            # Save document
            docx_doc.save(output_path)
            doc.close()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ConversionResult(
                True, ConversionOperation.PDF_TO_DOCX,
                f"PDF converted to DOCX successfully",
                input_path=input_path,
                output_path=output_path,
                source_format="pdf",
                target_format="docx",
                processing_time=processing_time,
                page_count=len(pages_to_process),
                file_size=os.path.getsize(output_path)
            )
            
        except Exception as e:
            return ConversionResult(
                False, ConversionOperation.PDF_TO_DOCX,
                f"PDF to DOCX conversion failed: {str(e)}"
            )
    
    def _process_text_blocks_to_docx(self, text_dict: Dict, docx_doc, settings: ConversionSettings):
        """Process PDF text blocks and add to DOCX with formatting"""
        try:
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    paragraph = docx_doc.add_paragraph()
                    
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if text.strip():
                                run = paragraph.add_run(text)
                                
                                # Apply basic formatting
                                font = span.get("font", "")
                                if "bold" in font.lower():
                                    run.bold = True
                                if "italic" in font.lower():
                                    run.italic = True
                                
                                # Set font size
                                font_size = span.get("size", 12)
                                run.font.size = docx.shared.Pt(font_size)
                        
                        paragraph.add_run("\n")
                        
        except Exception as e:
            self.logger.warning(f"Text formatting failed: {e}")
    
    def _extract_images_to_docx(self, page, docx_doc, settings: ConversionSettings):
        """Extract images from PDF page and add to DOCX"""
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Save temporary image
                temp_path = f"temp_image_{img_index}.{image_ext}"
                with open(temp_path, "wb") as f:
                    f.write(image_bytes)
                
                # Add to document
                try:
                    docx_doc.add_picture(temp_path, width=Inches(4))
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
        except Exception as e:
            self.logger.warning(f"Image extraction failed: {e}")
    
    def pdf_to_xlsx(self, input_path: str, output_path: str,
                   settings: ConversionSettings) -> ConversionResult:
        """Convert PDF to XLSX format (table-focused)"""
        try:
            if not HAS_OPENPYXL or not HAS_PYMUPDF:
                return ConversionResult(
                    False, ConversionOperation.PDF_TO_XLSX,
                    "Required libraries not available (openpyxl, PyMuPDF)"
                )
            
            start_time = datetime.now()
            
            # Open PDF
            doc = fitz.open(input_path)
            
            # Create workbook
            workbook = openpyxl.Workbook()
            workbook.remove(workbook.active)  # Remove default sheet
            
            # Process pages
            pages_to_process = settings.extract_pages or list(range(doc.page_count))
            
            for page_num in pages_to_process:
                if page_num >= doc.page_count:
                    continue
                
                page = doc[page_num]
                sheet_name = f"Page_{page_num + 1}"
                worksheet = workbook.create_sheet(title=sheet_name)
                
                # Extract tables if available
                if settings.preserve_tables:
                    tables = page.find_tables()
                    if tables:
                        self._process_tables_to_xlsx(tables, worksheet)
                    else:
                        # Extract as text if no tables found
                        text = page.get_text()
                        lines = text.split('\n')
                        for row, line in enumerate(lines, 1):
                            if line.strip():
                                worksheet.cell(row=row, column=1, value=line.strip())
                else:
                    # Extract as text
                    text = page.get_text()
                    lines = text.split('\n')
                    for row, line in enumerate(lines, 1):
                        if line.strip():
                            worksheet.cell(row=row, column=1, value=line.strip())
            
            # Save workbook
            workbook.save(output_path)
            doc.close()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ConversionResult(
                True, ConversionOperation.PDF_TO_XLSX,
                f"PDF converted to XLSX successfully",
                input_path=input_path,
                output_path=output_path,
                source_format="pdf",
                target_format="xlsx",
                processing_time=processing_time,
                page_count=len(pages_to_process),
                file_size=os.path.getsize(output_path)
            )
            
        except Exception as e:
            return ConversionResult(
                False, ConversionOperation.PDF_TO_XLSX,
                f"PDF to XLSX conversion failed: {str(e)}"
            )
    
    def _process_tables_to_xlsx(self, tables: List, worksheet):
        """Process PDF tables and add to Excel worksheet"""
        try:
            current_row = 1
            
            for table in tables:
                # Extract table data
                table_data = table.extract()
                
                for row_data in table_data:
                    for col, cell_data in enumerate(row_data, 1):
                        if cell_data:
                            worksheet.cell(row=current_row, column=col, value=str(cell_data))
                    current_row += 1
                
                # Add spacing between tables
                current_row += 2
                
        except Exception as e:
            self.logger.warning(f"Table processing failed: {e}")


class PDFToImageConverter:
    """Converts PDF to image formats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def pdf_to_images(self, input_path: str, output_dir: str,
                     settings: ConversionSettings) -> ConversionResult:
        """Convert PDF pages to images"""
        try:
            if not HAS_PYMUPDF:
                return ConversionResult(
                    False, ConversionOperation.PDF_TO_IMAGES,
                    "PyMuPDF library not available"
                )
            
            start_time = datetime.now()
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Open PDF
            doc = fitz.open(input_path)
            
            # Process pages
            pages_to_process = settings.extract_pages or list(range(doc.page_count))
            image_files = []
            
            for page_num in pages_to_process:
                if page_num >= doc.page_count:
                    continue
                
                page = doc[page_num]
                
                # Create transformation matrix for DPI
                mat = fitz.Matrix(settings.image_dpi / 72, settings.image_dpi / 72)
                
                # Render page
                pix = page.get_pixmap(matrix=mat)
                
                # Save image
                image_filename = f"page_{page_num + 1:03d}.{settings.image_format.lower()}"
                image_path = os.path.join(output_dir, image_filename)
                
                if settings.image_format.upper() == "PNG":
                    pix.save(image_path)
                else:
                    # Convert to PIL for other formats
                    if HAS_PIL:
                        img_data = pix.tobytes("ppm")
                        pil_image = Image.open(io.BytesIO(img_data))
                        pil_image.save(image_path, format=settings.image_format.upper())
                    else:
                        pix.save(image_path.replace(f".{settings.image_format.lower()}", ".png"))
                
                image_files.append(image_path)
            
            doc.close()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ConversionResult(
                True, ConversionOperation.PDF_TO_IMAGES,
                f"PDF converted to {len(image_files)} images successfully",
                input_path=input_path,
                output_path=output_dir,
                source_format="pdf",
                target_format=settings.image_format.lower(),
                processing_time=processing_time,
                page_count=len(pages_to_process),
                file_size=sum(os.path.getsize(f) for f in image_files if os.path.exists(f))
            )
            
        except Exception as e:
            return ConversionResult(
                False, ConversionOperation.PDF_TO_IMAGES,
                f"PDF to images conversion failed: {str(e)}"
            )


class ImageToPDFConverter:
    """Converts images to PDF format"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def images_to_pdf(self, image_paths: List[str], output_path: str,
                     settings: ConversionSettings) -> ConversionResult:
        """Convert multiple images to a single PDF"""
        try:
            if not image_paths:
                return ConversionResult(
                    False, ConversionOperation.IMAGES_TO_PDF,
                    "No image files provided"
                )
            
            start_time = datetime.now()
            
            if HAS_PYMUPDF:
                return self._images_to_pdf_pymupdf(image_paths, output_path, settings, start_time)
            elif HAS_PIL:
                return self._images_to_pdf_pil(image_paths, output_path, settings, start_time)
            else:
                return ConversionResult(
                    False, ConversionOperation.IMAGES_TO_PDF,
                    "No suitable library available (PyMuPDF or PIL required)"
                )
                
        except Exception as e:
            return ConversionResult(
                False, ConversionOperation.IMAGES_TO_PDF,
                f"Images to PDF conversion failed: {str(e)}"
            )
    
    def _images_to_pdf_pymupdf(self, image_paths: List[str], output_path: str,
                              settings: ConversionSettings, start_time: datetime) -> ConversionResult:
        """Convert images to PDF using PyMuPDF"""
        try:
            doc = fitz.open()
            
            for image_path in image_paths:
                if not os.path.exists(image_path):
                    continue
                
                # Open image and get dimensions
                img = fitz.open(image_path)
                page = doc.new_page(width=img[0].rect.width, height=img[0].rect.height)
                
                # Insert image
                page.insert_image(page.rect, filename=image_path)
                img.close()
            
            # Save PDF
            doc.save(output_path)
            doc.close()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ConversionResult(
                True, ConversionOperation.IMAGES_TO_PDF,
                f"Converted {len(image_paths)} images to PDF successfully",
                output_path=output_path,
                source_format="images",
                target_format="pdf",
                processing_time=processing_time,
                page_count=len(image_paths),
                file_size=os.path.getsize(output_path)
            )
            
        except Exception as e:
            return ConversionResult(
                False, ConversionOperation.IMAGES_TO_PDF,
                f"PyMuPDF conversion failed: {str(e)}"
            )
    
    def _images_to_pdf_pil(self, image_paths: List[str], output_path: str,
                          settings: ConversionSettings, start_time: datetime) -> ConversionResult:
        """Convert images to PDF using PIL"""
        try:
            images = []
            
            for image_path in image_paths:
                if not os.path.exists(image_path):
                    continue
                
                img = Image.open(image_path)
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                images.append(img)
            
            if images:
                # Save as PDF
                images[0].save(output_path, save_all=True, append_images=images[1:])
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ConversionResult(
                True, ConversionOperation.IMAGES_TO_PDF,
                f"Converted {len(images)} images to PDF successfully",
                output_path=output_path,
                source_format="images",
                target_format="pdf",
                processing_time=processing_time,
                page_count=len(images),
                file_size=os.path.getsize(output_path)
            )
            
        except Exception as e:
            return ConversionResult(
                False, ConversionOperation.IMAGES_TO_PDF,
                f"PIL conversion failed: {str(e)}"
            )


class PDFConversionEngine:
    """Main PDF conversion operations engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.document_converter = PDFToDocumentConverter()
        self.image_converter = PDFToImageConverter()
        self.image_to_pdf_converter = ImageToPDFConverter()
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check available conversion libraries"""
        return {
            'pymupdf': HAS_PYMUPDF,
            'pil': HAS_PIL,
            'docx': HAS_DOCX,
            'openpyxl': HAS_OPENPYXL,
            'pptx': HAS_PPTX
        }
    
    def convert_pdf(self, input_path: str, output_path: str,
                   target_format: ConversionFormat,
                   settings: ConversionSettings = None) -> ConversionResult:
        """Convert PDF to specified format"""
        if settings is None:
            settings = ConversionSettings()
        
        # Validate inputs
        valid, msg = PDFConversionValidator.validate_input_file(input_path)
        if not valid:
            return ConversionResult(False, ConversionOperation.AUTO_DETECT, msg)
        
        valid, msg = PDFConversionValidator.validate_conversion_settings(settings)
        if not valid:
            return ConversionResult(False, ConversionOperation.AUTO_DETECT, msg)
        
        # Route to appropriate converter
        if target_format == ConversionFormat.DOCX:
            return self.document_converter.pdf_to_docx(input_path, output_path, settings)
        elif target_format == ConversionFormat.XLSX:
            return self.document_converter.pdf_to_xlsx(input_path, output_path, settings)
        elif target_format in [ConversionFormat.PNG, ConversionFormat.JPEG, ConversionFormat.JPG]:
            settings.image_format = target_format.value.upper()
            output_dir = os.path.splitext(output_path)[0] + "_images"
            return self.image_converter.pdf_to_images(input_path, output_dir, settings)
        else:
            return ConversionResult(
                False, ConversionOperation.AUTO_DETECT,
                f"Conversion to {target_format.value} not yet implemented"
            )
    
    def convert_images_to_pdf(self, image_paths: List[str], output_path: str,
                             settings: ConversionSettings = None) -> ConversionResult:
        """Convert multiple images to PDF"""
        if settings is None:
            settings = ConversionSettings()
        
        return self.image_to_pdf_converter.images_to_pdf(image_paths, output_path, settings)
    
    def auto_detect_and_convert(self, input_path: str, output_path: str,
                               settings: ConversionSettings = None) -> ConversionResult:
        """Auto-detect input format and convert appropriately"""
        try:
            input_format = PDFConversionValidator.detect_format(input_path)
            output_format = PDFConversionValidator.detect_format(output_path)
            
            if not output_format:
                return ConversionResult(
                    False, ConversionOperation.AUTO_DETECT,
                    "Cannot determine output format from file extension"
                )
            
            if input_format and input_format.value == "pdf":
                return self.convert_pdf(input_path, output_path, output_format, settings)
            elif output_format.value == "pdf":
                # Convert to PDF (support images for now)
                if input_format and input_format.value in ["png", "jpg", "jpeg", "tiff", "bmp"]:
                    return self.convert_images_to_pdf([input_path], output_path, settings)
                else:
                    return ConversionResult(
                        False, ConversionOperation.AUTO_DETECT,
                        f"Conversion from {input_format.value if input_format else 'unknown'} to PDF not yet supported"
                    )
            else:
                return ConversionResult(
                    False, ConversionOperation.AUTO_DETECT,
                    f"Conversion from {input_format.value if input_format else 'unknown'} "
                    f"to {output_format.value} not yet supported"
                )
                
        except Exception as e:
            return ConversionResult(
                False, ConversionOperation.AUTO_DETECT,
                f"Auto-detection failed: {str(e)}"
            )
    
    def batch_convert(self, file_pairs: List[Tuple[str, str]],
                     settings: ConversionSettings = None) -> List[ConversionResult]:
        """Convert multiple files in batch"""
        results = []
        
        for input_path, output_path in file_pairs:
            try:
                result = self.auto_detect_and_convert(input_path, output_path, settings)
                results.append(result)
            except Exception as e:
                results.append(ConversionResult(
                    False, ConversionOperation.AUTO_DETECT,
                    f"Batch conversion failed for {input_path}: {str(e)}"
                ))
        
        return results


# Convenience functions for external access
def create_conversion_engine() -> PDFConversionEngine:
    """Create a new PDF conversion engine instance"""
    return PDFConversionEngine()


def create_conversion_settings(quality: ConversionQuality = ConversionQuality.STANDARD,
                              **kwargs) -> ConversionSettings:
    """Create conversion settings with convenience parameters"""
    settings = ConversionSettings(quality=quality)
    
    # Apply optional parameters
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    return settings
