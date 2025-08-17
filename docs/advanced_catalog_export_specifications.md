# Advanced File Catalog Generator - Export Format Specifications

## Export Engine Architecture

### Base Exporter Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path

class BaseExporter(ABC):
    """Abstract base class for all export formats."""
    
    def __init__(self, options: Dict[str, Any] = None):
        self.options = options or {}
        self.color_preservation = True
        self.accessibility_mode = False
    
    @abstractmethod
    def export(self, catalog_data: 'CatalogData', output_path: Path) -> bool:
        """Export catalog data to specified format."""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension for this format."""
        pass
    
    @abstractmethod
    def validate_options(self) -> bool:
        """Validate export options."""
        pass
    
    def set_accessibility_mode(self, enabled: bool) -> None:
        """Enable/disable accessibility features."""
        self.accessibility_mode = enabled
```

## HTML Export Specification

### HTML Exporter Class
```python
class HTMLExporter(BaseExporter):
    """Export catalog as HTML with embedded CSS and color preservation."""
    
    def __init__(self, options: HTMLExportOptions = None):
        super().__init__(options)
        self.include_css = options.include_css if options else True
        self.responsive_design = options.responsive_design if options else True
        self.print_styles = options.print_styles if options else True
        self.interactive_features = options.interactive_features if options else False
    
    def export(self, catalog_data: CatalogData, output_path: Path) -> bool:
        """Generate HTML catalog with color-coding."""
        try:
            html_content = self._generate_html(catalog_data)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"HTML export failed: {e}")
            return False
    
    def _generate_html(self, catalog_data: CatalogData) -> str:
        """Generate complete HTML document."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Catalog - {catalog_data.source_directory}</title>
    {self._generate_css()}
    {self._generate_javascript() if self.interactive_features else ''}
</head>
<body>
    {self._generate_header(catalog_data)}
    {self._generate_legend(catalog_data.color_legend)}
    {self._generate_file_list(catalog_data.entries)}
    {self._generate_footer(catalog_data)}
</body>
</html>"""
```

### HTML CSS Template
```css
/* Advanced Catalog CSS Template */
:root {
    --primary-color: #2196F3;
    --secondary-color: #FFC107;
    --background-color: #FAFAFA;
    --text-color: #212121;
    --border-color: #E0E0E0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    background-color: var(--background-color);
    color: var(--text-color);
}

.catalog-header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.catalog-title {
    font-size: 2.5em;
    margin: 0;
    font-weight: 300;
}

.catalog-subtitle {
    font-size: 1.2em;
    margin: 10px 0 0 0;
    opacity: 0.9;
}

.legend-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.legend-section {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid var(--primary-color);
}

.legend-title {
    font-size: 1.3em;
    font-weight: 600;
    margin-bottom: 15px;
    color: var(--primary-color);
}

.legend-item {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    padding: 8px;
    border-radius: 4px;
    transition: background-color 0.2s;
}

.legend-item:hover {
    background-color: #F5F5F5;
}

.color-sample {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    margin-right: 12px;
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}

.legend-label {
    font-weight: 500;
    margin-right: 10px;
    min-width: 80px;
}

.legend-description {
    color: #666;
    font-size: 0.9em;
}

.file-list {
    display: grid;
    gap: 8px;
}

.file-entry {
    display: grid;
    grid-template-columns: auto 1fr auto auto auto;
    align-items: center;
    padding: 12px 16px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    background: white;
    transition: all 0.2s ease;
    gap: 12px;
}

.file-entry:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.file-icon {
    font-size: 1.5em;
    width: 32px;
    text-align: center;
}

.file-name {
    font-weight: 500;
    color: var(--text-color);
    text-decoration: none;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.file-name:hover {
    color: var(--primary-color);
    text-decoration: underline;
}

.file-size {
    font-family: 'Courier New', monospace;
    color: #666;
    font-size: 0.9em;
    min-width: 80px;
    text-align: right;
}

.file-date {
    color: #666;
    font-size: 0.9em;
    min-width: 120px;
    text-align: right;
}

.file-type {
    background: var(--primary-color);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 500;
    text-transform: uppercase;
    min-width: 60px;
    text-align: center;
}

/* Color-coding classes */
.size-small { background-color: #E8F5E8; }
.size-medium { background-color: #E3F2FD; }
.size-large { background-color: #FFF3E0; }

.type-document { border-left: 4px solid #2196F3; }
.type-image { border-left: 4px solid #4CAF50; }
.type-video { border-left: 4px solid #F44336; }
.type-audio { border-left: 4px solid #9C27B0; }
.type-archive { border-left: 4px solid #FF9800; }
.type-executable { border-left: 4px solid #607D8B; }
.type-other { border-left: 4px solid #E0E0E0; }

.date-recent { background: linear-gradient(90deg, #E8F5E8 0%, transparent 100%); }
.date-moderate { background: linear-gradient(90deg, #FFFDE7 0%, transparent 100%); }
.date-old { background: linear-gradient(90deg, #FFEBEE 0%, transparent 100%); }

/* Accessibility patterns */
.accessibility-mode .pattern-dots {
    background-image: radial-gradient(circle, #000 1px, transparent 1px);
    background-size: 8px 8px;
}

.accessibility-mode .pattern-diagonal {
    background-image: repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);
}

/* Responsive design */
@media (max-width: 768px) {
    .file-entry {
        grid-template-columns: auto 1fr;
        gap: 8px;
    }
    
    .file-size, .file-date, .file-type {
        grid-column: 2;
        text-align: left;
        font-size: 0.8em;
    }
    
    .legend-container {
        grid-template-columns: 1fr;
    }
}

/* Print styles */
@media print {
    body {
        background: white;
        color: black;
    }
    
    .catalog-header {
        background: none !important;
        color: black !important;
        box-shadow: none !important;
        border: 2px solid black;
    }
    
    .file-entry {
        break-inside: avoid;
        border: 1px solid #ccc;
        margin-bottom: 2px;
    }
    
    .legend-section {
        break-inside: avoid;
        border: 1px solid #ccc;
        box-shadow: none;
    }
}
```

## PDF Export Specification

### PDF Exporter Class
```python
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

class PDFExporter(BaseExporter):
    """Export catalog as PDF with color preservation using reportlab."""
    
    def __init__(self, options: PDFExportOptions = None):
        super().__init__(options)
        self.page_size = getattr(options, 'page_size', A4) if options else A4
        self.include_bookmarks = getattr(options, 'include_bookmarks', True) if options else True
        self.dpi = getattr(options, 'dpi', 150) if options else 150
    
    def export(self, catalog_data: CatalogData, output_path: Path) -> bool:
        """Generate PDF catalog with colors and formatting."""
        try:
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=self.page_size,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph(f"File Catalog: {catalog_data.source_directory}", title_style))
            story.append(Spacer(1, 12))
            
            # Add legend
            story.extend(self._create_legend_elements(catalog_data.color_legend, styles))
            story.append(Spacer(1, 20))
            
            # Add file table
            story.extend(self._create_file_table(catalog_data.entries))
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"PDF export failed: {e}")
            return False
    
    def _create_file_table(self, entries: List[FileEntry]) -> List:
        """Create formatted table of files with color coding."""
        data = [['Icon', 'Name', 'Size', 'Type', 'Modified']]  # Header
        
        for entry in entries:
            data.append([
                entry.icon or '📄',
                entry.name,
                self._format_size(entry.size),
                entry.file_type.value,
                entry.modified_date.strftime('%Y-%m-%d %H:%M')
            ])
        
        table = Table(data, colWidths=[0.5*inch, 3*inch, 0.8*inch, 0.8*inch, 1.2*inch])
        
        # Apply color-coding based on categories
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]
        
        # Add color coding for each row
        for i, entry in enumerate(entries, 1):
            bg_color = self._get_pdf_color(entry.color_category)
            if bg_color:
                table_style.append(('BACKGROUND', (0, i), (-1, i), bg_color))
        
        table.setStyle(TableStyle(table_style))
        return [table]
```

## CSV Export Specification

### CSV Exporter Class
```python
import csv
from typing import List, Dict

class CSVExporter(BaseExporter):
    """Export catalog as CSV with color metadata columns."""
    
    def __init__(self, options: CSVExportOptions = None):
        super().__init__(options)
        self.include_color_data = getattr(options, 'include_color_data', True) if options else True
        self.include_metadata = getattr(options, 'include_metadata', True) if options else True
        self.delimiter = getattr(options, 'delimiter', ',') if options else ','
    
    def export(self, catalog_data: CatalogData, output_path: Path) -> bool:
        """Generate CSV with color metadata columns."""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = self._get_fieldnames()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=self.delimiter)
                
                writer.writeheader()
                
                for entry in catalog_data.entries:
                    row_data = self._create_row_data(entry)
                    writer.writerow(row_data)
            
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
    
    def _create_row_data(self, entry: FileEntry) -> Dict[str, str]:
        """Create CSV row data for a file entry."""
        row = {
            'name': entry.name,
            'path': str(entry.path),
            'size': entry.size,
            'size_formatted': self._format_size(entry.size),
            'type': entry.file_type.value,
            'extension': entry.extension,
            'created_date': entry.created_date.isoformat(),
            'modified_date': entry.modified_date.isoformat(),
            'accessed_date': entry.accessed_date.isoformat()
        }
        
        if self.include_color_data and entry.color_category:
            row.update({
                'color_hex': entry.color_category.color_hex,
                'color_rgb': f"rgb({entry.color_category.color_rgb})",
                'color_category': entry.color_category.category_name,
                'pattern_type': entry.color_category.pattern_type,
                'accessibility_icon': entry.color_category.icon,
                'accessibility_label': entry.color_category.accessibility_label
            })
        
        if self.include_metadata:
            import json
            row['metadata_json'] = json.dumps(entry.metadata)
        
        return row
```

## JSON Export Specification

### JSON Exporter Class
```python
import json
from datetime import datetime

class JSONExporter(BaseExporter):
    """Export catalog as JSON with structured data and color information."""
    
    def __init__(self, options: JSONExportOptions = None):
        super().__init__(options)
        self.pretty_print = getattr(options, 'pretty_print', True) if options else True
        self.include_schema = getattr(options, 'include_schema', True) if options else True
    
    def export(self, catalog_data: CatalogData, output_path: Path) -> bool:
        """Generate JSON with structured data and color information."""
        try:
            catalog_json = self._create_catalog_json(catalog_data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                if self.pretty_print:
                    json.dump(catalog_json, f, indent=2, ensure_ascii=False, default=str)
                else:
                    json.dump(catalog_json, f, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            print(f"JSON export failed: {e}")
            return False
    
    def _create_catalog_json(self, catalog_data: CatalogData) -> Dict:
        """Create complete JSON structure."""
        catalog_json = {
            "catalog_info": {
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "source_directory": str(catalog_data.source_directory),
                "total_files": len(catalog_data.entries),
                "sort_criteria": catalog_data.sort_criteria.value,
                "color_scheme": catalog_data.color_scheme.name
            },
            "statistics": {
                "total_size": catalog_data.statistics.total_size,
                "file_type_counts": catalog_data.statistics.file_type_counts,
                "size_distribution": catalog_data.statistics.size_distribution,
                "date_distribution": catalog_data.statistics.date_distribution
            },
            "color_legend": self._create_legend_json(catalog_data.color_legend),
            "files": [self._create_file_json(entry) for entry in catalog_data.entries]
        }
        
        if self.include_schema:
            catalog_json["$schema"] = "https://schemas.example.com/file-catalog/v1.0.json"
        
        return catalog_json
    
    def _create_file_json(self, entry: FileEntry) -> Dict:
        """Create JSON representation of a file entry."""
        file_json = {
            "name": entry.name,
            "path": str(entry.path),
            "size": {
                "bytes": entry.size,
                "formatted": self._format_size(entry.size),
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
                "accessed": entry.accessed_date.isoformat()
            },
            "color_coding": {
                "color_hex": entry.color_category.color_hex if entry.color_category else None,
                "color_rgb": entry.color_category.color_rgb if entry.color_category else None,
                "category": entry.color_category.category_name if entry.color_category else None,
                "pattern": entry.color_category.pattern_type if entry.color_category else None,
                "accessibility": {
                    "icon": entry.color_category.icon if entry.color_category else None,
                    "label": entry.color_category.accessibility_label if entry.color_category else None
                }
            },
            "metadata": entry.metadata
        }
        
        return file_json
```

## XML Export Specification

### XML Exporter Class
```python
import xml.etree.ElementTree as ET
from xml.dom import minidom

class XMLExporter(BaseExporter):
    """Export catalog as XML with color attributes."""
    
    def __init__(self, options: XMLExportOptions = None):
        super().__init__(options)
        self.pretty_print = getattr(options, 'pretty_print', True) if options else True
        self.include_dtd = getattr(options, 'include_dtd', False) if options else False
    
    def export(self, catalog_data: CatalogData, output_path: Path) -> bool:
        """Generate XML with color attributes."""
        try:
            root = self._create_catalog_xml(catalog_data)
            
            if self.pretty_print:
                xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            else:
                xml_str = ET.tostring(root, encoding='unicode')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)
            
            return True
            
        except Exception as e:
            print(f"XML export failed: {e}")
            return False
    
    def _create_catalog_xml(self, catalog_data: CatalogData) -> ET.Element:
        """Create XML structure with color attributes."""
        root = ET.Element("file_catalog")
        root.set("version", "1.0")
        root.set("generated_at", datetime.now().isoformat())
        root.set("source_directory", str(catalog_data.source_directory))
        
        # Add catalog info
        info = ET.SubElement(root, "catalog_info")
        ET.SubElement(info, "total_files").text = str(len(catalog_data.entries))
        ET.SubElement(info, "sort_criteria").text = catalog_data.sort_criteria.value
        ET.SubElement(info, "color_scheme").text = catalog_data.color_scheme.name
        
        # Add color legend
        legend = ET.SubElement(root, "color_legend")
        for category, items in catalog_data.color_legend.items():
            cat_elem = ET.SubElement(legend, "category")
            cat_elem.set("name", category)
            for item in items:
                item_elem = ET.SubElement(cat_elem, "legend_item")
                item_elem.set("color", item.color_hex)
                item_elem.set("pattern", item.pattern_type)
                item_elem.set("icon", item.icon)
                item_elem.text = item.label
        
        # Add files
        files = ET.SubElement(root, "files")
        for entry in catalog_data.entries:
            file_elem = self._create_file_xml(files, entry)
        
        return root
    
    def _create_file_xml(self, parent: ET.Element, entry: FileEntry) -> ET.Element:
        """Create XML element for a file entry."""
        file_elem = ET.SubElement(parent, "file")
        file_elem.set("name", entry.name)
        file_elem.set("size", str(entry.size))
        file_elem.set("type", entry.file_type.value)
        
        if entry.color_category:
            file_elem.set("color", entry.color_category.color_hex)
            file_elem.set("color_category", entry.color_category.category_name)
            file_elem.set("pattern", entry.color_category.pattern_type)
        
        # Add child elements
        ET.SubElement(file_elem, "path").text = str(entry.path)
        ET.SubElement(file_elem, "extension").text = entry.extension
        ET.SubElement(file_elem, "created_date").text = entry.created_date.isoformat()
        ET.SubElement(file_elem, "modified_date").text = entry.modified_date.isoformat()
        ET.SubElement(file_elem, "accessed_date").text = entry.accessed_date.isoformat()
        
        return file_elem
```

## Excel Export Specification

### Excel Exporter Class
```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
from openpyxl.utils.dataframe import dataframe_to_rows

class ExcelExporter(BaseExporter):
    """Export catalog as Excel with cell formatting and color-coding."""
    
    def __init__(self, options: ExcelExportOptions = None):
        super().__init__(options)
        self.conditional_formatting = getattr(options, 'conditional_formatting', True) if options else True
        self.auto_filter = getattr(options, 'auto_filter', True) if options else True
        self.freeze_headers = getattr(options, 'freeze_headers', True) if options else True
        self.worksheet_name = getattr(options, 'worksheet_name', 'File Catalog') if options else 'File Catalog'
    
    def export(self, catalog_data: CatalogData, output_path: Path) -> bool:
        """Generate Excel workbook with formatting."""
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = self.worksheet_name
            
            # Add headers
            headers = ['Name', 'Path', 'Size', 'Size (Formatted)', 'Type', 'Extension', 
                      'Created', 'Modified', 'Accessed', 'Color Category']
            ws.append(headers)
            
            # Style headers
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center")
            
            # Add data rows
            for entry in catalog_data.entries:
                row_data = [
                    entry.name,
                    str(entry.path),
                    entry.size,
                    self._format_size(entry.size),
                    entry.file_type.value,
                    entry.extension,
                    entry.created_date,
                    entry.modified_date,
                    entry.accessed_date,
                    entry.color_category.category_name if entry.color_category else ''
                ]
                ws.append(row_data)
            
            # Apply formatting
            self._apply_cell_formatting(ws, catalog_data.entries)
            
            if self.conditional_formatting:
                self._apply_conditional_formatting(ws, catalog_data.entries)
            
            if self.auto_filter:
                ws.auto_filter.ref = ws.dimensions
            
            if self.freeze_headers:
                ws.freeze_panes = "A2"
            
            # Create legend sheet
            self._create_legend_sheet(wb, catalog_data.color_legend)
            
            wb.save(output_path)
            return True
            
        except Exception as e:
            print(f"Excel export failed: {e}")
            return False
    
    def _apply_cell_formatting(self, ws, entries: List[FileEntry]) -> None:
        """Apply color-based cell formatting."""
        for row_idx, entry in enumerate(entries, 2):  # Start from row 2 (after header)
            if entry.color_category:
                # Convert hex color to RGB for Excel
                hex_color = entry.color_category.color_hex.lstrip('#')
                fill = PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")
                
                # Apply to entire row
                for col in range(1, 11):  # Columns A-J
                    ws.cell(row=row_idx, column=col).fill = fill
```

This comprehensive export specification ensures that all formats maintain color-coding information while providing format-specific optimizations and features.