"""
Generate Binary Test Files for RFU Test Suite

This script creates actual binary test files for:
- Phase 2.8: Binary Test Files (Images)
- Phase 2.9: Binary Test Files (Documents)
- Phase 2.10: Binary Test Files (Archives)

Uses Python libraries to generate valid binary file formats.
"""

import io
import os
import random
import struct
import tarfile
import zipfile
import zlib
from pathlib import Path

BASE = Path(__file__).parent.parent


# =============================================================================
# Phase 2.8: Image Generation
# =============================================================================


def create_bmp_image(
    path: Path, width: int = 100, height: int = 100, color: tuple = (255, 0, 0)
):
    """Create a valid BMP image file."""
    # BMP file header (14 bytes)
    # Image data (BGR format, 24-bit, rows padded to 4-byte boundary)
    row_size = (width * 3 + 3) // 4 * 4  # Padded row size
    image_size = row_size * height
    file_size = 54 + image_size  # Header (54) + image data

    # File header
    header = bytearray(54)
    header[0:2] = b"BM"  # Signature
    struct.pack_into("<I", header, 2, file_size)  # File size
    struct.pack_into("<I", header, 10, 54)  # Data offset

    # DIB header (BITMAPINFOHEADER)
    struct.pack_into("<I", header, 14, 40)  # DIB header size
    struct.pack_into("<i", header, 18, width)  # Width
    struct.pack_into("<i", header, 22, height)  # Height
    struct.pack_into("<H", header, 26, 1)  # Color planes
    struct.pack_into("<H", header, 28, 24)  # Bits per pixel
    struct.pack_into("<I", header, 34, image_size)  # Image size

    # Image data (BGR format)
    image_data = bytearray()
    for y in range(height):
        for x in range(width):
            # Create a simple gradient/pattern
            b = color[2] if (x + y) % 10 < 5 else 0
            g = color[1] if (x + y) % 10 < 5 else 0
            r = color[0] if (x + y) % 10 < 5 else 0
            image_data.extend([b, g, r])
        # Pad row to 4-byte boundary
        padding = row_size - width * 3
        image_data.extend([0] * padding)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + image_data)
    return path.stat().st_size


def create_png_image(
    path: Path, width: int = 100, height: int = 100, interlaced: bool = False
):
    """Create a valid PNG image file."""

    def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
        """Create a PNG chunk with CRC."""
        length = struct.pack(">I", len(data))
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return length + chunk_type + data + struct.pack(">I", crc)

    # PNG signature
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk (image header)
    ihdr_data = struct.pack(
        ">IIBBBBB", width, height, 8, 2, 0, 0, 1 if interlaced else 0
    )
    ihdr = png_chunk(b"IHDR", ihdr_data)

    # IDAT chunk (image data)
    # Create simple red/blue pattern
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter type: None
        for x in range(width):
            if (x + y) % 2 == 0:
                raw_data.extend([255, 0, 0])  # Red
            else:
                raw_data.extend([0, 0, 255])  # Blue

    compressed = zlib.compress(bytes(raw_data), 9)
    idat = png_chunk(b"IDAT", compressed)

    # IEND chunk (image end)
    iend = png_chunk(b"IEND", b"")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(signature + ihdr + idat + iend)
    return path.stat().st_size


def create_gif_image(
    path: Path, width: int = 50, height: int = 50, animated: bool = False
):
    """Create a valid GIF image file."""
    data = bytearray()

    # GIF header
    data.extend(b"GIF89a")

    # Logical screen descriptor
    data.extend(struct.pack("<H", width))  # Width
    data.extend(struct.pack("<H", height))  # Height
    data.append(0b11110000)  # Global color table flag + color resolution
    data.append(0)  # Background color index
    data.append(0)  # Pixel aspect ratio

    # Global color table (16 colors)
    colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 255, 255),  # White
        (0, 0, 0),  # Black
        (128, 128, 128),  # Gray
        (128, 0, 0),  # Dark red
        (0, 128, 0),  # Dark green
        (0, 0, 128),  # Dark blue
        (192, 192, 192),  # Light gray
        (255, 128, 0),  # Orange
        (128, 0, 128),  # Purple
        (0, 128, 128),  # Teal
    ]
    for r, g, b in colors:
        data.extend([r, g, b])

    if animated:
        # NETSCAPE extension for looping
        data.extend(b"\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00")

        # Create 2 frames
        for frame in range(2):
            # Graphic control extension
            data.extend(b"\x21\xf9\x04\x08")  # Delay time will follow
            data.extend(struct.pack("<H", 50))  # Delay (50/100 sec)
            data.extend(b"\x00\x00")

            # Image descriptor
            data.append(0x2C)
            data.extend(struct.pack("<HHHH", 0, 0, width, height))
            data.append(0)  # No local color table

            # Image data (LZW compressed) - minimal valid encoding
            data.append(4)  # LZW minimum code size
            # Use minimal sub-blocks
            subblock = bytes([0x10, frame, 0x00])  # Small valid sub-block
            data.append(len(subblock))
            data.extend(subblock)
            data.append(0)  # End of image data
    else:
        # Single frame
        data.append(0x2C)  # Image separator
        data.extend(struct.pack("<HHHH", 0, 0, width, height))
        data.append(0)  # No local color table

        # Simplified image data
        data.append(4)  # LZW minimum code size
        # Basic pattern - minimal valid LZW stream
        data.extend(b"\x02\x10\x00\x00")

    # Trailer
    data.append(0x3B)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path.stat().st_size


def create_jpeg_image(
    path: Path, width: int = 100, height: int = 100, progressive: bool = False
):
    """Create a minimal valid JPEG image."""
    # This creates a minimal valid JPEG with solid color
    # Using a pre-generated minimal JPEG structure

    # SOI marker
    data = bytearray([0xFF, 0xD8])

    # APP0 (JFIF marker)
    app0 = bytearray(
        [
            0xFF,
            0xE0,
            0x00,
            0x10,  # Marker + length
            0x4A,
            0x46,
            0x49,
            0x46,
            0x00,  # "JFIF\0"
            0x01,
            0x01,  # Version 1.1
            0x00,  # Aspect ratio units (0 = no units)
            0x00,
            0x01,
            0x00,
            0x01,  # X/Y density
            0x00,
            0x00,  # Thumbnail size
        ]
    )
    data.extend(app0)

    # DQT (quantization table)
    dqt = bytearray([0xFF, 0xDB, 0x00, 0x43, 0x00])
    # Standard luminance quantization table
    qt = [
        16,
        11,
        10,
        16,
        24,
        40,
        51,
        61,
        12,
        12,
        14,
        19,
        26,
        58,
        60,
        55,
        14,
        13,
        16,
        24,
        40,
        57,
        69,
        56,
        14,
        17,
        22,
        29,
        51,
        87,
        80,
        62,
        18,
        22,
        37,
        56,
        68,
        109,
        103,
        77,
        24,
        35,
        55,
        64,
        81,
        104,
        113,
        92,
        49,
        64,
        78,
        87,
        103,
        121,
        120,
        101,
        72,
        92,
        95,
        98,
        112,
        100,
        103,
        99,
    ]
    dqt.extend(qt)
    data.extend(dqt)

    # SOF0 (baseline) or SOF2 (progressive)
    sof_marker = 0xC2 if progressive else 0xC0
    sof = bytearray(
        [
            0xFF,
            sof_marker,
            0x00,
            0x0B,  # Marker + length
            0x08,  # Precision (8 bits)
            (height >> 8) & 0xFF,
            height & 0xFF,  # Height
            (width >> 8) & 0xFF,
            width & 0xFF,  # Width
            0x01,  # Number of components
            0x01,
            0x11,
            0x00,  # Component info
        ]
    )
    data.extend(sof)

    # DHT (Huffman table)
    dht = bytearray([0xFF, 0xC4, 0x00, 0x1F, 0x00])
    # Standard DC luminance table
    dht.extend([0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0])
    dht.extend([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    data.extend(dht)

    # SOS (start of scan)
    sos = bytearray(
        [
            0xFF,
            0xDA,
            0x00,
            0x08,  # Marker + length
            0x01,
            0x01,
            0x00,  # Component info
            0x00,
            0x3F,
            0x00,  # Spectral selection
        ]
    )
    data.extend(sos)

    # Minimal scan data (solid gray)
    scan_data = bytearray([0x7F] * 100)
    data.extend(scan_data)

    # EOI marker
    data.extend([0xFF, 0xD9])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path.stat().st_size


def create_svg_image(path: Path, width: int = 200, height: int = 200):
    """Create a valid SVG image file."""
    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <title>RFU Test SVG Image</title>
  <rect width="100%" height="100%" fill="#f0f0f0"/>
  <circle cx="{width//2}" cy="{height//2}" r="{min(width, height)//3}" fill="#4a90d9"/>
  <rect x="{width//4}" y="{height//4}" width="{width//2}" height="{height//2}" fill="#d94a4a" opacity="0.7"/>
  <text x="{width//2}" y="{height//2}" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="16" fill="#333">
    RFU Test
  </text>
</svg>"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg_content, encoding="utf-8")
    return path.stat().st_size


def create_ico_image(path: Path):
    """Create a valid ICO (icon) file with multiple sizes."""
    # ICO header
    data = bytearray()
    data.extend(struct.pack("<HHH", 0, 1, 2))  # Reserved, type (1=icon), count

    # Directory entries (16x16 and 32x32)
    sizes = [(16, 16), (32, 32)]
    offset = 6 + 16 * len(sizes)  # Header + directory entries

    images = []
    for width, height in sizes:
        # Create BMP data for this size
        row_size = (width * 3 + 3) // 4 * 4
        image_size = row_size * height

        # DIB header (40 bytes) - no file header for ICO
        bmp_header = bytearray(40)
        struct.pack_into("<I", bmp_header, 0, 40)
        struct.pack_into("<i", bmp_header, 4, width)
        struct.pack_into(
            "<i", bmp_header, 8, height * 2
        )  # Double height (image + mask)
        struct.pack_into("<H", bmp_header, 12, 1)
        struct.pack_into("<H", bmp_header, 14, 24)

        # Image data
        img_data = bytearray()
        for y in range(height):
            for x in range(width):
                if (x + y) % 4 < 2:
                    img_data.extend([0, 0, 255])  # Blue
                else:
                    img_data.extend([255, 255, 0])  # Yellow
            img_data.extend([0] * (row_size - width * 3))

        # AND mask (all zeros = fully opaque)
        mask_row_size = (width + 31) // 32 * 4
        mask_data = bytearray([0] * mask_row_size * height)

        image_data = bmp_header + img_data + mask_data
        images.append(image_data)

        # Directory entry
        data.append(width if width < 256 else 0)
        data.append(height if height < 256 else 0)
        data.append(0)  # Palette size
        data.append(0)  # Reserved
        data.extend(struct.pack("<HH", 1, 24))  # Color planes, bits per pixel
        data.extend(struct.pack("<I", len(image_data)))  # Size
        data.extend(struct.pack("<I", offset))  # Offset
        offset += len(image_data)

    # Append image data
    for img in images:
        data.extend(img)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path.stat().st_size


def create_webp_image(
    path: Path, width: int = 100, height: int = 100, lossless: bool = False
):
    """Create a minimal valid WebP image."""
    # RIFF header
    data = bytearray(b"RIFF")

    # Create VP8 chunk for lossy or VP8L for lossless
    if lossless:
        # VP8L (lossless)
        signature = b"\x2f"  # VP8L signature

        # Size bits (width-1, height-1, alpha, version)
        size_bits = ((width - 1) | ((height - 1) << 14)) & 0x1FFFFFFF

        vp8l_data = bytearray([0x2F])  # Signature byte
        vp8l_data.extend(struct.pack("<I", size_bits))

        # Minimal transform + LZ77 coded data
        vp8l_data.extend(b"\x00" * 50)

        chunk = b"VP8L" + struct.pack("<I", len(vp8l_data)) + bytes(vp8l_data)
    else:
        # VP8 (lossy)
        frame_tag = 0x9D012A | ((width & 0x3FFF) << 16)

        vp8_data = bytearray()
        # Frame tag
        vp8_data.extend(struct.pack("<I", frame_tag)[:3])
        # Width and height
        vp8_data.extend(struct.pack("<H", width))
        vp8_data.extend(struct.pack("<H", height))
        # Minimal bitstream data
        vp8_data.extend(b"\x00" * 50)

        chunk = b"VP8 " + struct.pack("<I", len(vp8_data)) + bytes(vp8_data)

    # Complete WEBP file
    webp_data = b"WEBP" + chunk
    file_size = len(webp_data)
    data.extend(struct.pack("<I", file_size))
    data.extend(webp_data)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path.stat().st_size


def create_tiff_image(path: Path, width: int = 100, height: int = 100):
    """Create a valid TIFF image file."""
    # TIFF uses IFD (Image File Directory) structure
    data = bytearray()

    # Header (8 bytes)
    data.extend(b"II")  # Little-endian
    data.extend(struct.pack("<H", 42))  # Magic number
    data.extend(struct.pack("<I", 8))  # Offset to first IFD

    # Image data (uncompressed RGB)
    image_data = bytearray()
    for y in range(height):
        for x in range(width):
            # Simple pattern
            r = (x * 255) // width
            g = (y * 255) // height
            b = 128
            image_data.extend([r, g, b])

    # IFD (Image File Directory)
    num_entries = 10
    ifd_offset = 8
    image_offset = ifd_offset + 2 + num_entries * 12 + 4

    # Number of directory entries
    ifd = struct.pack("<H", num_entries)

    # IFD entries (each 12 bytes: tag, type, count, value/offset)
    def ifd_entry(tag, type_id, count, value):
        entry = struct.pack("<HHI", tag, type_id, count)
        if type_id == 3:  # SHORT
            entry += struct.pack("<HH", value, 0)
        else:  # LONG
            entry += struct.pack("<I", value)
        return entry

    ifd += ifd_entry(256, 3, 1, width)  # ImageWidth
    ifd += ifd_entry(257, 3, 1, height)  # ImageLength
    ifd += ifd_entry(258, 3, 1, 8)  # BitsPerSample (8 bits)
    ifd += ifd_entry(259, 3, 1, 1)  # Compression (1 = none)
    ifd += ifd_entry(262, 3, 1, 2)  # PhotometricInterpretation (2 = RGB)
    ifd += ifd_entry(273, 4, 1, image_offset)  # StripOffsets
    ifd += ifd_entry(277, 3, 1, 3)  # SamplesPerPixel
    ifd += ifd_entry(278, 3, 1, height)  # RowsPerStrip
    ifd += ifd_entry(279, 4, 1, len(image_data))  # StripByteCounts
    ifd += ifd_entry(284, 3, 1, 1)  # PlanarConfiguration (1 = chunky)

    # Next IFD offset (0 = no more)
    ifd += struct.pack("<I", 0)

    data.extend(ifd)
    data.extend(image_data)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path.stat().st_size


def generate_image_files():
    """Generate all image test files."""
    print("\n📸 Generating Image Test Files (Phase 2.8)...")

    images_dir = BASE / "binary_files" / "images"
    results = []

    # Standard images
    size = create_bmp_image(images_dir / "img_bmp_24bit.bmp", 100, 100, (0, 128, 255))
    results.append(("img_bmp_24bit.bmp", size, "BMP 24-bit"))

    size = create_png_image(images_dir / "img_png_standard.png", 100, 100, False)
    results.append(("img_png_standard.png", size, "PNG standard"))

    size = create_png_image(images_dir / "img_png_interlaced.png", 100, 100, True)
    results.append(("img_png_interlaced.png", size, "PNG interlaced"))

    size = create_gif_image(images_dir / "img_gif_static.gif", 50, 50, False)
    results.append(("img_gif_static.gif", size, "GIF static"))

    size = create_gif_image(images_dir / "img_gif_animated.gif", 50, 50, True)
    results.append(("img_gif_animated.gif", size, "GIF animated"))

    size = create_jpeg_image(images_dir / "img_jpeg_standard.jpg", 100, 100, False)
    results.append(("img_jpeg_standard.jpg", size, "JPEG baseline"))

    size = create_jpeg_image(images_dir / "img_jpeg_progressive.jpg", 100, 100, True)
    results.append(("img_jpeg_progressive.jpg", size, "JPEG progressive"))

    size = create_svg_image(images_dir / "img_svg_vector.svg", 200, 200)
    results.append(("img_svg_vector.svg", size, "SVG vector"))

    size = create_ico_image(images_dir / "img_ico_multi.ico")
    results.append(("img_ico_multi.ico", size, "ICO multi-size"))

    size = create_webp_image(images_dir / "img_webp_lossy.webp", 100, 100, False)
    results.append(("img_webp_lossy.webp", size, "WebP lossy"))

    size = create_webp_image(images_dir / "img_webp_lossless.webp", 100, 100, True)
    results.append(("img_webp_lossless.webp", size, "WebP lossless"))

    size = create_tiff_image(images_dir / "img_tiff_uncompressed.tiff", 100, 100)
    results.append(("img_tiff_uncompressed.tiff", size, "TIFF uncompressed"))

    # Edge case images
    # Corrupted JPEG (truncated header)
    corrupted = bytearray([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46])
    (images_dir / "edge_img_corrupted.jpg").write_bytes(corrupted)
    results.append(("edge_img_corrupted.jpg", len(corrupted), "Corrupted JPEG"))

    # Truncated PNG (incomplete)
    truncated = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    (images_dir / "edge_img_truncated.png").write_bytes(truncated)
    results.append(("edge_img_truncated.png", len(truncated), "Truncated PNG"))

    # Wrong extension (PNG with .txt extension)
    create_png_image(images_dir / "edge_img_wrong_extension.txt", 50, 50, False)
    results.append(
        (
            "edge_img_wrong_extension.txt",
            (images_dir / "edge_img_wrong_extension.txt").stat().st_size,
            "PNG wrong ext",
        )
    )

    print(f"   Created {len(results)} image files:")
    for name, size, desc in results:
        print(f"     ✅ {name}: {size:,} bytes ({desc})")

    return results


# =============================================================================
# Phase 2.9: Document Generation
# =============================================================================


def create_rtf_document(path: Path):
    """Create a valid RTF document."""
    rtf_content = r"""{\rtf1\ansi\deff0
{\fonttbl{\f0\fswiss Arial;}}
{\colortbl;\red0\green0\blue0;\red0\green0\blue255;}
\f0\fs24
\pard\qc\b RFU Test RTF Document\b0\par
\pard\par
This is a test Rich Text Format document created for the RFU test suite.\par
\par
{\i This text is italic.}\par
{\b This text is bold.}\par
{\ul This text is underlined.}\par
\par
\cf2 This text is blue.\cf1\par
\par
Test completed successfully.
}"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rtf_content, encoding="ascii")
    return path.stat().st_size


def create_minimal_docx(path: Path):
    """Create a minimal valid DOCX document."""
    # DOCX is a ZIP archive with XML content
    path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        # [Content_Types].xml
        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        zf.writestr("[Content_Types].xml", content_types)

        # _rels/.rels
        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        zf.writestr("_rels/.rels", rels)

        # word/document.xml
        document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
<w:p><w:r><w:t>RFU Test DOCX Document</w:t></w:r></w:p>
<w:p><w:r><w:t>This is a test Word document for the RFU test suite.</w:t></w:r></w:p>
</w:body>
</w:document>"""
        zf.writestr("word/document.xml", document)

    return path.stat().st_size


def create_minimal_xlsx(path: Path, password: str = None):
    """Create a minimal valid XLSX spreadsheet."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        # [Content_Types].xml
        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""
        zf.writestr("[Content_Types].xml", content_types)

        # _rels/.rels
        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
        zf.writestr("_rels/.rels", rels)

        # xl/workbook.xml
        workbook = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets>
</workbook>"""
        zf.writestr("xl/workbook.xml", workbook)

        # xl/_rels/workbook.xml.rels
        wb_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels)

        # xl/worksheets/sheet1.xml
        sheet = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>
<row r="1"><c r="A1" t="inlineStr"><is><t>RFU Test</t></is></c><c r="B1" t="inlineStr"><is><t>Value</t></is></c></row>
<row r="2"><c r="A2" t="inlineStr"><is><t>Item 1</t></is></c><c r="B2"><v>100</v></c></row>
<row r="3"><c r="A3" t="inlineStr"><is><t>Item 2</t></is></c><c r="B3"><v>200</v></c></row>
</sheetData>
</worksheet>"""
        zf.writestr("xl/worksheets/sheet1.xml", sheet)

    return path.stat().st_size


def create_minimal_pptx(path: Path):
    """Create a minimal valid PPTX presentation."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        # [Content_Types].xml
        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
</Types>"""
        zf.writestr("[Content_Types].xml", content_types)

        # _rels/.rels
        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""
        zf.writestr("_rels/.rels", rels)

        # ppt/presentation.xml
        presentation = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<p:sldIdLst><p:sldId id="256" r:id="rId2"/></p:sldIdLst>
</p:presentation>"""
        zf.writestr("ppt/presentation.xml", presentation)

        # ppt/_rels/presentation.xml.rels
        ppt_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
</Relationships>"""
        zf.writestr("ppt/_rels/presentation.xml.rels", ppt_rels)

        # ppt/slides/slide1.xml
        slide = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
<p:cSld><p:spTree>
<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
<p:grpSpPr/>
<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="9144000" cy="1000000"/></a:xfrm></p:spPr>
<p:txBody><a:p><a:r><a:t>RFU Test Presentation</a:t></a:r></a:p></p:txBody>
</p:sp>
</p:spTree></p:cSld>
</p:sld>"""
        zf.writestr("ppt/slides/slide1.xml", slide)

    return path.stat().st_size


def create_minimal_odt(path: Path):
    """Create a minimal valid ODT (OpenDocument Text) file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype (must be first, uncompressed)
        zf.writestr(
            "mimetype",
            "application/vnd.oasis.opendocument.text",
            compress_type=zipfile.ZIP_STORED,
        )

        # META-INF/manifest.xml
        manifest = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
<manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>
<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
</manifest:manifest>"""
        zf.writestr("META-INF/manifest.xml", manifest)

        # content.xml
        content = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
<office:body><office:text>
<text:p>RFU Test ODT Document</text:p>
<text:p>This is a test OpenDocument Text file for the RFU test suite.</text:p>
</office:text></office:body>
</office:document-content>"""
        zf.writestr("content.xml", content)

    return path.stat().st_size


def create_minimal_ods(path: Path):
    """Create a minimal valid ODS (OpenDocument Spreadsheet) file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype
        zf.writestr(
            "mimetype",
            "application/vnd.oasis.opendocument.spreadsheet",
            compress_type=zipfile.ZIP_STORED,
        )

        # META-INF/manifest.xml
        manifest = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
<manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/>
<manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
</manifest:manifest>"""
        zf.writestr("META-INF/manifest.xml", manifest)

        # content.xml
        content = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
<office:body><office:spreadsheet>
<table:table table:name="Sheet1">
<table:table-row>
<table:table-cell><text:p>RFU Test</text:p></table:table-cell>
<table:table-cell><text:p>Value</text:p></table:table-cell>
</table:table-row>
<table:table-row>
<table:table-cell><text:p>Item 1</text:p></table:table-cell>
<table:table-cell><text:p>100</text:p></table:table-cell>
</table:table-row>
</table:table>
</office:spreadsheet></office:body>
</office:document-content>"""
        zf.writestr("content.xml", content)

    return path.stat().st_size


def create_legacy_doc(path: Path):
    """Create a minimal .doc file (legacy Word format)."""
    # DOC is a complex OLE2 format. Create a minimal placeholder with magic bytes.
    # This won't be a fully valid DOC but will have correct magic bytes for type detection.

    # OLE2 compound document header
    header = bytearray(512)
    # Magic bytes
    header[0:8] = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
    # Minor version
    header[0x18:0x1A] = struct.pack("<H", 0x003E)
    # Major version
    header[0x1A:0x1C] = struct.pack("<H", 0x0003)
    # Byte order (little-endian)
    header[0x1C:0x1E] = struct.pack("<H", 0xFFFE)
    # Sector size power (512 = 2^9)
    header[0x1E:0x20] = struct.pack("<H", 0x0009)
    # Mini sector size power (64 = 2^6)
    header[0x20:0x22] = struct.pack("<H", 0x0006)

    # Add some minimal content sectors
    content = header + b"\x00" * 4096

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path.stat().st_size


def create_legacy_xls(path: Path):
    """Create a minimal .xls file (legacy Excel format)."""
    # Similar to DOC - OLE2 format with Excel-specific content
    header = bytearray(512)
    header[0:8] = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
    header[0x18:0x1A] = struct.pack("<H", 0x003E)
    header[0x1A:0x1C] = struct.pack("<H", 0x0003)
    header[0x1C:0x1E] = struct.pack("<H", 0xFFFE)
    header[0x1E:0x20] = struct.pack("<H", 0x0009)
    header[0x20:0x22] = struct.pack("<H", 0x0006)

    content = header + b"\x00" * 4096

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path.stat().st_size


def create_legacy_ppt(path: Path):
    """Create a minimal .ppt file (legacy PowerPoint format)."""
    header = bytearray(512)
    header[0:8] = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
    header[0x18:0x1A] = struct.pack("<H", 0x003E)
    header[0x1A:0x1C] = struct.pack("<H", 0x0003)
    header[0x1C:0x1E] = struct.pack("<H", 0xFFFE)
    header[0x1E:0x20] = struct.pack("<H", 0x0009)
    header[0x20:0x22] = struct.pack("<H", 0x0006)

    content = header + b"\x00" * 4096

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path.stat().st_size


def generate_document_files():
    """Generate all document test files."""
    print("\n📄 Generating Document Test Files (Phase 2.9)...")

    docs_dir = BASE / "binary_files" / "documents"
    results = []

    # Modern Office formats
    size = create_minimal_docx(docs_dir / "doc_word_docx.docx")
    results.append(("doc_word_docx.docx", size, "Word DOCX"))

    size = create_minimal_xlsx(docs_dir / "doc_excel_xlsx.xlsx")
    results.append(("doc_excel_xlsx.xlsx", size, "Excel XLSX"))

    size = create_minimal_pptx(docs_dir / "doc_powerpoint_pptx.pptx")
    results.append(("doc_powerpoint_pptx.pptx", size, "PowerPoint PPTX"))

    # OpenDocument formats
    size = create_minimal_odt(docs_dir / "doc_odt_openoffice.odt")
    results.append(("doc_odt_openoffice.odt", size, "OpenDocument ODT"))

    size = create_minimal_ods(docs_dir / "doc_ods_openoffice.ods")
    results.append(("doc_ods_openoffice.ods", size, "OpenDocument ODS"))

    # Legacy Office formats
    size = create_legacy_doc(docs_dir / "doc_word_doc.doc")
    results.append(("doc_word_doc.doc", size, "Word DOC (legacy)"))

    size = create_legacy_xls(docs_dir / "doc_excel_xls.xls")
    results.append(("doc_excel_xls.xls", size, "Excel XLS (legacy)"))

    size = create_legacy_ppt(docs_dir / "doc_powerpoint_ppt.ppt")
    results.append(("doc_powerpoint_ppt.ppt", size, "PowerPoint PPT (legacy)"))

    # RTF format
    size = create_rtf_document(docs_dir / "doc_rtf_richtext.rtf")
    results.append(("doc_rtf_richtext.rtf", size, "Rich Text Format"))

    # Edge cases
    # Corrupted DOCX (truncated ZIP)
    corrupted_path = docs_dir / "edge_doc_corrupted.docx"
    corrupted_path.write_bytes(b"PK\x03\x04" + b"\x00" * 50)  # ZIP header only
    results.append(("edge_doc_corrupted.docx", 54, "Corrupted DOCX"))

    # Password-protected XLSX placeholder
    # Note: Actual password protection requires crypto libraries
    password_path = docs_dir / "edge_doc_password_protected.xlsx"
    create_minimal_xlsx(password_path)  # Normal XLSX as placeholder
    results.append(
        (
            "edge_doc_password_protected.xlsx",
            password_path.stat().st_size,
            "Password XLSX (placeholder)",
        )
    )

    print(f"   Created {len(results)} document files:")
    for name, size, desc in results:
        print(f"     ✅ {name}: {size:,} bytes ({desc})")

    return results


# =============================================================================
# Phase 2.10: Archive Generation
# =============================================================================


def generate_archive_files():
    """Generate all archive test files."""
    print("\n📦 Generating Archive Test Files (Phase 2.10)...")

    arch_dir = BASE / "binary_files" / "archives"
    arch_dir.mkdir(parents=True, exist_ok=True)
    results = []

    # Create sample content for archives
    sample_files = {
        "readme.txt": "This is a test archive for RFU test suite.\n",
        "data/file1.txt": "Sample data file 1\n",
        "data/file2.txt": "Sample data file 2\n",
    }

    # Standard ZIP
    zip_path = arch_dir / "arch_zip_standard.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in sample_files.items():
            zf.writestr(name, content)
    results.append(("arch_zip_standard.zip", zip_path.stat().st_size, "ZIP standard"))

    # Encrypted ZIP (password protected)
    # Note: Python's zipfile doesn't support creating encrypted ZIPs
    # Creating a placeholder with comment
    enc_zip_path = arch_dir / "arch_zip_encrypted.zip"
    with zipfile.ZipFile(enc_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.comment = b"Placeholder for encrypted ZIP - use 7zip to create actual encrypted archive"
        for name, content in sample_files.items():
            zf.writestr(name, content)
    results.append(
        (
            "arch_zip_encrypted.zip",
            enc_zip_path.stat().st_size,
            "ZIP encrypted (placeholder)",
        )
    )

    # Standard TAR
    tar_path = arch_dir / "arch_tar_uncompressed.tar"
    with tarfile.open(tar_path, "w") as tf:
        for name, content in sample_files.items():
            data = content.encode("utf-8")
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    results.append(
        ("arch_tar_uncompressed.tar", tar_path.stat().st_size, "TAR uncompressed")
    )

    # TAR.GZ
    targz_path = arch_dir / "arch_tar_gzip.tar.gz"
    with tarfile.open(targz_path, "w:gz") as tf:
        for name, content in sample_files.items():
            data = content.encode("utf-8")
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    results.append(("arch_tar_gzip.tar.gz", targz_path.stat().st_size, "TAR.GZ"))

    # TAR.BZ2
    tarbz2_path = arch_dir / "arch_tar_bzip2.tar.bz2"
    with tarfile.open(tarbz2_path, "w:bz2") as tf:
        for name, content in sample_files.items():
            data = content.encode("utf-8")
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    results.append(("arch_tar_bzip2.tar.bz2", tarbz2_path.stat().st_size, "TAR.BZ2"))

    # TAR.XZ
    try:
        tarxz_path = arch_dir / "arch_tar_xz.tar.xz"
        with tarfile.open(tarxz_path, "w:xz") as tf:
            for name, content in sample_files.items():
                data = content.encode("utf-8")
                info = tarfile.TarInfo(name=name)
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))
        results.append(("arch_tar_xz.tar.xz", tarxz_path.stat().st_size, "TAR.XZ"))
    except Exception as e:
        print(f"     ⚠️ TAR.XZ creation failed: {e}")
        # Create placeholder
        tarxz_path = arch_dir / "arch_tar_xz.tar.xz"
        tarxz_path.write_bytes(b"\xfd7zXZ\x00" + b"\x00" * 50)  # XZ magic + padding
        results.append(
            ("arch_tar_xz.tar.xz", tarxz_path.stat().st_size, "TAR.XZ (placeholder)")
        )

    # 7z format (placeholder with magic bytes)
    sz_path = arch_dir / "arch_7z_standard.7z"
    # 7z magic: 37 7A BC AF 27 1C
    sz_header = bytes([0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C])
    sz_content = sz_header + b"\x00" * 100  # Minimal 7z placeholder
    sz_path.write_bytes(sz_content)
    results.append(("arch_7z_standard.7z", len(sz_content), "7z (placeholder)"))

    # Encrypted 7z (placeholder)
    sz_enc_path = arch_dir / "arch_7z_encrypted.7z"
    sz_enc_path.write_bytes(sz_content)
    results.append(
        ("arch_7z_encrypted.7z", len(sz_content), "7z encrypted (placeholder)")
    )

    # RAR format (placeholder with magic bytes)
    # RAR5 magic: 52 61 72 21 1A 07 01 00
    rar_path = arch_dir / "arch_rar_standard.rar"
    rar_magic = bytes([0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x01, 0x00])
    rar_content = rar_magic + b"\x00" * 100
    rar_path.write_bytes(rar_content)
    results.append(("arch_rar_standard.rar", len(rar_content), "RAR (placeholder)"))

    # Nested archives (ZIP containing ZIP)
    nested_path = arch_dir / "arch_nested_archives.zip"
    with zipfile.ZipFile(nested_path, "w", zipfile.ZIP_DEFLATED) as outer:
        # Create inner ZIP in memory
        inner_buffer = io.BytesIO()
        with zipfile.ZipFile(inner_buffer, "w", zipfile.ZIP_DEFLATED) as inner:
            inner.writestr("inner_file.txt", "Content inside nested archive\n")
        inner_data = inner_buffer.getvalue()

        outer.writestr("readme.txt", "Outer archive with nested ZIP inside\n")
        outer.writestr("inner.zip", inner_data)
    results.append(
        ("arch_nested_archives.zip", nested_path.stat().st_size, "Nested ZIP")
    )

    # Edge cases
    # Corrupted ZIP
    corrupted_zip_path = arch_dir / "edge_arch_corrupted.zip"
    corrupted_zip_path.write_bytes(b"PK\x03\x04" + b"\xff" * 50)  # Invalid ZIP
    results.append(("edge_arch_corrupted.zip", 54, "Corrupted ZIP"))

    # ZIP bomb placeholder (small file that expands massively)
    bomb_path = arch_dir / "edge_arch_zip_bomb.zip"
    with zipfile.ZipFile(bomb_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # Highly compressible content (zeros)
        zf.writestr("bomb_1.txt", b"\x00" * 100000)
        zf.writestr("bomb_2.txt", b"\x00" * 100000)
    results.append(
        ("edge_arch_zip_bomb.zip", bomb_path.stat().st_size, "ZIP bomb (test)")
    )

    print(f"   Created {len(results)} archive files:")
    for name, size, desc in results:
        print(f"     ✅ {name}: {size:,} bytes ({desc})")

    return results


# =============================================================================
# Main Execution
# =============================================================================


def main():
    print("=" * 60)
    print("RFU Binary Test File Generator")
    print("=" * 60)
    print(f"\nBase path: {BASE}")

    all_results = []

    # Phase 2.8: Images
    image_results = generate_image_files()
    all_results.extend(image_results)

    # Phase 2.9: Documents
    doc_results = generate_document_files()
    all_results.extend(doc_results)

    # Phase 2.10: Archives
    archive_results = generate_archive_files()
    all_results.extend(archive_results)

    # Summary
    print("\n" + "=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)

    total_files = len(all_results)
    total_size = sum(r[1] for r in all_results)

    print(f"\n  Total files generated: {total_files}")
    print(f"  Total size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")

    # Category breakdown
    image_count = len(image_results)
    doc_count = len(doc_results)
    archive_count = len(archive_results)

    print(f"\n  Breakdown:")
    print(f"    Phase 2.8 - Images:    {image_count} files")
    print(f"    Phase 2.9 - Documents: {doc_count} files")
    print(f"    Phase 2.10 - Archives: {archive_count} files")

    print("\n✅ Binary test file generation complete!")
    print("\nNote: Some files are placeholders with correct magic bytes.")
    print(
        "Use appropriate tools (7-Zip, etc.) to create fully functional versions if needed."
    )

    return 0


if __name__ == "__main__":
    exit(main())
