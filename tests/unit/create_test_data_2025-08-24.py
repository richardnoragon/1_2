"""
Mock test data creation for encrypt.py tests
Creates sample PDF files and test data
Created: 2025-08-24
"""

import os

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_sample_pdf(filepath, content="Test PDF Content"):
    """Create a simple PDF file for testing"""
    try:
        c = canvas.Canvas(filepath, pagesize=letter)
        c.drawString(100, 750, content)
        c.drawString(100, 700, "Generated for encrypt.py unit tests")
        c.drawString(100, 650, f"File: {os.path.basename(filepath)}")
        c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False


def create_encrypted_pdf(input_pdf, output_pdf, password):
    """Create an encrypted PDF from an existing PDF"""
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        with open(output_pdf, "wb") as f:
            writer.write(f)

        return True
    except Exception as e:
        print(f"Error creating encrypted PDF: {e}")
        return False


def setup_test_data(test_dir):
    """Setup test data files in the specified directory"""
    print("Setting up test data files...")

    # Create sample PDFs
    sample_pdf = os.path.join(test_dir, "sample_test.pdf")
    encrypted_pdf = os.path.join(test_dir, "sample_encrypted_test.pdf")

    if create_sample_pdf(sample_pdf):
        print(f"✓ Created sample PDF: {sample_pdf}")
    else:
        print(f"✗ Failed to create sample PDF: {sample_pdf}")
        return False

    if create_encrypted_pdf(sample_pdf, encrypted_pdf, "test_password"):
        print(f"✓ Created encrypted PDF: {encrypted_pdf}")
    else:
        print(f"✗ Failed to create encrypted PDF: {encrypted_pdf}")
        return False

    return True


if __name__ == "__main__":
    test_directory = os.path.dirname(os.path.abspath(__file__))
    setup_test_data(test_directory)
