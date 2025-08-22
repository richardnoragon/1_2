"""CSV exporter for the Advanced File Catalog Generator.

This module exports catalog data as CSV with color metadata columns.
"""

import csv
from pathlib import Path
from typing import Dict, Any, List
from .base_exporter import BaseExporter


class CSVExporter(BaseExporter):
    """Export catalog as CSV with color metadata columns."""
    
    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})
        self.include_color_data = self.options.get('include_color_data', True)
        self.include_metadata = self.options.get('include_metadata', True)
        self.delimiter = self.options.get('delimiter', ',')
    
    def get_file_extension(self) -> str:
        """Return the file extension for CSV format."""
        return "csv"
    
    def validate_options(self) -> bool:
        """Validate CSV export options."""
        valid_delimiters = [',', ';', '\t', '|']
        return self.delimiter in valid_delimiters
    
    def export(self, catalog_data, output_path: Path) -> bool:
        """Generate CSV with color metadata columns."""
        try:
            if not self._validate_output_path(output_path):
                return False
            
            self._report_progress(10, "Preparing CSV data...")
            fieldnames = self._get_fieldnames()
            
            self._report_progress(30, "Writing CSV file...")
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, 
                                      delimiter=self.delimiter)
                
                writer.writeheader()
                
                total_entries = len(catalog_data.entries)
                for i, entry in enumerate(catalog_data.entries):
                    row_data = self._create_row_data(entry)
                    writer.writerow(row_data)
                    
                    if i % 100 == 0:  # Update progress every 100 entries
                        progress = 30 + (i / total_entries) * 60
                        self._report_progress(int(progress), 
                                            f"Processing entry {i+1}/{total_entries}")
            
            self._report_progress(100, "CSV export completed")
            return True
            
        except Exception as e:
            print(f"CSV export failed: {e}")
            return False
    
    def _get_fieldnames(self) -> List[str]:
        """Get CSV column headers."""
        fields = [
            'name', 'path', 'size', 'size_formatted', 'type', 'extension',
            'created_date', 'modified_date', 'accessed_date'
        ]
        
        if self.include_color_data:
            fields.extend([
                'color_hex', 'color_rgb', 'color_category', 'pattern_type',
                'accessibility_icon', 'accessibility_label'
            ])
        
        if self.include_metadata:
            fields.extend(['metadata_json'])
        
        return fields
    
    def _create_row_data(self, entry) -> Dict[str, str]:
        """Create CSV row data for a file entry."""
        row = {
            'name': entry.name,
            'path': str(entry.path),
            'size': str(entry.size),
            'size_formatted': entry.format_size(),
            'type': entry.file_type.value,
            'extension': entry.extension,
            'created_date': entry.created_date.isoformat(),
            'modified_date': entry.modified_date.isoformat(),
            'accessed_date': entry.accessed_date.isoformat()
        }
        
        if self.include_color_data and entry.color_category:
            row.update({
                'color_hex': entry.color_category.color_hex,
                'color_rgb': f"rgb{entry.color_category.color_rgb}",
                'color_category': entry.color_category.category_name,
                'pattern_type': entry.color_category.pattern_type,
                'accessibility_icon': entry.color_category.icon,
                'accessibility_label': entry.color_category.accessibility_label
            })
        elif self.include_color_data:
            # Fill with empty values if no color data
            row.update({
                'color_hex': '',
                'color_rgb': '',
                'color_category': '',
                'pattern_type': '',
                'accessibility_icon': '',
                'accessibility_label': ''
            })
        
        if self.include_metadata:
            import json
            row['metadata_json'] = json.dumps(entry.metadata)
        
        return row