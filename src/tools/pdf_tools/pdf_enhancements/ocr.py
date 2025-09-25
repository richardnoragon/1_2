# Import Libraries
import sys
import os
import re
import argparse
import pytesseract
from pytesseract import Output
import cv2
import numpy as np
import fitz
from io import BytesIO
from PIL import Image
import pandas as pd
import filetype
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from log_config import setup_logger

# Path Of The Tesseract OCR engine
TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
# Include tesseract executable
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Set up logger
logger = setup_logger(__name__)


def pix2np(pix):
    """
    Converts a pixmap buffer into a numpy array
    """
    try:
        # pix.samples = sequence of bytes of the image pixels like RGBA
        # pix.h = height in pixels
        # pix.w = width in pixels
        # pix.n = number of components per pixel (depends on the colorspace and alpha)
        im = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.h, pix.w, pix.n
        )
        try:
            im = np.ascontiguousarray(im[..., [2, 1, 0]])  # RGB To BGR
        except IndexError:
            # Convert Gray to RGB
            im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
            im = np.ascontiguousarray(im[..., [2, 1, 0]])  # RGB To BGR
        return im
    except Exception as e:
        logger.error("Error converting pixmap to numpy array: %s", str(e))
        return None


################################################################################
# Image Pre-Processing Functions to improve output accurracy
# Convert to grayscale


def grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# Remove noise
def remove_noise(img):
    return cv2.medianBlur(img, 5)


# Thresholding
def threshold(img):
    # return cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


# dilation
def dilate(img):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(img, kernel, iterations=1)


# erosion
def erode(img):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(img, kernel, iterations=1)


# opening -- erosion followed by a dilation
def opening(img):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


# canny edge detection
def canny(img):
    return cv2.Canny(img, 100, 200)


# skew correction
def deskew(img):
    coords = np.column_stack(np.where(img > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


# template matching
def match_template(img, template):
    return cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)


def convert_img2bin(img):
    """
    Pre-processes the image and generates a binary output
    """
    # Convert the image into a grayscale image
    output_img = grayscale(img)
    # Invert the grayscale image by flipping pixel values.
    # All pixels that are grater than 0 are set to 0 and all pixels that are = to 0 are set to 255
    output_img = cv2.bitwise_not(output_img)
    # Converting image to binary by Thresholding in order to show a clear separation between white and blacl pixels.
    output_img = threshold(output_img)
    return output_img


def display_img(title, img):
    """Displays an image on screen and maintains the output until the user presses a key"""
    try:
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        cv2.setWindowTitle("img", title)
        cv2.resizeWindow("img", 1200, 900)
        # Display Image on screen
        cv2.imshow("img", img)
        # Mantain output until user presses a key
        cv2.waitKey(0)
        # Destroy windows when user presses a key
        cv2.destroyAllWindows()
    except Exception as e:
        logger.error("Error displaying image: %s", str(e))


def generate_ss_text(ss_details):
    """Loops through the captured text of an image and arranges this text line by line.
    This function depends on the image layout."""
    # Arrange the captured text after scanning the page
    parse_text = []
    word_list = []
    last_word = ""
    # Loop through the captured text of the entire page
    for word in ss_details["text"]:
        # If the word captured is not empty
        if word != "":
            # Add it to the line word list
            word_list.append(word)
            last_word = word
        if (last_word != "" and word == "") or (
            word == ss_details["text"][-1]
        ):
            parse_text.append(word_list)
            word_list = []
    return parse_text


def search_for_text(ss_details, search_str):
    """Search for the search string within the image content"""
    # Find all matches within one page
    results = re.findall(search_str, ss_details["text"], re.IGNORECASE)
    # In case multiple matches within one page
    for result in results:
        yield result


def save_page_content(pdfContent, page_id, page_data):
    """Appends the content of a scanned page, line by line, to a pandas DataFrame."""
    if page_data:
        for idx, line in enumerate(page_data, 1):
            line = " ".join(line)
            pdfContent = pdfContent.append(
                {"page": page_id, "line_id": idx, "line": line},
                ignore_index=True,
            )
    return pdfContent


def save_file_content(pdfContent, input_file):
    """Outputs the content of the pandas DataFrame to a CSV file having the same path as the input_file
    but with different extension (.csv)"""
    content_file = os.path.join(
        os.path.dirname(input_file),
        os.path.splitext(os.path.basename(input_file))[0] + ".csv",
    )
    pdfContent.to_csv(content_file, sep=",", index=False)
    return content_file


def calculate_ss_confidence(ss_details: dict):
    """Calculate the confidence score of the text grabbed from the scanned image."""
    try:
        # page_num  --> Page number of the detected text or item
        # block_num --> Block number of the detected text or item
        # par_num   --> Paragraph number of the detected text or item
        # line_num  --> Line number of the detected text or item
        # Convert the dict to dataFrame
        df = pd.DataFrame.from_dict(ss_details)
        # Convert the field conf (confidence) to numeric
        df["conf"] = pd.to_numeric(df["conf"], errors="coerce")
        # Elliminate records with negative confidence
        df = df[df.conf != -1]
        # Calculate the mean confidence by page
        conf = df.groupby(["page_num"])["conf"].mean().tolist()
        return conf[0]
    except Exception as e:
        logger.error("Error calculating confidence score: %s", str(e))
        return 0


def ocr_img(
    img: np.array,
    input_file: str,
    search_str: str,
    highlight_readable_text: bool = False,
    action: str = "Highlight",
    show_comparison: bool = False,
    generate_output: bool = True,
):
    """Scans an image buffer or an image file.
    Pre-processes the image.
    Calls the Tesseract engine with pre-defined parameters.
    Calculates the confidence score of the image grabbed content.
    Draws a green rectangle around readable text items having a confidence score > 30.
    Searches for a specific text.
    Highlight or redact found matches of the searched text.
    Displays a window showing readable text fields or the highlighted or redacted text.
    Generates the text content of the image.
    Prints a summary to the console."""
    try:
        logger.info(
            "Starting OCR on image%s", f": {input_file}" if input_file else ""
        )
        logger.debug(
            "Parameters - Action: %s, Search: %s, Generate output: %s",
            action,
            search_str,
            generate_output,
        )

        # If image source file is inputted as a parameter
        if input_file:
            # Reading image using opencv
            img = cv2.imread(input_file)
        # Preserve a copy of this image for comparison purposes
        initial_img = img.copy()
        highlighted_img = img.copy()
        # Convert image to binary
        bin_img = convert_img2bin(img)
        # Calling Tesseract
        # Tesseract Configuration parameters
        # oem --> OCR engine mode = 3 >> Legacy + LSTM mode only (LSTM neutral net mode works the best)
        # psm --> page segmentation mode = 6 >> Assume as single uniform block of text (How a page of text can be analyzed)
        config_param = r"--oem 3 --psm 6"
        # Feeding image to tesseract
        details = pytesseract.image_to_data(
            bin_img, output_type=Output.DICT, config=config_param, lang="eng"
        )
        # The details dictionary contains the information of the input image
        # such as detected text, region, position, information, height, width, confidence score.
        ss_confidence = calculate_ss_confidence(details)
        boxed_img = None
        # Total readable items
        ss_readable_items = 0
        # Total matches found
        ss_matches = 0
        for seq in range(len(details["text"])):
            # Consider only text fields with confidence score > 30 (text is readable)
            if float(details["conf"][seq]) > 30.0:
                ss_readable_items += 1
                # Draws a green rectangle around readable text items having a confidence score > 30
                if highlight_readable_text:
                    (x, y, w, h) = (
                        details["left"][seq],
                        details["top"][seq],
                        details["width"][seq],
                        details["height"][seq],
                    )
                    boxed_img = cv2.rectangle(
                        img, (x, y), (x + w, y + h), (0, 255, 0), 2
                    )
                # Searches for the string
                if search_str:
                    results = re.findall(
                        search_str, details["text"][seq], re.IGNORECASE
                    )
                    for result in results:
                        ss_matches += 1
                        if action:
                            # Draw a red rectangle around the searchable text
                            (x, y, w, h) = (
                                details["left"][seq],
                                details["top"][seq],
                                details["width"][seq],
                                details["height"][seq],
                            )
                            # Details of the rectangle
                            # Starting coordinate representing the top left corner of the rectangle
                            start_point = (x, y)
                            # Ending coordinate representing the botton right corner of the rectangle
                            end_point = (x + w, y + h)
                            # Color in BGR -- Blue, Green, Red
                            if action == "Highlight":
                                color = (0, 255, 255)  # Yellow
                            elif action == "Redact":
                                color = (0, 0, 0)  # Black
                            # Thickness in px (-1 will fill the entire shape)
                            thickness = -1
                            boxed_img = cv2.rectangle(
                                img, start_point, end_point, color, thickness
                            )

        if (
            ss_readable_items > 0
            and highlight_readable_text
            and not (ss_matches > 0 and action in ("Highlight", "Redact"))
        ):
            highlighted_img = boxed_img.copy()
        # Highlight found matches of the search string
        if ss_matches > 0 and action == "Highlight":
            cv2.addWeighted(
                boxed_img, 0.4, highlighted_img, 1 - 0.4, 0, highlighted_img
            )
        # Redact found matches of the search string
        elif ss_matches > 0 and action == "Redact":
            highlighted_img = boxed_img.copy()
            # cv2.addWeighted(boxed_img, 1, highlighted_img, 0, 0, highlighted_img)
        # save the image
        cv2.imwrite("highlighted-text-image.jpg", highlighted_img)
        # Displays window showing readable text fields or the highlighted or redacted data
        if show_comparison and (highlight_readable_text or action):
            title = input_file if input_file else "Compare"
            conc_img = cv2.hconcat([initial_img, highlighted_img])
            display_img(title, conc_img)
        # Generates the text content of the image
        output_data = None
        if generate_output and details:
            output_data = generate_ss_text(details)
        # Prints a summary to the console
        if input_file:
            summary = {
                "File": input_file,
                "Total readable words": ss_readable_items,
                "Total matches": ss_matches,
                "Confidence score": ss_confidence,
            }
            # Printing Summary
            logger.info(
                "## Summary ########################################################"
            )
            logger.info(
                "\n".join("{}:{}".format(i, j) for i, j in summary.items())
            )
            logger.info(
                "###################################################################"
            )
        return (
            highlighted_img,
            ss_readable_items,
            ss_matches,
            ss_confidence,
            output_data,
        )
    except Exception as e:
        logger.error("Error in OCR processing: %s", str(e))
        return None, 0, 0, 0, None


def image_to_byte_array(image: Image):
    """
    Converts an image into a byte array
    """
    try:
        imgByteArr = BytesIO()
        image.save(imgByteArr, format=image.format if image.format else "JPEG")
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr
    except Exception as e:
        logger.error("Error converting image to byte array: %s", str(e))
        return None


def ocr_file(**kwargs):
    """Opens the input PDF File.
    Opens a memory buffer for storing the output PDF file.
    Creates a DataFrame for storing pages statistics
    Iterates throughout the chosen pages of the input PDF file
    Grabs a screen-shot of the selected PDF page.
    Converts the screen-shot pix to a numpy array
    Scans the grabbed screen-shot.
    Collects the statistics of the screen-shot(page).
    Saves the content of the screen-shot(page).
    Adds the updated screen-shot (Highlighted, Redacted) to the output file.
    Saves the whole content of the PDF file.
    Saves the output PDF file if required.
    Prints a summary to the console."""
    try:
        input_file = kwargs.get("input_file")
        output_file = kwargs.get("output_file")
        search_str = kwargs.get("search_str")
        pages = kwargs.get("pages")
        highlight_readable_text = kwargs.get("highlight_readable_text")
        action = kwargs.get("action")
        show_comparison = kwargs.get("show_comparison")
        generate_output = kwargs.get("generate_output")
        # Opens the input PDF file
        pdfIn = fitz.open(input_file)
        # Opens a memory buffer for storing the output PDF file.
        pdfOut = fitz.open()
        # Creates an empty DataFrame for storing pages statistics
        dfResult = pd.DataFrame(
            columns=[
                "page",
                "page_readable_items",
                "page_matches",
                "page_total_confidence",
            ]
        )
        # Creates an empty DataFrame for storing file content
        if generate_output:
            pdfContent = pd.DataFrame(columns=["page", "line_id", "line"])
        # Iterate throughout the pages of the input file
        for pg in range(pdfIn.page_count):
            if str(pages) != str(None):
                if str(pg) not in str(pages):
                    continue
            # Select a page
            page = pdfIn[pg]
            # Rotation angle
            rotate = int(0)
            # PDF Page is converted into a whole picture 1056*816 and then for each picture a screenshot is taken.
            # zoom = 1.33333333 -----> Image size = 1056*816
            # zoom = 2 ---> 2 * Default Resolution (text is clear, image text is hard to read)    = filesize small / Image size = 1584*1224
            # zoom = 4 ---> 4 * Default Resolution (text is clear, image text is barely readable) = filesize large
            # zoom = 8 ---> 8 * Default Resolution (text is clear, image text is readable) = filesize large
            zoom_x = 2
            zoom_y = 2
            # The zoom factor is equal to 2 in order to make text clear
            # Pre-rotate is to rotate if needed.
            mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
            # To captue a specific part of the PDF page
            # rect = page.rect #page size
            # mp = rect.tl + (rect.bl - (0.75)/zoom_x) #rectangular area 56 = 75/1.3333
            # clip = fitz.Rect(mp,rect.br) #The area to capture
            # pix = page.getPixmap(matrix=mat, alpha=False,clip=clip)
            # Get a screen-shot of the PDF page
            # Colorspace -> represents the color space of the pixmap (csRGB, csGRAY, csCMYK)
            # alpha -> Transparancy indicator
            pix = page.get_pixmap(matrix=mat, alpha=False, colorspace="csGRAY")
            # convert the screen-shot pix to numpy array
            img = pix2np(pix)
            # Erode image to omit or thin the boundaries of the bright area of the image
            # We apply Erosion on binary images.
            # kernel = np.ones((2,2) , np.uint8)
            # img = cv2.erode(img,kernel,iterations=1)
            (
                upd_np_array,
                pg_readable_items,
                pg_matches,
                pg_total_confidence,
                pg_output_data,
            ) = ocr_img(
                img=img,
                input_file=None,
                search_str=search_str,
                highlight_readable_text=highlight_readable_text,  # False
                action=action,  # 'Redact'
                show_comparison=show_comparison,  # True
                generate_output=generate_output,  # False
            )
            # Collects the statistics of the page
            dfResult = dfResult.append(
                {
                    "page": (pg + 1),
                    "page_readable_items": pg_readable_items,
                    "page_matches": pg_matches,
                    "page_total_confidence": pg_total_confidence,
                },
                ignore_index=True,
            )
            if generate_output:
                pdfContent = save_page_content(
                    pdfContent=pdfContent,
                    page_id=(pg + 1),
                    page_data=pg_output_data,
                )
            # Convert the numpy array to image object with mode = RGB
            # upd_img = Image.fromarray(np.uint8(upd_np_array)).convert('RGB')
            upd_img = Image.fromarray(upd_np_array[..., ::-1])
            # Convert the image to byte array
            upd_array = image_to_byte_array(upd_img)
            # Get Page Size
            """
            #To check whether initial page is portrait or landscape
            if page.rect.width > page.rect.height:
                fmt = fitz.PaperRect("a4-1")
            else:
                fmt = fitz.PaperRect("a4")

            #pno = -1 -> Insert after last page
            pageo = pdfOut.newPage(pno = -1, width = fmt.width, height = fmt.height)
            """
            pageo = pdfOut.newPage(
                pno=-1, width=page.rect.width, height=page.rect.height
            )
            pageo.insertImage(page.rect, stream=upd_array)
            # pageo.insertImage(page.rect, stream=upd_img.tobytes())
            # pageo.showPDFpage(pageo.rect, pdfDoc, page.number)
        content_file = None
        if generate_output:
            content_file = save_file_content(
                pdfContent=pdfContent, input_file=input_file
            )
        summary = {
            "File": input_file,
            "Total pages": pdfIn.pageCount,
            "Processed pages": dfResult["page"].count(),
            "Total readable words": dfResult["page_readable_items"].sum(),
            "Total matches": dfResult["page_matches"].sum(),
            "Confidence score": dfResult["page_total_confidence"].mean(),
            "Output file": output_file,
            "Content file": content_file,
        }
        # Printing Summary
        logger.info(
            "## Summary ########################################################"
        )
        logger.info(
            "\n".join("{}:{}".format(i, j) for i, j in summary.items())
        )
        logger.info("\nPages Statistics:")
        logger.info(dfResult, sep="\n")
        logger.info(
            "###################################################################"
        )
        pdfIn.close()
        if output_file:
            pdfOut.save(output_file)
        pdfOut.close()
    except Exception as e:
        logger.error("Error in file processing: %s", str(e))
        return False


def ocr_folder(**kwargs):
    """Scans all PDF Files within a specified path"""
    input_folder = kwargs.get("input_folder")
    # Run in recursive mode
    recursive = kwargs.get("recursive")
    search_str = kwargs.get("search_str")
    pages = kwargs.get("pages")
    action = kwargs.get("action")
    generate_output = kwargs.get("generate_output")
    # Loop though the files within the input folder.
    for foldername, dirs, filenames in os.walk(input_folder):
        for filename in filenames:
            # Check if pdf file
            if not filename.endswith(".pdf"):
                continue
            # PDF File found
            inp_pdf_file = os.path.join(foldername, filename)
            logger.info("Processing file = %s", inp_pdf_file)
            output_file = None
            if search_str:
                # Generate an output file
                output_file = os.path.join(
                    os.path.dirname(inp_pdf_file),
                    "ocr_" + os.path.basename(inp_pdf_file),
                )
            ocr_file(
                input_file=inp_pdf_file,
                output_file=output_file,
                search_str=search_str,
                pages=pages,
                highlight_readable_text=False,
                action=action,
                show_comparison=False,
                generate_output=generate_output,
            )
        if not recursive:
            break


def is_valid_path(path):
    """Validates the path inputted and checks whether it is a file path or a folder path"""
    if not path:
        raise ValueError(f"Invalid Path")
    if os.path.isfile(path):
        return path
    elif os.path.isdir(path):
        return path
    else:
        raise ValueError(f"Invalid Path {path}")


def parse_args():
    """Get user command line parameters"""
    parser = argparse.ArgumentParser(description="Available Options")
    parser.add_argument(
        "-i",
        "--input-path",
        type=is_valid_path,
        required=True,
        help="Enter the path of the file or the folder to process",
    )
    parser.add_argument(
        "-a",
        "--action",
        choices=["Highlight", "Redact"],
        type=str,
        help="Choose to highlight or to redact",
    )
    parser.add_argument(
        "-s",
        "--search-str",
        dest="search_str",
        type=str,
        help="Enter a valid search string",
    )
    parser.add_argument(
        "-p",
        "--pages",
        dest="pages",
        type=tuple,
        help="Enter the pages to consider in the PDF file, e.g. (0,1)",
    )
    parser.add_argument(
        "-g",
        "--generate-output",
        action="store_true",
        help="Generate text content in a CSV file",
    )
    path = parser.parse_known_args()[0].input_path
    if os.path.isfile(path):
        parser.add_argument(
            "-o",
            "--output_file",
            dest="output_file",
            type=str,
            help="Enter a valid output file",
        )
        parser.add_argument(
            "-t",
            "--highlight-readable-text",
            action="store_true",
            help="Highlight readable text in the generated image",
        )
        parser.add_argument(
            "-c",
            "--show-comparison",
            action="store_true",
            help="Show comparison between captured image and the generated image",
        )
    if os.path.isdir(path):
        parser.add_argument(
            "-r",
            "--recursive",
            action="store_true",
            help="Whether to process the directory recursively",
        )
    # To Porse The Command Line Arguments
    args = vars(parser.parse_args())
    # To Display The Command Line Arguments
    logger.info(
        "## Command Arguments #################################################"
    )
    logger.info("\n".join("{}:{}".format(i, j) for i, j in args.items()))
    logger.info(
        "######################################################################"
    )
    return args


class OcrUI(QtWidgets.QMainWindow):
    def __init__(self):
        try:
            super(OcrUI, self).__init__()
            uic.loadUi("ocr.ui", self)

            # Connect signals
            self.browseButton.clicked.connect(self.browse_file)
            self.processButton.clicked.connect(self.process_file)
            self.actionExit.triggered.connect(self.close)

            # Initialize state
            self.input_files = []  # Store multiple files/folder items
            self.is_batch = False  # Flag for batch processing
            self.current_preview_item = 0  # Track current preview item index

            # Set up preview scene
            self.preview_scene = QtWidgets.QGraphicsScene()
            self.previewView.setScene(self.preview_scene)
            self.previewView.setRenderHint(
                QtWidgets.QPainter.SmoothPixmapTransform
            )

            # Add navigation buttons for batch mode
            self.prev_button = QtWidgets.QPushButton("Previous")
            self.next_button = QtWidgets.QPushButton("Next")
            self.prev_button.clicked.connect(self.show_previous_preview)
            self.next_button.clicked.connect(self.show_next_preview)
            self.prev_button.hide()
            self.next_button.hide()

            # Add navigation buttons to status bar
            self.statusBar().addPermanentWidget(self.prev_button)
            self.statusBar().addPermanentWidget(self.next_button)

            # Add progress bar
            self.progressBar = QtWidgets.QProgressBar()
            self.statusBar().addPermanentWidget(self.progressBar)
            self.progressBar.hide()

            # Initially disable process button
            self.processButton.setEnabled(False)

            # Enable drag and drop
            self.setAcceptDrops(True)
            self.inputFileEdit.setAcceptDrops(True)

            logger.info("OCR tool initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize OCR tool: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Failed to initialize UI: {str(e)}"
            )
            self.close()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                if file_path.lower().endswith(
                    (".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff")
                ):
                    files.append(file_path)
            elif os.path.isdir(file_path):
                # If directory, add all supported files in it
                for root, _, filenames in os.walk(file_path):
                    for filename in filenames:
                        if filename.lower().endswith(
                            (".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff")
                        ):
                            files.append(os.path.join(root, filename))

        if files:
            self.input_files = files
            self.is_batch = len(files) > 1
            if self.is_batch:
                self.inputFileEdit.setText(f"Selected {len(files)} files")
                self.batchModeCheckbox.setChecked(True)
            else:
                self.inputFileEdit.setText(files[0])
                self.batchModeCheckbox.setChecked(False)
            self.processButton.setEnabled(True)

    def browse_file(self):
        try:
            if self.batchModeCheckbox.isChecked():
                # For batch mode, allow folder selection or multiple files
                choice = QMessageBox.question(
                    self,
                    "Batch Processing",
                    "Would you like to select a folder (Yes) or multiple files (No)?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )

                if choice == QMessageBox.Yes:
                    # Select folder
                    folder = QFileDialog.getExistingDirectory(
                        self, "Select Folder with PDFs/Images"
                    )
                    if folder:
                        self.input_files = []
                        for root, _, files in os.walk(folder):
                            for file in files:
                                if file.lower().endswith(
                                    (
                                        ".pdf",
                                        ".png",
                                        ".jpg",
                                        ".jpeg",
                                        ".bmp",
                                        ".tiff",
                                    )
                                ):
                                    self.input_files.append(
                                        os.path.join(root, file)
                                    )
                        if self.input_files:
                            self.inputFileEdit.setText(
                                f"Selected folder: {folder} ({len(self.input_files)} files)"
                            )
                            self.is_batch = True
                            self.processButton.setEnabled(True)
                        else:
                            QMessageBox.warning(
                                self,
                                "Warning",
                                "No supported files found in selected folder!",
                            )
                else:
                    # Select multiple files
                    filenames, _ = QFileDialog.getOpenFileNames(
                        self,
                        "Select files",
                        "",
                        "Supported Files (*.pdf *.png *.jpg *.jpeg *.bmp *.tiff)",
                    )
                    if filenames:
                        self.input_files = filenames
                        self.inputFileEdit.setText(
                            f"Selected {len(filenames)} files"
                        )
                        self.is_batch = True
                        self.processButton.setEnabled(True)
            else:
                # Single file mode
                filename, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select file",
                    "",
                    "Supported Files (*.pdf *.png *.jpg *.jpeg *.bmp *.tiff)",
                )
                if filename:
                    self.input_files = [filename]
                    self.inputFileEdit.setText(filename)
                    self.is_batch = False
                    self.processButton.setEnabled(True)

        except Exception as e:
            logger.error("Error browsing for file: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error browsing file: {str(e)}"
            )

    def process_file(self):
        try:
            if not self.input_files:
                logger.warning("No input files selected")
                QMessageBox.warning(
                    self, "Warning", "Please select file(s) first"
                )
                return

            search_text = self.searchEdit.text()
            action = self.actionCombo.currentText()
            generate_output = self.generateOutputCheckbox.isChecked()

            # Get page range if specified
            pages = None
            if self.pagesEdit.text():
                try:
                    pages = tuple(
                        int(p.strip())
                        for p in self.pagesEdit.text().split(",")
                    )
                    logger.info("Processing specific pages: %s", pages)
                except ValueError:
                    logger.error(
                        "Invalid page numbers format: %s",
                        self.pagesEdit.text(),
                    )
                    QMessageBox.warning(
                        self,
                        "Warning",
                        "Invalid page numbers format! Use comma-separated numbers.",
                    )
                    return

            # Clear previous output
            self.outputText.clear()
            self.statusBar().showMessage("Processing...")
            QtWidgets.QApplication.processEvents()

            self.progressBar.show()
            self.progressBar.setValue(0)

            total_files = len(self.input_files)
            successful = 0
            failed = 0

            for idx, input_file in enumerate(self.input_files, 1):
                try:
                    progress_base = (idx - 1) * 100 / total_files
                    self.statusBar().showMessage(
                        f"Processing file {idx} of {total_files}: {os.path.basename(input_file)}"
                    )
                    self.progressBar.setValue(int(progress_base))
                    QtWidgets.QApplication.processEvents()

                    if filetype.is_image(input_file):
                        # Process image file
                        img, readable, matches, confidence, data = ocr_img(
                            input_file=input_file,
                            search_str=search_text if search_text else None,
                            highlight_readable_text=False,
                            action=action,
                            show_comparison=False,
                            generate_output=generate_output,
                        )
                        if readable:
                            successful += 1
                            if not self.is_batch:
                                output = [
                                    f"Image processed successfully",
                                    f"OCR Confidence: {confidence:.1f}%",
                                ]
                                if matches:
                                    output.append(
                                        f"\nMatches found: {len(matches)}"
                                    )
                                    output.extend(matches)
                                self.outputText.setPlainText("\n".join(output))
                        else:
                            failed += 1

                    else:  # PDF file
                        output_file = (
                            os.path.join(
                                os.path.dirname(input_file),
                                "ocr_" + os.path.basename(input_file),
                            )
                            if generate_output
                            else None
                        )

                        success = ocr_file(
                            input_file=input_file,
                            output_file=output_file,
                            search_str=search_text if search_text else None,
                            pages=pages,
                            highlight_readable_text=False,
                            action=action,
                            show_comparison=False,
                            generate_output=generate_output,
                        )

                        if success:
                            successful += 1
                        else:
                            failed += 1

                except Exception as e:
                    logger.error(
                        f"Error processing file {input_file}: {str(e)}"
                    )
                    failed += 1
                    continue

                self.progressBar.setValue(int((idx * 100) / total_files))
                QtWidgets.QApplication.processEvents()

            # Show final results
            if self.is_batch:
                result_msg = f"Batch processing completed.\nSuccessful: {successful}\nFailed: {failed}"
                self.outputText.setPlainText(result_msg)
                if failed > 0:
                    QMessageBox.warning(self, "Batch Complete", result_msg)
                else:
                    QMessageBox.information(self, "Batch Complete", result_msg)

            self.progressBar.hide()
            self.statusBar().showMessage("Processing complete", 3000)

        except Exception as e:
            logger.error("Error in process operation: %s", str(e))
            QMessageBox.critical(
                self, "Error", f"Error in process operation: {str(e)}"
            )
            self.statusBar().showMessage("Error occurred", 3000)
            self.progressBar.hide()

    def preview_file(self, file_path):
        """Show preview of PDF or image file"""
        try:
            self.preview_scene.clear()

            if file_path.lower().endswith(".pdf"):
                # Preview first page of PDF
                doc = fitz.open(file_path)
                if doc.page_count > 0:
                    page = doc[0]
                    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                    img = QtGui.QImage(
                        pix.samples,
                        pix.width,
                        pix.height,
                        pix.stride,
                        QtGui.QImage.Format_RGB888,
                    )
                    pixmap = QtGui.QPixmap.fromImage(img)
                    doc.close()
            else:
                # Preview image file
                pixmap = QtGui.QPixmap(file_path)

            if not pixmap.isNull():
                # Scale pixmap to fit the view while maintaining aspect ratio
                view_size = self.previewView.size()
                scaled_pixmap = pixmap.scaled(
                    view_size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
                self.preview_scene.addPixmap(scaled_pixmap)
                self.preview_scene.setSceneRect(scaled_pixmap.rect())
                self.previewView.fitInView(
                    self.preview_scene.sceneRect(), QtCore.Qt.KeepAspectRatio
                )

                # Update navigation buttons
                self.update_navigation_buttons()

                logger.info("Preview generated for: %s", file_path)
            else:
                logger.error("Failed to load preview for: %s", file_path)

        except Exception as e:
            logger.error("Error generating preview: %s", str(e))
            self.preview_scene.clear()

    def show_next_preview(self):
        """Show next file in preview"""
        if (
            self.input_files
            and self.current_preview_item < len(self.input_files) - 1
        ):
            self.current_preview_item += 1
            self.preview_file(self.input_files[self.current_preview_item])

    def show_previous_preview(self):
        """Show previous file in preview"""
        if self.input_files and self.current_preview_item > 0:
            self.current_preview_item -= 1
            self.preview_file(self.input_files[self.current_preview_item])

    def update_navigation_buttons(self):
        """Update the state of navigation buttons"""
        if len(self.input_files) > 1:
            self.prev_button.setVisible(True)
            self.next_button.setVisible(True)
            self.prev_button.setEnabled(self.current_preview_item > 0)
            self.next_button.setEnabled(
                self.current_preview_item < len(self.input_files) - 1
            )
        else:
            self.prev_button.hide()
            self.next_button.hide()

    def resizeEvent(self, event):
        """Handle window resize event to keep preview scaled properly"""
        super().resizeEvent(event)
        if not self.preview_scene.items():
            return
        self.previewView.fitInView(
            self.preview_scene.sceneRect(), QtCore.Qt.KeepAspectRatio
        )


def main():
    try:
        app = QtWidgets.QApplication([])
        window = OcrUI()
        logger.info("Application started")
        app.exec_()
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
