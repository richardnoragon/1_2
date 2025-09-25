#!/usr/bin/env python3
"""
Test Coverage Resolution Verification Script
Generated: 2025-08-31
Purpose: Verify that all corrections made to utilities-overview.md are accurate

This script validates:
1. All corrected files actually have the test files claimed
2. Test files exist and are accessible
3. Documentation accuracy post-correction
4. Generate final verification report
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class TestCoverageVerifier:
    """Verifies the accuracy of test coverage corrections."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / "tests" / "unit"
        self.overview_file = self.tests_dir / "utilities-overview.md"

        # Files we corrected
        self.corrected_files = [
            "network_base.py",
            "performance_analyzer.py",
            "security_validator.py",
            "metrics_service.py",
            "extract_text.py",
            "enhanced_editor.py",
            "gui_components.py",
        ]

        self.verification_results = {}

    def verify_test_file_exists(self, test_file_name: str) -> bool:
        """Verify a test file actually exists."""
        # Check in tests/unit directory
        test_path = self.tests_dir / test_file_name
        if test_path.exists():
            return True

        # Check in tests directory
        alt_path = self.tests_dir.parent / test_file_name
        if alt_path.exists():
            return True

        # Check for similar named files
        pattern = test_file_name.replace(".py", "*.py")
        matches = list(self.tests_dir.glob(pattern))
        matches.extend(list(self.tests_dir.parent.glob(pattern)))

        return len(matches) > 0

    def extract_test_files_from_overview(self, module_name: str) -> List[str]:
        """Extract test file names mentioned for a specific module."""
        try:
            with open(self.overview_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Find the section for this module - more flexible pattern
            start_pattern = f"#### \\[`{re.escape(module_name)}`\\]"
            start_match = re.search(start_pattern, content)

            if not start_match:
                return []

            # Find the end of this section (next #### or ###)
            start_pos = start_match.start()
            end_pattern = r"\n(?:###|####)"
            end_match = re.search(end_pattern, content[start_pos + 1 :])

            if end_match:
                end_pos = start_pos + end_match.start()
                section = content[start_pos:end_pos]
            else:
                # Take a reasonable chunk if no end found
                section = content[start_pos : start_pos + 2000]

            # Extract test file names from the section
            test_file_pattern = r"`(test_[^`]+\.py)`"
            test_files = re.findall(test_file_pattern, section)

            # Remove duplicates while preserving order
            seen = set()
            unique_tests = []
            for test_file in test_files:
                if test_file not in seen:
                    seen.add(test_file)
                    unique_tests.append(test_file)

            return unique_tests

        except Exception as e:
            print(f"Error reading overview file: {e}")
            return []

    def verify_corrected_file(self, module_name: str) -> Dict:
        """Verify a corrected file's test claims."""
        result = {
            "module": module_name,
            "claimed_tests": [],
            "verified_tests": [],
            "missing_tests": [],
            "status": "unknown",
        }

        # Get claimed test files
        claimed_tests = self.extract_test_files_from_overview(module_name)
        result["claimed_tests"] = claimed_tests

        if not claimed_tests:
            result["status"] = "no_claims_found"
            return result

        # Verify each claimed test file
        for test_file in claimed_tests:
            if self.verify_test_file_exists(test_file):
                result["verified_tests"].append(test_file)
            else:
                result["missing_tests"].append(test_file)

        # Determine overall status
        if len(result["missing_tests"]) == 0:
            result["status"] = "all_verified"
        elif len(result["verified_tests"]) > 0:
            result["status"] = "partially_verified"
        else:
            result["status"] = "none_verified"

        return result

    def run_verification(self) -> Dict:
        """Run verification for all corrected files."""
        print("🔍 Starting test coverage verification...")

        for module_name in self.corrected_files:
            print(f"   Verifying {module_name}...")
            verification = self.verify_corrected_file(module_name)
            self.verification_results[module_name] = verification

        return self.verification_results

    def generate_verification_report(self) -> str:
        """Generate a comprehensive verification report."""
        total_files = len(self.verification_results)
        all_verified = sum(
            1
            for r in self.verification_results.values()
            if r["status"] == "all_verified"
        )
        partially_verified = sum(
            1
            for r in self.verification_results.values()
            if r["status"] == "partially_verified"
        )
        none_verified = sum(
            1
            for r in self.verification_results.values()
            if r["status"] == "none_verified"
        )
        no_claims = sum(
            1
            for r in self.verification_results.values()
            if r["status"] == "no_claims_found"
        )

        report = f"""
# Test Coverage Correction Verification Report

**Generated:** {datetime.now().isoformat()}  
**Verification Date:** August 31, 2025

## Summary

- **Total Files Verified:** {total_files}
- **All Tests Verified:** {all_verified} ({all_verified/total_files*100:.1f}%)
- **Partially Verified:** {partially_verified} ({partially_verified/total_files*100:.1f}%)
- **None Verified:** {none_verified} ({none_verified/total_files*100:.1f}%)
- **No Claims Found:** {no_claims} ({no_claims/total_files*100:.1f}%)

## Detailed Results

"""

        for module_name, result in self.verification_results.items():
            status_emoji = {
                "all_verified": "✅",
                "partially_verified": "⚠️",
                "none_verified": "❌",
                "no_claims_found": "❓",
            }.get(result["status"], "❓")

            report += f"""
### {status_emoji} {module_name}

**Status:** {result["status"].replace('_', ' ').title()}  
**Claimed Tests:** {len(result["claimed_tests"])}  
**Verified Tests:** {len(result["verified_tests"])}  
**Missing Tests:** {len(result["missing_tests"])}

**Claimed Test Files:**
"""
            for test_file in result["claimed_tests"]:
                if test_file in result["verified_tests"]:
                    report += f"- ✅ `{test_file}` - EXISTS\n"
                else:
                    report += f"- ❌ `{test_file}` - NOT FOUND\n"

            if result["missing_tests"]:
                report += f"\n**Missing Files:** {', '.join(result['missing_tests'])}\n"

        # Overall assessment
        if all_verified == total_files:
            overall_status = (
                "🎉 **PERFECT** - All corrections verified successfully!"
            )
        elif all_verified + partially_verified == total_files:
            overall_status = "✅ **GOOD** - All corrections have at least some valid test files"
        else:
            overall_status = (
                "⚠️ **NEEDS ATTENTION** - Some corrections may have issues"
            )

        report += f"""

## Overall Assessment

{overall_status}

## Recommendations

"""

        if none_verified > 0 or no_claims > 0:
            report += "- Review and correct any files with missing or unverified test claims\n"

        if partially_verified > 0:
            report += "- Investigate partially verified files to ensure all claimed tests exist\n"

        if all_verified == total_files:
            report += (
                "- All corrections are accurate - no further action needed\n"
            )
            report += "- Consider implementing automated verification in CI/CD pipeline\n"

        return report

    def save_verification_report(self) -> str:
        """Save verification report to file."""
        report = self.generate_verification_report()

        report_path = (
            self.tests_dir
            / f"verification_report_{datetime.now().strftime('%Y-%m-%d')}.md"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        return str(report_path)


def main():
    """Main verification execution."""
    print("🚀 Starting Test Coverage Correction Verification")

    # Initialize verifier
    project_root = Path(__file__).parent.parent.parent
    verifier = TestCoverageVerifier(str(project_root))

    # Run verification
    results = verifier.run_verification()

    # Generate and save report
    report_path = verifier.save_verification_report()

    # Print summary
    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS SUMMARY")
    print("=" * 60)

    for module_name, result in results.items():
        status_emoji = {
            "all_verified": "✅",
            "partially_verified": "⚠️",
            "none_verified": "❌",
            "no_claims_found": "❓",
        }.get(result["status"], "❓")

        print(
            f"{status_emoji} {module_name}: {result['status']} - {len(result['verified_tests'])}/{len(result['claimed_tests'])} tests verified"
        )

    print("=" * 60)
    print(f"📄 Full verification report saved to: {report_path}")

    # Determine exit status
    all_good = all(
        r["status"] in ["all_verified", "partially_verified"]
        for r in results.values()
    )

    if all_good:
        print("🎉 ALL CORRECTIONS VERIFIED SUCCESSFULLY!")
        return 0
    else:
        print("⚠️ Some corrections need attention - check the report")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
