# Import Libraries
import sys
import OpenSSL
import os
import time
import argparse
import pikepdf
from PIL import Image
from typing import Tuple, Optional
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import fitz
from log_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

def createKeyPair(type, bits):
    """
    Create a public/private key pair
    Arguments: Type - Key Type, must be one of TYPE_RSA and TYPE_DSA
               bits - Number of bits to use in the key (1024 or 2048 or 4096)
    Returns: The public/private key pair in a PKey object
    """
    pkey = OpenSSL.crypto.PKey()
    pkey.generate_key(type, bits)
    return pkey


def create_self_signed_cert(pKey):
    """Create a self signed certificate. This certificate will not require to be signed by a Certificate Authority."""
    # Create a self signed certificate
    cert = OpenSSL.crypto.X509()
    # Common Name (e.g. server FQDN or Your Name)
    cert.get_subject().CN = "BASSEM MARJI"
    # Serial Number
    cert.set_serial_number(int(time.time() * 10))
    # Not Before
    cert.gmtime_adj_notBefore(0)  # Not before
    # Not After (Expire after 10 years)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    # Identify issue
    cert.set_issuer((cert.get_subject()))
    cert.set_pubkey(pKey)
    cert.sign(pKey, 'md5')  # or cert.sign(pKey, 'sha256')
    return cert


def load():
    """Generate the certificate"""
    summary = {}
    summary['OpenSSL Version'] = OpenSSL.__version__
    
    # Create static directory if it doesn't exist
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Generating a Private Key...
    key = createKeyPair(OpenSSL.crypto.TYPE_RSA, 1024)
    
    # PEM encoded
    with open(os.path.join(static_dir, 'private_key.pem'), 'wb') as pk:
        pk_str = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
        pk.write(pk_str)
        summary['Private Key'] = pk_str
        
    # Generate self-signed certificate
    cert = create_self_signed_cert(pKey=key)
    with open(os.path.join(static_dir, 'certificate.cer'), 'wb') as cer:
        cer_str = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        cer.write(cer_str)
        summary['Self Signed Certificate'] = cer_str
        
    # Generate public key
    with open(os.path.join(static_dir, 'public_key.pem'), 'wb') as pub_key:
        pub_key_str = OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey())
        pub_key.write(pub_key_str)
        summary['Public Key'] = pub_key_str
        
    # Generate PKCS12 container
    p12 = OpenSSL.crypto.PKCS12()
    p12.set_privatekey(key)
    p12.set_certificate(cert)
    with open(os.path.join(static_dir, 'container.pfx'), 'wb') as f:
        f.write(p12.export())
        
    print("## Initialization Summary ##################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in summary.items()))
    print("############################################################################")
    return True


def sign_file(input_file: str, signatureID: str, x_coordinate: int,
            y_coordinate: int, pages: Tuple = None, output_file: Optional[str] = None):
    """Sign a PDF file"""
    if not output_file:
        output_file = (os.path.splitext(input_file)[0]) + "_signed.pdf"
        
    # Get paths for signature and certificate
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    sign_filename = os.path.join(static_dir, 'signature.jpg')
    pk_filename = os.path.join(static_dir, 'container.pfx')
    
    # Open the PDF
    pdf = pikepdf.Pdf.open(input_file)
    
    # Load signature image
    if os.path.exists(sign_filename):
        sign_img = Image.open(sign_filename)
        
        # Add signature to specified pages
        page_numbers = [int(p) for p in pages] if pages else range(len(pdf.pages))
        
        for page_num in page_numbers:
            if 0 <= page_num < len(pdf.pages):
                page = pdf.pages[page_num]
                
                # Create form XObject from signature image
                with open(sign_filename, 'rb') as img_file:
                    img_obj = pdf.make_stream(img_file.read())
                    img_obj['/Type'] = pikepdf.Name.XObject
                    img_obj['/Subtype'] = pikepdf.Name.Image
                    page.Contents = img_obj
    
    # Save the signed PDF
    pdf.save(output_file)
    
    # Create summary
    summary = {
        "Input File": input_file,
        "Signature ID": signatureID,
        "Output File": output_file,
        "Signature File": sign_filename,
        "Certificate File": pk_filename
    }
    
    print("## Summary ########################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in summary.items()))
    print("###################################################################")
    return True


def sign_folder(**kwargs):
    """Sign all PDF Files within a specified path"""
    input_folder = kwargs.get('input_folder')
    signatureID = kwargs.get('signatureID')
    pages = kwargs.get('pages')
    x_coordinate = int(kwargs.get('x_coordinate'))
    y_coordinate = int(kwargs.get('y_coordinate'))
    # Run in recursive mode
    recursive = kwargs.get('recursive')
    # Loop though the files within the input folder.
    for foldername, dirs, filenames in os.walk(input_folder):
        for filename in filenames:
            # Check if pdf file
            if not filename.endswith('.pdf'):
                continue
            # PDF File found
            inp_pdf_file = os.path.join(foldername, filename)
            print("Processing file =", inp_pdf_file)
            # Compress Existing file
            sign_file(input_file=inp_pdf_file, signatureID=signatureID, x_coordinate=x_coordinate,
                      y_coordinate=y_coordinate, pages=pages, output_file=None)
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
    parser.add_argument('-l', '--load', dest='load', action="store_true",
                        help="Load the required configurations and create the certificate")
    parser.add_argument('-i', '--input_path', dest='input_path', type=is_valid_path,
                        help="Enter the path of the file or the folder to process")
    parser.add_argument('-s', '--signatureID', dest='signatureID',
                        type=str, help="Enter the ID of the signature")
    parser.add_argument('-p', '--pages', dest='pages', type=tuple,
                        help="Enter the pages to consider e.g.: [1,3]")
    parser.add_argument('-x', '--x_coordinate', dest='x_coordinate',
                        type=int, help="Enter the x coordinate.")
    parser.add_argument('-y', '--y_coordinate', dest='y_coordinate',
                        type=int, help="Enter the y coordinate.")
    path = parser.parse_known_args()[0].input_path
    if path and os.path.isfile(path):
        parser.add_argument('-o', '--output_file', dest='output_file',
                            type=str, help="Enter a valid output file")
    if path and os.path.isdir(path):
        parser.add_argument('-r', '--recursive', dest='recursive', default=False, type=lambda x: (
            str(x).lower() in ['true', '1', 'yes']), help="Process Recursively or Non-Recursively")
    args = vars(parser.parse_args())
    # To Display The Command Line Arguments
    print("## Command Arguments #################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in args.items()))
    print("######################################################################")
    return args


def apply_signature(input_file: str, signature_file: str, pages: tuple = None, position: tuple = None) -> bool:
    """Apply signature to PDF file"""
    try:
        logger.info("Starting signature application")
        logger.debug("Parameters - Input: %s, Signature: %s, Pages: %s, Position: %s",
                    input_file, signature_file, pages, position)
        
        # Check if files exist
        if not os.path.exists(input_file):
            logger.error("Input file not found: %s", input_file)
            raise FileNotFoundError(f"Input file not found: {input_file}")
        if not os.path.exists(signature_file):
            logger.error("Signature file not found: %s", signature_file)
            raise FileNotFoundError(f"Signature file not found: {signature_file}")
            
        # Open the PDF
        pdf = fitz.open(input_file)
        
        # Get pages to process
        if pages:
            page_list = list(pages)
        else:
            page_list = range(len(pdf))
            
        logger.info("Processing %d pages", len(page_list))
        
        for page_num in page_list:
            try:
                if page_num >= len(pdf):
                    logger.warning("Page %d out of range, skipping", page_num + 1)
                    continue
                    
                page = pdf[page_num]
                
                # Calculate signature position if not provided
                if not position:
                    # Default to bottom right
                    rect = page.rect
                    position = (rect.width - 100, rect.height - 50)
                
                # Insert signature image
                logger.debug("Inserting signature on page %d at position %s", page_num + 1, position)
                page.insert_image((position[0], position[1], position[0] + 100, position[1] + 50), 
                                filename=signature_file)
                
            except Exception as e:
                logger.error("Error processing page %d: %s", page_num + 1, str(e))
                continue
                
        # Save the output file
        output_file = os.path.splitext(input_file)[0] + "_signed.pdf"
        logger.info("Saving signed PDF to: %s", output_file)
        pdf.save(output_file)
        pdf.close()
        
        logger.info("Signature application completed successfully")
        return True
        
    except Exception as e:
        logger.error("Error applying signature: %s", str(e))
        raise

class SignUI(QtWidgets.QMainWindow):
    def __init__(self):
        try:
            super(SignUI, self).__init__()
            uic.loadUi('sign.ui', self)
            
            # Connect signals
            self.browsePdfButton.clicked.connect(self.browse_pdf)
            self.browseSignatureButton.clicked.connect(self.browse_signature)
            self.signButton.clicked.connect(self.sign_document)
            self.actionExit.triggered.connect(self.close)
            
            logger.info("PDF signer initialized")
            self.show()
        except Exception as e:
            logger.error("Failed to initialize PDF signer: %s", str(e))
            raise

    def browse_pdf(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select PDF File",
                "",
                "PDF Files (*.pdf)"
            )
            if filename:
                logger.info("Selected input file: %s", filename)
                self.pdfFileEdit.setText(filename)
        except Exception as e:
            logger.error("Error browsing for PDF: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error selecting PDF: {str(e)}")

    def browse_signature(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select Signature Image",
                "",
                "Image Files (*.png *.jpg *.jpeg *.bmp)"
            )
            if filename:
                logger.info("Selected signature file: %s", filename)
                self.signatureFileEdit.setText(filename)
        except Exception as e:
            logger.error("Error browsing for signature: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error selecting signature: {str(e)}")

    def sign_document(self):
        try:
            # Get input files
            pdf_file = self.pdfFileEdit.text()
            signature_file = self.signatureFileEdit.text()
            
            if not pdf_file:
                logger.warning("No PDF file selected")
                QMessageBox.warning(self, "Error", "Please select a PDF file first!")
                return
                
            if not signature_file:
                logger.warning("No signature file selected")
                QMessageBox.warning(self, "Error", "Please select a signature image!")
                return
                
            # Get page range if specified
            pages = None
            if self.pagesEdit.text():
                try:
                    pages = tuple(int(p.strip())-1 for p in self.pagesEdit.text().split(','))
                    logger.info("Signing specific pages: %s", pages)
                except ValueError:
                    logger.error("Invalid page numbers format: %s", self.pagesEdit.text())
                    QMessageBox.warning(self, "Error", "Invalid page numbers! Use comma-separated numbers.")
                    return
            
            try:
                logger.info("Starting signature process")
                success = apply_signature(
                    input_file=pdf_file,
                    signature_file=signature_file,
                    pages=pages
                )
                
                if success:
                    logger.info("Document signed successfully")
                    QMessageBox.information(self, "Success", "Document signed successfully!")
                else:
                    logger.warning("Failed to sign document")
                    QMessageBox.warning(self, "Warning", "Failed to sign document")
                    
            except Exception as e:
                logger.error("Error during signing: %s", str(e))
                QMessageBox.critical(self, "Error", f"Error during signing: {str(e)}")
                
        except Exception as e:
            logger.error("Error in sign operation: %s", str(e))
            QMessageBox.critical(self, "Error", f"Error in sign operation: {str(e)}")

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = SignUI()
        logger.info("Application started")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical("Application failed to start: %s", str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
