# PDF Tools Phase 2.1 - Functional Architecture Plan

## 📋 Overview

This document outlines the comprehensive architectural plan for implementing functional button handlers for the basic PDF operations (merge, split, sign) in Phase 2.1 of the Enhanced PDF Tools Hub.

## 🔍 Current State Analysis

### Available PDF Libraries
Based on the codebase analysis, the following PDF processing libraries are available:
- **PyMuPDF (fitz)** - Primary library, used extensively across existing tools
- **PyPDF2** - Available for compatibility
- **pikepdf** - Used in signing functionality
- **pdfplumber** - Used for text extraction
- **camelot** - Used for table extraction

### Existing Implementation Patterns
From analyzing existing PDF tools, I identified these patterns:
1. **UI Pattern**: PyQt5 with `.ui` files loaded via `uic.loadUi()`
2. **Error Handling**: Comprehensive logging with `log_config.setup_logger()`
3. **File Operations**: File dialogs for input/output selection
4. **Progress Feedback**: Status messages and progress indicators
5. **Validation**: Input validation with user-friendly error messages

## 🏗️ Functional Architecture Design

### Core Components

#### 1. **PDF Operation Engine** (`pdf_operation_engine.py`)
Central engine for executing PDF operations with:
- **Unified Interface**: Common interface for all PDF operations
- **Progress Tracking**: Real-time progress updates with callbacks
- **Error Recovery**: Comprehensive error handling with recovery strategies
- **Resource Management**: Memory and file handle management
- **Validation**: Input validation and file integrity checks

#### 2. **Parameter Dialog System** (`pdf_parameter_dialogs.py`)
Dynamic dialog system for operation parameters:
- **Merge Dialog**: Multiple file selection with drag-and-drop reordering
- **Split Dialog**: Page range selection with preview
- **Sign Dialog**: Signature file selection and positioning options
- **Common Features**: Input validation, preview capabilities, help tooltips

#### 3. **File Management System** (`pdf_file_manager.py`)
Handles file operations and validation:
- **File Validation**: PDF integrity, permissions, encryption status
- **Output Management**: Automatic naming, conflict resolution
- **Temporary Files**: Safe temporary file handling
- **Backup Creation**: Optional backup before operations

#### 4. **Progress and Feedback System** (`pdf_progress_manager.py`)
User feedback and progress tracking:
- **Progress Bars**: Determinate progress for long operations
- **Status Messages**: Real-time operation status updates
- **Result Presentation**: Success/failure notifications with details
- **Cancellation Support**: Ability to cancel long-running operations

## 🔧 Implementation Strategy

### Phase 2.1.1: PDF Merge Functionality

#### **Merge Operation Features**
```python
class PDFMergeOperation:
    def __init__(self):
        self.input_files = []
        self.output_file = None
        self.merge_options = {
            'preserve_bookmarks': True,
            'preserve_metadata': True,
            'optimize_output': False,
            'page_ranges': {}  # Per-file page ranges
        }
    
    def execute(self, progress_callback=None):
        # Implementation with PyMuPDF
        pass
```

#### **Merge Dialog Interface**
- **File List**: Drag-and-drop reorderable list of PDF files
- **Preview Panel**: Thumbnail preview of selected files
- **Options Panel**: 
  - Preserve bookmarks/metadata
  - Output optimization
  - Page range selection per file
- **Output Selection**: Output file path with auto-naming

#### **Merge Implementation Details**
```python
def merge_pdfs(input_files, output_file, options, progress_callback=None):
    """
    Merge multiple PDF files using PyMuPDF
    
    Args:
        input_files: List of input PDF file paths
        output_file: Output PDF file path
        options: Merge options dictionary
        progress_callback: Progress update callback
    
    Returns:
        bool: Success status
    """
    try:
        result_doc = fitz.open()
        total_files = len(input_files)
        
        for i, file_path in enumerate(input_files):
            if progress_callback:
                progress_callback(i / total_files * 100, f"Processing {os.path.basename(file_path)}")
            
            # Validate and open source PDF
            source_doc = fitz.open(file_path)
            
            # Apply page range if specified
            page_range = options.get('page_ranges', {}).get(file_path)
            if page_range:
                # Insert specific pages
                for page_num in page_range:
                    result_doc.insert_pdf(source_doc, from_page=page_num, to_page=page_num)
            else:
                # Insert all pages
                result_doc.insert_pdf(source_doc)
            
            source_doc.close()
        
        # Apply output options
        if options.get('optimize_output'):
            result_doc.save(output_file, garbage=4, deflate=True)
        else:
            result_doc.save(output_file)
        
        result_doc.close()
        return True
        
    except Exception as e:
        logger.error(f"Merge operation failed: {e}")
        raise
```

### Phase 2.1.2: PDF Split Functionality

#### **Split Operation Features**
```python
class PDFSplitOperation:
    def __init__(self):
        self.input_file = None
        self.output_directory = None
        self.split_options = {
            'method': 'pages',  # 'pages', 'ranges', 'bookmarks', 'size'
            'pages_per_file': 1,
            'custom_ranges': [],
            'naming_pattern': 'split_{index}.pdf'
        }
    
    def execute(self, progress_callback=None):
        # Implementation with PyMuPDF
        pass
```

#### **Split Dialog Interface**
- **Input File**: PDF file selection with page count display
- **Split Method**: 
  - By page count (N pages per file)
  - By page ranges (custom ranges)
  - By bookmarks (chapter-based splitting)
  - By file size (approximate size limit)
- **Preview Panel**: Visual page range preview
- **Output Options**: Directory selection and naming pattern

#### **Split Implementation Details**
```python
def split_pdf(input_file, output_dir, options, progress_callback=None):
    """
    Split PDF file using various methods
    
    Args:
        input_file: Input PDF file path
        output_dir: Output directory path
        options: Split options dictionary
        progress_callback: Progress update callback
    
    Returns:
        List[str]: List of created output files
    """
    try:
        source_doc = fitz.open(input_file)
        total_pages = len(source_doc)
        output_files = []
        
        if options['method'] == 'pages':
            pages_per_file = options['pages_per_file']
            
            for i in range(0, total_pages, pages_per_file):
                if progress_callback:
                    progress_callback(i / total_pages * 100, f"Creating file {len(output_files) + 1}")
                
                new_doc = fitz.open()
                end_page = min(i + pages_per_file - 1, total_pages - 1)
                new_doc.insert_pdf(source_doc, from_page=i, to_page=end_page)
                
                output_file = os.path.join(output_dir, 
                    options['naming_pattern'].format(index=len(output_files) + 1))
                new_doc.save(output_file)
                new_doc.close()
                output_files.append(output_file)
        
        elif options['method'] == 'ranges':
            for i, page_range in enumerate(options['custom_ranges']):
                if progress_callback:
                    progress_callback(i / len(options['custom_ranges']) * 100, 
                        f"Creating range file {i + 1}")
                
                new_doc = fitz.open()
                new_doc.insert_pdf(source_doc, 
                    from_page=page_range[0], to_page=page_range[1])
                
                output_file = os.path.join(output_dir, 
                    f"range_{page_range[0]+1}-{page_range[1]+1}.pdf")
                new_doc.save(output_file)
                new_doc.close()
                output_files.append(output_file)
        
        source_doc.close()
        return output_files
        
    except Exception as e:
        logger.error(f"Split operation failed: {e}")
        raise
```

### Phase 2.1.3: PDF Sign Functionality

#### **Sign Operation Features**
```python
class PDFSignOperation:
    def __init__(self):
        self.input_file = None
        self.signature_file = None
        self.output_file = None
        self.sign_options = {
            'pages': 'all',  # 'all', 'first', 'last', or list of page numbers
            'position': 'bottom_right',  # Predefined positions or custom coordinates
            'size': (100, 50),  # Signature size in points
            'transparency': 0.8,
            'digital_signature': False,  # True for cryptographic signatures
            'certificate_file': None
        }
    
    def execute(self, progress_callback=None):
        # Implementation with PyMuPDF and pikepdf
        pass
```

#### **Sign Dialog Interface**
- **Input File**: PDF file selection
- **Signature Image**: Image file selection with preview
- **Position Options**: 
  - Predefined positions (corners, center)
  - Custom coordinates with visual positioning
- **Page Selection**: All pages, specific pages, or page ranges
- **Signature Options**: Size, transparency, digital signature
- **Certificate**: Optional digital certificate for cryptographic signing

#### **Sign Implementation Details**
```python
def sign_pdf(input_file, signature_file, output_file, options, progress_callback=None):
    """
    Add signature to PDF file
    
    Args:
        input_file: Input PDF file path
        signature_file: Signature image file path
        output_file: Output PDF file path
        options: Signing options dictionary
        progress_callback: Progress update callback
    
    Returns:
        bool: Success status
    """
    try:
        pdf_doc = fitz.open(input_file)
        total_pages = len(pdf_doc)
        
        # Determine pages to sign
        if options['pages'] == 'all':
            pages_to_sign = range(total_pages)
        elif options['pages'] == 'first':
            pages_to_sign = [0]
        elif options['pages'] == 'last':
            pages_to_sign = [total_pages - 1]
        else:
            pages_to_sign = options['pages']
        
        for i, page_num in enumerate(pages_to_sign):
            if progress_callback:
                progress_callback(i / len(pages_to_sign) * 100, 
                    f"Signing page {page_num + 1}")
            
            page = pdf_doc[page_num]
            
            # Calculate signature position
            rect = page.rect
            position = calculate_signature_position(rect, options['position'], options['size'])
            
            # Insert signature image
            page.insert_image(position, filename=signature_file, 
                overlay=True, alpha=int(options['transparency'] * 255))
        
        # Save signed PDF
        pdf_doc.save(output_file)
        pdf_doc.close()
        
        # Add digital signature if requested
        if options.get('digital_signature') and options.get('certificate_file'):
            add_digital_signature(output_file, options['certificate_file'])
        
        return True
        
    except Exception as e:
        logger.error(f"Sign operation failed: {e}")
        raise

def calculate_signature_position(page_rect, position, size):
    """Calculate signature position on page"""
    width, height = size
    
    positions = {
        'top_left': (10, 10),
        'top_right': (page_rect.width - width - 10, 10),
        'bottom_left': (10, page_rect.height - height - 10),
        'bottom_right': (page_rect.width - width - 10, page_rect.height - height - 10),
        'center': ((page_rect.width - width) / 2, (page_rect.height - height) / 2)
    }
    
    if isinstance(position, str) and position in positions:
        x, y = positions[position]
    else:
        x, y = position  # Custom coordinates
    
    return fitz.Rect(x, y, x + width, y + height)
```

## 🎨 User Interface Design

### Enhanced Parameter Dialogs

#### **Common Dialog Features**
- **Modern Styling**: Consistent with RFU hub theme
- **Input Validation**: Real-time validation with visual feedback
- **Preview Capabilities**: Visual previews where applicable
- **Help System**: Tooltips and help buttons for complex options
- **Responsive Layout**: Adaptive layout for different screen sizes

#### **Merge Dialog Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ Merge PDF Files                                        [?] │
├─────────────────────────────────────────────────────────────┤
│ Input Files                          │ Preview              │
│ ┌─────────────────────────────────┐   │ ┌─────────────────┐  │
│ │ [📄] document1.pdf              │   │ │     [thumb]     │  │
│ │ [📄] document2.pdf              │   │ │   document1.pdf │  │
│ │ [📄] document3.pdf              │   │ │    5 pages      │  │
│ │                                 │   │ └─────────────────┘  │
│ │ [+ Add Files] [Remove] [↑] [↓]  │   │                      │
│ └─────────────────────────────────┘   │                      │
├─────────────────────────────────────────────────────────────┤
│ Options                                                     │
│ ☑ Preserve bookmarks    ☑ Preserve metadata               │
│ ☐ Optimize output       ☐ Custom page ranges              │
├─────────────────────────────────────────────────────────────┤
│ Output: [output.pdf........................] [Browse]      │
│                                                             │
│                           [Cancel] [Merge PDFs]            │
└─────────────────────────────────────────────────────────────┘
```

#### **Split Dialog Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ Split PDF File                                         [?] │
├─────────────────────────────────────────────────────────────┤
│ Input: [document.pdf.....................] [Browse]       │
│ Pages: 150 pages                                           │
├─────────────────────────────────────────────────────────────┤
│ Split Method:                                              │
│ ○ By page count: [5] pages per file                       │
│ ○ By page ranges: [1-10,11-20,21-30]                     │
│ ○ By bookmarks (chapter-based)                            │
│ ○ By file size: [5] MB per file                           │
├─────────────────────────────────────────────────────────────┤
│ Preview                                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ File 1: Pages 1-5    File 2: Pages 6-10               │ │
│ │ File 3: Pages 11-15  File 4: Pages 16-20              │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Output Directory: [C:\Output\................] [Browse]    │
│ Naming Pattern: [split_{index}.pdf]                       │
│                                                             │
│                           [Cancel] [Split PDF]             │
└─────────────────────────────────────────────────────────────┘
```

#### **Sign Dialog Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ Sign PDF Document                                      [?] │
├─────────────────────────────────────────────────────────────┤
│ PDF File: [document.pdf..................] [Browse]       │
│ Signature: [signature.png................] [Browse]       │
├─────────────────────────────────────────────────────────────┤
│ Position                             │ Preview             │
│ ○ Top Left      ○ Top Right         │ ┌─────────────────┐  │
│ ○ Bottom Left   ● Bottom Right      │ │ ┌─────────────┐ │  │
│ ○ Center        ○ Custom: [x,y]     │ │ │             │ │  │
│                                     │ │ │   Page 1    │ │  │
│ Pages to Sign:                      │ │ │             │ │  │
│ ● All pages                         │ │ │        [sig]│ │  │
│ ○ First page only                   │ │ └─────────────┘ │  │
│ ○ Last page only                    │ └─────────────────┘  │
│ ○ Custom pages: [1,3,5]             │                      │
├─────────────────────────────────────────────────────────────┤
│ Options                                                     │
│ Size: [100] x [50] points    Transparency: [80]%           │
│ ☐ Add digital signature (requires certificate)            │
│ Certificate: [cert.pfx...................] [Browse]       │
├─────────────────────────────────────────────────────────────┤
│ Output: [document_signed.pdf.............] [Browse]       │
│                                                             │
│                           [Cancel] [Sign Document]         │
└─────────────────────────────────────────────────────────────┘
```

## 🔒 Error Handling and Validation

### File Validation Strategy
```python
class PDFValidator:
    @staticmethod
    def validate_pdf_file(file_path):
        """Comprehensive PDF file validation"""
        checks = {
            'exists': os.path.exists(file_path),
            'readable': os.access(file_path, os.R_OK),
            'valid_pdf': False,
            'encrypted': False,
            'corrupted': False,
            'page_count': 0
        }
        
        try:
            doc = fitz.open(file_path)
            checks['valid_pdf'] = True
            checks['encrypted'] = doc.needs_pass
            checks['page_count'] = len(doc)
            doc.close()
        except Exception as e:
            checks['corrupted'] = True
            checks['error'] = str(e)
        
        return checks
```

### Error Recovery Strategies
1. **File Access Errors**: Suggest checking permissions, closing other applications
2. **Corrupted PDFs**: Offer repair options or alternative processing methods
3. **Memory Errors**: Suggest processing in smaller batches
4. **Output Conflicts**: Automatic file naming with incremental suffixes
5. **Operation Cancellation**: Clean up temporary files and partial outputs

## 📊 Progress Tracking and User Feedback

### Progress Management System
```python
class OperationProgressManager:
    def __init__(self, operation_name, total_steps):
        self.operation_name = operation_name
        self.total_steps = total_steps
        self.current_step = 0
        self.callbacks = []
    
    def update_progress(self, step, message=""):
        """Update progress and notify callbacks"""
        self.current_step = step
        percentage = (step / self.total_steps) * 100
        
        for callback in self.callbacks:
            callback(percentage, message)
    
    def add_callback(self, callback):
        """Add progress callback"""
        self.callbacks.append(callback)
```

### User Feedback Components
- **Progress Bars**: Determinate progress for file operations
- **Status Messages**: Real-time operation status in status bar
- **Result Dialogs**: Comprehensive success/failure notifications
- **Log Viewer**: Optional detailed operation log viewer
- **Cancellation**: Graceful operation cancellation with cleanup

## 🧪 Testing Strategy

### Unit Testing
- **Operation Engine**: Test each PDF operation with various inputs
- **File Validation**: Test validation with different file types and conditions
- **Parameter Dialogs**: Test input validation and user interactions
- **Error Handling**: Test error scenarios and recovery mechanisms

### Integration Testing
- **End-to-End Workflows**: Test complete operation workflows
- **File System Integration**: Test with various file system conditions
- **Memory Management**: Test with large files and multiple operations
- **UI Integration**: Test dialog interactions and progress feedback

### Performance Testing
- **Large File Handling**: Test with large PDF files (>100MB)
- **Batch Operations**: Test multiple file operations
- **Memory Usage**: Monitor memory consumption during operations
- **Response Time**: Measure operation completion times

## 📈 Success Metrics

### Functionality Metrics
- **Operation Success Rate**: >95% success rate for valid inputs
- **Error Recovery**: Graceful handling of all error conditions
- **User Experience**: Intuitive dialogs with clear feedback
- **Performance**: Reasonable processing times for typical files

### Quality Metrics
- **Code Coverage**: >90% test coverage for core functionality
- **Error Handling**: Comprehensive error scenarios covered
- **Documentation**: Complete user and developer documentation
- **Maintainability**: Clean, modular code architecture

## 🚀 Implementation Timeline

### Phase 2.1.1: PDF Merge (Week 1)
- Day 1-2: Core merge engine implementation
- Day 3-4: Merge parameter dialog
- Day 5: Integration and testing

### Phase 2.1.2: PDF Split (Week 2)
- Day 1-2: Core split engine implementation
- Day 3-4: Split parameter dialog with preview
- Day 5: Integration and testing

### Phase 2.1.3: PDF Sign (Week 3)
- Day 1-2: Core signing engine implementation
- Day 3-4: Sign parameter dialog with positioning
- Day 5: Integration and testing

### Phase 2.1.4: Integration and Polish (Week 4)
- Day 1-2: Complete integration with enhanced PDF tools widget
- Day 3-4: Comprehensive testing and bug fixes
- Day 5: Documentation and final validation

## 📝 Next Steps

1. **Switch to Code Mode**: Begin implementation of the functional architecture
2. **Create Core Components**: Implement the PDF operation engine and file manager
3. **Build Parameter Dialogs**: Create the enhanced parameter dialogs
4. **Integrate with Widget**: Replace placeholder implementations
5. **Test and Validate**: Comprehensive testing with real PDF files
6. **Document Implementation**: Create user and developer documentation

This architectural plan provides a solid foundation for implementing robust, user-friendly PDF operations that integrate seamlessly with the existing Enhanced PDF Tools Hub.