#!/usr/bin/env python3
"""
Test PDF Sample Generator
Creates a simple PDF file for testing PDF utilities integration
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf():
    """Create a simple test PDF file for validation"""
    filename = "test_sample.pdf"
    
    # Create a simple PDF with text content
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "PDF Utilities Integration Test Document")
    
    # Add content
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    test_content = [
        "This is a test PDF document created for validating the PDF utilities integration.",
        "",
        "Test Features:",
        "• Text extraction capabilities",
        "• PDF splitting and merging",
        "• Metadata extraction",
        "• Image extraction (if images are present)",
        "• OCR processing validation",
        "",
        "Integration Test Points:",
        "1. Configuration system integration",
        "2. Logging system functionality", 
        "3. Error handling consistency",
        "4. UI responsiveness and theming",
        "5. Bridge architecture validation",
        "",
        "This document contains multiple lines of text to test various",
        "PDF processing capabilities and ensure the integration works",
        "correctly across all 23 PDF utility modules.",
        "",
        "Test completed successfully if this text can be extracted,",
        "the PDF can be split/merged, and metadata is accessible."
    ]
    
    for line in test_content:
        c.drawString(100, y_position, line)
        y_position -= 20
        
        # Add new page if needed
        if y_position < 100:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 100
    
    # Add a second page with different content
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 100, "Page 2 - Additional Test Content")
    
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    page2_content = [
        "This is the second page of the test document.",
        "",
        "Additional test scenarios:",
        "• Multi-page document handling",
        "• Page administration features",
        "• Document viewing capabilities",
        "• Watermarking functionality",
        "• Digital signing features",
        "",
        "The integration should handle this multi-page document",
        "correctly across all PDF utility modules."
    ]
    
    for line in page2_content:
        c.drawString(100, y_position, line)
        y_position -= 20
    
    c.save()
    print(f"Test PDF created: {filename}")
    return filename

if __name__ == "__main__":
    try:
        pdf_file = create_test_pdf()
        print(f"✅ Test PDF successfully created: {pdf_file}")
        print(f"📁 File size: {os.path.getsize(pdf_file)} bytes")
    except Exception as e:
        print(f"❌ Error creating test PDF: {e}")
        print("Note: This requires reportlab library. Install with: pip install reportlab")