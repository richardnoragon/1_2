"""
Office Metadata Tools Demo

This demo script showcases the Office Metadata Tools GUI functionality,
demonstrating metadata extraction, security analysis, and export capabilities.
"""

import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from src.tools.metadata.office_metadata import OfficeMetadataGUI
    
    def main():
        """Main function to run the Office Metadata Tools demo."""
        print("="*60)
        print("Office Metadata Tools - GUI Demo")
        print("="*60)
        print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Initialize the application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Show welcome message
        welcome_msg = """
        Welcome to Office Metadata Tools!
        
        This tool provides comprehensive metadata analysis for:
        • Microsoft Office documents (DOCX, XLSX, PPTX)
        • Legacy Office formats (DOC, XLS, PPT) 
        • PDF documents
        
        Features demonstrated:
        ✓ Multi-tab metadata viewing
        ✓ Security analysis and privacy scanning
        ✓ Export to JSON, XML, CSV formats
        ✓ File information and statistics
        ✓ Custom properties management
        
        Instructions:
        1. Click "Open File" to select an office document
        2. Browse through the tabs to explore metadata
        3. Check "Security Analysis" for privacy concerns
        4. Use "Export Metadata" to save analysis results
        
        Click OK to launch the Office Metadata Tools GUI...
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Office Metadata Tools - Demo")
        msg_box.setText(welcome_msg)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        if msg_box.exec_() == QMessageBox.Ok:
            print("Launching Office Metadata Tools GUI...")
            
            # Create and show the main window
            window = OfficeMetadataGUI()
            window.show()
            
            print("Office Metadata Tools GUI launched successfully!")
            print()
            print("GUI Features Available:")
            print("• File Information tab - Basic file details and statistics")
            print("• Core Properties tab - Title, author, subject, keywords")
            print("• App Properties tab - Application and document statistics")  
            print("• Custom Properties tab - User-defined metadata fields")
            print("• Security Analysis tab - Privacy and security concerns")
            print("• Raw Data tab - Complete metadata in JSON format")
            print()
            print("Security Features:")
            print("• Automatic detection of personal information")
            print("• Company and organizational data identification")
            print("• Custom property security scanning")
            print("• Privacy recommendation generation")
            print()
            print("Export Options:")
            print("• JSON format for structured data")
            print("• XML format for compatibility")
            print("• CSV format for spreadsheet analysis")
            print("• Text format for human readability")
            print()
            print("Future Enhancements:")
            print("• Metadata editing and modification")
            print("• Batch processing of multiple files")
            print("• Automated metadata cleaning")
            print("• Template-based metadata application")
            print()
            print("Note: Some features require additional Python libraries:")
            print("• olefile and python-oletools for legacy Office formats")
            print("• PyPDF2 or similar for full PDF metadata support")
            print()
            print("The GUI is now ready for use. The demo will continue running...")
            print("Close the GUI window to end the demo.")
            
            # Run the application
            result = app.exec_()
            
            print("\nOffice Metadata Tools demo completed.")
            print(f"Demo ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("Thank you for trying Office Metadata Tools!")
            
            return result
        else:
            print("Demo cancelled by user.")
            return 0

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("\nRequired dependencies:")
    print("• PyQt5 for GUI functionality")
    print("• Standard Python libraries (json, xml, zipfile)")
    print("\nOptional dependencies for enhanced features:")
    print("• olefile and python-oletools for legacy Office formats")
    print("• PyPDF2 for PDF metadata extraction")
    print("\nPlease install the required dependencies and try again.")
    
    def main():
        return 1

except Exception as e:
    print(f"Error running Office Metadata Tools demo: {e}")
    
    def main():
        return 1


if __name__ == "__main__":
    sys.exit(main())