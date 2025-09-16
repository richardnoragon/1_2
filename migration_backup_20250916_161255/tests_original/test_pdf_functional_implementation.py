#!/usr/bin/env python3
"""
Test PDF Functional Implementation - Phase 2.1
Comprehensive testing of functional PDF operations (merge, split, sign)
"""

import sys
import os
import logging
import tempfile
import shutil
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer

# Import our PDF components
try:
    from pdf_operation_engine import PDFOperationEngine, PDFValidator
    from pdf_parameter_dialogs import PDFMergeDialog, PDFSplitDialog, PDFSignDialog
    from pdf_functional_integration import PDFFunctionalIntegration
    from enhanced_pdf_tools_widget import EnhancedPDFToolsWidget
    
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import PDF components: {e}")
    COMPONENTS_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFFunctionalTestSuite:
    """Comprehensive test suite for PDF functional implementations"""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        self.sample_pdfs = []
        
    def setup_test_environment(self):
        """Set up test environment with sample files"""
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="pdf_test_")
            logger.info(f"Created test directory: {self.temp_dir}")
            
            # Create sample PDF files for testing
            self.create_sample_pdfs()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup test environment: {e}")
            return False
    
    def create_sample_pdfs(self):
        """Create sample PDF files for testing"""
        try:
            import fitz  # PyMuPDF
            
            # Create sample PDF 1
            doc1 = fitz.open()
            page1 = doc1.new_page()
            page1.insert_text((100, 100), "Sample PDF Document 1\nPage 1 Content", fontsize=12)
            page2 = doc1.new_page()
            page2.insert_text((100, 100), "Sample PDF Document 1\nPage 2 Content", fontsize=12)
            
            pdf1_path = os.path.join(self.temp_dir, "sample1.pdf")
            doc1.save(pdf1_path)
            doc1.close()
            self.sample_pdfs.append(pdf1_path)
            
            # Create sample PDF 2
            doc2 = fitz.open()
            page1 = doc2.new_page()
            page1.insert_text((100, 100), "Sample PDF Document 2\nSingle Page Content", fontsize=12)
            
            pdf2_path = os.path.join(self.temp_dir, "sample2.pdf")
            doc2.save(pdf2_path)
            doc2.close()
            self.sample_pdfs.append(pdf2_path)
            
            # Create sample PDF 3 (larger)
            doc3 = fitz.open()
            for i in range(5):
                page = doc3.new_page()
                page.insert_text((100, 100), f"Sample PDF Document 3\nPage {i+1} Content", fontsize=12)
            
            pdf3_path = os.path.join(self.temp_dir, "sample3.pdf")
            doc3.save(pdf3_path)
            doc3.close()
            self.sample_pdfs.append(pdf3_path)
            
            logger.info(f"Created {len(self.sample_pdfs)} sample PDF files")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample PDFs: {e}")
            return False
    
    def test_pdf_validator(self):
        """Test PDF validation functionality"""
        test_name = "PDF Validator"
        logger.info(f"Testing {test_name}")
        
        try:
            # Test valid PDF files
            for pdf_path in self.sample_pdfs:
                validation = PDFValidator.validate_pdf_file(pdf_path)
                
                if not validation['valid_pdf']:
                    raise AssertionError(f"Valid PDF failed validation: {pdf_path}")
                
                if validation['page_count'] <= 0:
                    raise AssertionError(f"Invalid page count: {validation['page_count']}")
            
            # Test invalid file
            invalid_path = os.path.join(self.temp_dir, "nonexistent.pdf")
            validation = PDFValidator.validate_pdf_file(invalid_path)
            
            if validation['exists']:
                raise AssertionError("Non-existent file reported as existing")
            
            # Test multiple files validation
            validation_results = PDFValidator.validate_multiple_files(self.sample_pdfs)
            
            if len(validation_results) != len(self.sample_pdfs):
                raise AssertionError("Multiple file validation count mismatch")
            
            self.test_results[test_name] = {
                'status': 'PASSED',
                'message': f'Validated {len(self.sample_pdfs)} PDF files successfully'
            }
            
        except Exception as e:
            self.test_results[test_name] = {
                'status': 'FAILED',
                'message': str(e)
            }
    
    def test_pdf_merge_operation(self):
        """Test PDF merge functionality"""
        test_name = "PDF Merge Operation"
        logger.info(f"Testing {test_name}")
        
        try:
            engine = PDFOperationEngine()
            
            # Test merging first two PDFs
            input_files = self.sample_pdfs[:2]
            output_file = os.path.join(self.temp_dir, "merged_test.pdf")
            
            options = {
                'preserve_bookmarks': True,
                'preserve_metadata': True,
                'optimize_output': False
            }
            
            result = engine.merge_pdfs(input_files, output_file, options)
            
            if not result.success:
                raise AssertionError(f"Merge failed: {result.error_message}")
            
            if not os.path.exists(output_file):
                raise AssertionError("Output file was not created")
            
            # Validate merged PDF
            validation = PDFValidator.validate_pdf_file(output_file)
            if not validation['valid_pdf']:
                raise AssertionError("Merged PDF is invalid")
            
            # Check page count (should be sum of input pages)
            expected_pages = sum(PDFValidator.validate_pdf_file(f)['page_count'] for f in input_files)
            if validation['page_count'] != expected_pages:
                raise AssertionError(f"Page count mismatch: expected {expected_pages}, got {validation['page_count']}")
            
            self.test_results[test_name] = {
                'status': 'PASSED',
                'message': f'Merged {len(input_files)} PDFs into {validation["page_count"]} pages'
            }
            
        except Exception as e:
            self.test_results[test_name] = {
                'status': 'FAILED',
                'message': str(e)
            }
    
    def test_pdf_split_operation(self):
        """Test PDF split functionality"""
        test_name = "PDF Split Operation"
        logger.info(f"Testing {test_name}")
        
        try:
            engine = PDFOperationEngine()
            
            # Use the larger PDF for splitting
            input_file = self.sample_pdfs[2]  # 5-page PDF
            output_dir = os.path.join(self.temp_dir, "split_output")
            os.makedirs(output_dir, exist_ok=True)
            
            options = {
                'method': 'pages',
                'pages_per_file': 2,
                'naming_pattern': 'split_{index}.pdf'
            }
            
            result = engine.split_pdf(input_file, output_dir, options)
            
            if not result.success:
                raise AssertionError(f"Split failed: {result.error_message}")
            
            if not result.output_files:
                raise AssertionError("No output files were created")
            
            # Validate split files
            total_pages = 0
            for output_file in result.output_files:
                if not os.path.exists(output_file):
                    raise AssertionError(f"Output file not found: {output_file}")
                
                validation = PDFValidator.validate_pdf_file(output_file)
                if not validation['valid_pdf']:
                    raise AssertionError(f"Split PDF is invalid: {output_file}")
                
                total_pages += validation['page_count']
            
            # Check total pages match original
            original_validation = PDFValidator.validate_pdf_file(input_file)
            if total_pages != original_validation['page_count']:
                raise AssertionError(f"Page count mismatch: expected {original_validation['page_count']}, got {total_pages}")
            
            self.test_results[test_name] = {
                'status': 'PASSED',
                'message': f'Split {original_validation["page_count"]} pages into {len(result.output_files)} files'
            }
            
        except Exception as e:
            self.test_results[test_name] = {
                'status': 'FAILED',
                'message': str(e)
            }
    
    def test_pdf_sign_operation(self):
        """Test PDF sign functionality"""
        test_name = "PDF Sign Operation"
        logger.info(f"Testing {test_name}")
        
        try:
            engine = PDFOperationEngine()
            
            # Create a simple signature image
            signature_file = self.create_sample_signature()
            
            input_file = self.sample_pdfs[0]
            output_file = os.path.join(self.temp_dir, "signed_test.pdf")
            
            options = {
                'pages': 'first',
                'position': 'bottom_right',
                'size': (100, 50),
                'transparency': 0.8
            }
            
            result = engine.sign_pdf(input_file, signature_file, output_file, options)
            
            if not result.success:
                raise AssertionError(f"Sign failed: {result.error_message}")
            
            if not os.path.exists(output_file):
                raise AssertionError("Signed output file was not created")
            
            # Validate signed PDF
            validation = PDFValidator.validate_pdf_file(output_file)
            if not validation['valid_pdf']:
                raise AssertionError("Signed PDF is invalid")
            
            # Check page count matches original
            original_validation = PDFValidator.validate_pdf_file(input_file)
            if validation['page_count'] != original_validation['page_count']:
                raise AssertionError("Page count changed after signing")
            
            self.test_results[test_name] = {
                'status': 'PASSED',
                'message': f'Signed PDF with {validation["page_count"]} pages'
            }
            
        except Exception as e:
            self.test_results[test_name] = {
                'status': 'FAILED',
                'message': str(e)
            }
    
    def create_sample_signature(self):
        """Create a sample signature image for testing"""
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple signature image
            img = Image.new('RGBA', (200, 100), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a simple signature-like shape
            draw.text((10, 30), "Test Signature", fill=(0, 0, 0, 255))
            draw.line([(10, 60), (190, 60)], fill=(0, 0, 0, 255), width=2)
            
            signature_path = os.path.join(self.temp_dir, "signature.png")
            img.save(signature_path)
            
            return signature_path
            
        except ImportError:
            # Fallback: create a minimal image file
            signature_path = os.path.join(self.temp_dir, "signature.txt")
            with open(signature_path, 'w') as f:
                f.write("Test signature placeholder")
            return signature_path
    
    def test_parameter_dialogs(self):
        """Test parameter dialog creation"""
        test_name = "Parameter Dialogs"
        logger.info(f"Testing {test_name}")
        
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # Test merge dialog creation
            merge_dialog = PDFMergeDialog()
            if not hasattr(merge_dialog, 'get_merge_options'):
                raise AssertionError("Merge dialog missing required methods")
            
            # Test split dialog creation
            split_dialog = PDFSplitDialog()
            if not hasattr(split_dialog, 'get_split_options'):
                raise AssertionError("Split dialog missing required methods")
            
            # Test sign dialog creation
            sign_dialog = PDFSignDialog()
            if not hasattr(sign_dialog, 'get_sign_options'):
                raise AssertionError("Sign dialog missing required methods")
            
            self.test_results[test_name] = {
                'status': 'PASSED',
                'message': 'All parameter dialogs created successfully'
            }
            
        except Exception as e:
            self.test_results[test_name] = {
                'status': 'FAILED',
                'message': str(e)
            }
    
    def test_enhanced_widget_integration(self):
        """Test enhanced PDF tools widget integration"""
        test_name = "Enhanced Widget Integration"
        logger.info(f"Testing {test_name}")
        
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # Create enhanced PDF tools widget
            widget = EnhancedPDFToolsWidget()
            
            # Check if functional integration was initialized
            if not hasattr(widget, '_pdf_integration'):
                logger.warning("Functional integration not available, using fallback mode")
            
            # Test basic widget functionality
            if not hasattr(widget, 'merge_pdfs'):
                raise AssertionError("Widget missing merge_pdfs method")
            
            if not hasattr(widget, 'split_pdf'):
                raise AssertionError("Widget missing split_pdf method")
            
            if not hasattr(widget, 'sign_pdf'):
                raise AssertionError("Widget missing sign_pdf method")
            
            self.test_results[test_name] = {
                'status': 'PASSED',
                'message': 'Enhanced widget integration successful'
            }
            
        except Exception as e:
            self.test_results[test_name] = {
                'status': 'FAILED',
                'message': str(e)
            }
    
    def run_all_tests(self):
        """Run all tests in the suite"""
        logger.info("Starting PDF Functional Implementation Test Suite")
        
        if not COMPONENTS_AVAILABLE:
            logger.error("PDF components not available, skipping tests")
            return False
        
        if not self.setup_test_environment():
            logger.error("Failed to setup test environment")
            return False
        
        # Run individual tests
        test_methods = [
            self.test_pdf_validator,
            self.test_pdf_merge_operation,
            self.test_pdf_split_operation,
            self.test_pdf_sign_operation,
            self.test_parameter_dialogs,
            self.test_enhanced_widget_integration
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                test_name = test_method.__name__.replace('test_', '').replace('_', ' ').title()
                self.test_results[test_name] = {
                    'status': 'ERROR',
                    'message': f'Test execution error: {str(e)}'
                }
        
        # Print results
        self.print_test_results()
        
        # Cleanup
        self.cleanup_test_environment()
        
        # Return overall success
        failed_tests = [name for name, result in self.test_results.items() 
                       if result['status'] in ['FAILED', 'ERROR']]
        
        return len(failed_tests) == 0
    
    def print_test_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("PDF FUNCTIONAL IMPLEMENTATION TEST RESULTS")
        print("="*80)
        
        passed = 0
        failed = 0
        errors = 0
        
        for test_name, result in self.test_results.items():
            status = result['status']
            message = result['message']
            
            if status == 'PASSED':
                print(f"✅ {test_name:<30} PASSED - {message}")
                passed += 1
            elif status == 'FAILED':
                print(f"❌ {test_name:<30} FAILED - {message}")
                failed += 1
            else:  # ERROR
                print(f"💥 {test_name:<30} ERROR  - {message}")
                errors += 1
        
        print("-"*80)
        total = passed + failed + errors
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        
        if failed == 0 and errors == 0:
            print("\n🎉 ALL TESTS PASSED! PDF Functional Implementation is ready.")
        else:
            print(f"\n⚠️  {failed + errors} tests failed. Review implementation.")
        
        print("="*80)
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up test directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup test directory: {e}")


class PDFTestWidget(QWidget):
    """Simple test widget for manual testing"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("PDF Functional Implementation Test")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Test buttons
        auto_test_btn = QPushButton("Run Automated Tests")
        auto_test_btn.clicked.connect(self.run_automated_tests)
        layout.addWidget(auto_test_btn)
        
        manual_test_btn = QPushButton("Open Enhanced PDF Tools")
        manual_test_btn.clicked.connect(self.open_enhanced_tools)
        layout.addWidget(manual_test_btn)
        
        # Results area
        self.results_label = QLabel("Click 'Run Automated Tests' to start testing...")
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet("margin: 10px; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(self.results_label)
        
    def run_automated_tests(self):
        """Run automated test suite"""
        self.results_label.setText("Running automated tests...")
        QApplication.processEvents()
        
        # Run tests in a timer to keep UI responsive
        QTimer.singleShot(100, self._execute_tests)
    
    def _execute_tests(self):
        """Execute the test suite"""
        test_suite = PDFFunctionalTestSuite()
        success = test_suite.run_all_tests()
        
        if success:
            self.results_label.setText("✅ All tests passed! PDF functional implementation is working correctly.")
        else:
            self.results_label.setText("❌ Some tests failed. Check console output for details.")
    
    def open_enhanced_tools(self):
        """Open enhanced PDF tools for manual testing"""
        try:
            if COMPONENTS_AVAILABLE:
                self.pdf_widget = EnhancedPDFToolsWidget()
                self.pdf_widget.show()
                self.results_label.setText("Enhanced PDF Tools opened for manual testing.")
            else:
                self.results_label.setText("PDF components not available for manual testing.")
        except Exception as e:
            self.results_label.setText(f"Error opening enhanced tools: {str(e)}")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("PDF Functional Implementation Test")
    app.setApplicationVersion("2.1.0")
    
    # Create and show test widget
    test_widget = PDFTestWidget()
    test_widget.setWindowTitle("PDF Functional Implementation Test - Phase 2.1")
    test_widget.resize(600, 400)
    test_widget.show()
    
    # Also run automated tests if requested via command line
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        print("Running automated tests...")
        test_suite = PDFFunctionalTestSuite()
        success = test_suite.run_all_tests()
        sys.exit(0 if success else 1)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()