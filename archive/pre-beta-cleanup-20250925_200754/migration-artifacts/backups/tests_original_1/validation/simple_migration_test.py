"""Simple migration test for Image Metadata Editor"""

def test_basic_imports():
    """Test basic imports work"""
    try:
        print("Testing core logic import...")
        from file_utilities_2.core.image_metadata_logic import ImageMetadataLogic
        print("✓ Core logic imported successfully")
        
        print("Testing GUI import...")
        from file_utilities_2.gui.image_metadata_gui import ImageMetadataEditor
        print("✓ GUI imported successfully")
        
        print("Testing package-level imports...")
        from file_utilities_2 import ImageMetadataLogic as PkgLogic
        from file_utilities_2 import ImageMetadataEditor as PkgEditor
        print("✓ Package-level imports successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_file_existence():
    """Test that migrated files exist"""
    import os
    
    files = [
        "file_utilities_2/core/image_metadata_logic.py",
        "file_utilities_2/gui/image_metadata_gui.py", 
        "file_utilities_2/gui/image_metadata.ui",
        "file_utilities_2/tests/test_image_metadata.py"
    ]
    
    all_exist = True
    for file_path in files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 50)
    print("IMAGE METADATA MIGRATION TEST")
    print("=" * 50)
    
    print("\nFile Existence Check:")
    files_ok = test_file_existence()
    
    print("\nImport Test:")
    imports_ok = test_basic_imports()
    
    print("\n" + "=" * 50)
    if files_ok and imports_ok:
        print("✓ MIGRATION TEST: SUCCESS")
        print("All basic components are working!")
    else:
        print("✗ MIGRATION TEST: FAILED")
        print("Some issues detected.")
    
    return files_ok and imports_ok

if __name__ == "__main__":
    main()