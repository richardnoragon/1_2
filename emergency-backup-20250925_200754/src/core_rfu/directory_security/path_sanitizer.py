"""
Path Sanitizer for RFU Hub

Sanitizes directory paths to prevent security vulnerabilities
while preserving functionality.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import os
import re
import logging
from typing import Optional


class PathSanitizer:
    """
    Sanitizes directory paths to prevent security vulnerabilities
    while preserving functionality.
    """

    def __init__(self):
        """Initialize PathSanitizer"""
        self.replacement_char = "_"
        self.max_component_length = 255
        self.logger = logging.getLogger("RFU.PathSanitizer")

        self.logger.info("PathSanitizer initialized successfully")

    def sanitize_path(self, directory_path: str) -> str:
        """
        Sanitize directory path for safe storage and usage

        Args:
            directory_path: Raw directory path

        Returns:
            Sanitized directory path
        """
        try:
            if not directory_path:
                return ""

            # Remove null bytes
            sanitized = directory_path.replace("\x00", "")

            # Remove control characters (except for newlines/tabs that we'll handle)
            sanitized = "".join(
                char
                for char in sanitized
                if ord(char) >= 32 or char in ["\n", "\t"]
            )

            # Replace dangerous characters
            dangerous_chars = ["<", ">", "|", "*", "?", '"']
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, self.replacement_char)

            # Remove any remaining control characters
            sanitized = sanitized.replace("\n", "").replace("\t", "")

            # Normalize path separators
            sanitized = sanitized.replace("\\", os.sep).replace("/", os.sep)

            # Remove multiple consecutive separators
            while os.sep + os.sep in sanitized:
                sanitized = sanitized.replace(os.sep + os.sep, os.sep)

            # Split into components and process each
            components = sanitized.split(os.sep)
            processed_components = []

            for i, comp in enumerate(components):
                # Handle drive letters on Windows (preserve them)
                if i == 0 and len(comp) == 2 and comp.endswith(":"):
                    processed_components.append(comp)
                    continue

                # Handle empty components (preserve root separator)
                if not comp:
                    if i == 0:  # Root component
                        processed_components.append(comp)
                    continue

                # Remove leading/trailing whitespace
                comp = comp.strip()

                # Skip empty components after stripping
                if not comp:
                    continue

                # Remove dangerous prefixes/suffixes
                comp = self._sanitize_component(comp)

                # Limit component length
                if len(comp) > self.max_component_length:
                    comp = comp[: self.max_component_length]

                # Ensure component is not empty after processing
                if comp:
                    processed_components.append(comp)

            # Reconstruct path
            if not processed_components:
                return ""

            sanitized = os.sep.join(processed_components)

            # Normalize the final path
            try:
                sanitized = os.path.normpath(sanitized)
            except (ValueError, TypeError):
                # If normalization fails, return the manually processed path
                pass

            return sanitized

        except Exception as e:
            self.logger.error(f"Path sanitization failed: {e}")
            # Return a safe fallback
            return self._create_safe_fallback(directory_path)

    def sanitize_for_display(self, directory_path: str) -> str:
        """
        Sanitize path for safe display in UI (additional anonymization)

        Args:
            directory_path: Directory path to sanitize for display

        Returns:
            Display-safe directory path
        """
        try:
            if not directory_path:
                return ""

            # Basic sanitization
            sanitized = self.sanitize_path(directory_path)

            # Replace user-specific information
            sanitized = self._anonymize_user_info(sanitized)

            # Truncate very long paths for display
            if len(sanitized) > 100:
                # Keep beginning and end, replace middle
                start = sanitized[:50]
                end = sanitized[-47:]
                sanitized = f"{start}...{end}"

            return sanitized

        except Exception as e:
            self.logger.error(f"Display sanitization failed: {e}")
            return "***SANITIZATION_ERROR***"

    def sanitize_for_logging(self, directory_path: str) -> str:
        """
        Sanitize path for safe logging (maximum anonymization)

        Args:
            directory_path: Directory path to sanitize for logging

        Returns:
            Log-safe directory path with anonymization
        """
        try:
            if not directory_path:
                return ""

            # Basic sanitization
            sanitized = self.sanitize_path(directory_path)

            # Heavy anonymization for logging
            sanitized = self._anonymize_for_logging(sanitized)

            return sanitized

        except Exception as e:
            self.logger.error(f"Logging sanitization failed: {e}")
            return "***LOG_SANITIZATION_ERROR***"

    def _sanitize_component(self, component: str) -> str:
        """Sanitize individual path component"""

        # Remove leading/trailing dots (except for legitimate hidden files)
        if component.startswith(".."):
            component = self.replacement_char + component[2:]
        elif component == ".":
            component = self.replacement_char

        # Remove trailing dots and spaces (Windows compatibility)
        component = component.rstrip(". ")

        # Handle reserved names on Windows
        windows_reserved = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]

        if component.upper() in windows_reserved:
            component = f"{component}{self.replacement_char}"

        # Remove any remaining dangerous characters
        component = re.sub(r'[<>:"|?*]', self.replacement_char, component)

        return component

    def _anonymize_user_info(self, path: str) -> str:
        """Anonymize user-specific information in paths"""

        if not path:
            return path

        # Replace username in common patterns

        # Windows user paths
        path = re.sub(
            r"\\Users\\[^\\]+\\",
            "\\Users\\[USER]\\",
            path,
            flags=re.IGNORECASE,
        )

        # Linux/macOS user paths
        path = re.sub(r"/home/[^/]+/", "/home/[USER]/", path)
        path = re.sub(r"/Users/[^/]+/", "/Users/[USER]/", path)

        return path

    def _anonymize_for_logging(self, path: str) -> str:
        """Heavy anonymization for logging purposes"""

        if not path:
            return path

        # Start with user info anonymization
        anonymized = self._anonymize_user_info(path)

        # Replace potentially sensitive directory names
        components = anonymized.split(os.sep)
        anonymized_components = []

        for component in components:
            if not component:
                anonymized_components.append(component)
                continue

            # Keep drive letters and basic structure
            if (
                len(component) == 2 and component.endswith(":")
            ) or component in ["[USER]"]:
                anonymized_components.append(component)
                continue

            # Anonymize long directory names (might contain PII)
            if len(component) > 20:
                anonymized_components.append("[LONG_NAME]")
            # Anonymize numeric directory names (might be IDs)
            elif (
                any(char.isdigit() for char in component)
                and len(component) > 8
            ):
                anonymized_components.append("[NUMERIC_NAME]")
            # Anonymize hidden directories
            elif component.startswith("."):
                anonymized_components.append("[HIDDEN]")
            # Keep short, common directory names
            elif len(component) <= 8 and component.isalpha():
                anonymized_components.append(component)
            else:
                anonymized_components.append("[DIR]")

        return os.sep.join(anonymized_components)

    def _create_safe_fallback(self, original_path: str) -> str:
        """Create a safe fallback path when sanitization fails"""

        try:
            # Try to extract just the drive/root and first component
            if os.name == "nt":  # Windows
                if len(original_path) >= 3 and original_path[1] == ":":
                    return original_path[:3]  # C:\
                return "C:\\"
            else:  # Unix-like
                return "/"

        except Exception:
            # Ultimate fallback
            if os.name == "nt":
                return "C:\\"
            else:
                return "/"

    def is_path_safe(self, directory_path: str) -> bool:
        """
        Check if a path is already safe (doesn't need sanitization)

        Args:
            directory_path: Directory path to check

        Returns:
            True if path is safe, False if it needs sanitization
        """
        try:
            if not directory_path:
                return True

            # Check for dangerous characters
            dangerous_chars = ["<", ">", "|", "*", "?", '"', "\x00"]
            if any(char in directory_path for char in dangerous_chars):
                return False

            # Check for control characters
            if any(ord(char) < 32 for char in directory_path):
                return False

            # Check for path traversal
            if ".." in directory_path:
                return False

            # Check for multiple consecutive separators
            if os.sep + os.sep in directory_path:
                return False

            # Check for very long components
            components = directory_path.split(os.sep)
            if any(
                len(comp) > self.max_component_length for comp in components
            ):
                return False

            return True

        except Exception:
            return False

    def get_sanitization_report(
        self, original_path: str, sanitized_path: str
    ) -> dict:
        """
        Generate a report of sanitization changes

        Args:
            original_path: Original directory path
            sanitized_path: Sanitized directory path

        Returns:
            Dictionary with sanitization report
        """
        report = {
            "original_length": len(original_path),
            "sanitized_length": len(sanitized_path),
            "changes_made": original_path != sanitized_path,
            "length_changed": len(original_path) != len(sanitized_path),
            "dangerous_chars_removed": False,
            "path_traversal_removed": False,
            "components_modified": False,
        }

        try:
            # Check for dangerous character removal
            dangerous_chars = ["<", ">", "|", "*", "?", '"', "\x00"]
            if any(char in original_path for char in dangerous_chars):
                report["dangerous_chars_removed"] = True

            # Check for path traversal removal
            if ".." in original_path:
                report["path_traversal_removed"] = True

            # Check for component modifications
            orig_components = original_path.split(os.sep)
            san_components = sanitized_path.split(os.sep)
            if len(orig_components) != len(san_components):
                report["components_modified"] = True
            else:
                for orig, san in zip(orig_components, san_components):
                    if orig != san:
                        report["components_modified"] = True
                        break

        except Exception as e:
            report["error"] = str(e)

        return report
