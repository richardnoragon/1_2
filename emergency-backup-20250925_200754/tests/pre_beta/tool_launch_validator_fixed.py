"""
Tool Launch Validation Framework

Comprehensive validation system for ensuring reliable tool launching
from the multi-pane file explorer with proper error handling and diagnostics.
"""

import inspect
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type


class ToolLaunchValidator:
    """Validates tool launch requirements and environment."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger('ToolLaunchValidator')
        self.validation_cache = {}
    
    def validate_tool_launch(self, tool_class: Type, tool_name: str, 
                           parent_widget: Any = None) -> Dict[str, Any]:
        """
        Comprehensive validation of tool launch requirements.
        
        Returns:
            Dict with validation results and recommended parameters
        """
        validation_result = {
            'valid': False,
            'constructor_info': {},
            'recommended_params': {},
            'errors': [],
            'warnings': [],
            'creation_strategy': None
        }
        
        try:
            # Validate tool class
            class_validation = self._validate_tool_class(tool_class, tool_name)
            validation_result.update(class_validation)
            
            if not class_validation['valid']:
                return validation_result
            
            # Analyze constructor requirements
            constructor_info = self._analyze_constructor(tool_class, tool_name)
            validation_result['constructor_info'] = constructor_info
            
            # Determine best creation strategy
            strategy = self._determine_creation_strategy(
                constructor_info, tool_name, parent_widget
            )
            validation_result['creation_strategy'] = strategy
            validation_result['recommended_params'] = strategy['params']
            
            # Final validation
            if strategy['strategy_id'] > 0:
                validation_result['valid'] = True
            
            return validation_result
            
        except Exception as e:
            validation_result['errors'].append(f"Validation failed: {e}")
            self.logger.error(f"Tool validation failed for {tool_name}: {e}")
            return validation_result
    
    def _validate_tool_class(self, tool_class: Type, tool_name: str) -> Dict[str, Any]:
        """Validate the tool class itself."""
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'tool_name': tool_name
        }
        
        try:
            # Check if it's actually a class
            if not isinstance(tool_class, type):
                result['errors'].append("Not a valid class type")
                return result
            
            # Check if it has a constructor
            if not hasattr(tool_class, '__init__'):
                result['errors'].append("No __init__ method found")
                return result
            
            # Check if it's likely a GUI class
            class_name = tool_class.__name__
            gui_indicators = ['GUI', 'Window', 'App', 'Dialog', 'Widget']
            
            has_gui_indicator = any(
                indicator in class_name for indicator in gui_indicators
            )
            if not has_gui_indicator:
                result['warnings'].append(
                    "Class name doesn't suggest GUI component"
                )
            
            # Check inheritance (basic)
            try:
                mro = tool_class.__mro__
                has_qwidget = any(
                    'QWidget' in str(base) or 'QMainWindow' in str(base)
                    for base in mro
                )
                if not has_qwidget:
                    result['warnings'].append(
                        "Class doesn't inherit from Qt widgets"
                    )
            except Exception:
                result['warnings'].append("Could not check inheritance chain")
            
            result['valid'] = True
            return result
            
        except Exception as e:
            result['errors'].append(f"Class validation error: {e}")
            return result
    
    def _analyze_constructor(
        self, tool_class: Type, tool_name: str
    ) -> Dict[str, Any]:
        """Analyze constructor signature and requirements."""
        constructor_info = {
            'parameters': [],
            'accepts_parent': False,
            'accepts_title': False,
            'accepts_window_type': False,
            'required_params': [],
            'optional_params': [],
            'signature_str': ''
        }
        
        try:
            sig = inspect.signature(tool_class.__init__)
            constructor_info['signature_str'] = str(sig)
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                param_info = {
                    'name': param_name,
                    'default': param.default,
                    'has_default': param.default != inspect.Parameter.empty,
                    'annotation': param.annotation
                }
                
                constructor_info['parameters'].append(param_info)
                
                # Check for specific parameters we care about
                if param_name == 'parent':
                    constructor_info['accepts_parent'] = True
                elif param_name == 'title':
                    constructor_info['accepts_title'] = True
                elif param_name == 'window_type':
                    constructor_info['accepts_window_type'] = True
                
                # Categorize as required or optional
                if param.default == inspect.Parameter.empty:
                    constructor_info['required_params'].append(param_name)
                else:
                    constructor_info['optional_params'].append(param_name)
            
            return constructor_info
            
        except Exception as e:
            self.logger.warning(
                f"Could not analyze constructor for {tool_name}: {e}"
            )
            return constructor_info
    
    def _determine_creation_strategy(
        self, constructor_info: Dict[str, Any],
        tool_name: str, parent_widget: Any
    ) -> Dict[str, Any]:
        """Determine the best strategy for creating the tool instance."""
        strategies = self._get_creation_strategies(tool_name, parent_widget)
        
        for strategy in strategies:
            if self._is_strategy_valid(strategy, constructor_info):
                strategy['params'] = self._filter_strategy_params(
                    strategy, constructor_info
                )
                return strategy
        
        # Fallback - return the default strategy
        return strategies[-1]

    def _get_creation_strategies(self, tool_name: str, parent_widget: Any):
        """Get available creation strategies."""
        return [
            {
                'strategy_id': 1,
                'name': 'parent_only',
                'description': 'Create with parent parameter',
                'params': {'parent': parent_widget},
                'requirements': ['accepts_parent']
            },
            {
                'strategy_id': 2,
                'name': 'full_params',
                'description': 'Create with all supported parameters',
                'params': {
                    'parent': parent_widget,
                    'title': f"{tool_name} - RFU Explorer",
                    'window_type': 'utility'
                },
                'requirements': ['accepts_parent']
            },
            {
                'strategy_id': 3,
                'name': 'title_only',
                'description': 'Create with title parameter',
                'params': {'title': f"{tool_name} - RFU Explorer"},
                'requirements': ['accepts_title']
            },
            {
                'strategy_id': 4,
                'name': 'window_type_only',
                'description': 'Create with window_type parameter',
                'params': {'window_type': 'utility'},
                'requirements': ['accepts_window_type']
            },
            {
                'strategy_id': 5,
                'name': 'default',
                'description': 'Create with no parameters',
                'params': {},
                'requirements': []
            }
        ]

    def _is_strategy_valid(self, strategy: Dict, constructor_info: Dict):
        """Check if a creation strategy is valid for the constructor."""
        # Check if all requirements are met
        for requirement in strategy['requirements']:
            if not constructor_info.get(requirement, False):
                return False
        
        # Check if any required parameters would be missing
        required_params = constructor_info.get('required_params', [])
        provided_params = set(strategy['params'].keys())
        missing_required = set(required_params) - provided_params
        
        return not missing_required

    def _filter_strategy_params(self, strategy: Dict, constructor_info: Dict):
        """Filter strategy parameters to only include accepted ones."""
        filtered_params = {}
        parameters = constructor_info.get('parameters', [])
        
        for param_name, param_value in strategy['params'].items():
            param_exists = any(
                p['name'] == param_name for p in parameters
            )
            if param_exists:
                filtered_params[param_name] = param_value
        
        return filtered_params
    
    def create_validated_instance(
        self, tool_class: Type, tool_name: str,
        parent_widget: Any = None
    ) -> Any:
        """Create tool instance using validated parameters."""
        try:
            validation = self.validate_tool_launch(
                tool_class, tool_name, parent_widget
            )
            
            if not validation['valid']:
                self.logger.error(
                    f"Tool validation failed for {tool_name}: "
                    f"{validation['errors']}"
                )
                return None
            
            strategy = validation['creation_strategy']
            params = strategy['params']
            
            self.logger.info(
                f"Creating {tool_name} with strategy: {strategy['name']}"
            )
            self.logger.debug(f"Parameters: {params}")
            
            # Create the instance
            tool_instance = tool_class(**params)
            
            # Post-creation configuration
            self._configure_instance(tool_instance, tool_name, parent_widget)
            
            return tool_instance
            
        except Exception as e:
            self.logger.error(
                f"Failed to create validated instance for {tool_name}: {e}"
            )
            return None
    
    def _configure_instance(
        self, tool_instance: Any, tool_name: str,
        parent_widget: Any = None
    ):
        """Configure tool instance after creation."""
        try:
            # Set parent if not already set and parent is available
            if (parent_widget and
                    hasattr(tool_instance, 'setParent') and
                    tool_instance.parent() != parent_widget):
                try:
                    tool_instance.setParent(parent_widget)
                    self.logger.debug(f"Set parent for {tool_name}")
                except Exception as e:
                    self.logger.warning(
                        f"Could not set parent for {tool_name}: {e}"
                    )
            
            # Ensure proper window title
            if hasattr(tool_instance, 'setWindowTitle'):
                current_title = getattr(
                    tool_instance, 'windowTitle', lambda: ""
                )()
                if not current_title:
                    tool_instance.setWindowTitle(f"{tool_name} - RFU Explorer")
            
            # Set window flags for proper behavior
            if hasattr(tool_instance, 'setWindowFlags'):
                # Ensure window is properly independent
                from PyQt5.QtCore import Qt
                tool_instance.setWindowFlags(
                    tool_instance.windowFlags() | Qt.Window
                )
            
            # Set focus policy
            if hasattr(tool_instance, 'setFocusPolicy'):
                from PyQt5.QtCore import Qt
                tool_instance.setFocusPolicy(Qt.StrongFocus)
            
        except Exception as e:
            self.logger.warning(
                f"Instance configuration failed for {tool_name}: {e}"
            )


# Global validator instance
_validator = None


def get_tool_validator() -> ToolLaunchValidator:
    """Get the global tool launch validator."""
    global _validator
    if _validator is None:
        _validator = ToolLaunchValidator()
    return _validator 
 