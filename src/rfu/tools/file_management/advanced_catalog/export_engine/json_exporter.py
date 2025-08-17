"""JSON exporter for the Advanced File Catalog Generator.

This module exports catalog data as JSON with structured data and color information.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .base_exporter import BaseExporter


class JSONExporter(BaseExporter):
    """Export catalog as JSON with structured data and color information."""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options or {})
        self.pretty_print = self.options.get('pretty_print', True)
        self.include_schema = self.options.get('include_schema', True)
    
    def get_file_extension(self) -> str:
        """Return the file extension for JSON format."""
        return "json"
    
    def validate_options(self) -> bool:
        """Validate JSON export options."""
        return True  # JSON options are all boolean, so always valid
    
    def export(self, catalog_data, output_path: Path) -> bool:
        """Generate JSON with structured data and color information."""
        try:
            if not self._validate_output_path(output_path):
                return False
            
            self._report_progress(10, "Creating JSON structure...")
            catalog_json = self._create_catalog_json(catalog_data)
            
            self._report_progress(80, "Writing JSON file...")
            with open(output_path, 'w', encoding='utf-8') as f:
                if self.pretty_print:
                    json.dump(catalog_json, f, indent=2, ensure_ascii=False, 
                             default=self._json_serializer)
                else:
                    json.dump(catalog_json, f, ensure_ascii=False, 
                             default=self._json_serializer)
            
            self._report_progress(100, "JSON export completed")
            return True
            
        except Exception as e:
            print(f"JSON export failed: {e}")
            return False
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime and other objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def _create_catalog_json(self, catalog_data) -> Dict:
        """Create complete JSON structure."""
        catalog_json = {
            "catalog_info": {
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "source_directory": str(catalog_data.source_directory) 
                                  if catalog_data.source_directory else None,
                "total_files": len(catalog_data.entries),
                "sort_criteria": catalog_data.sort_criteria.value,
                "color_scheme": catalog_data.color_scheme.value
            },
            "statistics": self._create_statistics_json(catalog_data.statistics),
            "color_legend": self._create_legend_json(catalog_data.color_legend),
            "files": [self._create_file_json(entry) for entry in catalog_data.entries]
        }
        
        if self.include_schema:
            catalog_json["$schema"] = "https://schemas.example.com/file-catalog/v1.0.json"
        
        return catalog_json
    
    def _create_statistics_json(self, statistics) -> Dict:
        """Create JSON representation of catalog statistics."""
        return {
            "total_files": statistics.total_files,
            "total_size": statistics.total_size,
            "total_size_formatted": self._format_size(statistics.total_size),
            "file_type_counts": {
                ft.value: count for ft, count in statistics.file_type_counts.items()
            },
            "size_distribution": {
                sc.value: count for sc, count in statistics.size_distribution.items()
            },
            "date_distribution": {
                dc.value: count for dc, count in statistics.date_distribution.items()
            },
            "largest_file": {
                "name": statistics.largest_file.name,
                "size": statistics.largest_file.size,
                "path": str(statistics.largest_file.path)
            } if statistics.largest_file else None,
            "smallest_file": {
                "name": statistics.smallest_file.name,
                "size": statistics.smallest_file.size,
                "path": str(statistics.smallest_file.path)
            } if statistics.smallest_file else None,
            "newest_file": {
                "name": statistics.newest_file.name,
                "modified_date": statistics.newest_file.modified_date.isoformat(),
                "path": str(statistics.newest_file.path)
            } if statistics.newest_file else None,
            "oldest_file": {
                "name": statistics.oldest_file.name,
                "modified_date": statistics.oldest_file.modified_date.isoformat(),
                "path": str(statistics.oldest_file.path)
            } if statistics.oldest_file else None
        }
    
    def _create_legend_json(self, color_legend) -> Dict:
        """Create JSON representation of color legend."""
        if not color_legend:
            return {}
        
        legend_json = {}
        for category, items in color_legend.items():
            legend_json[category] = [
                {
                    "color_hex": item.color_hex,
                    "color_rgb": item.color_rgb,
                    "pattern_type": item.pattern_type,
                    "icon": item.icon,
                    "accessibility_label": item.accessibility_label,
                    "category_name": item.category_name
                }
                for item in items
            ]
        
        return legend_json
    
    def _create_file_json(self, entry) -> Dict:
        """Create JSON representation of a file entry."""
        file_json = {
            "name": entry.name,
            "path": str(entry.path),
            "size": {
                "bytes": entry.size,
                "formatted": entry.format_size(),
                "category": entry.get_size_category().value
            },
            "type": {
                "category": entry.file_type.value,
                "extension": entry.extension,
                "mime_type": entry.metadata.get('mime_type')
            },
            "dates": {
                "created": entry.created_date.isoformat(),
                "modified": entry.modified_date.isoformat(),
                "accessed": entry.accessed_date.isoformat(),
                "age_category": entry.get_date_category().value
            },
            "alphabetical_category": entry.get_alphabetical_category().value,
            "color_coding": self._create_color_json(entry.color_category) 
                           if entry.color_category else None,
            "sort_key": entry.sort_key,
            "metadata": entry.metadata
        }
        
        return file_json
    
    def _create_color_json(self, color_category) -> Dict:
        """Create JSON representation of color information."""
        return {
            "color_hex": color_category.color_hex,
            "color_rgb": color_category.color_rgb,
            "category_name": color_category.category_name,
            "pattern_type": color_category.pattern_type,
            "accessibility": {
                "icon": color_category.icon,
                "label": color_category.accessibility_label
            }
        }