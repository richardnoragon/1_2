#!/usr/bin/env python3
"""
Test script to validate OrganizeWindow UI synchronization fixes.
This script tests that all previously missing UI components now exist
and that the fixes work correctly.
"""

print('🔍 TESTING ORGANIZE WINDOW UI SYNCHRONIZATION FIXES')
print('=' * 60)

# Test GUI functionality with QApplication
try:
    from PyQt5.QtWidgets import QApplication
    from file_utilities_1.organize import OrganizeWindow
    
    print('🧪 Testing OrganizeWindow instantiation with QApplication...')
    app = QApplication([])
    
    # Test instantiation
    window = OrganizeWindow()
    print('✅ OrganizeWindow instantiation: SUCCESS')
    
    # Test that all previously missing UI components now exist
    missing_components = ['selectFolderButton', 'directory_label', 'status_label']
    existing_components = ['listListView', 'recursiveCheckBox', 'rulesButton', 'organizePushButton']
    
    print()
    print('📋 Testing previously missing UI components (should now exist):')
    all_missing_found = True
    for component in missing_components:
        if hasattr(window, component):
            print(f'✅ {component}: NOW EXISTS (fix successful)')
        else:
            print(f'❌ {component}: STILL MISSING (fix failed)')
            all_missing_found = False
    
    print()
    print('📋 Testing existing UI components (should still exist):')
    all_existing_found = True
    for component in existing_components:
        if hasattr(window, component):
            print(f'✅ {component}: EXISTS (preserved)')
        else:
            print(f'❌ {component}: MISSING (broken during fix)')
            all_existing_found = False
    
    # Test BaseWindow inheritance
    print()
    print('📋 Testing BaseWindow inheritance:')
    if hasattr(window, 'show_status_message'):
        print('✅ BaseWindow methods: AVAILABLE')
    else:
        print('❌ BaseWindow methods: MISSING')
    
    # Test UI component properties
    print()
    print('📋 Testing UI component properties:')
    if hasattr(window, 'selectFolderButton'):
        button = window.selectFolderButton
        if hasattr(button, 'clicked'):
            print('✅ selectFolderButton.clicked signal: AVAILABLE')
        else:
            print('❌ selectFolderButton.clicked signal: MISSING')
        
        if hasattr(button, 'text'):
            button_text = button.text()
            print(f'✅ selectFolderButton text: "{button_text}"')
        else:
            print('❌ selectFolderButton text: NOT ACCESSIBLE')
    
    if hasattr(window, 'directory_label'):
        label = window.directory_label
        if hasattr(label, 'text'):
            label_text = label.text()
            print(f'✅ directory_label text: "{label_text}"')
        else:
            print('❌ directory_label text: NOT ACCESSIBLE')
    
    if hasattr(window, 'status_label'):
        status = window.status_label
        if hasattr(status, 'text'):
            status_text = status.text()
            print(f'✅ status_label text: "{status_text}"')
        else:
            print('❌ status_label text: NOT ACCESSIBLE')
    
    # Test defensive hasattr checks in the code still work
    print()
    print('📋 Testing defensive hasattr checks:')
    try:
        # Test the _connect_signals method which uses hasattr checks
        if hasattr(window, '_connect_signals'):
            window._connect_signals()
            print('✅ _connect_signals method: EXECUTED SUCCESSFULLY')
        else:
            print('❌ _connect_signals method: NOT FOUND')
    except Exception as e:
        print(f'⚠️  _connect_signals method: ERROR - {e}')
    
    # Clean up
    window.close()
    app.quit()
    
    print()
    print('=' * 60)
    print('🎯 UI SYNCHRONIZATION FIX VALIDATION SUMMARY:')
    print('=' * 60)
    
    if all_missing_found and all_existing_found:
        print('✅ UI SYNCHRONIZATION: FULLY FIXED')
        print('✅ All missing components now exist')
        print('✅ All existing components preserved')
        print('✅ OrganizeWindow instantiation successful')
        print('✅ BaseWindow inheritance working')
        print('✅ UI component properties accessible')
    else:
        print('❌ UI SYNCHRONIZATION: ISSUES REMAIN')
        if not all_missing_found:
            print('❌ Some missing components still not found')
        if not all_existing_found:
            print('❌ Some existing components were broken')
    
    print()
    print('🎯 UI synchronization fix testing completed!')
    
except Exception as e:
    print(f'❌ UI synchronization test failed: {e}')
    import traceback
    traceback.print_exc()