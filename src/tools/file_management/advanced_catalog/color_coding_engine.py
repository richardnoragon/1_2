"""Color coding engine for the Advanced File Catalog Generator.

This module manages color assignment and accessibility features for file
categorization with support for multiple color schemes.
"""

from typing import Dict, List, Optional
from .catalog_data_model import (
    FileEntry,
    ColorInfo,
    SortCriteria,
    ColorScheme,
    FileType,
    SizeCategory,
    DateCategory,
    AlphabeticalCategory,
)


class ColorCodingEngine:
    """Manages color assignment and accessibility features."""

    # Default color scheme definitions
    DEFAULT_COLORS = {
        # Size-based colors
        "size": {
            SizeCategory.SMALL.value: ColorInfo(
                color_hex="#E8F5E8",
                color_rgb=(232, 245, 232),
                pattern_type="dots",
                icon="📄",
                accessibility_label="Small",
                category_name="Small Files (<1MB)",
            ),
            SizeCategory.MEDIUM.value: ColorInfo(
                color_hex="#E3F2FD",
                color_rgb=(227, 242, 253),
                pattern_type="diagonal",
                icon="📋",
                accessibility_label="Medium",
                category_name="Medium Files (1MB-100MB)",
            ),
            SizeCategory.LARGE.value: ColorInfo(
                color_hex="#FFF3E0",
                color_rgb=(255, 243, 224),
                pattern_type="grid",
                icon="📊",
                accessibility_label="Large",
                category_name="Large Files (>100MB)",
            ),
        },
        # Type-based colors
        "type": {
            FileType.DOCUMENT.value: ColorInfo(
                color_hex="#2196F3",
                color_rgb=(33, 150, 243),
                pattern_type="horizontal",
                icon="📄",
                accessibility_label="Documents",
                category_name="Documents",
            ),
            FileType.IMAGE.value: ColorInfo(
                color_hex="#4CAF50",
                color_rgb=(76, 175, 80),
                pattern_type="checkerboard",
                icon="🖼️",
                accessibility_label="Images",
                category_name="Images",
            ),
            FileType.VIDEO.value: ColorInfo(
                color_hex="#F44336",
                color_rgb=(244, 67, 54),
                pattern_type="vertical",
                icon="🎥",
                accessibility_label="Videos",
                category_name="Videos",
            ),
            FileType.AUDIO.value: ColorInfo(
                color_hex="#9C27B0",
                color_rgb=(156, 39, 176),
                pattern_type="waves",
                icon="🎵",
                accessibility_label="Audio",
                category_name="Audio Files",
            ),
            FileType.ARCHIVE.value: ColorInfo(
                color_hex="#FF9800",
                color_rgb=(255, 152, 0),
                pattern_type="crosshatch",
                icon="📦",
                accessibility_label="Archives",
                category_name="Archive Files",
            ),
            FileType.EXECUTABLE.value: ColorInfo(
                color_hex="#607D8B",
                color_rgb=(96, 125, 139),
                pattern_type="solid",
                icon="⚙️",
                accessibility_label="Executables",
                category_name="Executable Files",
            ),
            FileType.CODE.value: ColorInfo(
                color_hex="#795548",
                color_rgb=(121, 85, 72),
                pattern_type="code",
                icon="💻",
                accessibility_label="Code",
                category_name="Code Files",
            ),
            FileType.DATA.value: ColorInfo(
                color_hex="#009688",
                color_rgb=(0, 150, 136),
                pattern_type="data",
                icon="📊",
                accessibility_label="Data",
                category_name="Data Files",
            ),
            FileType.OTHER.value: ColorInfo(
                color_hex="#E0E0E0",
                color_rgb=(224, 224, 224),
                pattern_type="sparse_dots",
                icon="❓",
                accessibility_label="Other",
                category_name="Other Files",
            ),
        },
        # Date-based colors
        "date": {
            DateCategory.RECENT.value: ColorInfo(
                color_hex="#8BC34A",
                color_rgb=(139, 195, 74),
                pattern_type="fresh",
                icon="🆕",
                accessibility_label="Recent",
                category_name="Recent Files (<30 days)",
            ),
            DateCategory.MODERATE.value: ColorInfo(
                color_hex="#FFEB3B",
                color_rgb=(255, 235, 59),
                pattern_type="medium_fade",
                icon="📅",
                accessibility_label="Moderate",
                category_name="Moderate Age (30-365 days)",
            ),
            DateCategory.OLD.value: ColorInfo(
                color_hex="#FFCDD2",
                color_rgb=(255, 205, 210),
                pattern_type="aged",
                icon="📜",
                accessibility_label="Old",
                category_name="Old Files (>365 days)",
            ),
        },
        # Alphabetical colors
        "alphabetical": {
            AlphabeticalCategory.A_E.value: ColorInfo(
                color_hex="#FFEBEE",
                color_rgb=(255, 235, 238),
                pattern_type="light_dots",
                icon="🅰️",
                accessibility_label="A-E",
                category_name="A-E Range",
            ),
            AlphabeticalCategory.F_J.value: ColorInfo(
                color_hex="#FFF3E0",
                color_rgb=(255, 243, 224),
                pattern_type="light_diagonal",
                icon="🅵",
                accessibility_label="F-J",
                category_name="F-J Range",
            ),
            AlphabeticalCategory.K_O.value: ColorInfo(
                color_hex="#FFFDE7",
                color_rgb=(255, 253, 231),
                pattern_type="light_grid",
                icon="🅺",
                accessibility_label="K-O",
                category_name="K-O Range",
            ),
            AlphabeticalCategory.P_T.value: ColorInfo(
                color_hex="#E8F5E8",
                color_rgb=(232, 245, 232),
                pattern_type="light_horizontal",
                icon="🅿️",
                accessibility_label="P-T",
                category_name="P-T Range",
            ),
            AlphabeticalCategory.U_Z.value: ColorInfo(
                color_hex="#E3F2FD",
                color_rgb=(227, 242, 253),
                pattern_type="light_vertical",
                icon="🆄",
                accessibility_label="U-Z",
                category_name="U-Z Range",
            ),
        },
    }

    # High contrast color scheme
    HIGH_CONTRAST_COLORS = {
        "size": {
            SizeCategory.SMALL.value: ColorInfo(
                color_hex="#FFFFFF",
                color_rgb=(255, 255, 255),
                pattern_type="dots",
                icon="📄",
                accessibility_label="Small",
                category_name="Small Files (<1MB)",
            ),
            SizeCategory.MEDIUM.value: ColorInfo(
                color_hex="#000080",
                color_rgb=(0, 0, 128),
                pattern_type="diagonal",
                icon="📋",
                accessibility_label="Medium",
                category_name="Medium Files (1MB-100MB)",
            ),
            SizeCategory.LARGE.value: ColorInfo(
                color_hex="#800000",
                color_rgb=(128, 0, 0),
                pattern_type="grid",
                icon="📊",
                accessibility_label="Large",
                category_name="Large Files (>100MB)",
            ),
        }
        # Add other high contrast definitions as needed
    }

    def __init__(self, scheme: ColorScheme = ColorScheme.DEFAULT):
        self.scheme = scheme
        self.accessibility_mode = False
        self.high_contrast_mode = False
        self.custom_colors = {}

    def assign_colors(
        self, entries: List[FileEntry], sort_criteria: SortCriteria
    ) -> None:
        """Assign colors to entries based on sort criteria."""
        color_map = self._get_color_map_for_criteria(sort_criteria)

        for entry in entries:
            category_key = self._get_category_key(entry, sort_criteria)
            if category_key in color_map:
                entry.color_category = color_map[category_key]

    def _get_category_key(
        self, entry: FileEntry, criteria: SortCriteria
    ) -> str:
        """Get the category key for an entry based on criteria."""
        if criteria == SortCriteria.ALPHABETICAL:
            return entry.get_alphabetical_category().value
        elif criteria == SortCriteria.SIZE:
            return entry.get_size_category().value
        elif criteria == SortCriteria.TYPE:
            return entry.file_type.value
        else:  # Date-based
            date_type = "modified"
            if criteria == SortCriteria.CREATED_DATE:
                date_type = "created"
            elif criteria == SortCriteria.ACCESSED_DATE:
                date_type = "accessed"
            return entry.get_date_category(date_type).value

    def _get_color_map_for_criteria(
        self, criteria: SortCriteria
    ) -> Dict[str, ColorInfo]:
        """Get color map for the specified criteria."""
        if self.scheme == ColorScheme.HIGH_CONTRAST:
            colors = self.HIGH_CONTRAST_COLORS
        elif self.scheme == ColorScheme.CUSTOM:
            colors = self.custom_colors
        else:
            colors = self.DEFAULT_COLORS

        if criteria == SortCriteria.ALPHABETICAL:
            return colors.get("alphabetical", {})
        elif criteria == SortCriteria.SIZE:
            return colors.get("size", {})
        elif criteria == SortCriteria.TYPE:
            return colors.get("type", {})
        else:  # Date-based
            return colors.get("date", {})

    def get_color_for_category(
        self, category: str, criteria: SortCriteria
    ) -> Optional[ColorInfo]:
        """Get color information for a specific category."""
        color_map = self._get_color_map_for_criteria(criteria)
        return color_map.get(category)

    def generate_legend(
        self, sort_criteria: SortCriteria
    ) -> Dict[str, List[ColorInfo]]:
        """Generate color legend for the current sort criteria."""
        color_map = self._get_color_map_for_criteria(sort_criteria)

        legend = {
            self._get_criteria_display_name(sort_criteria): list(
                color_map.values()
            )
        }

        return legend

    def _get_criteria_display_name(self, criteria: SortCriteria) -> str:
        """Get display name for sort criteria."""
        display_names = {
            SortCriteria.ALPHABETICAL: "Alphabetical Ranges",
            SortCriteria.SIZE: "File Sizes",
            SortCriteria.TYPE: "File Types",
            SortCriteria.CREATED_DATE: "Creation Dates",
            SortCriteria.MODIFIED_DATE: "Modification Dates",
            SortCriteria.ACCESSED_DATE: "Access Dates",
        }
        return display_names.get(criteria, "Categories")

    def enable_accessibility_mode(self, enabled: bool = True) -> None:
        """Enable or disable accessibility mode."""
        self.accessibility_mode = enabled

    def enable_high_contrast_mode(self, enabled: bool = True) -> None:
        """Enable or disable high contrast mode."""
        self.high_contrast_mode = enabled
        if enabled:
            self.scheme = ColorScheme.HIGH_CONTRAST

    def get_pattern_for_category(
        self, category: str, criteria: SortCriteria
    ) -> str:
        """Get pattern type for accessibility."""
        color_info = self.get_color_for_category(category, criteria)
        return color_info.pattern_type if color_info else "none"

    def get_css_for_color_scheme(self, sort_criteria: SortCriteria) -> str:
        """Generate CSS for the current color scheme."""
        color_map = self._get_color_map_for_criteria(sort_criteria)
        css_rules = []

        for category, color_info in color_map.items():
            # Basic color class
            css_rules.append(
                f"""
.color-{category.replace('_', '-')} {{
    background-color: {color_info.color_hex};
    border-left: 4px solid {color_info.color_hex};
}}"""
            )

            # Pattern overlay for accessibility
            if self.accessibility_mode:
                pattern_css = self._get_pattern_css(color_info.pattern_type)
                if pattern_css:
                    css_rules.append(
                        f"""
.accessibility-mode .color-{category.replace('_', '-')} {{
    {pattern_css}
}}"""
                    )

        return "\n".join(css_rules)

    def _get_pattern_css(self, pattern_type: str) -> str:
        """Get CSS for accessibility patterns."""
        patterns = {
            "dots": """background-image: radial-gradient(circle, #000 1px, transparent 1px);
    background-size: 8px 8px;""",
            "diagonal": """background-image: repeating-linear-gradient(
        45deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);""",
            "horizontal": """background-image: repeating-linear-gradient(
        0deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);""",
            "vertical": """background-image: repeating-linear-gradient(
        90deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);""",
            "grid": """background-image: 
        repeating-linear-gradient(0deg, transparent, transparent 4px, rgba(0,0,0,0.1) 4px, rgba(0,0,0,0.1) 5px),
        repeating-linear-gradient(90deg, transparent, transparent 4px, rgba(0,0,0,0.1) 4px, rgba(0,0,0,0.1) 5px);""",
            "checkerboard": """background-image: 
        linear-gradient(45deg, rgba(0,0,0,0.1) 25%, transparent 25%),
        linear-gradient(-45deg, rgba(0,0,0,0.1) 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, rgba(0,0,0,0.1) 75%),
        linear-gradient(-45deg, transparent 75%, rgba(0,0,0,0.1) 75%);
    background-size: 8px 8px;
    background-position: 0 0, 0 4px, 4px -4px, -4px 0px;""",
            "waves": """background-image: repeating-linear-gradient(
        0deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 3px);
    background-size: 100% 6px;""",
            "crosshatch": """background-image: 
        repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px),
        repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(0,0,0,0.1) 2px, rgba(0,0,0,0.1) 4px);""",
        }
        return patterns.get(pattern_type, "")

    def set_custom_color_scheme(self, custom_colors: Dict) -> None:
        """Set a custom color scheme."""
        self.custom_colors = custom_colors
        self.scheme = ColorScheme.CUSTOM

    def get_available_schemes(self) -> List[ColorScheme]:
        """Get list of available color schemes."""
        return list(ColorScheme)

    def export_color_scheme(self, sort_criteria: SortCriteria) -> Dict:
        """Export current color scheme as JSON-serializable dict."""
        color_map = self._get_color_map_for_criteria(sort_criteria)

        export_data = {
            "scheme_name": self.scheme.value,
            "criteria": sort_criteria.value,
            "accessibility_mode": self.accessibility_mode,
            "high_contrast_mode": self.high_contrast_mode,
            "colors": {},
        }

        for category, color_info in color_map.items():
            export_data["colors"][category] = {
                "color_hex": color_info.color_hex,
                "color_rgb": color_info.color_rgb,
                "pattern_type": color_info.pattern_type,
                "icon": color_info.icon,
                "accessibility_label": color_info.accessibility_label,
                "category_name": color_info.category_name,
            }

        return export_data
