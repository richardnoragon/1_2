# Advanced File Catalog Generator - Color Schemes and Accessibility

## Color Scheme Definitions

### Default Color Scheme

#### Size-Based Colors
- **Small files (<1MB)**
  - Color: `#E8F5E8` (Light Green)
  - RGB: (232, 245, 232)
  - Pattern: Dots
  - Icon: 📄 (Small document)

- **Medium files (1MB-100MB)**
  - Color: `#E3F2FD` (Light Blue)
  - RGB: (227, 242, 253)
  - Pattern: Diagonal lines
  - Icon: 📋 (Medium document)

- **Large files (>100MB)**
  - Color: `#FFF3E0` (Light Orange)
  - RGB: (255, 243, 224)
  - Pattern: Grid
  - Icon: 📊 (Large document)

#### Type-Based Colors
- **Documents (.pdf, .doc, .docx, .txt, .rtf)**
  - Color: `#2196F3` (Blue)
  - RGB: (33, 150, 243)
  - Pattern: Horizontal lines
  - Icon: 📄

- **Images (.jpg, .png, .gif, .bmp, .svg)**
  - Color: `#4CAF50` (Green)
  - RGB: (76, 175, 80)
  - Pattern: Checkerboard
  - Icon: 🖼️

- **Videos (.mp4, .avi, .mkv, .mov, .wmv)**
  - Color: `#F44336` (Red)
  - RGB: (244, 67, 54)
  - Pattern: Vertical lines
  - Icon: 🎥

- **Audio (.mp3, .wav, .flac, .aac, .ogg)**
  - Color: `#9C27B0` (Purple)
  - RGB: (156, 39, 176)
  - Pattern: Waves
  - Icon: 🎵

- **Archives (.zip, .rar, .7z, .tar, .gz)**
  - Color: `#FF9800` (Orange)
  - RGB: (255, 152, 0)
  - Pattern: Cross-hatch
  - Icon: 📦

- **Executables (.exe, .msi, .app, .deb, .rpm)**
  - Color: `#607D8B` (Blue Gray)
  - RGB: (96, 125, 139)
  - Pattern: Solid fill
  - Icon: ⚙️

- **Other/Unknown**
  - Color: `#E0E0E0` (Light Gray)
  - RGB: (224, 224, 224)
  - Pattern: Sparse dots
  - Icon: ❓

#### Date-Based Colors
- **Recent (<30 days)**
  - Color: `#8BC34A` (Light Green)
  - RGB: (139, 195, 74)
  - Pattern: Fresh (solid)
  - Icon: 🆕

- **Moderate (30-365 days)**
  - Color: `#FFEB3B` (Yellow)
  - RGB: (255, 235, 59)
  - Pattern: Medium fade
  - Icon: 📅

- **Old (>365 days)**
  - Color: `#FFCDD2` (Light Red)
  - RGB: (255, 205, 210)
  - Pattern: Aged (faded)
  - Icon: 📜

#### Alphabetical Colors (A-Z Ranges)
- **A-E Range**
  - Color: `#FFEBEE` (Light Red)
  - RGB: (255, 235, 238)
  - Pattern: Light dots

- **F-J Range**
  - Color: `#FFF3E0` (Light Orange)
  - RGB: (255, 243, 224)
  - Pattern: Light diagonal

- **K-O Range**
  - Color: `#FFFDE7` (Light Yellow)
  - RGB: (255, 253, 231)
  - Pattern: Light grid

- **P-T Range**
  - Color: `#E8F5E8` (Light Green)
  - RGB: (232, 245, 232)
  - Pattern: Light horizontal

- **U-Z Range**
  - Color: `#E3F2FD` (Light Blue)
  - RGB: (227, 242, 253)
  - Pattern: Light vertical

### High Contrast Color Scheme

#### Size-Based (High Contrast)
- **Small files**: `#000000` on `#FFFFFF` (Black on White)
- **Medium files**: `#FFFFFF` on `#000080` (White on Navy)
- **Large files**: `#FFFF00` on `#800000` (Yellow on Maroon)

#### Type-Based (High Contrast)
- **Documents**: `#FFFFFF` on `#000080` (White on Navy)
- **Images**: `#000000` on `#00FF00` (Black on Lime)
- **Videos**: `#FFFFFF` on `#FF0000` (White on Red)
- **Audio**: `#FFFF00` on `#800080` (Yellow on Purple)
- **Archives**: `#000000` on `#FFA500` (Black on Orange)
- **Executables**: `#FFFFFF` on `#000000` (White on Black)
- **Other**: `#000000` on `#C0C0C0` (Black on Silver)

### Colorblind-Friendly Scheme

#### Using ColorBrewer Safe Colors
- **Category 1**: `#1f77b4` (Blue)
- **Category 2**: `#ff7f0e` (Orange)
- **Category 3**: `#2ca02c` (Green)
- **Category 4**: `#d62728` (Red)
- **Category 5**: `#9467bd` (Purple)
- **Category 6**: `#8c564b` (Brown)
- **Category 7**: `#e377c2` (Pink)
- **Category 8**: `#7f7f7f` (Gray)

### Monochrome Scheme

#### Grayscale Variations
- **Level 1**: `#F8F8F8` (Very Light Gray)
- **Level 2**: `#E0E0E0` (Light Gray)
- **Level 3**: `#C0C0C0` (Medium Light Gray)
- **Level 4**: `#A0A0A0` (Medium Gray)
- **Level 5**: `#808080` (Gray)
- **Level 6**: `#606060` (Dark Gray)
- **Level 7**: `#404040` (Very Dark Gray)
- **Level 8**: `#202020` (Almost Black)

## Accessibility Features

### Pattern Definitions

#### Pattern Types for Color-Blind Support
```css
/* CSS Pattern Definitions */
.pattern-dots {
    background-image: radial-gradient(circle, #000 1px, transparent 1px);
    background-size: 8px 8px;
}

.pattern-diagonal {
    background-image: repeating-linear-gradient(
        45deg,
        transparent,
        transparent 2px,
        #000 2px,
        #000 4px
    );
}

.pattern-horizontal {
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        #000 2px,
        #000 4px
    );
}

.pattern-vertical {
    background-image: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 2px,
        #000 2px,
        #000 4px
    );
}

.pattern-grid {
    background-image: 
        repeating-linear-gradient(0deg, transparent, transparent 4px, #000 4px, #000 5px),
        repeating-linear-gradient(90deg, transparent, transparent 4px, #000 4px, #000 5px);
}

.pattern-checkerboard {
    background-image: 
        linear-gradient(45deg, #000 25%, transparent 25%),
        linear-gradient(-45deg, #000 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #000 75%),
        linear-gradient(-45deg, transparent 75%, #000 75%);
    background-size: 8px 8px;
    background-position: 0 0, 0 4px, 4px -4px, -4px 0px;
}

.pattern-waves {
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        #000 2px,
        #000 3px
    );
    background-size: 100% 6px;
}

.pattern-crosshatch {
    background-image: 
        repeating-linear-gradient(45deg, transparent, transparent 2px, #000 2px, #000 4px),
        repeating-linear-gradient(-45deg, transparent, transparent 2px, #000 2px, #000 4px);
}
```

### Text Indicators

#### Category Labels
- **Size Categories**: "SMALL", "MEDIUM", "LARGE"
- **Type Categories**: "DOC", "IMG", "VID", "AUD", "ARC", "EXE", "OTH"
- **Date Categories**: "NEW", "MOD", "OLD"
- **Alpha Categories**: "A-E", "F-J", "K-O", "P-T", "U-Z"

### Icon Support

#### Unicode Icons for Categories
```python
CATEGORY_ICONS = {
    # Size-based
    'small': '📄',
    'medium': '📋',
    'large': '📊',
    
    # Type-based
    'document': '📄',
    'image': '🖼️',
    'video': '🎥',
    'audio': '🎵',
    'archive': '📦',
    'executable': '⚙️',
    'other': '❓',
    
    # Date-based
    'recent': '🆕',
    'moderate': '📅',
    'old': '📜',
    
    # Status indicators
    'duplicate': '🔄',
    'large_file': '⚠️',
    'system_file': '🔒'
}
```

## Legend Generation

### HTML Legend Template
```html
<div class="color-legend">
    <h3>Color Legend</h3>
    <div class="legend-section">
        <h4>{{category_name}}</h4>
        {{#legend_items}}
        <div class="legend-item">
            <div class="color-sample" style="background-color: {{color}}; {{pattern_css}}">
                <span class="icon">{{icon}}</span>
            </div>
            <span class="label">{{label}}</span>
            <span class="description">{{description}}</span>
        </div>
        {{/legend_items}}
    </div>
</div>
```

### PDF Legend Layout
```python
def draw_legend_pdf(canvas, legend_data, x, y, width, height):
    """Draw color legend on PDF canvas."""
    current_y = y + height - 20
    
    # Title
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(x, current_y, "Color Legend")
    current_y -= 25
    
    for category, items in legend_data.items():
        # Category header
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(x, current_y, category)
        current_y -= 20
        
        for item in items:
            # Color sample
            canvas.setFillColor(item.color)
            canvas.rect(x, current_y - 10, 15, 15, fill=1)
            
            # Label and description
            canvas.setFillColor(colors.black)
            canvas.setFont("Helvetica", 10)
            canvas.drawString(x + 20, current_y - 5, f"{item.icon} {item.label}")
            canvas.drawString(x + 100, current_y - 5, item.description)
            
            current_y -= 18
        
        current_y -= 10  # Extra space between categories
```

## Color Scheme Configuration

### JSON Color Scheme Format
```json
{
    "name": "Custom Scheme",
    "description": "User-defined color scheme",
    "version": "1.0",
    "categories": {
        "size": {
            "small": {
                "color": "#E8F5E8",
                "pattern": "dots",
                "icon": "📄",
                "label": "Small",
                "description": "Files smaller than 1MB"
            },
            "medium": {
                "color": "#E3F2FD",
                "pattern": "diagonal",
                "icon": "📋",
                "label": "Medium",
                "description": "Files between 1MB and 100MB"
            },
            "large": {
                "color": "#FFF3E0",
                "pattern": "grid",
                "icon": "📊",
                "label": "Large",
                "description": "Files larger than 100MB"
            }
        },
        "type": {
            "document": {
                "color": "#2196F3",
                "pattern": "horizontal",
                "icon": "📄",
                "label": "Documents",
                "description": "Text documents and PDFs"
            }
            // ... more type definitions
        }
        // ... more category definitions
    },
    "accessibility": {
        "high_contrast": true,
        "patterns_enabled": true,
        "icons_enabled": true,
        "text_labels": true
    }
}
```

This comprehensive color scheme system ensures that the catalog generator provides excellent visual organization while maintaining full accessibility for all users, including those with color vision deficiencies.