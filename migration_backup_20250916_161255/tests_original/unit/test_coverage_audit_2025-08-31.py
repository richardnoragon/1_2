#!/usr/bin/env python3
"""
Comprehensive Test Coverage Audit Script
Generated: 2025-08-31
Purpose: Identify actual test coverage gaps and correct the utilities-overview.md file

This script will:
1. Search for all utility files in the project
2. Check for corresponding test files
3. Generate an accurate coverage report
4. Identify files that actually need tests
5. Update the utilities-overview.md with correct information
"""

import glob
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


class TestCoverageAuditor:
    """Comprehensive test coverage auditor for the RFU project."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        self.unit_tests_dir = self.tests_dir / "unit"
        
        # Results storage
        self.coverage_report = {
            "audit_date": datetime.now().isoformat(),
            "total_utilities": 0,
            "total_test_files": 0,
            "files_with_tests": {},
            "files_without_tests": {},
            "misreported_files": {},
            "test_file_patterns": {},
            "summary": {}
        }
        
        # File patterns for utilities
        self.utility_patterns = [
            "**/*.py",
        ]
        
        # Exclude patterns (files that don't need tests)
        self.exclude_patterns = [
            "__init__.py",
            "__pycache__",
            "setup.py",
            "conftest.py",
            "**/tests/**",
            "**/test_**",
            "**/backup/**",
            "**/legacy/**",
            "**/deprecated/**"
        ]
        
        # Test file patterns
        self.test_patterns = [
            "test_*.py",
            "*_test.py",
            "test*.py"
        ]
    
    def find_utility_files(self) -> List[Path]:
        """Find all utility files in the src directory."""
        utility_files = []
        
        for pattern in self.utility_patterns:
            files = list(self.src_dir.glob(pattern))
            utility_files.extend(files)
        
        # Filter out excluded files
        filtered_files = []
        for file_path in utility_files:
            relative_path = file_path.relative_to(self.project_root)
            exclude = False
            
            for exclude_pattern in self.exclude_patterns:
                if file_path.match(exclude_pattern) or exclude_pattern in str(relative_path):
                    exclude = True
                    break
            
            if not exclude and file_path.is_file():
                filtered_files.append(file_path)
        
        return sorted(filtered_files)
    
    def find_test_files(self) -> List[Path]:
        """Find all test files in the project."""
        test_files = []
        
        # Search in multiple locations
        search_dirs = [
            self.tests_dir,
            self.project_root,  # Root level test files
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in self.test_patterns:
                    files = list(search_dir.glob(f"**/{pattern}"))
                    test_files.extend(files)
        
        return sorted(list(set(test_files)))
    
    def extract_module_name(self, file_path: Path) -> str:
        """Extract the module name from a file path."""
        return file_path.stem
    
    def find_tests_for_utility(self, utility_path: Path, test_files: List[Path]) -> List[Path]:
        """Find test files that correspond to a specific utility."""
        module_name = self.extract_module_name(utility_path)
        matching_tests = []
        
        # Common test naming patterns
        patterns = [
            f"test_{module_name}.py",
            f"test_{module_name}_*.py",
            f"{module_name}_test.py",
            f"test*{module_name}*.py"
        ]
        
        for test_file in test_files:
            test_name = test_file.name
            for pattern in patterns:
                if re.match(pattern.replace("*", ".*"), test_name, re.IGNORECASE):
                    matching_tests.append(test_file)
                    break
        
        return matching_tests
    
    def analyze_test_quality(self, test_file_path: Path) -> Dict:
        """Analyze the quality and comprehensiveness of a test file."""
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "file_size": len(content),
                "line_count": len(content.split('\n')),
                "test_functions": len(re.findall(r'def test_\w+', content)),
                "test_classes": len(re.findall(r'class Test\w+', content)),
                "has_pytest": 'pytest' in content,
                "has_mock": 'mock' in content.lower() or 'Mock' in content,
                "has_fixtures": '@pytest.fixture' in content,
                "has_parametrize": 'parametrize' in content,
                "has_coverage": 'coverage' in content.lower(),
                "has_error_handling": 'except' in content or 'Exception' in content,
                "comprehensive": False
            }
            
            # Determine if test is comprehensive
            analysis["comprehensive"] = (
                analysis["test_functions"] >= 5 and
                analysis["has_mock"] and
                analysis["has_error_handling"] and
                analysis["line_count"] >= 100
            )
            
            return analysis
            
        except Exception as e:
            return {"error": str(e), "comprehensive": False}
    
    def audit_coverage(self) -> Dict:
        """Perform comprehensive test coverage audit."""
        print("🔍 Starting comprehensive test coverage audit...")
        
        # Find all files
        utility_files = self.find_utility_files()
        test_files = self.find_test_files()
        
        print(f"📁 Found {len(utility_files)} utility files")
        print(f"🧪 Found {len(test_files)} test files")
        
        self.coverage_report["total_utilities"] = len(utility_files)
        self.coverage_report["total_test_files"] = len(test_files)
        
        # Analyze each utility file
        for utility_file in utility_files:
            relative_path = str(utility_file.relative_to(self.project_root))
            module_name = self.extract_module_name(utility_file)
            
            # Find corresponding tests
            matching_tests = self.find_tests_for_utility(utility_file, test_files)
            
            if matching_tests:
                # Analyze test quality
                test_analyses = []
                for test_file in matching_tests:
                    analysis = self.analyze_test_quality(test_file)
                    analysis["test_file"] = str(test_file.relative_to(self.project_root))
                    test_analyses.append(analysis)
                
                self.coverage_report["files_with_tests"][relative_path] = {
                    "module_name": module_name,
                    "test_files": [str(t.relative_to(self.project_root)) for t in matching_tests],
                    "test_count": len(matching_tests),
                    "test_analyses": test_analyses,
                    "comprehensive": any(analysis.get("comprehensive", False) for analysis in test_analyses)
                }
            else:
                self.coverage_report["files_without_tests"][relative_path] = {
                    "module_name": module_name,
                    "needs_tests": True
                }
        
        # Generate summary
        files_with_tests = len(self.coverage_report["files_with_tests"])
        files_without_tests = len(self.coverage_report["files_without_tests"])
        total_files = files_with_tests + files_without_tests
        
        coverage_percentage = (files_with_tests / total_files * 100) if total_files > 0 else 0
        
        self.coverage_report["summary"] = {
            "total_files": total_files,
            "files_with_tests": files_with_tests,
            "files_without_tests": files_without_tests,
            "coverage_percentage": round(coverage_percentage, 2),
            "comprehensive_tests": sum(1 for info in self.coverage_report["files_with_tests"].values() if info.get("comprehensive", False))
        }
        
        return self.coverage_report
    
    def check_utilities_overview_accuracy(self) -> Dict:
        """Check the accuracy of utilities-overview.md against actual test files."""
        overview_path = self.unit_tests_dir / "utilities-overview.md"
        
        if not overview_path.exists():
            return {"error": "utilities-overview.md not found"}
        
        with open(overview_path, 'r', encoding='utf-8') as f:
            overview_content = f.read()
        
        # Find all "No Tests" claims
        no_test_pattern = r'- \*\*\[`([^`]+)`\].*\*\* - ❌ \*\*No Tests\*\*'
        no_test_matches = re.findall(no_test_pattern, overview_content)
        
        misreported = {}
        
        for filename in no_test_matches:
            # Check if tests actually exist for this file
            module_name = Path(filename).stem
            
            # Search for test files
            test_search_patterns = [
                f"test_{module_name}*.py",
                f"test*{module_name}*.py"
            ]
            
            found_tests = []
            for pattern in test_search_patterns:
                found_tests.extend(list(self.unit_tests_dir.glob(pattern)))
                found_tests.extend(list(self.tests_dir.glob(f"**/{pattern}")))
            
            if found_tests:
                misreported[filename] = {
                    "claimed": "No Tests",
                    "actual_tests": [str(t.relative_to(self.project_root)) for t in found_tests],
                    "status": "MISREPORTED - Tests exist!"
                }
        
        self.coverage_report["misreported_files"] = misreported
        return misreported
    
    def generate_corrected_overview_section(self) -> str:
        """Generate corrected sections for utilities-overview.md."""
        
        # Check specific files mentioned in the original overview
        files_to_check = [
            "network_base.py",
            "performance_analyzer.py", 
            "security_validator.py",
            "metrics_service.py",
            "extract_text.py",
            "enhanced_editor.py"
        ]
        
        corrected_sections = []
        
        for filename in files_to_check:
            module_name = Path(filename).stem
            
            # Find test files
            test_files = []
            search_patterns = [
                f"test_{module_name}*.py",
                f"test*{module_name}*.py"
            ]
            
            for pattern in search_patterns:
                test_files.extend(list(self.unit_tests_dir.glob(pattern)))
                test_files.extend(list(self.tests_dir.glob(f"**/{pattern}")))
            
            if test_files:
                # Analyze the most recent test file
                latest_test = max(test_files, key=lambda x: x.stat().st_mtime)
                analysis = self.analyze_test_quality(latest_test)
                
                status = "✅ **Comprehensive Testing Available**" if analysis.get("comprehensive", False) else "✅ **Testing Available**"
                
                corrected_sections.append(f"""
#### [`{filename}`](../../src/utilities/network/network_connectivity_complex/core/{filename})

**Status:** {status}  
**Test Files:** {', '.join([f'[`{t.name}`]({t.relative_to(self.project_root)})' for t in test_files])}  
**Test Functions:** {analysis.get('test_functions', 0)}  
**Test Classes:** {analysis.get('test_classes', 0)}  
**Comprehensive Coverage:** {'Yes' if analysis.get('comprehensive', False) else 'Partial'}  
**Last Updated:** {datetime.fromtimestamp(latest_test.stat().st_mtime).strftime('%B %d, %Y')}
""")
            else:
                corrected_sections.append(f"""
#### [`{filename}`](../../src/utilities/network/network_connectivity_complex/core/{filename})

**Status:** ❌ **No Tests Created** - VERIFIED  
**Priority:** HIGH - Tests needed  
**Recommendation:** Create comprehensive test suite including unit tests, integration tests, and edge cases
""")
        
        return "\n".join(corrected_sections)
    
    def save_report(self, output_path: str = None) -> str:
        """Save the audit report to a file."""
        if output_path is None:
            output_path = self.unit_tests_dir / f"test_coverage_audit_report_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.coverage_report, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        summary = self.coverage_report["summary"]
        misreported = self.coverage_report["misreported_files"]
        
        report = f"""
# Test Coverage Audit Report
**Generated:** {self.coverage_report['audit_date']}

## Summary Statistics
- **Total Utility Files:** {summary['total_files']}
- **Files with Tests:** {summary['files_with_tests']}
- **Files without Tests:** {summary['files_without_tests']}
- **Overall Coverage:** {summary['coverage_percentage']}%
- **Comprehensive Tests:** {summary['comprehensive_tests']}

## Misreported Files (utilities-overview.md inaccuracies)
"""
        
        if misreported:
            report += f"**Found {len(misreported)} misreported files:**\n\n"
            for filename, info in misreported.items():
                report += f"- **{filename}:** {info['status']}\n"
                report += f"  - Tests found: {', '.join(info['actual_tests'])}\n\n"
        else:
            report += "No misreported files found - utilities-overview.md is accurate!\n\n"
        
        # Files that actually need tests
        actual_missing = [f for f, info in self.coverage_report["files_without_tests"].items() 
                         if info.get("needs_tests", True)]
        
        if actual_missing:
            report += f"\n## Files Actually Missing Tests ({len(actual_missing)} files)\n"
            for filename in actual_missing[:10]:  # Show first 10
                report += f"- {filename}\n"
            if len(actual_missing) > 10:
                report += f"... and {len(actual_missing) - 10} more files\n"
        
        return report


def main():
    """Main audit execution."""
    print("🚀 Starting Test Coverage Audit for RFU Project")
    
    # Initialize auditor
    project_root = Path(__file__).parent.parent.parent
    auditor = TestCoverageAuditor(str(project_root))
    
    # Perform audit
    print("\n📊 Performing comprehensive coverage analysis...")
    coverage_report = auditor.audit_coverage()
    
    # Check utilities-overview.md accuracy
    print("\n📋 Checking utilities-overview.md accuracy...")
    misreported = auditor.check_utilities_overview_accuracy()
    
    # Generate reports
    print("\n📄 Generating reports...")
    report_path = auditor.save_report()
    summary = auditor.generate_summary_report()
    corrected_sections = auditor.generate_corrected_overview_section()
    
    # Print summary
    print("\n" + "="*60)
    print(summary)
    print("="*60)
    
    if misreported:
        print(f"\n⚠️  FOUND {len(misreported)} MISREPORTED FILES!")
        print("The utilities-overview.md file needs to be updated.")
        print("\nMisreported files:")
        for filename, info in misreported.items():
            print(f"  - {filename}: {info['status']}")
    
    print(f"\n📁 Full report saved to: {report_path}")
    print(f"🔍 Total utility files analyzed: {coverage_report['total_utilities']}")
    print(f"🧪 Total test files found: {coverage_report['total_test_files']}")
    print(f"✅ Coverage percentage: {coverage_report['summary']['coverage_percentage']}%")
    
    # Save corrected sections
    corrected_path = auditor.unit_tests_dir / "corrected_overview_sections_2025-08-31.md"
    with open(corrected_path, 'w', encoding='utf-8') as f:
        f.write("# Corrected Utilities Overview Sections\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(corrected_sections)
    
    print(f"📝 Corrected sections saved to: {corrected_path}")
    
    return coverage_report


if __name__ == "__main__":
    main()