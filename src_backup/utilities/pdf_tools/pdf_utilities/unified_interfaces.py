"""
Unified Input/Output Interfaces for PDF Tools Hub
Provides consistent interfaces for file handling, parameter management,
and result processing across all PDF tools.
"""

import os
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5.QtCore import QObject, pyqtSignal

from progress_manager import get_progress_manager
from error_manager import get_error_manager, handle_error
from log_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class FileInfo:
    """Information about a file."""
    path: str
    size: int = 0
    exists: bool = True
    readable: bool = True
    writable: bool = True
    
    def __post_init__(self):
        """Initialize file information."""
        if os.path.exists(self.path):
            try:
                stat = os.stat(self.path)
                self.size = stat.st_size
                self.readable = os.access(self.path, os.R_OK)
                self.writable = os.access(self.path, os.W_OK)
            except OSError:
                self.exists = False
                self.readable = False
                self.writable = False
        else:
            self.exists = False
            self.readable = False
            self.writable = False


@dataclass
class OperationResult:
    """Result of a PDF operation."""
    success: bool
    message: str
    output_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: Optional[float] = None
    error_details: Optional[str] = None
    
    def add_output_file(self, file_path: str):
        """Add an output file to the result."""
        if file_path not in self.output_files:
            self.output_files.append(file_path)
    
    def set_error(self, message: str, details: Optional[str] = None):
        """Set error information."""
        self.success = False
        self.message = message
        self.error_details = details


class FileSelector:
    """Unified file selection interface."""
    
    @staticmethod
    def select_input_file(parent: Optional[QWidget] = None,
                         title: str = "Select PDF File",
                         file_filter: str = "PDF Files (*.pdf)") -> Optional[str]:
        """Select a single input file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                parent, title, "", file_filter
            )
            return file_path if file_path else None
        except Exception as e:
            logger.error(f"Error selecting input file: {e}")
            return None
    
    @staticmethod
    def select_input_files(parent: Optional[QWidget] = None,
                          title: str = "Select PDF Files",
                          file_filter: str = "PDF Files (*.pdf)") -> List[str]:
        """Select multiple input files."""
        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                parent, title, "", file_filter
            )
            return file_paths if file_paths else []
        except Exception as e:
            logger.error(f"Error selecting input files: {e}")
            return []
    
    @staticmethod
    def select_output_file(parent: Optional[QWidget] = None,
                          title: str = "Save PDF File",
                          file_filter: str = "PDF Files (*.pdf)",
                          default_name: str = "") -> Optional[str]:
        """Select output file location."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                parent, title, default_name, file_filter
            )
            return file_path if file_path else None
        except Exception as e:
            logger.error(f"Error selecting output file: {e}")
            return None
    
    @staticmethod
    def select_output_directory(parent: Optional[QWidget] = None,
                               title: str = "Select Output Directory") -> Optional[str]:
        """Select output directory."""
        try:
            directory = QFileDialog.getExistingDirectory(parent, title)
            return directory if directory else None
        except Exception as e:
            logger.error(f"Error selecting output directory: {e}")
            return None


class ParameterValidator:
    """Validates operation parameters."""
    
    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
        """Validate a file path."""
        if not file_path:
            return False
        
        if must_exist and not os.path.exists(file_path):
            return False
        
        return True
    
    @staticmethod
    def validate_output_directory(directory: str, create_if_missing: bool = True) -> bool:
        """Validate output directory."""
        if not directory:
            return False
        
        if not os.path.exists(directory):
            if create_if_missing:
                try:
                    os.makedirs(directory, exist_ok=True)
                    return True
                except OSError:
                    return False
            else:
                return False
        
        return os.path.isdir(directory) and os.access(directory, os.W_OK)
    
    @staticmethod
    def validate_page_range(page_range: str, total_pages: int) -> bool:
        """Validate page range specification."""
        if not page_range:
            return False
        
        try:
            # Handle single page
            if page_range.isdigit():
                page = int(page_range)
                return 1 <= page <= total_pages
            
            # Handle range
            if '-' in page_range:
                start, end = page_range.split('-', 1)
                start_page = int(start) if start else 1
                end_page = int(end) if end else total_pages
                
                return (1 <= start_page <= total_pages and
                        1 <= end_page <= total_pages and
                        start_page <= end_page)
            
            return False
        except ValueError:
            return False
    
    @staticmethod
    def validate_compression_level(level: Union[int, str]) -> bool:
        """Validate compression level."""
        try:
            level_int = int(level)
            return 0 <= level_int <= 100
        except (ValueError, TypeError):
            return False


class PDFToolInterface(ABC):
    """Abstract base class for PDF tool interfaces."""
    
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.progress_manager = get_progress_manager()
        self.error_manager = get_error_manager()
        self.current_operation_id: Optional[str] = None
    
    @abstractmethod
    def get_required_parameters(self) -> Dict[str, Any]:
        """Get required parameters for the tool."""
        pass
    
    @abstractmethod
    def get_optional_parameters(self) -> Dict[str, Any]:
        """Get optional parameters for the tool."""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate tool parameters."""
        pass
    
    @abstractmethod
    def process_file(self, input_file: str, output_file: Optional[str] = None,
                    parameters: Dict[str, Any] = None) -> OperationResult:
        """Process a single file."""
        pass
    
    def process_files(self, input_files: List[str], 
                     output_directory: Optional[str] = None,
                     parameters: Dict[str, Any] = None) -> List[OperationResult]:
        """Process multiple files."""
        if parameters is None:
            parameters = {}
        
        results = []
        
        # Create batch operation
        operation_id = self.progress_manager.create_batch_operation(
            self.tool_name, "batch_process", input_files
        )
        self.current_operation_id = operation_id
        self.progress_manager.start_operation(operation_id, "Starting batch processing...")
        
        try:
            for i, input_file in enumerate(input_files):
                try:
                    # Generate output file path
                    output_file = None
                    if output_directory:
                        filename = os.path.basename(input_file)
                        name, ext = os.path.splitext(filename)
                        output_file = os.path.join(output_directory, f"{name}_processed{ext}")
                    
                    # Update progress
                    progress = int((i / len(input_files)) * 100)
                    self.progress_manager.update_progress(
                        operation_id, progress, 
                        f"Processing {os.path.basename(input_file)}", input_file
                    )
                    
                    # Process file
                    result = self.process_file(input_file, output_file, parameters)
                    results.append(result)
                    
                    if not result.success:
                        logger.warning(f"Failed to process {input_file}: {result.message}")
                
                except Exception as e:
                    error_context = {
                        'tool_name': self.tool_name,
                        'file_path': input_file,
                        'operation_id': operation_id
                    }
                    handle_error(e, error_context)
                    
                    result = OperationResult(
                        success=False,
                        message=f"Error processing {input_file}: {str(e)}"
                    )
                    results.append(result)
            
            # Complete operation
            successful_results = [r for r in results if r.success]
            success_rate = len(successful_results) / len(results) * 100
            
            if success_rate == 100:
                message = f"All {len(input_files)} files processed successfully"
                success = True
            elif success_rate > 0:
                message = f"Processed {len(successful_results)}/{len(input_files)} files successfully"
                success = True
            else:
                message = "No files were processed successfully"
                success = False
            
            self.progress_manager.complete_operation(operation_id, success, message)
            
        except Exception as e:
            self.progress_manager.complete_operation(
                operation_id, False, f"Batch processing failed: {str(e)}"
            )
            raise
        
        finally:
            self.current_operation_id = None
        
        return results
    
    def update_progress(self, percent: int, message: str = ""):
        """Update operation progress."""
        if self.current_operation_id:
            self.progress_manager.update_progress(
                self.current_operation_id, percent, message
            )
    
    def get_file_info(self, file_path: str) -> FileInfo:
        """Get information about a file."""
        return FileInfo(file_path)
    
    def create_output_filename(self, input_file: str, suffix: str = "_processed",
                              extension: Optional[str] = None) -> str:
        """Create output filename based on input file."""
        path = Path(input_file)
        name = path.stem
        ext = extension or path.suffix
        
        return str(path.parent / f"{name}{suffix}{ext}")


class StandardPDFTool(PDFToolInterface):
    """Standard implementation of PDF tool interface."""
    
    def __init__(self, tool_name: str, operation_function: Callable):
        super().__init__(tool_name)
        self.operation_function = operation_function
        self._required_parameters = {}
        self._optional_parameters = {}
    
    def set_parameters(self, required: Dict[str, Any] = None, 
                      optional: Dict[str, Any] = None):
        """Set parameter definitions."""
        if required:
            self._required_parameters = required
        if optional:
            self._optional_parameters = optional
    
    def get_required_parameters(self) -> Dict[str, Any]:
        """Get required parameters."""
        return self._required_parameters
    
    def get_optional_parameters(self) -> Dict[str, Any]:
        """Get optional parameters."""
        return self._optional_parameters
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters."""
        # Check required parameters
        for param_name in self._required_parameters:
            if param_name not in parameters:
                logger.error(f"Missing required parameter: {param_name}")
                return False
        
        # Validate specific parameter types
        for param_name, param_value in parameters.items():
            if param_name == 'page_range' and 'total_pages' in parameters:
                if not ParameterValidator.validate_page_range(
                    param_value, parameters['total_pages']
                ):
                    return False
            elif param_name == 'compression_level':
                if not ParameterValidator.validate_compression_level(param_value):
                    return False
        
        return True
    
    def process_file(self, input_file: str, output_file: Optional[str] = None,
                    parameters: Dict[str, Any] = None) -> OperationResult:
        """Process a single file."""
        if parameters is None:
            parameters = {}
        
        result = OperationResult(success=False, message="")
        
        try:
            # Validate input file
            if not ParameterValidator.validate_file_path(input_file, must_exist=True):
                result.set_error(f"Input file not found or invalid: {input_file}")
                return result
            
            # Validate parameters
            if not self.validate_parameters(parameters):
                result.set_error("Invalid parameters provided")
                return result
            
            # Call the operation function
            start_time = time.time()
            
            operation_result = self.operation_function(
                input_file, output_file, **parameters
            )
            
            end_time = time.time()
            result.processing_time = end_time - start_time
            
            # Handle different return types
            if isinstance(operation_result, bool):
                result.success = operation_result
                result.message = "Operation completed" if operation_result else "Operation failed"
                if output_file and operation_result:
                    result.add_output_file(output_file)
            
            elif isinstance(operation_result, dict):
                result.success = operation_result.get('success', False)
                result.message = operation_result.get('message', '')
                
                if 'output_files' in operation_result:
                    for file_path in operation_result['output_files']:
                        result.add_output_file(file_path)
                
                if 'metadata' in operation_result:
                    result.metadata.update(operation_result['metadata'])
            
            else:
                result.success = True
                result.message = "Operation completed successfully"
                if output_file:
                    result.add_output_file(output_file)
        
        except Exception as e:
            result.set_error(f"Error processing file: {str(e)}", str(e))
            
            # Handle error through error manager
            error_context = {
                'tool_name': self.tool_name,
                'file_path': input_file,
                'output_file': output_file,
                'parameters': parameters
            }
            handle_error(e, error_context)
        
        return result


class ToolRegistry:
    """Registry for PDF tool interfaces."""
    
    def __init__(self):
        self.tools: Dict[str, PDFToolInterface] = {}
        logger.info("Tool Registry initialized")
    
    def register_tool(self, tool_name: str, tool_interface: PDFToolInterface):
        """Register a tool interface."""
        self.tools[tool_name] = tool_interface
        logger.info(f"Registered tool interface: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[PDFToolInterface]:
        """Get a tool interface by name."""
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, PDFToolInterface]:
        """Get all registered tools."""
        return self.tools.copy()
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")


# Global registry instance
_tool_registry_instance: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _tool_registry_instance
    if _tool_registry_instance is None:
        _tool_registry_instance = ToolRegistry()
    return _tool_registry_instance


# Convenience functions
def register_tool(tool_name: str, operation_function: Callable,
                 required_params: Dict[str, Any] = None,
                 optional_params: Dict[str, Any] = None) -> StandardPDFTool:
    """Register a standard PDF tool."""
    tool = StandardPDFTool(tool_name, operation_function)
    tool.set_parameters(required_params, optional_params)
    get_tool_registry().register_tool(tool_name, tool)
    return tool


def get_tool_interface(tool_name: str) -> Optional[PDFToolInterface]:
    """Get a tool interface by name."""
    return get_tool_registry().get_tool(tool_name)


if __name__ == '__main__':
    # Test the unified interfaces
    import time
    
    # Test file selector (would need GUI)
    print("Testing unified interfaces...")
    
    # Test parameter validator
    assert ParameterValidator.validate_page_range("1-5", 10) == True
    assert ParameterValidator.validate_page_range("1-15", 10) == False
    assert ParameterValidator.validate_compression_level(50) == True
    assert ParameterValidator.validate_compression_level(150) == False
    
    # Test tool registration
    def dummy_operation(input_file, output_file=None, **kwargs):
        """Dummy operation for testing."""
        time.sleep(0.1)  # Simulate processing
        return True
    
    tool = register_tool(
        "test_tool", 
        dummy_operation,
        required_params={'input_file': str},
        optional_params={'compression_level': int}
    )
    
    # Test file processing
    result = tool.process_file("test.pdf", "output.pdf", {'compression_level': 50})
    print(f"Test result: {result.success}, {result.message}")
    
    print("Unified interfaces test completed")