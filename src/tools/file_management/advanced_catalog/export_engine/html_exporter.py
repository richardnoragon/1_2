"""HTML exporter for the Advanced File Catalog Generator.

This module exports catalog data as HTML with embedded CSS and color preservation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.gui.themes import token

from .base_exporter import BaseExporter


class HTMLExporter(BaseExporter):
    """Export catalog as HTML with embedded CSS and color preservation."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options)
        self.include_css = self.options.get("include_css", True)
        self.responsive_design = self.options.get("responsive_design", True)
        self.print_styles = self.options.get("print_styles", True)
        self.interactive_features = self.options.get(
            "interactive_features", False
        )

    def get_file_extension(self) -> str:
        """Return the file extension for HTML format."""
        return "html"

    def validate_options(self) -> bool:
        """Validate HTML export options."""
        return True  # HTML options are all boolean, so always valid

    def export(self, catalog_data, output_path: Path) -> bool:
        """Generate HTML catalog with color-coding."""
        try:
            if not self._validate_output_path(output_path):
                return False

            self._report_progress(10, "Generating HTML structure...")
            html_content = self._generate_html(catalog_data)

            self._report_progress(90, "Writing HTML file...")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            self._report_progress(100, "HTML export completed")
            return True

        except Exception as e:
            print(f"HTML export failed: {e}")
            return False

    def _generate_html(self, catalog_data) -> str:
        """Generate complete HTML document."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Catalog - {self._get_directory_name(catalog_data)}</title>
    {self._generate_css(catalog_data) if self.include_css else ''}
    {self._generate_javascript() if self.interactive_features else ''}
</head>
<body>
    {self._generate_header(catalog_data)}
    {self._generate_legend(catalog_data)}
    {self._generate_file_list(catalog_data)}
    {self._generate_footer(catalog_data)}
</body>
</html>"""

    def _get_directory_name(self, catalog_data) -> str:
        """Get directory name for title."""
        if catalog_data.source_directory:
            return catalog_data.source_directory.name
        return "Unknown Directory"

    def _generate_css(self, catalog_data) -> str:
        """Generate embedded CSS styles."""
        return f"""
<style>
:root {{
    --primary-color: {token('button_primary')};
    --secondary-color: {token('color_amber')};
    --background-color: {token('surface')};
    --text-color: {token('color_text_darkest')};
    --border-color: {token('border_light')};
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    background-color: var(--background-color);
    color: var(--text-color);
}}

.catalog-header {{
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}}

.catalog-title {{
    font-size: 2.5em;
    margin: 0;
    font-weight: 300;
}}

.catalog-subtitle {{
    font-size: 1.2em;
    margin: 10px 0 0 0;
    opacity: 0.9;
}}

.catalog-stats {{
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 15px;
    font-size: 0.9em;
}}

.stat-item {{
    background: rgba(255,255,255,0.2);
    padding: 5px 10px;
    border-radius: 4px;
}}

.legend-container {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}}

.legend-section {{
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid var(--primary-color);
}}

.legend-title {{
    font-size: 1.3em;
    font-weight: 600;
    margin-bottom: 15px;
    color: var(--primary-color);
}}

.legend-item {{
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    padding: 8px;
    border-radius: 4px;
    transition: background-color 0.2s;
}}

.legend-item:hover {{
    background-color: {token('surface')};
}}

.color-sample {{
    width: 24px;
    height: 24px;
    border-radius: 4px;
    margin-right: 12px;
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}}

.legend-label {{
    font-weight: 500;
    margin-right: 10px;
    min-width: 80px;
}}

.legend-description {{
    color: {token('text_muted')};
    font-size: 0.9em;
}}

.file-list {{
    display: grid;
    gap: 8px;
}}

.file-entry {{
    display: grid;
    grid-template-columns: auto 1fr auto auto auto;
    align-items: center;
    padding: 12px 16px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    background: white;
    transition: all 0.2s ease;
    gap: 12px;
}}

.file-entry:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}}

.file-icon {{
    font-size: 1.5em;
    width: 32px;
    text-align: center;
}}

.file-name {{
    font-weight: 500;
    color: var(--text-color);
    text-decoration: none;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

.file-name:hover {{
    color: var(--primary-color);
    text-decoration: underline;
}}

.file-size {{
    font-family: 'Courier New', monospace;
    color: {token('text_muted')};
    font-size: 0.9em;
    min-width: 80px;
    text-align: right;
}}

.file-date {{
    color: {token('text_muted')};
    font-size: 0.9em;
    min-width: 120px;
    text-align: right;
}}

.file-type {{
    background: var(--primary-color);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 500;
    text-transform: uppercase;
    min-width: 60px;
    text-align: center;
}}

.footer {{
    margin-top: 40px;
    text-align: center;
    color: {token('text_muted')};
    font-size: 0.9em;
    border-top: 1px solid var(--border-color);
    padding-top: 20px;
}}

{self._generate_color_classes(catalog_data)}

{self._generate_responsive_css() if self.responsive_design else ''}

{self._generate_print_css() if self.print_styles else ''}

{self._generate_accessibility_css() if self.accessibility_mode else ''}
</style>"""

    def _generate_color_classes(self, catalog_data) -> str:
        """Generate CSS classes for color coding."""
        css_rules = []

        # Get color information from entries
        color_categories = set()
        for entry in catalog_data.entries:
            if entry.color_category:
                color_categories.add(
                    (
                        entry.sort_key or "default",
                        entry.color_category.color_hex,
                        entry.color_category.pattern_type,
                    )
                )

        for category, color_hex, pattern_type in color_categories:
            safe_category = (
                category.replace("_", "-").replace(" ", "-").lower()
            )
            css_rules.append(
                f"""
.color-{safe_category} {{
    background-color: {color_hex};
    border-left: 4px solid {color_hex};
}}"""
            )

            if self.accessibility_mode:
                pattern_css = self._get_pattern_css(pattern_type)
                if pattern_css:
                    css_rules.append(
                        f"""
.accessibility-mode .color-{safe_category} {{
    {pattern_css}
}}"""
                    )

        return "\n".join(css_rules)

    def _get_pattern_css(self, pattern_type: str) -> str:
        """Get CSS for accessibility patterns."""
        patterns = {
            "dots": f"background-image: radial-gradient(circle, {token('color_black')} 1px, transparent 1px); background-size: 8px 8px;",
            "diagonal": "background-image: repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);",
            "horizontal": "background-image: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);",
            "vertical": "background-image: repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);",
        }
        return patterns.get(pattern_type, "")

    def _generate_responsive_css(self) -> str:
        """Generate responsive CSS for mobile devices."""
        return """
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
    
    .catalog-stats {
        flex-direction: column;
        gap: 10px;
    }
}"""

    def _generate_print_css(self) -> str:
        """Generate print-friendly CSS."""
        return f"""
@media print {{
    body {{
        background: white;
        color: black;
    }}
    
    .catalog-header {{
        background: none !important;
        color: black !important;
        box-shadow: none !important;
        border: 2px solid black;
    }}
    
    .file-entry {{
        break-inside: avoid;
        border: 1px solid {token('border')};
        margin-bottom: 2px;
    }}
    
    .legend-section {{
        break-inside: avoid;
        border: 1px solid {token('border')};
        box-shadow: none;
    }}
    
    .file-entry:hover {{
        transform: none;
        box-shadow: none;
    }}
}}"""

    def _generate_accessibility_css(self) -> str:
        """Generate accessibility CSS."""
        return f"""
.accessibility-mode .file-entry {{
    border-width: 2px;
}}

.accessibility-mode .color-sample {{
    border-width: 2px;
    border-color: {token('color_black')};
}}

.accessibility-mode .file-name {{
    font-weight: 600;
}}"""

    def _generate_javascript(self) -> str:
        """Generate JavaScript for interactive features."""
        return """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Add sorting functionality
    const sortButtons = document.querySelectorAll('.sort-button');
    sortButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sortType = this.dataset.sort;
            sortFileList(sortType);
        });
    });
    
    // Add search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterFileList(this.value);
        });
    }
});

function sortFileList(sortType) {
    const fileList = document.querySelector('.file-list');
    const entries = Array.from(fileList.children);
    
    entries.sort((a, b) => {
        const aValue = a.querySelector(`.file-${sortType}`).textContent;
        const bValue = b.querySelector(`.file-${sortType}`).textContent;
        return aValue.localeCompare(bValue);
    });
    
    entries.forEach(entry => fileList.appendChild(entry));
}

function filterFileList(searchTerm) {
    const entries = document.querySelectorAll('.file-entry');
    const term = searchTerm.toLowerCase();
    
    entries.forEach(entry => {
        const fileName = entry.querySelector('.file-name').textContent.toLowerCase();
        entry.style.display = fileName.includes(term) ? 'grid' : 'none';
    });
}
</script>"""

    def _generate_header(self, catalog_data) -> str:
        """Generate HTML header section."""
        stats = catalog_data.statistics
        return f"""
<div class="catalog-header">
    <h1 class="catalog-title">File Catalog</h1>
    <p class="catalog-subtitle">{self._escape_html(str(catalog_data.source_directory) if catalog_data.source_directory else 'Unknown Directory')}</p>
    <div class="catalog-stats">
        <div class="stat-item">📁 {stats.total_files} files</div>
        <div class="stat-item">💾 {self._format_size(stats.total_size)}</div>
        <div class="stat-item">📅 {self._format_date(catalog_data.generation_time, '%Y-%m-%d %H:%M')}</div>
        <div class="stat-item">🎨 {catalog_data.sort_criteria.value.title()} Sort</div>
    </div>
</div>"""

    def _generate_legend(self, catalog_data) -> str:
        """Generate color legend section."""
        if not catalog_data.color_legend:
            return ""

        legend_html = ['<div class="legend-container">']

        for category_name, color_items in catalog_data.color_legend.items():
            legend_html.append(
                f"""
<div class="legend-section">
    <h3 class="legend-title">{self._escape_html(category_name)}</h3>"""
            )

            for color_info in color_items:
                icon = (
                    self._escape_html(color_info.icon)
                    if self.accessibility_mode
                    else ""
                )
                legend_html.append(
                    f"""
    <div class="legend-item">
        <div class="color-sample" style="background-color: {color_info.color_hex};">
            {icon}
        </div>
        <span class="legend-label">{self._escape_html(color_info.accessibility_label)}</span>
        <span class="legend-description">{self._escape_html(color_info.category_name)}</span>
    </div>"""
                )

            legend_html.append("</div>")

        legend_html.append("</div>")
        return "\n".join(legend_html)

    def _generate_file_list(self, catalog_data) -> str:
        """Generate file list section."""
        file_html = ['<div class="file-list">']

        for entry in catalog_data.entries:
            color_class = ""
            if entry.sort_key:
                safe_key = (
                    entry.sort_key.replace("_", "-").replace(" ", "-").lower()
                )
                color_class = f"color-{safe_key}"

            icon = self._get_file_type_icon(entry.file_type)
            file_link = f"file:///{entry.path}"

            file_html.append(
                f"""
<div class="file-entry {color_class}">
    <div class="file-icon">{icon}</div>
    <a href="{file_link}" class="file-name" title="{self._escape_html(str(entry.path))}">{self._escape_html(entry.name)}</a>
    <div class="file-size">{entry.format_size()}</div>
    <div class="file-date">{self._format_date(entry.modified_date, '%Y-%m-%d %H:%M')}</div>
    <div class="file-type">{entry.file_type.value}</div>
</div>"""
            )

        file_html.append("</div>")
        return "\n".join(file_html)

    def _generate_footer(self, catalog_data) -> str:
        """Generate footer section."""
        metadata = self._create_export_metadata(catalog_data)
        return f"""
<div class="footer">
    <p>Generated by Advanced File Catalog Generator on {self._format_date(datetime.now())}</p>
    <p>Export format: {metadata['export_format'].upper()} | 
       Color preservation: {'Enabled' if metadata['color_preservation'] else 'Disabled'} | 
       Accessibility mode: {'Enabled' if metadata['accessibility_mode'] else 'Disabled'}</p>
</div>"""
