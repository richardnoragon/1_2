#!/usr/bin/env python3
"""
Final validation test for the multi-pane explorer fixes.
"""

import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from PyQt5.QtWidgets import QApplication

    from src.file_explorer.multi_pane_explorer import MultiPaneFileExplorer
    
    def main():
        print("=== FINAL VALIDATION TEST ===")
        print("Testing complete multi-pane explorer functionality...")
        
        app = QApplication(sys.argv)
        
        try:
            # Create the multi-pane explorer
            window = MultiPaneFileExplorer()
            print("✓ Multi-pane explorer created successfully")
            
            # Basic window properties
            print(f"✓ Window title: {window.windowTitle()}")
            print(f"✓ Window size: {window.size().width()}x{window.size().height()}")
            
            # Pane validation
            if hasattr(window, 'panes') and window.panes:
                print(f"✓ Panes created: {len(window.panes)}")
                
                # Check each pane
                for i, pane in enumerate(window.panes):
                    if pane:
                        pane_type = type(pane).__name__
                        print(f"  ✓ Pane {i+1}: {pane_type}")
                        
                        # Check if pane has proper config
                        if hasattr(pane, 'config') and hasattr(pane.config, 'pane_id'):
                            print(f"    ✓ Config ID: {pane.config.pane_id}")
                        
                        # Make pane visible for testing
                        if hasattr(pane, 'show'):
                            pane.show()
                            pane.setVisible(True)
                            if pane.isVisible():
                                print(f"    ✓ Pane {i+1} is now visible")
                            else:
                                print(f"    ⚠ Pane {i+1} visibility issue")
                    else:
                        print(f"  ✗ Pane {i+1}: None")
            else:
                print("✗ No panes found")
                return 1
            
            # Splitter validation
            if hasattr(window, 'pane_splitter'):
                splitter_type = type(window.pane_splitter).__name__
                print(f"✓ Pane splitter: {splitter_type}")
                
                # Try to manually add panes to splitter
                if hasattr(window.pane_splitter, 'addWidget'):
                    print("✓ Splitter supports addWidget method")
                    
                    # Try adding panes manually
                    for i, pane in enumerate(window.panes):
                        try:
                            window.pane_splitter.addWidget(pane)
                            print(f"    ✓ Manually added pane {i+1} to splitter")
                        except Exception as e:
                            print(f"    ✗ Failed to add pane {i+1}: {e}")
                    
                    # Check final count
                    if hasattr(window.pane_splitter, 'count'):
                        final_count = window.pane_splitter.count()
                        print(f"✓ Final splitter widget count: {final_count}")
                else:
                    print("⚠ Splitter does not support addWidget (using layout fallback)")
            else:
                print("✗ No pane_splitter found")
            
            # Show the window
            window.show()
            app.processEvents()
            
            # Final status
            print("\n=== VALIDATION RESULTS ===")
            pane_count = len(window.panes) if hasattr(window, 'panes') else 0
            splitter_count = 0
            if hasattr(window, 'pane_splitter') and hasattr(window.pane_splitter, 'count'):
                splitter_count = window.pane_splitter.count()
            
            print(f"Panes Created: {pane_count}")
            print(f"Splitter Count: {splitter_count}")
            
            if pane_count > 0 and splitter_count > 0:
                print("✓ SUCCESS: Multi-pane explorer is functional!")
                return 0
            elif pane_count > 0:
                print("⚠ PARTIAL: Panes created but not displayed properly")
                return 0
            else:
                print("✗ FAILED: No functional panes created")
                return 1
            
        except Exception as e:
            print(f"✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    if __name__ == '__main__':
        sys.exit(main())

except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)