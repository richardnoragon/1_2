# PDF Tools User Guide
**Richard's File Utilities Hub - PDF Tools Integration**  
**Version:** 1.0  
**Last Updated:** 2025-07-25

## Overview

The PDF Tools section provides comprehensive PDF processing capabilities integrated into Richard's File Utilities Hub. This guide covers all available PDF utilities and how to use them effectively.

## Getting Started

### Accessing PDF Tools

1. **Launch RFU Hub:** Start the main Richard's File Utilities application
2. **Navigate to PDF Tools:** Click the "PDF Tools" button in the main interface
3. **Select Operation:** Choose from 23 available PDF utilities

### PDF Tools Interface

The PDF Tools hub provides organized access to all PDF utilities:

- **Basic Operations:** Split, Merge, Compress, View
- **Content Extraction:** Text, Images, Tables, Links, Metadata
- **Enhancement:** OCR, Watermark, Highlight
- **Conversion:** DOCX, Image, HTML to PDF
- **Security:** Encrypt, Digital Signing
- **Administration:** Page Management, Settings, Logs

## Available PDF Utilities

### 📄 Basic Operations

#### PDF Splitting (`split.py`)
**Purpose:** Split large PDF files into smaller documents
**Features:**
- Split by page ranges
- Split by page count
- Extract specific pages
- Batch processing support

**Usage:**
1. Select input PDF file
2. Choose split method (pages, ranges, or count)
3. Specify output directory
4. Click "Split PDF"

#### PDF Merging (`merg.py`)
**Purpose:** Combine multiple PDF files into one document
**Features:**
- Drag-and-drop file ordering
- Page range selection from each file
- Bookmark preservation
- Metadata merging

**Usage:**
1. Add PDF files to merge list
2. Arrange files in desired order
3. Select page ranges (optional)
4. Click "Merge PDFs"

#### PDF Viewing (`view.py`)
**Purpose:** View and navigate PDF documents
**Features:**
- Multi-page viewing
- Zoom controls
- Page navigation
- Search functionality

#### Page Administration (`page_administration.py`)
**Purpose:** Advanced page management operations
**Features:**
- Page rotation
- Page deletion
- Page reordering
- Page extraction

### 📝 Content Extraction

#### Text Extraction (`extract_text.py`)
**Purpose:** Extract text content from PDF files
**Features:**
- Full document text extraction
- Page-specific extraction
- Multiple output formats (TXT, JSON)
- Encoding options

**Usage:**
1. Select PDF file
2. Choose extraction scope (all pages or specific range)
3. Select output format
4. Click "Extract Text"

#### Image Extraction (`extract_image_cli.py`)
**Purpose:** Extract images from PDF documents
**Features:**
- All image formats supported
- Quality preservation
- Batch extraction
- Organized output folders

#### Table Extraction (`extract_tables_camelot.py`)
**Purpose:** Extract tables from PDF documents
**Features:**
- Automatic table detection
- CSV/Excel output formats
- Table structure preservation
- Multiple extraction methods

#### Link Extraction (`extract_links.py`)
**Purpose:** Extract hyperlinks from PDF documents
**Features:**
- Internal and external links
- Link validation
- Organized output formats
- Metadata inclusion

#### Metadata Extraction (`extract_metadata.py`)
**Purpose:** Extract document metadata and properties
**Features:**
- Document information
- Creation/modification dates
- Author and title information
- Custom properties

### 🔧 Enhancement Tools

#### OCR Processing (`ocr.py`)
**Purpose:** Optical Character Recognition for scanned PDFs
**Features:**
- Multiple language support
- Searchable PDF creation
- Text layer addition
- Quality optimization

#### Watermarking (`watermark.py`)
**Purpose:** Add watermarks to PDF documents
**Features:**
- Text and image watermarks
- Position and opacity control
- Batch processing
- Template support

#### Text Highlighting (`highlight.py`)
**Purpose:** Highlight text in PDF documents
**Features:**
- Keyword highlighting
- Color customization
- Pattern matching
- Annotation support

### 🔄 Conversion Tools

#### DOCX Conversion (`convert_to_docx.py`)
**Purpose:** Convert PDF files to Microsoft Word format
**Features:**
- Layout preservation
- Image handling
- Table conversion
- Formatting retention

#### Image Conversion (`convert_to_image.py`)
**Purpose:** Convert PDF pages to image files
**Features:**
- Multiple image formats (PNG, JPG, TIFF)
- Resolution control
- Quality settings
- Batch conversion

#### HTML to PDF (`convert_html_to_pdf.py`)
**Purpose:** Convert HTML content to PDF format
**Features:**
- CSS styling support
- Image embedding
- Link preservation
- Custom page sizes

### 🔒 Security Tools

#### PDF Encryption (`encrypt.py`)
**Purpose:** Encrypt and decrypt PDF documents
**Features:**
- Password protection
- Permission controls
- Encryption strength options
- Batch processing

#### Digital Signing (`sign.py`)
**Purpose:** Add digital signatures to PDF documents
**Features:**
- Certificate-based signing
- Signature validation
- Timestamp support
- Multiple signature formats

### ⚙️ Administration Tools

#### Settings Manager (`settings_manager.py`)
**Purpose:** Configure PDF tools preferences
**Features:**
- Default output directories
- Quality settings
- Processing preferences
- Theme customization

#### Log Manager (`log_manager.py`)
**Purpose:** View and manage PDF processing logs
**Features:**
- Operation history
- Error tracking
- Performance metrics
- Log filtering

#### PDF Miner (`miner.py`)
**Purpose:** Advanced PDF analysis and data mining
**Features:**
- Document structure analysis
- Content pattern detection
- Statistical analysis
- Export capabilities

## Configuration and Settings

### Global Settings

PDF Tools inherit settings from the main RFU Hub configuration system:

- **Output Directories:** Default locations for processed files
- **Quality Settings:** Default compression and quality levels
- **Processing Options:** Batch processing preferences
- **Theme Integration:** Consistent UI styling

### PDF-Specific Settings

Access PDF-specific settings through the Settings Manager:

- **Default PDF Viewer:** Choose preferred viewing application
- **OCR Language:** Set default language for OCR processing
- **Watermark Templates:** Manage reusable watermark designs
- **Security Defaults:** Default encryption and permission settings

## Tips and Best Practices

### Performance Optimization

1. **Large Files:** Use page ranges for large documents
2. **Batch Processing:** Process multiple files together when possible
3. **Quality Settings:** Balance quality vs. file size for your needs
4. **Memory Management:** Close unused PDF viewers to free memory

### File Organization

1. **Output Folders:** Use descriptive folder names for outputs
2. **Naming Conventions:** Maintain consistent file naming
3. **Backup Originals:** Keep copies of original files
4. **Version Control:** Use timestamps in output filenames

### Quality Control

1. **Preview Results:** Always preview before final processing
2. **Test Settings:** Use small files to test settings first
3. **Validate Outputs:** Check extracted content for accuracy
4. **Error Handling:** Review logs for processing issues

## Troubleshooting

### Common Issues

#### "File Not Found" Errors
- Verify file paths are correct
- Check file permissions
- Ensure files are not open in other applications

#### "Processing Failed" Errors
- Check available disk space
- Verify PDF file is not corrupted
- Review error logs for specific details

#### "Memory Errors" with Large Files
- Process files in smaller batches
- Use page ranges instead of full documents
- Close other applications to free memory

#### "Permission Denied" Errors
- Check file write permissions
- Ensure output directories exist
- Run application with appropriate privileges

### Getting Help

1. **Log Files:** Check the log manager for detailed error information
2. **Settings Reset:** Reset to default settings if issues persist
3. **File Validation:** Use PDF viewers to verify file integrity
4. **Support Documentation:** Refer to individual module help files

## Integration Features

### Unified Configuration
- All PDF tools share common configuration settings
- Changes apply across all modules
- Centralized preference management

### Consistent Logging
- All operations logged to central system
- Searchable operation history
- Error tracking and reporting

### Theme Integration
- PDF tools match main application theme
- Consistent UI elements and styling
- Accessibility features inherited

### Error Handling
- Graceful error recovery
- User-friendly error messages
- Detailed logging for troubleshooting

## Advanced Features

### Drag-and-Drop Support
- Drop PDF files directly onto the main interface
- Automatic operation selection for single files
- Batch processing for multiple files

### Keyboard Shortcuts
- Quick access to common operations
- Navigation shortcuts in viewers
- Accessibility support

### Automation Support
- Batch processing capabilities
- Template-based operations
- Scheduled processing (future feature)

## Version History

### Version 1.0 (2025-07-25)
- Initial integration with RFU Hub
- All 23 PDF utilities integrated
- Unified configuration and logging
- Bridge architecture implementation
- Hub interface integration

---

**For technical support or feature requests, please refer to the main RFU Hub documentation or contact the development team.**