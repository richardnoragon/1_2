# PDF Tools Hub - Web Interface

A comprehensive web-based interface for batch processing PDF files using the PDF Tools Hub system. This interface provides a modern, user-friendly way to upload, configure, process, and download PDF files through your web browser.

## Features

### 🚀 Core Functionality
- **File Upload**: Drag-and-drop or click to upload multiple PDF files
- **Batch Processing**: Process multiple files simultaneously with configurable concurrency
- **Real-time Progress**: Live progress tracking with WebSocket updates
- **Operation Configuration**: Customizable parameters for each PDF operation
- **Results Management**: Download individual files or complete batches
- **Error Handling**: Comprehensive error reporting and recovery suggestions

### 📋 Supported Operations
- **Split PDF**: Split PDFs by page count, ranges, or single pages
- **Merge PDFs**: Combine multiple PDFs into one document
- **Compress PDF**: Reduce file size with adjustable compression levels
- **Extract Text**: Extract text content in various formats (TXT, JSON, CSV)
- **Extract Images**: Extract images with format and size options
- **Add Watermark**: Apply text watermarks with opacity and positioning
- **Encrypt PDF**: Password protect PDFs with 128-bit or 256-bit encryption
- **Convert to Images**: Convert PDF pages to PNG, JPG, or TIFF images

### 🎨 User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, intuitive interface with smooth animations
- **Tab Navigation**: Organized workflow through Upload → Configure → Process → Results
- **Real-time Updates**: Live status updates and progress indicators
- **Status Messages**: Clear feedback for all user actions

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Navigate to the web interface directory**:
   ```bash
   cd src/utilities/pdf_tools/pdf_utilities/web_interface
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the interface**:
   Open your web browser and navigate to: `http://localhost:5000`

## Usage Guide

### 1. Upload Files
- **Drag and Drop**: Drag PDF files directly onto the upload area
- **Click to Browse**: Click the upload area to open file browser
- **Multiple Selection**: Select multiple PDF files at once
- **File Validation**: Only PDF files are accepted (automatic filtering)

### 2. Configure Operations
- **Select Operation**: Choose from 8 different PDF operations
- **Set Parameters**: Configure operation-specific settings
- **Output Directory**: Specify where processed files should be saved
- **Processing Options**: Set priority level and concurrent job count

### 3. Start Processing
- **Review Settings**: Verify configuration before starting
- **Monitor Progress**: Watch real-time progress updates
- **Control Processing**: Pause, resume, or cancel operations
- **View Logs**: Monitor detailed processing logs

### 4. Download Results
- **Individual Downloads**: Download specific processed files
- **Batch Download**: Download all successful results
- **Processing Report**: Generate detailed processing reports
- **Error Analysis**: Review failed operations and error details

## API Endpoints

### File Management
- `POST /api/upload` - Upload PDF files
- `GET /api/operations` - Get available operations and parameters

### Job Management
- `POST /api/process` - Start batch processing job
- `GET /api/jobs/<job_id>/status` - Get job status and progress
- `POST /api/jobs/<job_id>/cancel` - Cancel running job
- `GET /api/jobs/<job_id>/results/<filename>` - Download processed file

### WebSocket Events
- `job_status_update` - Job status changes
- `job_progress_update` - File and overall progress updates
- `job_file_completed` - Individual file completion notifications

## Configuration

### Environment Variables
Create a `.env` file in the web interface directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Upload Configuration
MAX_CONTENT_LENGTH=524288000  # 500MB in bytes
UPLOAD_FOLDER=uploads

# Processing Configuration
DEFAULT_CONCURRENT_JOBS=2
MAX_CONCURRENT_JOBS=8
```

### Application Settings
Modify `app.py` to customize:

```python
# Maximum file size (500MB default)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# Upload directory
app.config['UPLOAD_FOLDER'] = 'uploads'

# Session configuration
app.config['SECRET_KEY'] = 'your-secret-key'
```

## Architecture

### Frontend Components
- **HTML**: Semantic structure with accessibility features
- **CSS**: Modern styling with CSS Grid and Flexbox
- **JavaScript**: ES6+ with async/await and WebSocket integration

### Backend Components
- **Flask**: Web framework for HTTP endpoints
- **Flask-SocketIO**: Real-time WebSocket communication
- **Werkzeug**: File upload handling and security
- **Threading**: Asynchronous job processing

### Integration Points
- **Batch Processor**: Core PDF processing engine
- **Error Manager**: Centralized error handling
- **Progress Manager**: Real-time progress tracking

## File Structure

```
web_interface/
├── app.py                 # Flask application and API endpoints
├── index.html            # Main web interface
├── styles.css            # CSS styling and responsive design
├── script.js             # JavaScript functionality and WebSocket handling
├── requirements.txt      # Python dependencies
├── README.md            # This documentation
├── templates/           # Flask templates directory
│   └── index.html       # Template copy for Flask
├── uploads/             # Temporary file storage (created automatically)
└── static/              # Static assets (if needed)
```

## Development

### Running in Development Mode
```bash
# Enable debug mode
export FLASK_ENV=development
python app.py
```

### Testing the Interface
1. **Upload Test**: Try uploading various PDF files
2. **Operation Test**: Test different PDF operations
3. **Progress Test**: Monitor progress updates during processing
4. **Error Test**: Test error handling with invalid inputs
5. **Download Test**: Verify file downloads work correctly

### Customization

#### Adding New Operations
1. **Update Operations List**: Add operation definition in `get_operations()` endpoint
2. **Add Parameters**: Define operation-specific parameters
3. **Update Frontend**: Add parameter handling in JavaScript
4. **Integrate Backend**: Connect to actual PDF processing tools

#### Styling Customization
- **Colors**: Modify CSS custom properties in `:root`
- **Layout**: Adjust CSS Grid and Flexbox properties
- **Animations**: Customize transition and animation durations
- **Responsive**: Modify media queries for different screen sizes

## Security Considerations

### File Upload Security
- **File Type Validation**: Only PDF files accepted
- **Filename Sanitization**: Secure filename handling
- **Size Limits**: Maximum file size enforcement
- **Session Isolation**: User files isolated by session

### Processing Security
- **Path Validation**: Prevent directory traversal attacks
- **Resource Limits**: Concurrent job limitations
- **Error Sanitization**: Safe error message display
- **Session Management**: Secure session handling

## Troubleshooting

### Common Issues

#### Upload Problems
- **File Too Large**: Check `MAX_CONTENT_LENGTH` setting
- **Invalid File Type**: Ensure files have `.pdf` extension
- **Network Timeout**: Increase server timeout for large files

#### Processing Issues
- **Job Stuck**: Check server logs for processing errors
- **Memory Issues**: Reduce concurrent job count
- **Permission Errors**: Verify output directory permissions

#### Connection Problems
- **WebSocket Errors**: Check firewall and proxy settings
- **CORS Issues**: Configure CORS for cross-origin requests
- **Port Conflicts**: Ensure port 5000 is available

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files
Check application logs for detailed error information:
- Flask logs: Console output when running `python app.py`
- Processing logs: Available through web interface log viewer

## Performance Optimization

### Server-Side
- **Concurrent Processing**: Adjust `max_concurrent` based on server capacity
- **Memory Management**: Monitor memory usage during large batch operations
- **File Cleanup**: Implement automatic cleanup of temporary files
- **Caching**: Add caching for frequently accessed data

### Client-Side
- **File Chunking**: Implement chunked uploads for large files
- **Progress Batching**: Batch progress updates to reduce WebSocket traffic
- **UI Optimization**: Lazy load results and optimize DOM updates

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Make changes and test thoroughly
5. Submit a pull request

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ features and consistent formatting
- **CSS**: Use BEM methodology for class naming
- **HTML**: Semantic markup with accessibility considerations

## License

This project is part of the PDF Tools Hub system. See the main project license for details.

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review existing issues in the project repository
3. Create a new issue with detailed information
4. Include error logs and steps to reproduce

---

**PDF Tools Hub Web Interface** - Making PDF processing accessible through modern web technology.