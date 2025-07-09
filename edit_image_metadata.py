import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS as PIL_TAGS
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QFileDialog,
    QMessageBox, QTreeWidgetItem
)
from PyQt5.uic import loadUi

try:
    import piexif
    import piexif.helper
except ImportError:
    print("piexif module not found. Please install it using:")
    print("pip install piexif")
    sys.exit(1)

# Combine piexif's tags with PIL's for better name resolution
ALL_KNOWN_TAGS = {
    ifd: {code: piexif.TAGS[ifd][code].get('name', f'UnknownTag_{code}')
          for code in piexif.TAGS[ifd]}
    for ifd in piexif.TAGS
}
# Add PIL tags if missing (might be duplicates, piexif takes precedence)
for code, name in PIL_TAGS.items():
    found = False
    for ifd_tags in ALL_KNOWN_TAGS.values():
        if code in ifd_tags:
            found = True
            break
    if not found:
        # Add to a default IFD like '0th' if not found anywhere
        if 0xFFFE < code:  # Treat higher codes generally
            if 'Exif' not in ALL_KNOWN_TAGS: ALL_KNOWN_TAGS['Exif'] = {}
            if code not in ALL_KNOWN_TAGS['Exif']: ALL_KNOWN_TAGS['Exif'][code] = name
        else:
            if '0th' not in ALL_KNOWN_TAGS: ALL_KNOWN_TAGS['0th'] = {}
            if code not in ALL_KNOWN_TAGS['0th']: ALL_KNOWN_TAGS['0th'][code] = name


def get_tag_name(ifd_name, tag_code):
    """Gets a human-readable tag name."""
    if ifd_name in ALL_KNOWN_TAGS and tag_code in ALL_KNOWN_TAGS[ifd_name]:
        return ALL_KNOWN_TAGS[ifd_name][tag_code]
    # Fallback using PIL tags directly by code
    return PIL_TAGS.get(tag_code, f'UnknownTag_{tag_code}')


def format_exif_value(value):
    """Formats EXIF value for display, handling bytes."""
    if isinstance(value, bytes):
        try:
            # Try decoding common text encodings
            # Strip null terminators and potential whitespace padding
            return value.decode('utf-8').strip('\x00 ')
        except UnicodeDecodeError:
            # Handle specific known byte structures or return hex/repr
            if len(value) > 16:  # Avoid huge hex strings
                return f'{value[:16].hex()}... (bytes)'
            else:
                return f'{value.hex()} (bytes)' # Or repr(value)
    elif isinstance(value, tuple) and all(isinstance(x, int) for x in value):
        # Often represents rational (num, den), display as fraction or float
        if len(value) == 2 and value[1] != 0:
            # Heuristic: If den is 1 or num/den is simple float, show float
            if value[1] == 1:
                return str(value[0])
            # Show as fraction for typical EXIF rationals (exposure, aperture)
            # Avoid float conversion for precision (e.g., 1/3)
            return f"{value[0]}/{value[1]}"
        else:
            # Other tuples just show as string representation
            return str(value)
    # Handle other types like int, float, str directly
    return str(value)


def parse_exif_value(value_str, original_type, tag_code):
    """Attempts to parse string input back to appropriate EXIF type."""
    # Simple heuristic based on original type
    if isinstance(original_type, bytes):
        # Try encoding back to UTF-8, common for text tags stored as bytes
        # Some tags (e.g., UserComment) have specific encoding prefixes
        if tag_code == piexif.ExifIFD.UserComment:
            # Needs encoding preamble (e.g., ASCII\x00\x00\x00...)
            # Piexif helper handles this if given a string
            return value_str # Let piexif.helper.UserComment.dump handle it
        try:
            # Assume UTF-8 is the most likely intended encoding for editable strings
            return value_str.encode('utf-8')
        except Exception:
            raise ValueError(f"Cannot encode '{value_str}' back to bytes for this tag.")
    elif isinstance(original_type, int):
        try:
            return int(value_str)
        except ValueError:
            raise ValueError(f"Invalid integer value: '{value_str}'")
    elif isinstance(original_type, tuple) and len(original_type) == 2 and all(isinstance(x, int) for x in original_type):
        # Handle rational (fraction or float input)
        try:
            if '/' in value_str:
                num, den = map(int, value_str.split('/', 1))
                if den == 0: raise ValueError("Denominator cannot be zero")
                # TODO: Simplify fraction if needed? Piexif might handle this.
                return (num, den)
            else:
                # Try converting float to rational (might lose precision)
                # Piexif might handle float input directly for some tags?
                # For simplicity, require fraction input for now.
                # Or attempt float -> Fraction -> num/den? Requires 'fractions' module.
                f_val = float(value_str)
                # Basic float to rational - limited precision
                # Using high denominator for better precision, fractions module is better
                # from fractions import Fraction
                # frac = Fraction(f_val).limit_denominator()
                # return (frac.numerator, frac.denominator)

                # Simple conversion for basic floats
                if f_val == int(f_val):
                    return (int(f_val), 1)
                else:
                    # A common approach without fractions module, but limited
                    # Could implement a more robust float-to-rational here if needed
                    # For now, stick to requiring fraction format for non-integers
                    raise ValueError("Use fraction format (e.g., 1/100) for non-integer rational values. Float conversion is limited.")

        except ValueError as e:
            raise ValueError(f"Invalid rational value format: '{value_str}'. Use 'num/den'. Error: {e}")
    elif original_type is str: # Explicitly check for str type
        return value_str
    else:
        # Default to string if original type wasn't bytes, int, or rational tuple
        # This covers ASCII tags etc. Piexif types tags correctly on dump.
        return value_str


class ExifEditorLogic(QObject):
    """Handles loading and saving EXIF data using piexif."""
    # {ifd_name: {tag_code: {'name': name, 'value': display_value, 'original_value': raw_value, 'original_type': type}}}
    exif_data_loaded = pyqtSignal(dict)
    save_result = pyqtSignal(bool, str)  # success, message
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal() # Signal completion of load/save attempt

    def __init__(self):
        super().__init__()
        self._filepath = None
        self.original_exif_dict = None  # Store the raw loaded dict from piexif

    def load_exif(self, filepath):
        """Loads EXIF data from the specified image file."""
        self._filepath = filepath
        self.original_exif_dict = None
        processed_data = {}
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")

            # Check if it's likely an image piexif can handle (basic check)
            try:
                # Pillow check can be more robust
                img = Image.open(filepath)
                img.verify()  # Verify structure
                fmt = img.format
                img.close() # Close file handle opened by PIL
                if fmt not in ('JPEG', 'TIFF'):
                    raise ValueError(f"Unsupported format: {fmt}. Only JPEG/TIFF supported by piexif.")
                # Check if file actually has EXIF before trying piexif load
                # Pillow's _getexif() is one way, piexif.load is another
            except Exception as pil_e:
                # Could be not an image, or corrupted
                raise ValueError(f"Cannot open or verify image file: {pil_e}")

            # Load EXIF data using piexif
            self.original_exif_dict = piexif.load(filepath)

            if not self.original_exif_dict or not any(self.original_exif_dict.values()):
                # Check if dict is empty or all IFDs are empty
                self.exif_data_loaded.emit({})  # Emit empty dict to indicate no EXIF
                # self.error_occurred.emit("No EXIF data found in the image.") # Optional: signal no data
                self.finished.emit()
                return

            # Process the dictionary for display
            for ifd_name in self.original_exif_dict:
                # Skip thumbnail binary data itself, but process other IFDs like 1st (where thumbnail offset is)
                if ifd_name == 'thumbnail': continue
                if not self.original_exif_dict[ifd_name]: continue # Skip empty IFDs

                processed_data[ifd_name] = {}
                for tag_code, value in self.original_exif_dict[ifd_name].items():
                    tag_name = get_tag_name(ifd_name, tag_code)
                    display_value = format_exif_value(value)
                    processed_data[ifd_name][tag_code] = {
                        'name': tag_name,
                        'value': display_value, # Formatted value for display/editing
                        'original_value': value, # Store original raw value for type info and comparison
                        'original_type': type(value) # Store original type for parsing later
                    }

            self.exif_data_loaded.emit(processed_data)

        except FileNotFoundError as e:
            self.error_occurred.emit(str(e))
        except ValueError as e: # Catches format errors from PIL/manual checks
            self.error_occurred.emit(str(e))
        except piexif.InvalidImageDataError:
            self.error_occurred.emit(f"Invalid image data or piexif unsupported format: {os.path.basename(filepath)}")
        except PermissionError:
            self.error_occurred.emit(f"Permission denied reading file: {os.path.basename(filepath)}")
        except Exception as e:
            # Catch-all for other piexif/IO errors
            self.error_occurred.emit(f"Error loading EXIF data: {e}")
        finally:
            self.finished.emit() # Ensure finished is always emitted

    def save_exif(self, filepath, modified_data):
        """Saves the modified EXIF data back to the file."""
        try:
            if not self.original_exif_dict:
                # This shouldn't happen if load was successful and returned data, but check.
                # Maybe allow creating EXIF from scratch? More complex.
                # For now, assume we're modifying existing or adding to a file that had none.
                # If original_exif_dict is None because the file had no EXIF initially:
                if os.path.exists(filepath):
                     print("Original file had no EXIF data. Attempting to add new EXIF.")
                     self.original_exif_dict = {} # Start fresh if file exists but had no EXIF
                else:
                     raise RuntimeError("Original file path not set or file missing. Cannot save.")

            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found (was it moved/deleted?): {filepath}")

            # Create a new exif dictionary based on modifications
            # Start with a clean slate or potentially copy non-modified IFDs?
            # Let's build it from modified_data, referencing original_exif_dict for types/unchanged values
            new_exif_dict = {}

            # Populate the new dictionary with parsed values from GUI data
            for ifd_name, tags in modified_data.items():
                if ifd_name == 'thumbnail': continue # Should not be directly edited this way

                if ifd_name not in new_exif_dict:
                    new_exif_dict[ifd_name] = {}

                for tag_code, tag_info in tags.items():
                    original_value = tag_info.get('original_value', None) # Use .get for safety
                    original_type = tag_info.get('original_type', str) # Default to str if unknown
                    current_value_str = tag_info['value'] # Assumes 'value' is the potentially edited string

                    # Get original value's display string for comparison
                    # Handle case where original value didn't exist (adding new tag)
                    original_display_val = format_exif_value(original_value) if original_value is not None else None

                    # Check if value was actually modified or is new
                    if current_value_str == original_display_val and original_value is not None:
                        # Value unchanged, use original raw value
                        new_exif_dict[ifd_name][tag_code] = original_value
                    else:
                        # Value changed or is new, try to parse it back
                        try:
                            # Use original_type to guide parsing
                            parsed_value = parse_exif_value(current_value_str, original_type(), tag_code) # Call type() if stored as type object

                            # Handle specific helper cases (like UserComment) after parsing
                            if tag_code == piexif.ExifIFD.UserComment and isinstance(parsed_value, str):
                                # Dump using helper to add encoding prefix etc.
                                new_exif_dict[ifd_name][tag_code] = piexif.helper.UserComment.dump(parsed_value)
                            else:
                                new_exif_dict[ifd_name][tag_code] = parsed_value
                        except ValueError as e:
                            # Provide context for the parsing error
                            tag_name_for_error = get_tag_name(ifd_name, tag_code)
                            raise ValueError(f"Error parsing value for tag '{tag_name_for_error}' ({ifd_name}/{tag_code}): {e}")

            # Preserve original thumbnail if it exists
            if 'thumbnail' in self.original_exif_dict and self.original_exif_dict['thumbnail']:
                new_exif_dict['thumbnail'] = self.original_exif_dict['thumbnail']
            else:
                # Ensure thumbnail key exists but is None if no thumbnail originally
                new_exif_dict['thumbnail'] = None # piexif needs the key

            # Remove empty IFDs before dumping (except potentially thumbnail which might be None)
            ifds_to_remove = [ifd for ifd, tags in new_exif_dict.items() if not tags and ifd != 'thumbnail']
            for ifd in ifds_to_remove:
                del new_exif_dict[ifd]

            # If all IFDs (except potentially thumbnail) are empty, dump an empty dict essentially
            # piexif.dump({}) works, piexif.insert(b'Exif\\x00\\x00MM\\x00*\\x00\\x00\\x00\\x08\\x00\\x00', filepath) might remove exif

            exif_bytes = b'' # Default to empty bytes
            if any(ifd != 'thumbnail' and tags for ifd, tags in new_exif_dict.items()) or new_exif_dict.get('thumbnail') is not None:
                 # Only dump if there's actual data or a thumbnail to preserve/add
                try:
                    exif_bytes = piexif.dump(new_exif_dict)
                except Exception as dump_e:
                    raise ValueError(f"Error converting data to EXIF format: {dump_e}")


            # Insert the bytes back into the image file
            # If exif_bytes is empty (b''), piexif.insert should remove existing EXIF
            try:
                piexif.insert(exif_bytes, filepath)
                if not exif_bytes:
                    self.save_result.emit(True, f"All EXIF data removed from {os.path.basename(filepath)}.")
                else:
                    self.save_result.emit(True, f"EXIF data successfully saved to {os.path.basename(filepath)}.")
            except Exception as insert_e:
                 # Catch potential errors during file writing/insertion
                 raise IOError(f"Error writing EXIF data to file: {insert_e}")


        except FileNotFoundError as e:
            self.error_occurred.emit(str(e))
            self.save_result.emit(False, str(e))
        except ValueError as e: # Catches parsing errors, dump errors
            self.error_occurred.emit(str(e))
            self.save_result.emit(False, str(e))
        except RuntimeError as e: # Catches logic errors like original data not loaded
            self.error_occurred.emit(str(e))
            self.save_result.emit(False, str(e))
        except piexif.InvalidImageDataError:
            err_msg = f"Invalid image data or unsupported format for saving: {os.path.basename(filepath)}"
            self.error_occurred.emit(err_msg)
            self.save_result.emit(False, err_msg)
        except PermissionError:
            err_msg = f"Permission denied writing file: {os.path.basename(filepath)}"
            self.error_occurred.emit(err_msg)
            self.save_result.emit(False, err_msg)
        except IOError as e: # Catches file writing errors during insert
             err_msg = f"File writing error: {e}"
             self.error_occurred.emit(err_msg)
             self.save_result.emit(False, err_msg)
        except Exception as e:
            err_msg = f"An unexpected error occurred during saving: {e}"
            self.error_occurred.emit(err_msg)
            self.save_result.emit(False, err_msg)
        finally:
            self.finished.emit() # Ensure finished is always emitted

class ImageMetadataEditor(BaseWindow):
    def __init__(self):
        super().__init__()
        # Load the UI
        uifile_path = os.path.join(os.path.dirname(__file__), "edit_image_metadata.ui")
        loadUi(uifile_path, self)
        
        # Initialize the logic handler
        self.exif_logic = ExifEditorLogic()
        
        # Connect signals from logic
        self.exif_logic.exif_data_loaded.connect(self.update_exif_view)
        self.exif_logic.save_result.connect(self.handle_save_result)
        self.exif_logic.error_occurred.connect(self.show_error)
        self.exif_logic.finished.connect(self.handle_operation_finished)
        
        # Connect UI signals
        self.actionOpen.triggered.connect(self.browse_file)
        self.actionSave.triggered.connect(self.save_changes)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.show_about)
        self.browseButton.clicked.connect(self.browse_file)
        self.saveButton.clicked.connect(self.save_changes)
        
        # Setup tree widget
        self.exifTreeWidget.itemChanged.connect(self.handle_item_changed)
        self.current_file = None
        self.modified_data = {}
        
    def browse_file(self):
        filepath, _ = get_open_file_name(
            self,
            "Select Image File",
            "",
            "Images (*.jpg *.jpeg *.tif *.tiff);;All Files (*.*)"
        )
        if filepath:
            self.current_file = filepath
            self.filePathEdit.setText(filepath)
            self.exif_logic.load_exif(filepath)
            
    def update_exif_view(self, exif_data):
        self.exifTreeWidget.clear()
        self.modified_data = exif_data
        
        if not exif_data:
            self.saveButton.setEnabled(False)
            self.actionSave.setEnabled(False)
            return
            
        for ifd_name, tags in exif_data.items():
            ifd_item = QTreeWidgetItem([ifd_name, "", ""])
            self.exifTreeWidget.addTopLevelItem(ifd_item)
            
            for tag_code, tag_info in tags.items():
                tag_item = QTreeWidgetItem([
                    "",
                    tag_info['name'],
                    tag_info['value']
                ])
                tag_item.setData(1, Qt.UserRole, (ifd_name, tag_code))
                tag_item.setFlags(tag_item.flags() | Qt.ItemIsEditable)
                ifd_item.addChild(tag_item)
                
        self.exifTreeWidget.expandAll()
        self.saveButton.setEnabled(True)
        self.actionSave.setEnabled(True)
        
    def handle_item_changed(self, item, column):
        if column == 2 and item.data(1, Qt.UserRole):  # Only handle value column changes
            ifd_name, tag_code = item.data(1, Qt.UserRole)
            new_value = item.text(column)
            if ifd_name in self.modified_data and tag_code in self.modified_data[ifd_name]:
                self.modified_data[ifd_name][tag_code]['value'] = new_value
                
    def save_changes(self):
        if self.current_file and self.modified_data:
            self.exif_logic.save_exif(self.current_file, self.modified_data)
            
    def handle_save_result(self, success, message):
        if success:
            show_info_dialogself, "Success", message
        else:
            show_error_dialogself, "Error", message
            
    def show_error(self, message):
        show_error_dialogself, "Error", message
        
    def handle_operation_finished(self):
        # Could add a progress bar or status message here if needed
        pass
        
    def show_about(self):
        QMessageBox.about(
            self,
            "About Image Metadata Editor",
            "Image Metadata Editor\n\n"
            "A tool to view and edit EXIF metadata in images.\n"
            "Supports JPEG and TIFF formats."
        )

def main():
    app = QApplication(sys.argv)
    window = ImageMetadataEditor()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()