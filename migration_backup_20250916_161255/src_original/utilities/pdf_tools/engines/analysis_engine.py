"""
PDF Analysis Engine - Phase 2.6 Implementation
Provides document comparison, annotation tools, markup capabilities,
version tracking, and collaborative review features.
"""

import os
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import json
import hashlib

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import difflib
    HAS_DIFFLIB = True
except ImportError:
    HAS_DIFFLIB = False


class AnalysisOperation(Enum):
    """Types of analysis operations"""
    COMPARE_DOCUMENTS = "compare_documents"
    EXTRACT_ANNOTATIONS = "extract_annotations"
    ADD_ANNOTATIONS = "add_annotations"
    GENERATE_REPORT = "generate_report"
    VERSION_ANALYSIS = "version_analysis"
    CONTENT_ANALYSIS = "content_analysis"
    STRUCTURE_ANALYSIS = "structure_analysis"


class AnnotationType(Enum):
    """Types of annotations"""
    HIGHLIGHT = "highlight"
    NOTE = "note"
    STAMP = "stamp"
    UNDERLINE = "underline"
    STRIKEOUT = "strikeout"
    SQUIGGLY = "squiggly"
    FREETEXT = "freetext"
    CIRCLE = "circle"
    SQUARE = "square"
    LINE = "line"
    ARROW = "arrow"


class ComparisonMode(Enum):
    """Document comparison modes"""
    TEXT_ONLY = "text_only"
    VISUAL = "visual"
    STRUCTURAL = "structural"
    COMPREHENSIVE = "comprehensive"


@dataclass
class AnalysisResult:
    """Result of an analysis operation"""
    success: bool
    operation: AnalysisOperation
    message: str
    analysis_data: Dict[str, Any] = field(default_factory=dict)
    differences: List[Dict[str, Any]] = field(default_factory=list)
    annotations: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    output_path: Optional[str] = None
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ComparisonSettings:
    """Document comparison configuration"""
    mode: ComparisonMode = ComparisonMode.COMPREHENSIVE
    ignore_formatting: bool = False
    ignore_whitespace: bool = True
    ignore_case: bool = False
    page_range: Optional[Tuple[int, int]] = None
    highlight_differences: bool = True
    generate_report: bool = True
    include_statistics: bool = True
    tolerance_pixels: int = 5  # For visual comparison
    minimum_change_size: int = 10  # Minimum characters for text changes


@dataclass
class AnnotationData:
    """Annotation information"""
    annotation_id: str
    type: AnnotationType
    page_number: int
    coordinates: Tuple[float, float, float, float]  # x0, y0, x1, y1
    content: str = ""
    author: str = ""
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    color: Tuple[float, float, float] = (1.0, 1.0, 0.0)  # RGB
    opacity: float = 0.5
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VersionInfo:
    """Document version information"""
    version_id: str
    document_path: str
    creation_date: datetime
    author: str = ""
    description: str = ""
    file_hash: str = ""
    file_size: int = 0
    page_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class PDFComparisonEngine:
    """Handles PDF document comparison operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compare_documents(self, doc1_path: str, doc2_path: str,
                         settings: ComparisonSettings) -> AnalysisResult:
        """Compare two PDF documents"""
        try:
            start_time = datetime.now()
            
            # Validate inputs
            if not os.path.exists(doc1_path):
                return AnalysisResult(
                    False, AnalysisOperation.COMPARE_DOCUMENTS,
                    f"First document not found: {doc1_path}"
                )
            
            if not os.path.exists(doc2_path):
                return AnalysisResult(
                    False, AnalysisOperation.COMPARE_DOCUMENTS,
                    f"Second document not found: {doc2_path}"
                )
            
            if not HAS_PYMUPDF:
                return AnalysisResult(
                    False, AnalysisOperation.COMPARE_DOCUMENTS,
                    "PyMuPDF library required for document comparison"
                )
            
            # Perform comparison based on mode
            if settings.mode == ComparisonMode.TEXT_ONLY:
                result = self._compare_text_content(doc1_path, doc2_path, settings)
            elif settings.mode == ComparisonMode.VISUAL:
                result = self._compare_visual_content(doc1_path, doc2_path, settings)
            elif settings.mode == ComparisonMode.STRUCTURAL:
                result = self._compare_document_structure(doc1_path, doc2_path, settings)
            else:  # COMPREHENSIVE
                result = self._compare_comprehensive(doc1_path, doc2_path, settings)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"Document comparison failed: {e}")
            return AnalysisResult(
                False, AnalysisOperation.COMPARE_DOCUMENTS,
                f"Comparison failed: {str(e)}"
            )
    
    def _compare_text_content(self, doc1_path: str, doc2_path: str,
                             settings: ComparisonSettings) -> AnalysisResult:
        """Compare text content of documents"""
        try:
            doc1 = fitz.open(doc1_path)
            doc2 = fitz.open(doc2_path)
            
            differences = []
            statistics = {
                'total_pages_doc1': doc1.page_count,
                'total_pages_doc2': doc2.page_count,
                'pages_compared': 0,
                'differences_found': 0,
                'text_similarity': 0.0
            }
            
            # Determine page range
            max_pages = max(doc1.page_count, doc2.page_count)
            start_page, end_page = settings.page_range or (0, max_pages - 1)
            
            all_text1 = []
            all_text2 = []
            
            for page_num in range(start_page, min(end_page + 1, max_pages)):
                text1 = ""
                text2 = ""
                
                if page_num < doc1.page_count:
                    page1 = doc1[page_num]
                    text1 = page1.get_text()
                
                if page_num < doc2.page_count:
                    page2 = doc2[page_num]
                    text2 = page2.get_text()
                
                # Apply text processing options
                if settings.ignore_case:
                    text1 = text1.lower()
                    text2 = text2.lower()
                
                if settings.ignore_whitespace:
                    text1 = ' '.join(text1.split())
                    text2 = ' '.join(text2.split())
                
                all_text1.append(text1)
                all_text2.append(text2)
                
                # Compare page texts
                if text1 != text2:
                    page_differences = self._find_text_differences(
                        text1, text2, page_num, settings
                    )
                    differences.extend(page_differences)
                    statistics['differences_found'] += len(page_differences)
                
                statistics['pages_compared'] += 1
            
            # Calculate overall similarity
            if HAS_DIFFLIB:
                combined_text1 = '\n'.join(all_text1)
                combined_text2 = '\n'.join(all_text2)
                similarity = difflib.SequenceMatcher(None, combined_text1, combined_text2).ratio()
                statistics['text_similarity'] = similarity * 100
            
            doc1.close()
            doc2.close()
            
            return AnalysisResult(
                True, AnalysisOperation.COMPARE_DOCUMENTS,
                f"Text comparison completed - found {len(differences)} differences",
                analysis_data={'comparison_mode': 'text_only'},
                differences=differences,
                statistics=statistics
            )
            
        except Exception as e:
            return AnalysisResult(
                False, AnalysisOperation.COMPARE_DOCUMENTS,
                f"Text comparison failed: {str(e)}"
            )
    
    def _find_text_differences(self, text1: str, text2: str, page_num: int,
                              settings: ComparisonSettings) -> List[Dict[str, Any]]:
        """Find differences between two text blocks"""
        differences = []
        
        if not HAS_DIFFLIB:
            return differences
        
        try:
            # Create differ
            differ = difflib.unified_diff(
                text1.splitlines(keepends=True),
                text2.splitlines(keepends=True),
                lineterm=''
            )
            
            line_num = 0
            for line in differ:
                if line.startswith('@@'):
                    # Extract line numbers from diff header
                    continue
                elif line.startswith('-'):
                    # Text removed
                    content = line[1:]
                    if len(content.strip()) >= settings.minimum_change_size:
                        differences.append({
                            'type': 'deletion',
                            'page': page_num + 1,
                            'line': line_num,
                            'content': content.strip(),
                            'position': 'doc1'
                        })
                elif line.startswith('+'):
                    # Text added
                    content = line[1:]
                    if len(content.strip()) >= settings.minimum_change_size:
                        differences.append({
                            'type': 'addition',
                            'page': page_num + 1,
                            'line': line_num,
                            'content': content.strip(),
                            'position': 'doc2'
                        })
                
                line_num += 1
                
        except Exception as e:
            self.logger.warning(f"Text difference analysis failed: {e}")
        
        return differences
    
    def _compare_visual_content(self, doc1_path: str, doc2_path: str,
                               settings: ComparisonSettings) -> AnalysisResult:
        """Compare visual appearance of documents"""
        try:
            doc1 = fitz.open(doc1_path)
            doc2 = fitz.open(doc2_path)
            
            differences = []
            statistics = {
                'total_pages_doc1': doc1.page_count,
                'total_pages_doc2': doc2.page_count,
                'pages_compared': 0,
                'visual_differences': 0
            }
            
            # Compare page by page visually
            max_pages = max(doc1.page_count, doc2.page_count)
            start_page, end_page = settings.page_range or (0, max_pages - 1)
            
            for page_num in range(start_page, min(end_page + 1, max_pages)):
                if page_num < doc1.page_count and page_num < doc2.page_count:
                    page1 = doc1[page_num]
                    page2 = doc2[page_num]
                    
                    # Render pages as images
                    pix1 = page1.get_pixmap()
                    pix2 = page2.get_pixmap()
                    
                    # Compare image data (basic implementation)
                    if pix1.samples != pix2.samples:
                        differences.append({
                            'type': 'visual_difference',
                            'page': page_num + 1,
                            'description': 'Visual content differs',
                            'confidence': 'medium'
                        })
                        statistics['visual_differences'] += 1
                
                elif page_num < doc1.page_count:
                    differences.append({
                        'type': 'page_missing',
                        'page': page_num + 1,
                        'description': 'Page exists only in document 1',
                        'document': 'doc1'
                    })
                elif page_num < doc2.page_count:
                    differences.append({
                        'type': 'page_missing',
                        'page': page_num + 1,
                        'description': 'Page exists only in document 2',
                        'document': 'doc2'
                    })
                
                statistics['pages_compared'] += 1
            
            doc1.close()
            doc2.close()
            
            return AnalysisResult(
                True, AnalysisOperation.COMPARE_DOCUMENTS,
                f"Visual comparison completed - found {len(differences)} differences",
                analysis_data={'comparison_mode': 'visual'},
                differences=differences,
                statistics=statistics
            )
            
        except Exception as e:
            return AnalysisResult(
                False, AnalysisOperation.COMPARE_DOCUMENTS,
                f"Visual comparison failed: {str(e)}"
            )
    
    def _compare_document_structure(self, doc1_path: str, doc2_path: str,
                                   settings: ComparisonSettings) -> AnalysisResult:
        """Compare document structure (metadata, bookmarks, etc.)"""
        try:
            doc1 = fitz.open(doc1_path)
            doc2 = fitz.open(doc2_path)
            
            differences = []
            
            # Compare basic document properties
            if doc1.page_count != doc2.page_count:
                differences.append({
                    'type': 'page_count_difference',
                    'doc1_pages': doc1.page_count,
                    'doc2_pages': doc2.page_count,
                    'description': f'Page count differs: {doc1.page_count} vs {doc2.page_count}'
                })
            
            # Compare metadata
            meta1 = doc1.metadata
            meta2 = doc2.metadata
            
            for key in set(meta1.keys()) | set(meta2.keys()):
                val1 = meta1.get(key, '')
                val2 = meta2.get(key, '')
                
                if val1 != val2:
                    differences.append({
                        'type': 'metadata_difference',
                        'field': key,
                        'doc1_value': val1,
                        'doc2_value': val2,
                        'description': f'Metadata field "{key}" differs'
                    })
            
            # Compare bookmarks/outline
            outline1 = doc1.get_toc()
            outline2 = doc2.get_toc()
            
            if outline1 != outline2:
                differences.append({
                    'type': 'outline_difference',
                    'description': 'Document outlines/bookmarks differ',
                    'doc1_outline_items': len(outline1),
                    'doc2_outline_items': len(outline2)
                })
            
            statistics = {
                'structural_differences': len(differences),
                'metadata_fields_doc1': len(meta1),
                'metadata_fields_doc2': len(meta2),
                'outline_items_doc1': len(outline1),
                'outline_items_doc2': len(outline2)
            }
            
            doc1.close()
            doc2.close()
            
            return AnalysisResult(
                True, AnalysisOperation.COMPARE_DOCUMENTS,
                f"Structural comparison completed - found {len(differences)} differences",
                analysis_data={'comparison_mode': 'structural'},
                differences=differences,
                statistics=statistics
            )
            
        except Exception as e:
            return AnalysisResult(
                False, AnalysisOperation.COMPARE_DOCUMENTS,
                f"Structural comparison failed: {str(e)}"
            )
    
    def _compare_comprehensive(self, doc1_path: str, doc2_path: str,
                              settings: ComparisonSettings) -> AnalysisResult:
        """Perform comprehensive comparison combining all methods"""
        try:
            # Perform all comparison types
            text_result = self._compare_text_content(doc1_path, doc2_path, settings)
            visual_result = self._compare_visual_content(doc1_path, doc2_path, settings)
            struct_result = self._compare_document_structure(doc1_path, doc2_path, settings)
            
            # Combine results
            all_differences = []
            all_differences.extend(text_result.differences)
            all_differences.extend(visual_result.differences)
            all_differences.extend(struct_result.differences)
            
            combined_statistics = {}
            combined_statistics.update(text_result.statistics)
            combined_statistics.update(visual_result.statistics)
            combined_statistics.update(struct_result.statistics)
            combined_statistics['total_differences'] = len(all_differences)
            
            return AnalysisResult(
                True, AnalysisOperation.COMPARE_DOCUMENTS,
                f"Comprehensive comparison completed - found {len(all_differences)} total differences",
                analysis_data={'comparison_mode': 'comprehensive'},
                differences=all_differences,
                statistics=combined_statistics
            )
            
        except Exception as e:
            return AnalysisResult(
                False, AnalysisOperation.COMPARE_DOCUMENTS,
                f"Comprehensive comparison failed: {str(e)}"
            )


class PDFAnnotationManager:
    """Handles PDF annotation operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_annotations(self, file_path: str) -> AnalysisResult:
        """Extract all annotations from PDF"""
        try:
            if not HAS_PYMUPDF:
                return AnalysisResult(
                    False, AnalysisOperation.EXTRACT_ANNOTATIONS,
                    "PyMuPDF library required for annotation extraction"
                )
            
            doc = fitz.open(file_path)
            annotations = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                for annot in page.annots():
                    annotation_data = {
                        'id': f"page_{page_num}_{annot.xref}",
                        'page': page_num + 1,
                        'type': annot.type[1],  # Get annotation type name
                        'content': annot.info.get('content', ''),
                        'author': annot.info.get('title', ''),
                        'coordinates': list(annot.rect),
                        'creation_date': annot.info.get('creationDate', ''),
                        'modification_date': annot.info.get('modDate', ''),
                        'opacity': getattr(annot, 'opacity', 1.0),
                        'color': getattr(annot, 'colors', {}).get('stroke', [1.0, 1.0, 0.0])
                    }
                    annotations.append(annotation_data)
            
            doc.close()
            
            statistics = {
                'total_annotations': len(annotations),
                'annotations_by_type': {},
                'annotations_by_page': {}
            }
            
            # Calculate statistics
            for annot in annotations:
                annot_type = annot['type']
                page_num = annot['page']
                
                statistics['annotations_by_type'][annot_type] = \
                    statistics['annotations_by_type'].get(annot_type, 0) + 1
                statistics['annotations_by_page'][f'page_{page_num}'] = \
                    statistics['annotations_by_page'].get(f'page_{page_num}', 0) + 1
            
            return AnalysisResult(
                True, AnalysisOperation.EXTRACT_ANNOTATIONS,
                f"Extracted {len(annotations)} annotations successfully",
                annotations=annotations,
                statistics=statistics
            )
            
        except Exception as e:
            return AnalysisResult(
                False, AnalysisOperation.EXTRACT_ANNOTATIONS,
                f"Annotation extraction failed: {str(e)}"
            )
    
    def add_annotation(self, file_path: str, output_path: str,
                      annotation: AnnotationData) -> AnalysisResult:
        """Add annotation to PDF"""
        try:
            if not HAS_PYMUPDF:
                return AnalysisResult(
                    False, AnalysisOperation.ADD_ANNOTATIONS,
                    "PyMuPDF library required for adding annotations"
                )
            
            doc = fitz.open(file_path)
            
            if annotation.page_number >= doc.page_count:
                return AnalysisResult(
                    False, AnalysisOperation.ADD_ANNOTATIONS,
                    f"Page {annotation.page_number} does not exist"
                )
            
            page = doc[annotation.page_number]
            
            # Create annotation based on type
            rect = fitz.Rect(*annotation.coordinates)
            
            if annotation.type == AnnotationType.HIGHLIGHT:
                annot = page.add_highlight_annot(rect)
            elif annotation.type == AnnotationType.NOTE:
                annot = page.add_text_annot(rect.tl, annotation.content)
            elif annotation.type == AnnotationType.FREETEXT:
                annot = page.add_freetext_annot(rect, annotation.content)
            elif annotation.type == AnnotationType.SQUARE:
                annot = page.add_rect_annot(rect)
            elif annotation.type == AnnotationType.CIRCLE:
                annot = page.add_circle_annot(rect)
            else:
                # Default to highlight
                annot = page.add_highlight_annot(rect)
            
            # Set annotation properties
            if annotation.content:
                annot.set_info(content=annotation.content)
            if annotation.author:
                annot.set_info(title=annotation.author)
            
            annot.set_colors(stroke=annotation.color)
            annot.set_opacity(annotation.opacity)
            annot.update()
            
            # Save document
            doc.save(output_path)
            doc.close()
            
            return AnalysisResult(
                True, AnalysisOperation.ADD_ANNOTATIONS,
                f"Annotation added successfully to {output_path}",
                output_path=output_path
            )
            
        except Exception as e:
            return AnalysisResult(
                False, AnalysisOperation.ADD_ANNOTATIONS,
                f"Adding annotation failed: {str(e)}"
            )


class PDFVersionTracker:
    """Handles PDF version tracking and analysis"""
    
    def __init__(self, storage_dir: str = "version_storage"):
        self.logger = logging.getLogger(__name__)
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def create_version(self, document_path: str, author: str = "",
                      description: str = "") -> VersionInfo:
        """Create a new version entry for a document"""
        try:
            # Calculate file hash
            file_hash = self._calculate_file_hash(document_path)
            
            # Get file info
            file_size = os.path.getsize(document_path)
            
            # Get page count if PDF
            page_count = 0
            if document_path.lower().endswith('.pdf') and HAS_PYMUPDF:
                try:
                    doc = fitz.open(document_path)
                    page_count = doc.page_count
                    doc.close()
                except:
                    pass
            
            # Create version info
            version_info = VersionInfo(
                version_id=file_hash[:16],  # Use first 16 chars of hash as ID
                document_path=document_path,
                creation_date=datetime.now(),
                author=author,
                description=description,
                file_hash=file_hash,
                file_size=file_size,
                page_count=page_count
            )
            
            # Store version info
            self._store_version_info(version_info)
            
            return version_info
            
        except Exception as e:
            self.logger.error(f"Version creation failed: {e}")
            raise
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _store_version_info(self, version_info: VersionInfo):
        """Store version information to disk"""
        try:
            version_file = os.path.join(self.storage_dir, f"{version_info.version_id}.json")
            
            # Convert to dict for JSON serialization
            version_dict = {
                'version_id': version_info.version_id,
                'document_path': version_info.document_path,
                'creation_date': version_info.creation_date.isoformat(),
                'author': version_info.author,
                'description': version_info.description,
                'file_hash': version_info.file_hash,
                'file_size': version_info.file_size,
                'page_count': version_info.page_count,
                'metadata': version_info.metadata
            }
            
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_dict, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Version storage failed: {e}")
            raise


class PDFAnalysisEngine:
    """Main PDF analysis and collaboration engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.comparison_engine = PDFComparisonEngine()
        self.annotation_manager = PDFAnnotationManager()
        self.version_tracker = PDFVersionTracker()
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check available analysis libraries"""
        return {
            'pymupdf': HAS_PYMUPDF,
            'difflib': HAS_DIFFLIB
        }
    
    def compare_documents(self, doc1_path: str, doc2_path: str,
                         settings: ComparisonSettings = None) -> AnalysisResult:
        """Compare two PDF documents"""
        if settings is None:
            settings = ComparisonSettings()
        
        return self.comparison_engine.compare_documents(doc1_path, doc2_path, settings)
    
    def extract_annotations(self, file_path: str) -> AnalysisResult:
        """Extract annotations from PDF"""
        return self.annotation_manager.extract_annotations(file_path)
    
    def add_annotation(self, file_path: str, output_path: str,
                      annotation: AnnotationData) -> AnalysisResult:
        """Add annotation to PDF"""
        return self.annotation_manager.add_annotation(file_path, output_path, annotation)
    
    def analyze_document_content(self, file_path: str) -> AnalysisResult:
        """Analyze document content and structure"""
        try:
            if not HAS_PYMUPDF:
                return AnalysisResult(
                    False, AnalysisOperation.CONTENT_ANALYSIS,
                    "PyMuPDF library required for content analysis"
                )
            
            start_time = datetime.now()
            doc = fitz.open(file_path)
            
            analysis_data = {
                'basic_info': {
                    'page_count': doc.page_count,
                    'file_size': os.path.getsize(file_path),
                    'is_encrypted': doc.needs_pass,
                    'is_form_pdf': doc.is_form_pdf,
                    'metadata': doc.metadata
                },
                'content_analysis': {
                    'total_characters': 0,
                    'total_words': 0,
                    'total_paragraphs': 0,
                    'total_images': 0,
                    'total_links': 0,
                    'languages_detected': [],
                    'text_density_by_page': []
                },
                'structure_analysis': {
                    'has_bookmarks': len(doc.get_toc()) > 0,
                    'bookmark_count': len(doc.get_toc()),
                    'has_annotations': False,
                    'annotation_count': 0,
                    'page_sizes': []
                }
            }
            
            # Analyze each page
            total_annotations = 0
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Text analysis
                text = page.get_text()
                analysis_data['content_analysis']['total_characters'] += len(text)
                analysis_data['content_analysis']['total_words'] += len(text.split())
                analysis_data['content_analysis']['total_paragraphs'] += len([p for p in text.split('\n\n') if p.strip()])
                analysis_data['content_analysis']['text_density_by_page'].append(len(text))
                
                # Image analysis
                images = page.get_images()
                analysis_data['content_analysis']['total_images'] += len(images)
                
                # Link analysis
                links = page.get_links()
                analysis_data['content_analysis']['total_links'] += len(links)
                
                # Annotation analysis
                annots = list(page.annots())
                total_annotations += len(annots)
                
                # Page size analysis
                analysis_data['structure_analysis']['page_sizes'].append({
                    'page': page_num + 1,
                    'width': page.rect.width,
                    'height': page.rect.height
                })
            
            analysis_data['structure_analysis']['has_annotations'] = total_annotations > 0
            analysis_data['structure_analysis']['annotation_count'] = total_annotations
            
            doc.close()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResult(
                True, AnalysisOperation.CONTENT_ANALYSIS,
                "Document analysis completed successfully",
                analysis_data=analysis_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            return AnalysisResult(
                False, AnalysisOperation.CONTENT_ANALYSIS,
                f"Content analysis failed: {str(e)}"
            )
    
    def generate_analysis_report(self, analysis_results: List[AnalysisResult],
                                output_path: str) -> AnalysisResult:
        """Generate comprehensive analysis report"""
        try:
            report_data = {
                'report_metadata': {
                    'generation_date': datetime.now().isoformat(),
                    'total_analyses': len(analysis_results),
                    'report_version': '1.0'
                },
                'analyses': []
            }
            
            for result in analysis_results:
                analysis_summary = {
                    'operation': result.operation.value,
                    'success': result.success,
                    'message': result.message,
                    'processing_time': result.processing_time,
                    'statistics': result.statistics,
                    'differences_count': len(result.differences),
                    'annotations_count': len(result.annotations)
                }
                report_data['analyses'].append(analysis_summary)
            
            # Save report as JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            return AnalysisResult(
                True, AnalysisOperation.GENERATE_REPORT,
                f"Analysis report generated successfully",
                output_path=output_path,
                analysis_data=report_data
            )
            
        except Exception as e:
            return AnalysisResult(
                False, AnalysisOperation.GENERATE_REPORT,
                f"Report generation failed: {str(e)}"
            )


# Convenience functions for external access
def create_analysis_engine() -> PDFAnalysisEngine:
    """Create a new PDF analysis engine instance"""
    return PDFAnalysisEngine()


def create_comparison_settings(mode: ComparisonMode = ComparisonMode.COMPREHENSIVE,
                              **kwargs) -> ComparisonSettings:
    """Create comparison settings with convenience parameters"""
    settings = ComparisonSettings(mode=mode)
    
    # Apply optional parameters
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    return settings


def create_annotation(annotation_type: AnnotationType, page_number: int,
                     coordinates: Tuple[float, float, float, float],
                     content: str = "", **kwargs) -> AnnotationData:
    """Create annotation data with convenience parameters"""
    annotation = AnnotationData(
        annotation_id=f"annot_{datetime.now().timestamp()}",
        type=annotation_type,
        page_number=page_number,
        coordinates=coordinates,
        content=content
    )
    
    # Apply optional parameters
    for key, value in kwargs.items():
        if hasattr(annotation, key):
            setattr(annotation, key, value)
    
    return annotation
