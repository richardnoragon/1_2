# Richards PDF Utilities

A comprehensive suite of PDF manipulation tools built with Python and PyQt5. This application provides a user-friendly graphical interface for various PDF operations.

## Features

### Basic Operations
- **Compress**: Reduce PDF file size while maintaining quality
  - Multiple compression levels (High, Medium, Low)
  - Progress tracking
  - Preview capability
- **Split**: Split PDFs by page numbers or ranges
  - Custom page range selection
  - Batch output naming
  - Preview functionality
- **Merge**: Combine multiple PDFs
  - Drag and drop file ordering
  - Custom order manipulation
  - Preview capability
- **Page Administration**: Complete page management
  - Delete specific pages
  - Rotate pages (90°, 180°, 270°)
  - Move pages between documents
  - Reorder pages
  - Combine multiple PDFs
  - Split documents

### Content Extraction
- **Extract Text**: Extract text content from PDF files
  - Page selection support 
  - Multiple output formats (TXT, DOCX)
  - Various encoding options
- **Extract Images**: Extract embedded images from PDF documents
  - Size/format filtering
  - Batch processing
  - Preview capability
- **Extract Tables**: 
  - Camelot-based extraction with advanced options
  - Multiple export formats (CSV, HTML, JSON, Markdown, SQLite)
  - Table detection customization
  - Preview functionality
- **Extract Links**: Extract and validate hyperlinks
  - Internal/external link support
  - Multiple export formats (TXT, CSV, JSON)
  - Optional link validation
- **Extract Metadata**: View and export document metadata
  - Complete metadata extraction
  - Multiple export formats
- **PDF Miner**: Advanced content analysis
  - Extract text, images, fonts, and metadata
  - Multiple output formats (TXT, JSON, XML)
  - Detailed page information
  - Preview capability

### Document Conversion
- **Convert to DOCX**: PDF to Microsoft Word conversion
- **Convert to Images**: PDF to image formats (PNG, JPG, BMP)
- **HTML to PDF**: Convert from:
  - URLs
  - HTML files
  - Raw HTML content

### Security
- **Encrypt/Decrypt**: PDF security management
  - Password protection
  - Multiple encryption levels
  - Decryption support
  - Password recovery tools

### Enhancements
- **Watermark**: Add text or image watermarks
  - Customizable opacity
  - Position control
  - Font size and rotation options
- **OCR**: Optical Character Recognition
  - Convert scanned documents to searchable PDFs
  - Multiple language support
  - Batch processing
  - Preview capability
- **Highlight**: Text manipulation tools
  - Text highlighting with custom colors
  - Text framing
  - Redaction capability
  - Opacity control

### View & Analysis
- **PDF Viewer**: Built-in document viewer
  - Page navigation
  - Zoom controls
  - Document information display
- **PDF Miner**: Detailed PDF analysis
  - Structure examination
  - Content extraction
  - Multiple export formats

### Administration
- **Settings Manager**: Centralized configuration
  - Module-specific settings
  - Import/Export capabilities
  - User preference storage
- **Log Manager**: Comprehensive logging
  - Log level filtering
  - Search functionality
  - Export capabilities
  - Log rotation

## Core Features
- Drag and drop support across all modules
- Progress tracking for long operations
- Preview functionality where applicable
- Comprehensive error handling
- Detailed logging system
- Persistent user settings
- Modern GUI with consistent design

## Requirements
- Python 3.x
- PyQt5
- Various PDF processing libraries (see requirements.txt)

## Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run main.py to launch the graphical interface:
```bash
python main.py
```

Each module can also be run independently by executing its corresponding Python file.

## Configuration
The application uses a central configuration system for managing settings across different modules. Settings can be customized through:
- The Settings Manager interface
- Direct configuration file editing
- Module-specific interfaces

## Error Handling and Logging
- Comprehensive error logging system
- User-friendly error messages
- Detailed debug logging
- Log rotation and management
- Searchable log history

## Contributing
[Contribution Guidelines]

## License
[Specify License]