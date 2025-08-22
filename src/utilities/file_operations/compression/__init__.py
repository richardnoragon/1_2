"""File compression and decompression tools.

This module provides functionality for compressing and decompressing files
with support for various archive formats including ZIP, 7Z, TAR.GZ, and TAR.BZ2.
"""

from .compress_decompress import CompressDecompressApp

__all__ = ['CompressDecompressApp']