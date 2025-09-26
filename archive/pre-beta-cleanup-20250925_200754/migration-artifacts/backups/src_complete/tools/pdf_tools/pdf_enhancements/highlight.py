# Import Libraries
from typing import Tuple
from io import BytesIO
import os
import argparse
import re
import fitz
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5 import uic
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

class HighlightUI(QMainWindow):
    def __init__(self):
        try:
            super(HighlightUI, self).__init__()
            uic.loadUi('highlight.ui', self)
            
            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.processButton.clicked.connect(self.process)
            self.actionExit.triggered.connect(self.close)
            self.actionCombo.currentTextChanged.connect(self.on_action_changed)
            
            # Initialize color and opacity controls
            self.colorCombo.setEnabled(True)
            self.opacitySlider.setEnabled(True)
            
            logger.info("Highlight tool initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize highlight tool: %s", str(e))
            raise
    
    def on_action_changed(self, action):
        """Enable/disable color and opacity based on action"""
        color_enabled = action not in ['Redact', 'Remove']
        self.colorCombo.setEnabled(color_enabled)
        self.opacitySlider.setEnabled(color_enabled)

    def browse_file(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self, "Select PDF file", "", "PDF Files (*.pdf)")
            if filename:
                self.inputPathEdit.setText(filename)
                self.input_file = filename
                logger.info("Selected input file: %s", filename)
                # Extract and show file info
                success, info = extract_info(filename)
                if success:
                    self.statusBar().showMessage("File loaded successfully")
                else:
                    self.statusBar().showMessage("Error loading file")
        except Exception as e:
            logger.error("Error browsing for file: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error selecting file: {str(e)}")
    
    def process(self):
        try:
            if not self.input_file:
                logger.warning("No input file selected")
                QMessageBox.warning(self, "Error", "Please select a PDF file first")
                return
            
            search_str = self.searchEdit.text()
            if not search_str:
                logger.warning("No search text provided")
                QMessageBox.warning(self, "Error", "Please enter search text")
                return
            
            # Get the action type and color
            action = self.actionCombo.currentText()
            color = self.colorCombo.currentText().lower() if action not in ['Redact', 'Remove'] else None
            opacity = self.opacitySlider.value() / 100.0 if action not in ['Redact', 'Remove'] else 1.0
            
            # Get pages if specified
            pages = None
            pages_text = self.pagesEdit.text()
            if pages_text:
                try:
                    pages = tuple(map(str, pages_text.split(',')))
                    logger.info("Processing specific pages: %s", pages)
                except:
                    logger.error("Invalid page numbers format: %s", pages_text)
                    QMessageBox.warning(self, "Error", "Invalid page numbers format")
                    return
            
            # Create output filename
            output_file = os.path.splitext(self.input_file)[0] + "_processed.pdf"
            
            try:
                logger.info("Starting PDF processing")
                logger.debug("Parameters - Input: %s, Output: %s, Search: %s, Action: %s, Color: %s, Opacity: %f, Pages: %s",
                           self.input_file, output_file, search_str, action, color, opacity, pages)
                
                process_data(
                    input_file=self.input_file,
                    output_file=output_file,
                    search_str=search_str,
                    pages=pages,
                    action=action,
                    color=color,
                    opacity=opacity
                )
                
                logger.info("Processing completed successfully")
                QMessageBox.information(self, "Success", f"File processed successfully and saved as {output_file}")
                
            except Exception as e:
                logger.error("Error during processing: %s", str(e))
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
                
        except Exception as e:
            logger.error("Error in process operation: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error in process operation: {str(e)}")

def extract_info(input_file: str):
    """
    Extracts file info
    """
    try:
        logger.info("Extracting info from: %s", input_file)
        pdfDoc = fitz.open(input_file)
        output = {
            "File": input_file, "Encrypted": ("True" if pdfDoc.isEncrypted else "False")
        }
        # If PDF is encrypted the file metadata cannot be extracted
        if not pdfDoc.isEncrypted:
            for key, value in pdfDoc.metadata.items():
                output[key] = value

        # To Display File Info
        print("## File Information ##################################################")
        print("\n".join("{}:{}".format(i, j) for i, j in output.items()))
        print("######################################################################")

        return True, output
    except Exception as e:
        logger.error("Error extracting info: %s", str(e))
        return None


def search_for_text(lines, search_str):
    """
    Search for the search string within the document lines
    """
    try:
        logger.debug("Searching for text: %s", search_str)
        for line in lines:
            # Find all matches within one line
            results = re.findall(search_str, line, re.IGNORECASE)
            # In case multiple matches within one line
            for result in results:
                logger.debug("Found match: %s", result)
                yield result
    except Exception as e:
        logger.error("Error searching text: %s", str(e))
        return []


def redact_matching_data(page, matched_values):
    """
    Redacts matching values
    """
    try:
        logger.debug("Redacting %d matches", len(matched_values))
        matches_found = 0
        # Loop throughout matching values
        for val in matched_values:
            matches_found += 1
            matching_val_area = page.searchFor(val)
            # Redact matching values
            [page.addRedactAnnot(area, text=" ", fill=(0, 0, 0))
             for area in matching_val_area]
        # Apply the redaction
        page.apply_redactions()
        logger.debug("Redaction completed")
        return matches_found
    except Exception as e:
        logger.error("Error during redaction: %s", str(e))
        return 0


def frame_matching_data(page, matched_values):
    """
    frames matching values
    """
    try:
        logger.debug("Framing %d matches", len(matched_values))
        matches_found = 0
        # Loop throughout matching values
        for val in matched_values:
            matches_found += 1
            matching_val_area = page.searchFor(val)
            for area in matching_val_area:
                if isinstance(area, fitz.fitz.Rect):
                    # Draw a rectangle around matched values
                    annot = page.addRectAnnot(area)
                    # , fill = fitz.utils.getColor('black')
                    annot.setColors(stroke=fitz.utils.getColor('red'))
                    # If you want to remove matched data
                    #page.addFreetextAnnot(area, ' ')
                    annot.update()
        logger.debug("Framing completed")
        return matches_found
    except Exception as e:
        logger.error("Error during framing: %s", str(e))
        return 0


def highlight_matching_data(page, matched_values, type, color=None, opacity=1.0):
    """
    Highlight matching values with customizable color and opacity
    """
    try:
        logger.debug("Highlighting %d matches with type '%s' and color '%s'", len(matched_values), type, color)
        matches_found = 0
        
        # Define colors (RGB values)
        color_map = {
            'yellow': (1, 1, 0),
            'red': (1, 0, 0),
            'green': (0, 1, 0),
            'blue': (0, 0, 1),
            'purple': (0.7, 0, 0.7)
        }
        
        # Get color values or default to yellow
        fill_color = color_map.get(color, (1, 1, 0))
        
        # Loop throughout matching values
        for val in matched_values:
            matches_found += 1
            matching_val_area = page.searchFor(val)
            
            highlight = None
            if type == 'Highlight':
                highlight = page.addHighlightAnnot(matching_val_area)
            elif type == 'Squiggly':
                highlight = page.addSquigglyAnnot(matching_val_area)
            elif type == 'Underline':
                highlight = page.addUnderlineAnnot(matching_val_area)
            elif type == 'Strikeout':
                highlight = page.addStrikeoutAnnot(matching_val_area)
            else:
                highlight = page.addHighlightAnnot(matching_val_area)
                
            if highlight:
                # Set color and opacity
                highlight.set_opacity(opacity)
                highlight.setColors(stroke=None, fill=fill_color)
                highlight.update()
                
        logger.debug("Highlighting completed")
        return matches_found
    except Exception as e:
        logger.error("Error during highlighting: %s", str(e))
        return 0


def process_data(input_file: str, output_file: str, search_str: str, pages: Tuple = None, action: str = 'Highlight', color: str = None, opacity: float = 1.0):
    """
    Process the pages of the PDF File
    """
    try:
        logger.info("Processing PDF file: %s", input_file)
        logger.debug("Parameters - Output: %s, Search: %s, Pages: %s, Action: %s, Color: %s, Opacity: %f",
                    output_file, search_str, pages, action, color, opacity)
        
        # Open the PDF
        pdfDoc = fitz.open(input_file)
        # Save the generated PDF to memory buffer
        output_buffer = BytesIO()
        total_matches = 0
        # Iterate through pages
        for pg in range(pdfDoc.pageCount):
            # If required for specific pages
            if pages:
                if str(pg) not in pages:
                    continue
            # Select the page
            page = pdfDoc[pg]
            # Get Matching Data
            # Split page by lines
            page_lines = page.getText("text").split('\n')
            matched_values = search_for_text(page_lines, search_str)
            if matched_values:
                if action == 'Redact':
                    matches_found = redact_matching_data(page, matched_values)
                elif action == 'Frame':
                    matches_found = frame_matching_data(page, matched_values)
                elif action in ('Highlight', 'Squiggly', 'Underline', 'Strikeout'):
                    matches_found = highlight_matching_data(
                        page, matched_values, action, color, opacity)
                else:
                    matches_found = highlight_matching_data(
                        page, matched_values, 'Highlight', color, opacity)
                total_matches += matches_found
        logger.info(f"{total_matches} Match(es) Found of Search String {search_str} In Input File: {input_file}")
        # Save to output
        pdfDoc.save(output_buffer)
        pdfDoc.close()
        # Save the output buffer to the output file
        with open(output_file, mode='wb') as f:
            f.write(output_buffer.getbuffer())
        logger.info("Processing completed successfully")
        return True
        
    except Exception as e:
        logger.error("Error processing data: %s", str(e))
        raise


def remove_highlght(input_file: str, output_file: str, pages: Tuple = None):
    try:
        logger.info("Removing highlights from: %s", input_file)
        pdfDoc = fitz.open(input_file)
        # Save the generated PDF to memory buffer
        output_buffer = BytesIO()
        # Initialize a counter for annotations
        annot_found = 0
        # Iterate through pages
        for pg in range(pdfDoc.pageCount):
            # If required for specific pages
            if pages:
                if str(pg) not in pages:
                    continue
            # Select the page
            page = pdfDoc[pg]
            annot = page.firstAnnot
            while annot:
                annot_found += 1
                page.deleteAnnot(annot)
                annot = annot.next
        if annot_found >= 0:
            logger.info(f"Annotation(s) Found In The Input File: {input_file}")
        # Save to output
        pdfDoc.save(output_buffer)
        pdfDoc.close()
        # Save the output buffer to the output file
        with open(output_file, mode='wb') as f:
            f.write(output_buffer.getbuffer())
        logger.info("Highlight removal completed successfully")
        return True
        
    except Exception as e:
        logger.error("Error removing highlights: %s", str(e))
        return False


def process_file(**kwargs):
    """
    To process one single file
    Redact, Frame, Highlight... one PDF File
    Remove Highlights from a single PDF File
    """
    try:
        logger.info("Processing single file with parameters: %s", kwargs)
        input_file = kwargs.get('input_file')
        output_file = kwargs.get('output_file')
        if output_file is None:
            output_file = input_file
        search_str = kwargs.get('search_str')
        pages = kwargs.get('pages')
        # Redact, Frame, Highlight, Squiggly, Underline, Strikeout, Remove
        action = kwargs.get('action')
        if action == "Remove":
            # Remove the Highlights except Redactions
            remove_highlght(input_file=input_file,
                            output_file=output_file, pages=pages)
        else:
            process_data(input_file=input_file, output_file=output_file,
                         search_str=search_str, pages=pages, action=action)
        return True
    except Exception as e:
        logger.error("Error in file processing: %s", str(e))
        return False


def process_folder(**kwargs):
    """
    Redact, Frame, Highlight... all PDF Files within a specified path
    Remove Highlights from all PDF Files within a specified path
    """
    try:
        logger.info("Processing folder with parameters: %s", kwargs)
        input_folder = kwargs.get('input_folder')
        search_str = kwargs.get('search_str')
        # Run in recursive mode
        recursive = kwargs.get('recursive')
        #Redact, Frame, Highlight, Squiggly, Underline, Strikeout, Remove
        action = kwargs.get('action')
        pages = kwargs.get('pages')
        # Loop though the files within the input folder.
        for foldername, dirs, filenames in os.walk(input_folder):
            for filename in filenames:
                # Check if pdf file
                if not filename.endswith('.pdf'):
                    continue
                 # PDF File found
                inp_pdf_file = os.path.join(foldername, filename)
                logger.info("Processing file: %s", inp_pdf_file)
                process_file(input_file=inp_pdf_file, output_file=None,
                             search_str=search_str, action=action, pages=pages)
            if not recursive:
                break
        return True
    except Exception as e:
        logger.error("Error in folder processing: %s", str(e))
        return False


def is_valid_path(path):
    """
    Validates the path inputted and checks whether it is a file path or a folder path
    """
    try:
        if not path:
            raise ValueError(f"Invalid Path")
        if os.path.isfile(path):
            logger.debug("Valid path: %s", path)
            return path
        elif os.path.isdir(path):
            logger.debug("Valid path: %s", path)
            return path
        else:
            raise ValueError(f"Invalid Path {path}")
    except Exception as e:
        logger.error("Error validating path: %s", str(e))
        raise


def parse_args():
    """
    Get user command line parameters
    """
    parser = argparse.ArgumentParser(description="Available Options")
    parser.add_argument('-i', '--input_path', dest='input_path', type=is_valid_path,
                        required=True, help="Enter the path of the file or the folder to process")
    parser.add_argument('-a', '--action', dest='action', choices=['Redact', 'Frame', 'Highlight', 'Squiggly', 'Underline', 'Strikeout', 'Remove'], type=str,
                        default='Highlight', help="Choose whether to Redact or to Frame or to Highlight or to Squiggly or to Underline or to Strikeout or to Remove")
    parser.add_argument('-p', '--pages', dest='pages', type=tuple,
                        help="Enter the pages to consider e.g.: [2,4]")
    action = parser.parse_known_args()[0].action
    if action != 'Remove':
        parser.add_argument('-s', '--search_str', dest='search_str'                            # lambda x: os.path.has_valid_dir_syntax(x)
                            , type=str, required=True, help="Enter a valid search string")
    path = parser.parse_known_args()[0].input_path
    if os.path.isfile(path):
        parser.add_argument('-o', '--output_file', dest='output_file', type=str  # lambda x: os.path.has_valid_dir_syntax(x)
                            , help="Enter a valid output file")
    if os.path.isdir(path):
        parser.add_argument('-r', '--recursive', dest='recursive', default=False, type=lambda x: (
            str(x).lower() in ['true', '1', 'yes']), help="Process Recursively or Non-Recursively")
    args = vars(parser.parse_args())
    # To Display The Command Line Arguments
    print("## Command Arguments #################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in args.items()))
    print("######################################################################")
    return args


def main():
    # Check if command line arguments are provided
    import sys
    if len(sys.argv) > 1:
        # Parsing command line arguments entered by user
        args = parse_args()
        # If File Path
        if os.path.isfile(args['input_path']):
            # Extracting File Info
            extract_info(input_file=args['input_path'])
            # Process a file
            process_file(
                input_file=args['input_path'], output_file=args['output_file'], 
                search_str=args['search_str'] if 'search_str' in (args.keys()) else None, 
                pages=args['pages'], action=args['action']
            )
        # If Folder Path
        elif os.path.isdir(args['input_path']):
            # Process a folder
            process_folder(
                input_folder=args['input_path'], 
                search_str=args['search_str'] if 'search_str' in (args.keys()) else None, 
                action=args['action'], pages=args['pages'], recursive=args['recursive']
            )
    else:
        # Launch the GUI
        app = QApplication(sys.argv)
        window = HighlightUI()
        logger.info("Application started")
        app.exec_()

if __name__ == "__main__":
    main()
