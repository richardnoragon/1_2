"""
Test Data Setup for PDF Sign Module Tests
Created: 2025-08-24

This script creates necessary test data files including sample PDFs,
signature images, and certificate files for comprehensive testing.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    import OpenSSL
    import pikepdf
    from PIL import Image, ImageDraw, ImageFont
    
    def create_sample_pdf(output_path: str, pages: int = 3):
        """Create a sample PDF with multiple pages for testing"""
        pdf = pikepdf.Pdf.new()
        
        for i in range(pages):
            # Create a page with content
            page = pdf.add_blank_page()
            
        pdf.save(output_path)
        print(f"Created sample PDF: {output_path}")
    
    def create_signature_images(output_dir: str):
        """Create sample signature images for testing"""
        # Create different signature images
        signatures = [
            ("signature.jpg", (200, 100), "blue", "John Doe"),
            ("signature_large.png", (400, 200), "navy", "Jane Smith"),
            ("signature_small.jpg", (100, 50), "darkblue", "Test User")
        ]
        
        for filename, size, color, text in signatures:
            # Create image
            img = Image.new('RGB', size, color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font, fallback to basic if not available
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Draw signature text
            draw.text((10, 10), text, fill=color, font=font)
            draw.rectangle([5, 5, size[0]-5, size[1]-5], outline=color, width=2)
            
            # Save image
            image_path = os.path.join(output_dir, filename)
            
            if filename.endswith('.jpg'):
                img.save(image_path, 'JPEG', quality=95)
            else:
                img.save(image_path, 'PNG')
            
            print(f"Created signature image: {image_path}")
    
    def create_test_certificates(output_dir: str):
        """Create test certificate files"""
        # Generate key pair
        key = OpenSSL.crypto.PKey()
        key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
        
        # Create certificate
        cert = OpenSSL.crypto.X509()
        cert.get_subject().CN = "Test Certificate"
        cert.get_subject().O = "Test Organization"
        cert.get_subject().OU = "Test Unit"
        cert.set_serial_number(12345)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365*24*60*60)  # 1 year
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')
        
        # Save private key
        with open(os.path.join(output_dir, 'test_private_key.pem'), 'wb') as f:
            f.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key))
        
        # Save certificate
        with open(os.path.join(output_dir, 'test_certificate.cer'), 'wb') as f:
            f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))
        
        # Save public key
        with open(os.path.join(output_dir, 'test_public_key.pem'), 'wb') as f:
            f.write(OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey()))
        
        # Create PKCS12 container (simplified for compatibility)
        with open(os.path.join(output_dir, 'test_container.pfx'), 'wb') as f:
            f.write(b'DUMMY_PKCS12_CONTAINER_FOR_TESTING')
        
        print(f"Created test certificates in: {output_dir}")
    
    def create_test_data():
        """Main function to create all test data"""
        # Define paths
        test_data_dir = Path(__file__).parent / "sign_test_assets"
        test_data_dir.mkdir(exist_ok=True)
        
        # Create sample PDFs
        pdf_files = [
            "sample_single_page.pdf",
            "sample_multi_page.pdf", 
            "sample_large.pdf"
        ]
        
        for i, pdf_file in enumerate(pdf_files, 1):
            pdf_path = test_data_dir / pdf_file
            create_sample_pdf(str(pdf_path), pages=i)
        
        # Create signature images
        create_signature_images(str(test_data_dir))
        
        # Create test certificates
        create_test_certificates(str(test_data_dir))
        
        # Create additional test files
        with open(test_data_dir / "test_text_file.txt", 'w') as f:
            f.write("This is a test text file that should be ignored during PDF processing.")
        
        with open(test_data_dir / "corrupt_pdf.pdf", 'wb') as f:
            f.write(b"This is not a valid PDF file")
        
        print("Test data creation completed successfully!")
        print(f"Test data location: {test_data_dir}")
        return str(test_data_dir)

except ImportError as e:
    print(f"Warning: Some imports not available: {e}")
    print("Creating minimal test data without full functionality...")
    
    def create_minimal_test_data():
        """Create minimal test data when dependencies are not available"""
        test_data_dir = Path(__file__).parent / "sign_test_assets"
        test_data_dir.mkdir(exist_ok=True)
        
        # Create dummy PDF files
        for i, filename in enumerate(["sample_single_page.pdf", "sample_multi_page.pdf"], 1):
            with open(test_data_dir / filename, 'wb') as f:
                f.write(b'%PDF-1.4\n%dummy PDF content for testing\n%%EOF')
        
        # Create dummy signature images
        for filename in ["signature.jpg", "signature_large.png", "signature_small.jpg"]:
            with open(test_data_dir / filename, 'wb') as f:
                if filename.endswith('.jpg'):
                    f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xfe\x00\x13Created with Python\xff\xd9')
                else:
                    f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00\x00\x00\x007n\xf9$\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01s\x07]\x8d\x00\x00\x00\x00IEND\xaeB`\x82')
        
        # Create dummy certificate files
        cert_files = {
            'test_private_key.pem': b'-----BEGIN PRIVATE KEY-----\nDUMMY_PRIVATE_KEY_FOR_TESTING\n-----END PRIVATE KEY-----',
            'test_certificate.cer': b'-----BEGIN CERTIFICATE-----\nDUMMY_CERTIFICATE_FOR_TESTING\n-----END CERTIFICATE-----',
            'test_public_key.pem': b'-----BEGIN PUBLIC KEY-----\nDUMMY_PUBLIC_KEY_FOR_TESTING\n-----END PUBLIC KEY-----',
            'test_container.pfx': b'DUMMY_PKCS12_CONTAINER_FOR_TESTING'
        }
        
        for filename, content in cert_files.items():
            with open(test_data_dir / filename, 'wb') as f:
                f.write(content)
        
        # Create text file
        with open(test_data_dir / "test_text_file.txt", 'w') as f:
            f.write("This is a test text file that should be ignored during PDF processing.")
        
        print("Minimal test data created successfully!")
        print(f"Test data location: {test_data_dir}")
        return str(test_data_dir)
    
    create_test_data = create_minimal_test_data


if __name__ == "__main__":
    create_test_data()