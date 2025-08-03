#!/usr/bin/env python3
"""
PDF Tools Hub - Web Interface Backend
Flask application for handling PDF batch processing through web interface
"""

import os
import sys
import json
import uuid
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Add the parent directory to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from batch_processor import BatchProcessor, JobConfig, JobPriority
    from error_manager import ErrorManager, ErrorCategory
    from progress_manager import ProgressManager
except ImportError as e:
    print(f"Warning: Could not import PDF tools modules: {e}")
    print("Running in demo mode with mock implementations")
    
    # Mock implementations for demo
    class JobPriority:
        LOW = "low"
        NORMAL = "normal"
        HIGH = "high"
        URGENT = "urgent"
    
    @dataclass
    class JobConfig:
        operation: str
        input_files: List[str]
        output_directory: str
        parameters: Dict[str, Any]
        priority: str = JobPriority.NORMAL
        max_concurrent: int = 2
        
    class BatchProcessor:
        def __init__(self):
            self.jobs = {}
            
        async def submit_job(self, config: JobConfig) -> str:
            job_id = str(uuid.uuid4())
            self.jobs[job_id] = {"config": config, "status": "queued"}
            return job_id
            
        def get_job_status(self, job_id: str) -> Dict:
            return self.jobs.get(job_id, {"status": "not_found"})
            
        def cancel_job(self, job_id: str) -> bool:
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "cancelled"
                return True
            return False
    
    class ErrorManager:
        @staticmethod
        def categorize_error(error: Exception) -> str:
            return "general"
            
        @staticmethod
        def get_user_friendly_message(error: Exception) -> str:
            return str(error)
    
    class ProgressManager:
        def __init__(self):
            pass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pdf-tools-hub-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global instances
batch_processor = BatchProcessor()
error_manager = ErrorManager()
progress_manager = ProgressManager()

# Active jobs tracking
active_jobs: Dict[str, Dict] = {}
job_progress: Dict[str, Dict] = {}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@dataclass
class WebJobStatus:
    """Web-specific job status information"""
    job_id: str
    status: str  # queued, running, completed, failed, cancelled
    operation: str
    total_files: int
    completed_files: int
    failed_files: int
    current_file: Optional[str]
    progress_percentage: float
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error_message: Optional[str]
    results: List[Dict]

def allowed_file(filename: str) -> bool:
    """Check if uploaded file is a valid PDF"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/operations')
def get_operations():
    """Get available PDF operations"""
    operations = [
        {
            'id': 'split',
            'name': 'Split PDF',
            'description': 'Split PDF into multiple files',
            'category': 'Basic Operations',
            'parameters': [
                {'name': 'method', 'type': 'select', 'options': ['pages', 'ranges', 'single'], 'default': 'pages'},
                {'name': 'pages_per_file', 'type': 'number', 'default': 1, 'min': 1}
            ]
        },
        {
            'id': 'merge',
            'name': 'Merge PDFs',
            'description': 'Combine multiple PDFs into one',
            'category': 'Basic Operations',
            'parameters': []
        },
        {
            'id': 'compress',
            'name': 'Compress PDF',
            'description': 'Reduce PDF file size',
            'category': 'Optimization',
            'parameters': [
                {'name': 'compression_level', 'type': 'range', 'min': 0, 'max': 100, 'default': 50},
                {'name': 'image_quality', 'type': 'select', 'options': ['high', 'medium', 'low'], 'default': 'medium'}
            ]
        },
        {
            'id': 'extract_text',
            'name': 'Extract Text',
            'description': 'Extract text content from PDF',
            'category': 'Content Extraction',
            'parameters': [
                {'name': 'output_format', 'type': 'select', 'options': ['txt', 'json', 'csv'], 'default': 'txt'}
            ]
        },
        {
            'id': 'extract_images',
            'name': 'Extract Images',
            'description': 'Extract images from PDF',
            'category': 'Content Extraction',
            'parameters': [
                {'name': 'image_format', 'type': 'select', 'options': ['png', 'jpg', 'tiff'], 'default': 'png'},
                {'name': 'min_size', 'type': 'number', 'default': 100, 'min': 1}
            ]
        },
        {
            'id': 'watermark',
            'name': 'Add Watermark',
            'description': 'Add text or image watermark',
            'category': 'Security & Branding',
            'parameters': [
                {'name': 'text', 'type': 'text', 'required': True},
                {'name': 'opacity', 'type': 'range', 'min': 0, 'max': 100, 'default': 50},
                {'name': 'position', 'type': 'select', 'options': ['center', 'top-left', 'top-right', 'bottom-left', 'bottom-right'], 'default': 'center'}
            ]
        },
        {
            'id': 'encrypt',
            'name': 'Encrypt PDF',
            'description': 'Password protect PDF',
            'category': 'Security & Branding',
            'parameters': [
                {'name': 'password', 'type': 'password', 'required': True},
                {'name': 'encryption_level', 'type': 'select', 'options': ['128', '256'], 'default': '128'}
            ]
        },
        {
            'id': 'convert_to_images',
            'name': 'Convert to Images',
            'description': 'Convert PDF pages to images',
            'category': 'Conversion',
            'parameters': [
                {'name': 'format', 'type': 'select', 'options': ['png', 'jpg', 'tiff'], 'default': 'png'},
                {'name': 'dpi', 'type': 'number', 'default': 300, 'min': 72, 'max': 600}
            ]
        }
    ]
    
    return jsonify(operations)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        uploaded_files = []
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        
        # Create session-specific upload directory
        session_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(session_upload_dir, exist_ok=True)
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                
                filepath = os.path.join(session_upload_dir, filename)
                file.save(filepath)
                
                # Get file info
                file_size = os.path.getsize(filepath)
                uploaded_files.append({
                    'filename': file.filename,  # Original filename
                    'stored_filename': filename,  # Stored filename
                    'filepath': filepath,
                    'size': file_size,
                    'size_formatted': format_file_size(file_size)
                })
        
        if not uploaded_files:
            return jsonify({'error': 'No valid PDF files uploaded'}), 400
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} file(s)',
            'files': uploaded_files,
            'session_id': session_id
        })
        
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large. Maximum size is 500MB.'}), 413
    except Exception as e:
        error_msg = error_manager.get_user_friendly_message(e)
        return jsonify({'error': f'Upload failed: {error_msg}'}), 500

@app.route('/api/process', methods=['POST'])
def start_processing():
    """Start batch processing job"""
    try:
        data = request.get_json()
        
        # Validate request data
        required_fields = ['operation', 'files', 'output_directory']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get session info
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No active session. Please upload files first.'}), 400
        
        # Validate files exist
        session_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        input_files = []
        
        for file_info in data['files']:
            filepath = os.path.join(session_upload_dir, file_info['stored_filename'])
            if not os.path.exists(filepath):
                return jsonify({'error': f'File not found: {file_info["filename"]}'}), 400
            input_files.append(filepath)
        
        # Create job configuration
        job_config = JobConfig(
            operation=data['operation'],
            input_files=input_files,
            output_directory=data['output_directory'],
            parameters=data.get('parameters', {}),
            priority=data.get('priority', JobPriority.NORMAL),
            max_concurrent=data.get('concurrent_jobs', 2)
        )
        
        # Submit job to batch processor
        job_id = asyncio.run(batch_processor.submit_job(job_config))
        
        # Initialize job tracking
        active_jobs[job_id] = {
            'session_id': session_id,
            'config': asdict(job_config),
            'status': 'queued',
            'created_at': datetime.now(),
            'total_files': len(input_files),
            'completed_files': 0,
            'failed_files': 0,
            'current_file': None,
            'progress_percentage': 0.0,
            'results': []
        }
        
        # Start background processing
        threading.Thread(target=process_job_async, args=(job_id,), daemon=True).start()
        
        return jsonify({
            'job_id': job_id,
            'message': 'Processing started successfully',
            'status': 'queued'
        })
        
    except Exception as e:
        error_msg = error_manager.get_user_friendly_message(e)
        return jsonify({'error': f'Failed to start processing: {error_msg}'}), 500

@app.route('/api/jobs/<job_id>/status')
def get_job_status(job_id: str):
    """Get job status and progress"""
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job_info = active_jobs[job_id]
    
    # Get latest status from batch processor
    processor_status = batch_processor.get_job_status(job_id)
    
    # Update our tracking with processor status
    if processor_status.get('status'):
        job_info['status'] = processor_status['status']
    
    return jsonify({
        'job_id': job_id,
        'status': job_info['status'],
        'operation': job_info['config']['operation'],
        'total_files': job_info['total_files'],
        'completed_files': job_info['completed_files'],
        'failed_files': job_info['failed_files'],
        'current_file': job_info['current_file'],
        'progress_percentage': job_info['progress_percentage'],
        'created_at': job_info['created_at'].isoformat(),
        'results': job_info['results']
    })

@app.route('/api/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id: str):
    """Cancel a running job"""
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    try:
        success = batch_processor.cancel_job(job_id)
        if success:
            active_jobs[job_id]['status'] = 'cancelled'
            
            # Emit status update via WebSocket
            socketio.emit('job_status_update', {
                'job_id': job_id,
                'status': 'cancelled',
                'message': 'Job cancelled by user'
            }, room=f'job_{job_id}')
            
            return jsonify({'message': 'Job cancelled successfully'})
        else:
            return jsonify({'error': 'Failed to cancel job'}), 500
            
    except Exception as e:
        error_msg = error_manager.get_user_friendly_message(e)
        return jsonify({'error': f'Failed to cancel job: {error_msg}'}), 500

@app.route('/api/jobs/<job_id>/results/<filename>')
def download_result(job_id: str, filename: str):
    """Download a processed file"""
    if job_id not in active_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job_info = active_jobs[job_id]
    output_dir = job_info['config']['output_directory']
    
    # Security: ensure filename is safe and exists
    safe_filename = secure_filename(filename)
    file_path = os.path.join(output_dir, safe_filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Verify file is in the job's output directory
    if not os.path.commonpath([output_dir, file_path]) == output_dir:
        return jsonify({'error': 'Access denied'}), 403
    
    return send_file(file_path, as_attachment=True)

def process_job_async(job_id: str):
    """Process job asynchronously with progress updates"""
    try:
        job_info = active_jobs[job_id]
        job_info['status'] = 'running'
        job_info['start_time'] = datetime.now()
        
        # Emit initial status
        socketio.emit('job_status_update', {
            'job_id': job_id,
            'status': 'running',
            'message': 'Processing started'
        }, room=f'job_{job_id}')
        
        # Simulate processing with progress updates
        # In a real implementation, this would integrate with the actual batch processor
        total_files = job_info['total_files']
        
        for i, file_path in enumerate(job_info['config']['input_files']):
            if job_info['status'] == 'cancelled':
                break
                
            filename = os.path.basename(file_path)
            job_info['current_file'] = filename
            
            # Emit file start
            socketio.emit('job_progress_update', {
                'job_id': job_id,
                'current_file': filename,
                'file_progress': 0,
                'overall_progress': (i / total_files) * 100
            }, room=f'job_{job_id}')
            
            # Simulate file processing with incremental progress
            for progress in range(0, 101, 10):
                if job_info['status'] == 'cancelled':
                    break
                    
                # Simulate processing time
                threading.Event().wait(0.1)
                
                # Update progress
                socketio.emit('job_progress_update', {
                    'job_id': job_id,
                    'current_file': filename,
                    'file_progress': progress,
                    'overall_progress': ((i + progress/100) / total_files) * 100
                }, room=f'job_{job_id}')
            
            if job_info['status'] == 'cancelled':
                break
            
            # Simulate occasional errors (5% chance)
            if i > 0 and len(job_info['config']['input_files']) > 2 and hash(filename) % 20 == 0:
                job_info['failed_files'] += 1
                job_info['results'].append({
                    'filename': filename,
                    'status': 'error',
                    'error': 'Simulated processing error',
                    'processing_time': 2.5
                })
                
                socketio.emit('job_file_completed', {
                    'job_id': job_id,
                    'filename': filename,
                    'status': 'error',
                    'error': 'Simulated processing error'
                }, room=f'job_{job_id}')
            else:
                job_info['completed_files'] += 1
                output_filename = f"processed_{filename}"
                job_info['results'].append({
                    'filename': filename,
                    'output_filename': output_filename,
                    'status': 'success',
                    'processing_time': 2.0 + (hash(filename) % 30) / 10
                })
                
                socketio.emit('job_file_completed', {
                    'job_id': job_id,
                    'filename': filename,
                    'output_filename': output_filename,
                    'status': 'success'
                }, room=f'job_{job_id}')
        
        # Complete job
        if job_info['status'] != 'cancelled':
            job_info['status'] = 'completed'
            job_info['end_time'] = datetime.now()
            job_info['progress_percentage'] = 100.0
            
            socketio.emit('job_status_update', {
                'job_id': job_id,
                'status': 'completed',
                'message': f'Processing completed: {job_info["completed_files"]} successful, {job_info["failed_files"]} failed'
            }, room=f'job_{job_id}')
        
    except Exception as e:
        job_info['status'] = 'failed'
        job_info['error_message'] = str(e)
        job_info['end_time'] = datetime.now()
        
        socketio.emit('job_status_update', {
            'job_id': job_id,
            'status': 'failed',
            'message': f'Processing failed: {str(e)}'
        }, room=f'job_{job_id}')

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to PDF Tools Hub'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_job')
def handle_join_job(data):
    """Join a job room for real-time updates"""
    job_id = data.get('job_id')
    if job_id:
        join_room(f'job_{job_id}')
        emit('joined_job', {'job_id': job_id})

@socketio.on('leave_job')
def handle_leave_job(data):
    """Leave a job room"""
    job_id = data.get('job_id')
    if job_id:
        leave_room(f'job_{job_id}')
        emit('left_job', {'job_id': job_id})

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 500MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting PDF Tools Hub Web Interface...")
    print("Access the application at: http://localhost:5000")
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Copy index.html to templates directory for Flask
    index_source = os.path.join(os.path.dirname(__file__), 'index.html')
    index_dest = os.path.join(templates_dir, 'index.html')
    
    if os.path.exists(index_source) and not os.path.exists(index_dest):
        import shutil
        shutil.copy2(index_source, index_dest)
        print("Copied index.html to templates directory")
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)