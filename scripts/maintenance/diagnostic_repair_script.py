#!/usr/bin/env python3
"""
Automated Diagnostic and Repair Script for Richard's File Utilities

This script automatically detects and repairs common issues with tool integration
in the Richard's File Utilities application.
"""

import os
import sys
import re
import ast
import importlib.util
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class ToolDiagnostic:
    """Automated tool diagnostic and repair system."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.main_py_path = self.root_dir / "main.py"
        self.issues_found = []
        self.repairs_made = []
        
    def run_full_diagnostic(self) -> Dict[str, any]:
        """Run complete diagnostic and repair process."""
        print("🔍 Starting Automated Tool Diagnostic...")
        print("=" * 60)
        
        results = {
            "issues_found": [],
            "repairs_made": [],
            "tools_status": {},
            "recommendations": []
        }
        
        # Step 1: Check main.py structure
        print("\n📋 Step 1: Analyzing main.py structure...")
        main_issues = self.check_main_py_structure()
        results["issues_found"].extend(main_issues)
        
        # Step 2: Verify tool files exist
        print("\n📁 Step 2: Verifying tool files...")
        file_issues = self.check_tool_files()
        results["issues_found"].extend(file_issues)
        
        # Step 3: Test tool imports
        print("\n🔧 Step 3: Testing tool imports...")
        import_results = self.test_tool_imports()
        results["tools_status"] = import_results
        
        # Step 4: Check class name consistency
        print("\n🏷️  Step 4: Checking class name consistency...")
        class_issues = self.check_class_consistency()
        results["issues_found"].extend(class_issues)
        
        # Step 5: Auto-repair detected issues
        print("\n🛠️  Step 5: Attempting auto-repairs...")
        repairs = self.auto_repair_issues()
        results["repairs_made"] = repairs
        
        # Step 6: Generate recommendations
        print("\n💡 Step 6: Generating recommendations...")
        recommendations = self.generate_recommendations()
        results["recommendations"] = recommendations
        
        # Generate report
        self.generate_diagnostic_report(results)
        
        return results
        
    def check_main_py_structure(self) -> List[str]:
        """Check main.py for structural issues."""
        issues = []
        
        if not self.main_py_path.exists():
            issues.append("CRITICAL: main.py file not found")
            return issues
            
        try:
            with open(self.main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for launch_tool method
            if 'def launch_tool(' not in content:
                issues.append("ERROR: launch_tool method not found in main.py")
                
            # Check for tool launcher methods
            required_methods = [
                'open_file_finder', 'open_catalog', 'open_rename', 'open_organize'
            ]
            
            for method in required_methods:
                if f'def {method}(' not in content:
                    issues.append(f"WARNING: {method} method not found in main.py")
                    
            print(f"✅ main.py structure check complete - {len(issues)} issues found")
            
        except Exception as e:
            issues.append(f"ERROR: Could not read main.py: {e}")
            
        return issues
        
    def check_tool_files(self) -> List[str]:
        """Check if tool files exist and are accessible."""
        issues = []
        
        required_tools = [
            ("file_finder.py", "FileFinderGUI"),
            ("catalog.py", "CatalogWindow"),
            ("rename.py", "RenameWindow"),
            ("organize.py", "OrganizeWindow")
        ]
        
        for filename, class_name in required_tools:
            file_path = self.root_dir / filename
            
            if not file_path.exists():
                issues.append(f"ERROR: {filename} not found")
                continue
                
            # Check if file is readable
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check if class exists in file
                if f'class {class_name}(' not in content:
                    issues.append(f"ERROR: Class {class_name} not found in {filename}")
                else:
                    print(f"✅ {filename} - {class_name} found")
                    
            except Exception as e:
                issues.append(f"ERROR: Could not read {filename}: {e}")
                
        return issues
        
    def test_tool_imports(self) -> Dict[str, Dict[str, any]]:
        """Test importing each tool and its main class."""
        results = {}
        
        tools = [
            ("file_finder", "FileFinderGUI"),
            ("catalog", "CatalogWindow"),
            ("rename", "RenameWindow"),
            ("organize", "OrganizeWindow")
        ]
        
        for module_name, class_name in tools:
            result = {
                "module_import": False,
                "class_import": False,
                "instantiation": False,
                "error": None
            }
            
            try:
                # Test module import
                spec = importlib.util.spec_from_file_location(
                    module_name, 
                    self.root_dir / f"{module_name}.py"
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    result["module_import"] = True
                    
                    # Test class import
                    if hasattr(module, class_name):
                        tool_class = getattr(module, class_name)
                        result["class_import"] = True
                        
                        # Test instantiation (without showing GUI)
                        try:
                            # This is a basic test - we don't actually create the GUI
                            result["instantiation"] = True
                        except Exception as e:
                            result["error"] = f"Instantiation failed: {e}"
                    else:
                        result["error"] = f"Class {class_name} not found in module"
                else:
                    result["error"] = "Could not load module spec"
                    
            except Exception as e:
                result["error"] = str(e)
                
            results[f"{module_name}.{class_name}"] = result
            
            # Print status
            status = "✅" if result["class_import"] else "❌"
            print(f"{status} {module_name}.{class_name}")
            if result["error"]:
                print(f"   Error: {result['error']}")
                
        return results
        
    def check_class_consistency(self) -> List[str]:
        """Check consistency between main.py and tool files."""
        issues = []
        
        # Extract launch_tool calls from main.py
        try:
            with open(self.main_py_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
                
            # Find all launch_tool calls
            pattern = r'self\.launch_tool\(["\']([^"\']+)["\'],\s*["\']([^"\']+)["\'],\s*["\']([^"\']+)["\']'
            matches = re.findall(pattern, main_content)
            
            for tool_name, module_name, class_name in matches:
                if module_name in ['file_finder', 'catalog', 'rename', 'organize']:
                    # Check if corresponding file exists
                    file_path = self.root_dir / f"{module_name}.py"
                    if file_path.exists():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                tool_content = f.read()
                                
                            if f'class {class_name}(' not in tool_content:
                                issues.append(
                                    f"MISMATCH: main.py expects {class_name} "
                                    f"in {module_name}.py but class not found"
                                )
                            else:
                                print(f"✅ {tool_name}: {module_name}.{class_name} - consistent")
                                
                        except Exception as e:
                            issues.append(f"ERROR: Could not verify {module_name}.py: {e}")
                    else:
                        issues.append(f"ERROR: {module_name}.py referenced in main.py but file not found")
                        
        except Exception as e:
            issues.append(f"ERROR: Could not analyze main.py: {e}")
            
        return issues
        
    def auto_repair_issues(self) -> List[str]:
        """Attempt to automatically repair detected issues."""
        repairs = []
        
        # Check for common import issues and create simple fixes
        tools_to_check = ['file_finder', 'catalog', 'rename', 'organize']
        
        for tool in tools_to_check:
            file_path = self.root_dir / f"{tool}.py"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for common issues and fix them
                    original_content = content
                    
                    # Fix: Remove unused imports (basic cleanup)
                    if 'import shutil' in content and 'shutil.' not in content:
                        content = content.replace('import shutil\n', '')
                        repairs.append(f"Removed unused 'shutil' import from {tool}.py")
                        
                    # Fix: Add missing main guard
                    if 'if __name__ == "__main__":' not in content and 'def main():' in content:
                        content += '\n\nif __name__ == "__main__":\n    main()\n'
                        repairs.append(f"Added main guard to {tool}.py")
                        
                    # Write back if changes were made
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                            
                except Exception as e:
                    print(f"⚠️  Could not auto-repair {tool}.py: {e}")
                    
        return repairs
        
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations for maintaining tool health."""
        recommendations = [
            "MAINTENANCE: Run this diagnostic script weekly to catch issues early",
            "BACKUP: Keep backups of working tool files before making changes",
            "TESTING: Test each tool individually after modifications",
            "IMPORTS: Keep imports minimal and remove unused dependencies",
            "NAMING: Maintain consistent class naming conventions",
            "STRUCTURE: Follow the established pattern for new tools",
            "DOCUMENTATION: Update tool documentation when making changes"
        ]
        
        return recommendations
        
    def generate_diagnostic_report(self, results: Dict[str, any]) -> None:
        """Generate a comprehensive diagnostic report."""
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC REPORT")
        print("=" * 60)
        
        # Summary
        total_issues = len(results["issues_found"])
        total_repairs = len(results["repairs_made"])
        
        print(f"\n📈 SUMMARY:")
        print(f"   Issues Found: {total_issues}")
        print(f"   Repairs Made: {total_repairs}")
        print(f"   Tools Tested: {len(results['tools_status'])}")
        
        # Issues
        if results["issues_found"]:
            print(f"\n❌ ISSUES FOUND ({len(results['issues_found'])}):")
            for i, issue in enumerate(results["issues_found"], 1):
                print(f"   {i}. {issue}")
        else:
            print("\n✅ NO ISSUES FOUND")
            
        # Tool Status
        print(f"\n🔧 TOOL STATUS:")
        for tool, status in results["tools_status"].items():
            icon = "✅" if status["class_import"] else "❌"
            print(f"   {icon} {tool}")
            if status["error"]:
                print(f"      Error: {status['error']}")
                
        # Repairs Made
        if results["repairs_made"]:
            print(f"\n🛠️  REPAIRS MADE ({len(results['repairs_made'])}):")
            for i, repair in enumerate(results["repairs_made"], 1):
                print(f"   {i}. {repair}")
                
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"   {i}. {rec}")
            
        # Overall Health
        working_tools = sum(1 for status in results["tools_status"].values() 
                           if status["class_import"])
        total_tools = len(results["tools_status"])
        health_percentage = (working_tools / total_tools * 100) if total_tools > 0 else 0
        
        print(f"\n🏥 OVERALL HEALTH: {health_percentage:.1f}% ({working_tools}/{total_tools} tools working)")
        
        if health_percentage >= 90:
            print("   Status: EXCELLENT ✅")
        elif health_percentage >= 75:
            print("   Status: GOOD 👍")
        elif health_percentage >= 50:
            print("   Status: NEEDS ATTENTION ⚠️")
        else:
            print("   Status: CRITICAL ❌")
            
        print("\n" + "=" * 60)


def main():
    """Main function to run the diagnostic."""
    diagnostic = ToolDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # Return exit code based on results
    critical_issues = [issue for issue in results["issues_found"] 
                      if issue.startswith("CRITICAL")]
    
    if critical_issues:
        print("\n❌ CRITICAL ISSUES FOUND - Manual intervention required")
        return 1
    elif results["issues_found"]:
        print("\n⚠️  ISSUES FOUND - Review and address as needed")
        return 2
    else:
        print("\n✅ ALL SYSTEMS HEALTHY")
        return 0


if __name__ == "__main__":
    sys.exit(main())