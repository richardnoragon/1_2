"""
Simple import verification for Phase 3 migration
This script tests the key imports without GUI instantiation
"""

def test_imports():
    """Test all critical imports"""
    results = []
    
    # Test 1: file_utilities_1 package import
    try:
        from file_utilities_1 import FileFinderWindow
        results.append("✅ file_utilities_1.FileFinderWindow import: SUCCESS")
    except Exception as e:
        results.append(f"❌ file_utilities_1.FileFinderWindow import: FAILED - {e}")
    
    # Test 2: Backward compatibility import
    try:
        from file_finder import FileFinder
        results.append("✅ file_finder.FileFinder import: SUCCESS")
    except Exception as e:
        results.append(f"❌ file_finder.FileFinder import: FAILED - {e}")
    
    # Test 3: Direct module import
    try:
        from file_utilities_1.file_finder import FileFinderWindow as FFW
        results.append("✅ Direct module import: SUCCESS")
    except Exception as e:
        results.append(f"❌ Direct module import: FAILED - {e}")
    
    # Test 4: Package structure
    try:
        import file_utilities_1
        if hasattr(file_utilities_1, 'FileFinderWindow'):
            results.append("✅ Package exports FileFinderWindow: SUCCESS")
        else:
            results.append("❌ Package exports FileFinderWindow: FAILED")
    except Exception as e:
        results.append(f"❌ Package structure test: FAILED - {e}")
    
    return results

if __name__ == "__main__":
    print("Phase 3 Import Verification")
    print("=" * 40)
    
    results = test_imports()
    for result in results:
        print(result)
    
    success_count = sum(1 for r in results if r.startswith("✅"))
    total_count = len(results)
    
    print("=" * 40)
    print(f"Results: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("🎉 All imports working correctly!")
    else:
        print("⚠️ Some imports failed - check above for details")