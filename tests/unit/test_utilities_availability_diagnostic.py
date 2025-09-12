#!/usr/bin/env python3
"""
Phase 6: Utilities Module Availability Diagnostic Test
Created: September 9, 2025
Purpose: Debug utilities module availability issue (CF-001)

CRITICAL INVESTIGATION: Issue CF-001
- Current: 20% utilities availability
- Required: 50% utilities availability  
- Target: Debug root cause of module accessibility issues
"""

import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for imports (proper path configuration)
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

print("=== PHASE 6: UTILITIES AVAILABILITY DIAGNOSTIC ===")
print(f"Source path: {src_path}")
print(f"Python path includes src: {str(src_path) in sys.path}")


def detailed_import_analysis() -> Dict[str, Any]:
    """Perform detailed analysis of utilities import capabilities."""
    
    results = {
        'utilities_package': None,
        'module_availability': {},
        'direct_imports': {},
        'error_details': {},
        'recommendations': []
    }
    
    # Step 1: Test utilities package import
    print("\n--- STEP 1: UTILITIES PACKAGE IMPORT ---")
    try:
        import utilities
        results['utilities_package'] = {
            'imported': True,
            'module_path': getattr(utilities, '__file__', 'Unknown'),
            'version': getattr(utilities, '__version__', 'Unknown'),
            'all_exports': getattr(utilities, '__all__', [])
        }
        print(f"✅ utilities package imported successfully")
        print(f"   Path: {results['utilities_package']['module_path']}")
        print(f"   Version: {results['utilities_package']['version']}")
        print(f"   Exports: {results['utilities_package']['all_exports']}")
        
        # Test get_available_utilities function
        if hasattr(utilities, 'get_available_utilities'):
            available_utils = utilities.get_available_utilities()
            print(f"   Available utilities: {len(available_utils)}")
            for name, info in available_utils.items():
                status = "✅ Available" if info['available'] else "❌ Not Available"
                print(f"     {name}: {status}")
                results['module_availability'][name] = info['available']
        
    except ImportError as e:
        results['utilities_package'] = {'imported': False, 'error': str(e)}
        results['error_details']['utilities_package'] = traceback.format_exc()
        print(f"❌ utilities package import failed: {e}")
        return results
    
    # Step 2: Test individual module access via getattr
    print("\n--- STEP 2: MODULE ACCESS VIA GETATTR ---")
    target_modules = ['analysis', 'security', 'network', 'privacy', 'file_management']
    
    for module_name in target_modules:
        try:
            module = getattr(utilities, module_name, None)
            if module is not None:
                results['direct_imports'][module_name] = {
                    'accessible': True,
                    'module_type': str(type(module)),
                    'module_path': getattr(module, '__file__', 'Unknown'),
                    'has_classes': len([attr for attr in dir(module) 
                                      if not attr.startswith('_')]) > 0
                }
                print(f"✅ {module_name}: Accessible via getattr")
                print(f"   Type: {results['direct_imports'][module_name]['module_type']}")
                print(f"   Path: {results['direct_imports'][module_name]['module_path']}")
                print(f"   Has classes: {results['direct_imports'][module_name]['has_classes']}")
            else:
                results['direct_imports'][module_name] = {
                    'accessible': False,
                    'error': 'getattr returned None'
                }
                print(f"❌ {module_name}: getattr returned None")
                
        except Exception as e:
            results['direct_imports'][module_name] = {
                'accessible': False,
                'error': str(e)
            }
            results['error_details'][f'getattr_{module_name}'] = traceback.format_exc()
            print(f"❌ {module_name}: getattr error: {e}")
    
    # Step 3: Test direct imports of submodules
    print("\n--- STEP 3: DIRECT SUBMODULE IMPORTS ---")
    direct_import_tests = [
        ('utilities.analysis', 'Analysis Tools'),
        ('utilities.security', 'Security Tools'),
        ('utilities.network', 'Network Tools'),
        ('utilities.privacy', 'Privacy Tools'),
        ('utilities.file_management', 'File Management Tools')
    ]
    
    for import_path, description in direct_import_tests:
        try:
            module = __import__(import_path, fromlist=[''])
            results[f'direct_import_{import_path.split(".")[-1]}'] = {
                'imported': True,
                'description': description,
                'module_path': getattr(module, '__file__', 'Unknown'),
                'exports': getattr(module, '__all__', [])
            }
            print(f"✅ {import_path}: Direct import successful")
            print(f"   Description: {description}")
            print(f"   Path: {getattr(module, '__file__', 'Unknown')}")
            
            # Test if module has validation functions
            if hasattr(module, 'validate_imports'):
                try:
                    validation_result = module.validate_imports()
                    print(f"   Validation: {'✅ Passed' if validation_result else '❌ Failed'}")
                except Exception as ve:
                    print(f"   Validation error: {ve}")
            
        except ImportError as e:
            results[f'direct_import_{import_path.split(".")[-1]}'] = {
                'imported': False,
                'error': str(e),
                'description': description
            }
            results['error_details'][f'direct_import_{import_path}'] = traceback.format_exc()
            print(f"❌ {import_path}: Direct import failed: {e}")
    
    # Step 4: Analyze getattr vs direct import discrepancies
    print("\n--- STEP 4: DISCREPANCY ANALYSIS ---")
    for module_name in target_modules:
        getattr_success = results['direct_imports'].get(module_name, {}).get('accessible', False)
        direct_import_success = results.get(f'direct_import_{module_name}', {}).get('imported', False)
        
        if direct_import_success and not getattr_success:
            discrepancy = f"Module {module_name} can be imported directly but not accessible via getattr"
            results['recommendations'].append(discrepancy)
            print(f"🔍 DISCREPANCY: {discrepancy}")
        elif getattr_success and not direct_import_success:
            discrepancy = f"Module {module_name} accessible via getattr but direct import fails"
            results['recommendations'].append(discrepancy)
            print(f"🔍 DISCREPANCY: {discrepancy}")
    
    return results


def calculate_availability_metrics(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate utilities availability metrics."""
    
    # Count modules accessible via getattr (current test method)
    getattr_available = sum(1 for module_info in results['direct_imports'].values() 
                           if module_info.get('accessible', False))
    total_modules = len(results['direct_imports'])
    getattr_percentage = (getattr_available / total_modules * 100) if total_modules > 0 else 0
    
    # Count modules available via direct import
    direct_import_available = sum(1 for key, module_info in results.items() 
                                 if key.startswith('direct_import_') and 
                                 module_info.get('imported', False))
    direct_import_percentage = (direct_import_available / total_modules * 100) if total_modules > 0 else 0
    
    metrics = {
        'getattr_availability': {
            'available_count': getattr_available,
            'total_count': total_modules,
            'percentage': getattr_percentage,
            'meets_threshold': getattr_percentage >= 50.0
        },
        'direct_import_availability': {
            'available_count': direct_import_available,
            'total_count': total_modules,
            'percentage': direct_import_percentage,
            'meets_threshold': direct_import_percentage >= 50.0
        }
    }
    
    return metrics


def generate_resolution_recommendations(results: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
    """Generate specific recommendations for fixing the utilities availability issue."""
    
    recommendations = []
    
    # Check if utilities package imported successfully
    if not results.get('utilities_package', {}).get('imported', False):
        recommendations.append("CRITICAL: Fix utilities package import error")
        return recommendations
    
    # Check getattr vs direct import discrepancies
    getattr_success = metrics['getattr_availability']['meets_threshold']
    direct_import_success = metrics['direct_import_availability']['meets_threshold']
    
    if direct_import_success and not getattr_success:
        recommendations.append("SOLUTION: utilities package modules available but not properly exposed in __init__.py")
        recommendations.append("ACTION: Fix utilities.__init__.py to properly expose submodules via globals()")
        recommendations.append("TECHNICAL: safe_import() may be returning None instead of actual modules")
    
    elif not direct_import_success and not getattr_success:
        recommendations.append("ISSUE: Fundamental import problems with utilities submodules")
        recommendations.append("ACTION: Debug individual submodule __init__.py files")
        recommendations.append("CHECK: Verify all required dependencies are available")
    
    elif getattr_success:
        recommendations.append("STATUS: Utilities availability issue may be resolved")
        recommendations.append("ACTION: Re-run comprehensive tests to validate")
    
    # Add specific module recommendations
    for module_name, module_info in results['direct_imports'].items():
        if not module_info.get('accessible', False):
            error = module_info.get('error', 'Unknown error')
            recommendations.append(f"DEBUG: {module_name} module issue: {error}")
    
    return recommendations


def main():
    """Execute comprehensive utilities availability diagnostic."""
    
    print("DIAGNOSING ISSUE CF-001: Utilities Module Availability")
    print("Target: Identify root cause of 20% vs 50% availability gap")
    print("=" * 60)
    
    # Execute detailed analysis
    results = detailed_import_analysis()
    
    # Calculate metrics
    metrics = calculate_availability_metrics(results)
    
    # Display metrics
    print("\n=== AVAILABILITY METRICS ===")
    print(f"Current getattr method: {metrics['getattr_availability']['percentage']:.1f}% "
          f"({metrics['getattr_availability']['available_count']}/{metrics['getattr_availability']['total_count']})")
    print(f"Direct import method: {metrics['direct_import_availability']['percentage']:.1f}% "
          f"({metrics['direct_import_availability']['available_count']}/{metrics['direct_import_availability']['total_count']})")
    
    print(f"Meets 50% threshold (getattr): {'✅ Yes' if metrics['getattr_availability']['meets_threshold'] else '❌ No'}")
    print(f"Meets 50% threshold (direct): {'✅ Yes' if metrics['direct_import_availability']['meets_threshold'] else '❌ No'}")
    
    # Generate and display recommendations
    recommendations = generate_resolution_recommendations(results, metrics)
    
    print("\n=== RESOLUTION RECOMMENDATIONS ===")
    for i, recommendation in enumerate(recommendations, 1):
        print(f"{i}. {recommendation}")
    
    # Determine next actions
    print("\n=== IMMEDIATE NEXT ACTIONS ===")
    
    if metrics['direct_import_availability']['meets_threshold']:
        print("🎯 SOLUTION IDENTIFIED: Utilities modules are available but not properly exposed")
        print("🔧 ACTION: Fix utilities.__init__.py to properly expose modules via getattr")
        print("⏱️ ESTIMATED TIME: 15-30 minutes")
        print("🧪 VALIDATION: Re-run comprehensive tests after fix")
    else:
        print("🚨 DEEPER INVESTIGATION REQUIRED: Fundamental import issues detected")
        print("🔍 ACTION: Debug individual submodule import failures")
        print("⏱️ ESTIMATED TIME: 1-2 hours")
        print("📋 PRIORITY: Address import errors before proceeding")
    
    # Return success status
    success = (metrics['getattr_availability']['meets_threshold'] or 
              metrics['direct_import_availability']['meets_threshold'])
    
    print(f"\n=== DIAGNOSTIC RESULT ===")
    print(f"Status: {'🎉 ROOT CAUSE IDENTIFIED' if success else '🚨 ADDITIONAL INVESTIGATION REQUIRED'}")
    
    return results, metrics, recommendations


if __name__ == '__main__':
    try:
        results, metrics, recommendations = main()
        print("\nDiagnostic completed successfully")
    except Exception as e:
        print(f"\nDiagnostic failed: {e}")
        traceback.print_exc()
        sys.exit(1)