#!/usr/bin/env python3
"""
Test script for PDF operations
Creates a simple test PDF to verify the split, merge, and sign functions work
"""


def create_test_pdf(filename, num_pages=3):
    """Create a simple test PDF with multiple pages"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        for i in range(num_pages):
            # Add some content to each page
            c.drawString(100, height - 100, f"Test PDF - Page {i + 1}")
            c.drawString(100, height - 150, 
                        f"This is page {i + 1} of {num_pages}")
            c.drawString(100, height - 200, 
                        "Created for testing PDF operations")
            
            # Add a simple rectangle
            c.rect(100, height - 300, 200, 100)
            c.drawString(110, height - 270, f"Content box {i + 1}")
            
            c.showPage()
        
        c.save()
        print(f"Created test PDF: {filename}")
        return True
        
    except ImportError:
        print("reportlab library not found. Cannot create test PDF.")
        return False
    except Exception as e:
        print(f"Error creating test PDF: {e}")
        return False


def create_test_signature_image():
    """Create a simple signature image for testing"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple signature image
        img = Image.new('RGBA', (200, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple signature-like scribble
        points = [(20, 50), (50, 30), (80, 60), (120, 40), (160, 55), (180, 45)]
        draw.line(points, fill=(0, 0, 255, 180), width=3)
        draw.text((60, 70), "Test Signature", fill=(0, 0, 0, 200))
        
        sig_file = "test_signature.png"
        img.save(sig_file)
        print(f"Created test signature: {sig_file}")
        return sig_file
        
    except ImportError:
        print("PIL library not found. Cannot create test signature.")
        return None
    except Exception as e:
        print(f"Error creating test signature: {e}")
        return None


def test_pdf_operations():
    """Test the PDF operations"""
    print("Testing PDF Operations...")
    
    # Create test files
    test_pdf1 = "test_document_1.pdf"
    test_pdf2 = "test_document_2.pdf"
    
    success1 = create_test_pdf(test_pdf1, 2)
    success2 = create_test_pdf(test_pdf2, 3)
    
    if success1 and success2:
        print(f"Created test PDFs: {test_pdf1}, {test_pdf2}")
        print("You can now test the PDF operations in the application:")
        print("1. Go to the PDF Tools tab")
        print("2. Select a PDF file using 'Select PDF File'")
        print("3. Try Split, Merge, or Sign operations")
        print(f"   - Use {test_pdf1} or {test_pdf2} for splitting")
        print(f"   - Use both files for merging")
        print("   - Use any file for signing")
    else:
        print("Could not create test PDFs")
    
    # Create test signature
    sig_file = create_test_signature_image()
    if sig_file:
        print(f"Created test signature: {sig_file}")
        print("You can use this image file for signing PDFs")


if __name__ == "__main__":
    test_pdf_operations()
