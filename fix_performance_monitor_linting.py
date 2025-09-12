"""Fix linting issues in performance_monitor.py"""

import os
import re


def fix_performance_monitor_linting():
    """Fix all linting issues in performance_monitor.py"""
    
    file_path = r"c:\Users\HP1\1_2\src\rfu\advanced_folders\core\performance_monitor.py"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove unused import
    content = content.replace('from pathlib import Path\n', '')
    
    # Fix trailing whitespace
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove trailing whitespace
        fixed_line = line.rstrip()
        
        # Fix long lines by breaking them appropriately
        if len(fixed_line) > 79:
            # Handle specific long lines
            if 'self.alert_thresholds = alert_thresholds or self._get_default_thresholds()' in fixed_line:
                fixed_line = '        self.alert_thresholds = (alert_thresholds or '
                fixed_lines.append(fixed_line)
                fixed_lines.append('                                 self._get_default_thresholds())')
                continue
            elif 'Collects metrics, monitors system resources, generates alerts,' in fixed_line:
                fixed_line = '    Collects metrics, monitors system resources, generates'
                fixed_lines.append(fixed_line)
                fixed_lines.append('    alerts, and provides optimization recommendations.')
                continue
            elif 'def __init__(' in fixed_line and 'monitoring_interval_seconds:' in fixed_line:
                # Split long function definition
                indent = ' ' * 8
                fixed_line = '    def __init__('
                fixed_lines.append(fixed_line)
                fixed_lines.append(f'{indent}self,')
                fixed_lines.append(f'{indent}db_path: Optional[str] = None,')
                fixed_lines.append(f'{indent}max_memory_metrics: int = 10000,')
                fixed_lines.append(f'{indent}alert_thresholds: Optional[Dict[str, float]] = None,')
                fixed_lines.append(f'{indent}enable_system_monitoring: bool = True,')
                fixed_lines.append(f'{indent}monitoring_interval_seconds: float = 5.0')
                fixed_lines.append('    ):')
                continue
            elif len(fixed_line) > 79 and 'Initialize performance monitor.' in fixed_line:
                fixed_line = '        """'
                fixed_lines.append(fixed_line)
                fixed_lines.append('        Initialize performance monitor.')
                continue
            elif len(fixed_line) > 79 and '# Threading' in fixed_line:
                # Handle comment lines
                fixed_line = fixed_line
            elif len(fixed_line) > 79 and 'self.metrics_by_type: Dict[PerformanceMetricType, deque]' in fixed_line:
                # Split long type annotation
                fixed_line = '        self.metrics_by_type: Dict['
                fixed_lines.append(fixed_line)
                fixed_lines.append('            PerformanceMetricType, deque')
                fixed_lines.append('        ] = defaultdict(lambda: deque(maxlen=1000))')
                continue
            elif len(fixed_line) > 79 and '"Average operation duration is' in fixed_line:
                # Split long string
                fixed_line = '                description=('
                fixed_lines.append(fixed_line)
                fixed_lines.append('                    f"Average operation duration is {summary.average_duration_ms:.1f}ms, "')
                fixed_lines.append('                    "which may impact user experience."')
                fixed_lines.append('                ),')
                continue
        
        fixed_lines.append(fixed_line)
    
    # Join lines back together
    fixed_content = '\n'.join(fixed_lines)
    
    # Additional fixes for common issues
    
    # Fix docstring formatting
    fixed_content = re.sub(
        r'(\s+"""[\w\s\.,]+)(\n\s+)(Args:)',
        r'\1\n\2\3',
        fixed_content
    )
    
    # Ensure proper spacing around operators
    fixed_content = re.sub(r'(\w)=(\w)', r'\1 = \2', fixed_content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Performance monitor linting fixes applied")

if __name__ == "__main__":
    fix_performance_monitor_linting()