"""
PDF Tool Discovery System
Automatically discovers and registers PDF utility tools from the
pdf_utilities directory.
"""

import os
import sys
import inspect
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from log_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for a discovered PDF tool."""
    name: str
    module_name: str
    class_name: str
    category: str
    description: str
    file_path: str
    ui_file: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    supports_batch: bool = False
    has_preview: bool = False
    input_formats: List[str] = field(default_factory=lambda: ['pdf'])
    output_formats: List[str] = field(default_factory=list)


class PDFToolDiscovery:
    """
    Discovers and manages PDF utility tools.
    
    This class automatically scans the pdf_utilities directory to find
    available PDF tools, extracts their metadata, and categorizes them
    for the enhanced PDF hub interface.
    """
    
    def __init__(self, utilities_dir: Optional[str] = None):
        """
        Initialize the tool discovery system.
        
        Args:
            utilities_dir: Path to the PDF utilities directory
        """
        if utilities_dir is None:
            utilities_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.utilities_dir = Path(utilities_dir)
        self.discovered_tools: Dict[str, ToolMetadata] = {}
        self.categories = {
            'basic_operations': {
                'name': 'Basic Operations',
                'description': 'Core PDF manipulation tools',
                'tools': []
            },
            'content_extraction': {
                'name': 'Content Extraction',
                'description': 'Extract content from PDF documents',
                'tools': []
            },
            'security': {
                'name': 'Security & Encryption',
                'description': 'PDF security and encryption tools',
                'tools': []
            },
            'conversion': {
                'name': 'Document Conversion',
                'description': 'Convert PDFs to/from other formats',
                'tools': []
            },
            'enhancement': {
                'name': 'Enhancement Tools',
                'description': 'Enhance and modify PDF documents',
                'tools': []
            },
            'analysis': {
                'name': 'Analysis & Viewing',
                'description': 'Analyze and view PDF documents',
                'tools': []
            },
            'administration': {
                'name': 'Administration',
                'description': 'System administration and settings',
                'tools': []
            }
        }
        
        # Tool categorization mapping
        self.tool_category_mapping = {
            'split': 'basic_operations',
            'merg': 'basic_operations',
            'merge': 'basic_operations',
            'page_administration': 'basic_operations',
            'compress': 'basic_operations',
            'extract_text': 'content_extraction',
            'extract_image': 'content_extraction',
            'extract_tables': 'content_extraction',
            'extract_links': 'content_extraction',
            'extract_metadata': 'content_extraction',
            'miner': 'content_extraction',
            'encrypt': 'security',
            'decrypt': 'security',
            'sign': 'security',
            'convert_to_docx': 'conversion',
            'convert_to_image': 'conversion',
            'convert_html_to_pdf': 'conversion',
            'watermark': 'enhancement',
            'ocr': 'enhancement',
            'highlight': 'enhancement',
            'view': 'analysis',
            'viewer': 'analysis',
            'settings_manager': 'administration',
            'log_manager': 'administration'
        }
        
        logger.info(
            f"Initialized PDF Tool Discovery for directory: "
            f"{self.utilities_dir}"
        )
    
    def discover_tools(self) -> Dict[str, ToolMetadata]:
        """
        Discover all available PDF tools in the utilities directory.
        
        Returns:
            Dictionary of discovered tools with their metadata
        """
        logger.info("Starting PDF tool discovery...")
        
        try:
            # Clear previous discoveries
            self.discovered_tools.clear()
            for category in self.categories.values():
                category['tools'].clear()
            
            # Scan for Python files
            python_files = list(self.utilities_dir.glob("*.py"))
            logger.debug(f"Found {len(python_files)} Python files to analyze")
            
            for py_file in python_files:
                skip_files = ['main.py', 'config_manager.py', 'log_config.py']
                if py_file.name.startswith('__') or py_file.name in skip_files:
                    continue
                
                try:
                    tool_metadata = self._analyze_tool_file(py_file)
                    if tool_metadata:
                        self.discovered_tools[tool_metadata.name] = (
                            tool_metadata
                        )
                        self._categorize_tool(tool_metadata)
                        logger.debug(f"Discovered tool: {tool_metadata.name}")
                
                except Exception as e:
                    logger.warning(f"Failed to analyze {py_file.name}: {e}")
                    continue
            
            logger.info(
                f"Discovery complete. Found {len(self.discovered_tools)} tools"
            )
            self._log_discovery_summary()
            
            return self.discovered_tools
            
        except Exception as e:
            logger.error(f"Error during tool discovery: {e}", exc_info=True)
            return {}
    
    def _analyze_tool_file(self, py_file: Path) -> Optional[ToolMetadata]:
        """
        Analyze a Python file to extract tool metadata.
        
        Args:
            py_file: Path to the Python file
            
        Returns:
            ToolMetadata if a valid tool is found, None otherwise
        """
        try:
            module_name = py_file.stem
            
            # Read the file to extract information
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to import the module
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules temporarily for import
            sys.modules[module_name] = module
            
            try:
                spec.loader.exec_module(module)
            except Exception as e:
                logger.debug(f"Could not execute module {module_name}: {e}")
                return None
            finally:
                # Clean up sys.modules
                if module_name in sys.modules:
                    del sys.modules[module_name]
            
            # Find UI classes
            ui_classes = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (name.endswith('UI') or name.endswith('Window') or 
                    (hasattr(obj, '__bases__') and 
                     any(base.__name__ == 'QMainWindow'
                         for base in obj.__bases__))):
                    ui_classes.append((name, obj))
            
            if not ui_classes:
                return None
            
            # Use the first UI class found
            class_name, ui_class = ui_classes[0]
            
            # Extract metadata
            description = self._extract_description(content, ui_class)
            category = self._determine_category(module_name)
            ui_file = self._find_ui_file(py_file)
            
            # Extract additional metadata from docstrings and code
            supports_batch = self._check_batch_support(content)
            has_preview = self._check_preview_support(content)
            input_formats, output_formats = self._extract_formats(content)
            dependencies = self._extract_dependencies(content)
            parameters = self._extract_parameters(content, ui_class)
            
            tool_metadata = ToolMetadata(
                name=self._format_tool_name(module_name),
                module_name=module_name,
                class_name=class_name,
                category=category,
                description=description,
                file_path=str(py_file),
                ui_file=ui_file,
                dependencies=dependencies,
                parameters=parameters,
                supports_batch=supports_batch,
                has_preview=has_preview,
                input_formats=input_formats,
                output_formats=output_formats
            )
            
            return tool_metadata
            
        except Exception as e:
            logger.debug(f"Error analyzing {py_file.name}: {e}")
            return None
    
    def _extract_description(self, content: str, ui_class) -> str:
        """Extract description from module docstring or class docstring."""
        # Try class docstring first
        if hasattr(ui_class, '__doc__') and ui_class.__doc__:
            return ui_class.__doc__.strip().split('\n')[0]
        
        # Try module docstring
        lines = content.split('\n')
        in_docstring = False
        docstring_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('"""') or line.startswith("'''"):
                if in_docstring:
                    break
                in_docstring = True
                # Handle single-line docstring
                if line.count('"""') == 2 or line.count("'''") == 2:
                    return line.strip('"""').strip("'''").strip()
                continue
            elif in_docstring:
                if line and not line.startswith('#'):
                    docstring_lines.append(line)
        
        if docstring_lines:
            return docstring_lines[0]
        
        return f"PDF {self._format_tool_name(ui_class.__name__)} Tool"
    
    def _determine_category(self, module_name: str) -> str:
        """Determine the category for a tool based on its module name."""
        module_lower = module_name.lower()
        
        for keyword, category in self.tool_category_mapping.items():
            if keyword in module_lower:
                return category
        
        return 'basic_operations'  # Default category
    
    def _find_ui_file(self, py_file: Path) -> Optional[str]:
        """Find the corresponding UI file for a Python tool."""
        ui_file = py_file.with_suffix('.ui')
        if ui_file.exists():
            return str(ui_file)
        return None
    
    def _check_batch_support(self, content: str) -> bool:
        """Check if the tool supports batch processing."""
        batch_indicators = [
            'batch', 'multiple', 'files', 'list', 'queue',
            'for file in', 'for pdf in', 'process_files'
        ]
        content_lower = content.lower()
        return any(
            indicator in content_lower for indicator in batch_indicators
        )
    
    def _check_preview_support(self, content: str) -> bool:
        """Check if the tool supports preview functionality."""
        preview_indicators = [
            'preview', 'view', 'display', 'show', 'render'
        ]
        content_lower = content.lower()
        return any(
            indicator in content_lower for indicator in preview_indicators
        )
    
    def _extract_formats(self, content: str) -> Tuple[List[str], List[str]]:
        """Extract supported input and output formats."""
        input_formats = ['pdf']  # All tools support PDF input
        output_formats = []
        
        format_patterns = {
            'pdf': ['pdf'],
            'docx': ['docx', 'doc'],
            'txt': ['txt', 'text'],
            'csv': ['csv'],
            'json': ['json'],
            'xml': ['xml'],
            'html': ['html', 'htm'],
            'png': ['png'],
            'jpg': ['jpg', 'jpeg'],
            'bmp': ['bmp'],
            'tiff': ['tiff', 'tif']
        }
        
        content_lower = content.lower()
        for format_name, patterns in format_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                if format_name not in input_formats:
                    output_formats.append(format_name)
        
        return input_formats, output_formats
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from import statements."""
        dependencies = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # Extract package names
                if 'import ' in line:
                    parts = line.split('import ')
                    if len(parts) > 1:
                        package = parts[1].split()[0].split('.')[0]
                        if package not in ['os', 'sys', 'pathlib', 'typing']:
                            dependencies.append(package)
        
        return list(set(dependencies))
    
    def _extract_parameters(self, content: str, ui_class) -> Dict[str, Any]:
        """Extract tool parameters from the UI class and content."""
        parameters = {}
        
        # Look for common parameter patterns
        if 'compression' in content.lower():
            parameters['compression_level'] = {
                'type': 'int', 'default': 50, 'range': [0, 100]
            }
        
        if 'quality' in content.lower():
            parameters['quality'] = {
                'type': 'int', 'default': 80, 'range': [1, 100]
            }
        
        if 'password' in content.lower():
            parameters['password'] = {'type': 'str', 'secure': True}
        
        if 'page' in content.lower():
            parameters['page_range'] = {
                'type': 'str', 'pattern': r'\d+(-\d+)?'
            }
        
        return parameters
    
    def _format_tool_name(self, name: str) -> str:
        """Format tool name for display."""
        # Remove common suffixes
        name = name.replace('UI', '').replace('Window', '').replace('_', ' ')
        
        # Handle special cases
        name_mapping = {
            'merg': 'Merge PDFs',
            'split': 'Split PDF',
            'extract text': 'Extract Text',
            'extract image cli': 'Extract Images',
            'extract tables camelot': 'Extract Tables',
            'extract links': 'Extract Links',
            'extract metadata': 'Extract Metadata',
            'convert to docx': 'Convert to DOCX',
            'convert to image': 'Convert to Images',
            'convert html to pdf': 'HTML to PDF',
            'page administration': 'Page Administration',
            'settings manager': 'Settings Manager',
            'log manager': 'Log Manager'
        }
        
        name_lower = name.lower().strip()
        if name_lower in name_mapping:
            return name_mapping[name_lower]
        
        # Default formatting
        return ' '.join(word.capitalize() for word in name.split())
    
    def _categorize_tool(self, tool_metadata: ToolMetadata):
        """Add tool to its appropriate category."""
        category = tool_metadata.category
        if category in self.categories:
            self.categories[category]['tools'].append(tool_metadata.name)
    
    def _log_discovery_summary(self):
        """Log a summary of discovered tools by category."""
        logger.info("Tool Discovery Summary:")
        for category_id, category_info in self.categories.items():
            tool_count = len(category_info['tools'])
            if tool_count > 0:
                logger.info(f"  {category_info['name']}: {tool_count} tools")
                for tool_name in category_info['tools']:
                    logger.debug(f"    - {tool_name}")
    
    def get_tools_by_category(self, category: str) -> List[ToolMetadata]:
        """Get all tools in a specific category."""
        if category not in self.categories:
            return []
        
        tool_names = self.categories[category]['tools']
        return [
            self.discovered_tools[name] for name in tool_names
            if name in self.discovered_tools
        ]
    
    def get_tool_by_name(self, name: str) -> Optional[ToolMetadata]:
        """Get tool metadata by name."""
        return self.discovered_tools.get(name)
    
    def get_all_categories(self) -> Dict[str, Dict]:
        """Get all categories with their information."""
        return self.categories
    
    def refresh_discovery(self) -> Dict[str, ToolMetadata]:
        """Refresh the tool discovery process."""
        logger.info("Refreshing tool discovery...")
        return self.discover_tools()


# Global instance for singleton pattern
_tool_discovery_instance: Optional[PDFToolDiscovery] = None


def get_tool_discovery() -> PDFToolDiscovery:
    """Get a singleton instance of the PDF tool discovery system."""
    global _tool_discovery_instance
    if _tool_discovery_instance is None:
        _tool_discovery_instance = PDFToolDiscovery()
    return _tool_discovery_instance


if __name__ == '__main__':
    # Test the discovery system
    discovery = PDFToolDiscovery()
    tools = discovery.discover_tools()
    
    print(f"Discovered {len(tools)} PDF tools:")
    for category_id, category_info in discovery.get_all_categories().items():
        if category_info['tools']:
            print(f"\n{category_info['name']}:")
            for tool_name in category_info['tools']:
                tool = discovery.get_tool_by_name(tool_name)
                if tool:
                    print(f"  - {tool.name}: {tool.description}")