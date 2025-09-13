"""
Preview Subsystem for RFU Multi-Pane File Explorer

This module provides multi-format file preview capabilities with lazy loading,
memory management, and extensible preview handlers.

Author: Richard Noragon
Version: 2.0.0
"""

import logging

# Setup module logging
logger = logging.getLogger('RFU.Preview')

try:
    # Core preview components
    from .memory_manager import MemoryManager, PreviewCache
    from .preview_handlers import (ArchivePreviewHandler, AudioPreviewHandler,
                                   BasePreviewHandler, CodePreviewHandler,
                                   ImagePreviewHandler, PDFPreviewHandler,
                                   TextPreviewHandler, VideoPreviewHandler)
    from .preview_manager import PreviewManager, PreviewRequest, PreviewResult
    from .preview_widget import PreviewContainer, PreviewWidget
    from .thumbnail_generator import ThumbnailCache, ThumbnailGenerator
    
    logger.debug("Preview subsystem components loaded successfully")
    
except ImportError as e:
    logger.error(f"Failed to import preview components: {e}")
    # Provide fallback None values for graceful degradation
    PreviewManager = None
    PreviewRequest = None
    PreviewResult = None
    BasePreviewHandler = None
    TextPreviewHandler = None
    ImagePreviewHandler = None
    AudioPreviewHandler = None
    VideoPreviewHandler = None
    PDFPreviewHandler = None
    CodePreviewHandler = None
    ArchivePreviewHandler = None
    PreviewWidget = None
    PreviewContainer = None
    ThumbnailGenerator = None
    ThumbnailCache = None
    MemoryManager = None
    PreviewCache = None

__all__ = [
    # Core preview management
    'PreviewManager',
    'PreviewRequest',
    'PreviewResult',
    
    # Preview handlers
    'BasePreviewHandler',
    'TextPreviewHandler',
    'ImagePreviewHandler',
    'AudioPreviewHandler',
    'VideoPreviewHandler',
    'PDFPreviewHandler',
    'CodePreviewHandler',
    'ArchivePreviewHandler',
    
    # Preview widgets
    'PreviewWidget',
    'PreviewContainer',
    
    # Thumbnail support
    'ThumbnailGenerator',
    'ThumbnailCache',
    
    # Memory management
    'MemoryManager',
    'PreviewCache',
]

# Version information
__version__ = '2.0.0'
__author__ = 'Richard Noragon'