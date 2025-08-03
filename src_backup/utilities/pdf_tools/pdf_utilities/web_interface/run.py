#!/usr/bin/env python3
"""
PDF Tools Hub - Web Interface Launcher
Simple script to start the web interface with proper configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_socketio
        print("✓ Flask dependencies found")
        return True
    except ImportError as e:
        print(f"✗ Missing dependencies: {e}")
        print("\nTo install dependencies, run:")
        print("pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup environment variables and directories"""
    # Set Flask environment
    os.environ['FLASK_ENV'] = 'development'
    
    # Create necessary directories
    upload_dir = Path('uploads')
    upload_dir.mkdir(exist_ok=True)
    
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Copy index.html to templates if needed
    index_source = Path('index.html')
    index_dest = templates_dir / 'index.html'
    
    if index_source.exists() and not index_dest.exists():
        import shutil
        shutil.copy2(index_source, index_dest)
        print("✓ Copied index.html to templates directory")
    
    print("✓ Environment setup complete")

def main():
    """Main launcher function"""
    print("PDF Tools Hub - Web Interface Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Start the application
    print("\nStarting PDF Tools Hub Web Interface...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the Flask app
        from app import app, socketio
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except ImportError:
        print("Error: Could not import Flask application")
        print("Make sure app.py is in the current directory")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down PDF Tools Hub Web Interface...")
        print("Goodbye!")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()