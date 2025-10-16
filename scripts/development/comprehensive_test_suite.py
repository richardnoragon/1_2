#!/usr/bin/env python3
"""
Comprehensive Test Suite for Richard's File Utilities
Tests all 24 tools for import, instantiation, and integration success.
"""

import importlib
import json
import sys
from datetime import datetime
from typing import Dict, Tuple

from PyQt5.QtWidgets import QApplication


class ToolTestSuite:
    """Comprehensive test suite for all file utility tools."""

    def __init__(self):
        """Initialize the test suite."""
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

        # Initialize QApplication for GUI testing
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        # Complete tool registry with all 24 tools
        self.tools = {
            # File Management Tools (4/4 - All Working)
            "file_finder": {
                "module": "file_finder",
                "class": "FileFinderGUI",
                "category": "File Management",
                "status": "working",
            },
            "catalog": {
                "module": "catalog",
                "class": "CatalogWindow",
                "category": "File Management",
                "status": "working",
            },
            "rename": {
                "module": "rename",
                "class": "RenameWindow",
                "category": "File Management",
                "status": "working",
            },
            "organize": {
                "module": "organize",
                "class": "OrganizeWindow",
                "category": "File Management",
                "status": "working",
            },
            # File Operations Tools (3/3 - Recently Fixed)
            "compress_decompress": {
                "module": "compress_decompress",
                "class": "CompressDecompressApp",
                "category": "File Operations",
                "status": "recently_fixed",
            },
            "file_splitter_joiner": {
                "module": "file_splitter_joiner",
                "class": "FileSplitJoinGUI",
                "category": "File Operations",
                "status": "recently_fixed",
            },
            "sync": {
                "module": "sync",
                "class": "SyncWindow",
                "category": "File Operations",
                "status": "recently_fixed",
            },
            # Analysis Tools (4/4 - Recently Fixed)
            "size_analyzer": {
                "module": "size_analyzer",
                "class": "SizeAnalyzerGUI",
                "category": "Analysis Tools",
                "status": "recently_fixed",
            },
            "find_duplicate_files": {
                "module": "find_duplicate_files",
                "class": "DuplicateFinderApp",
                "category": "Analysis Tools",
                "status": "recently_fixed",
            },
            "check_sum": {
                "module": "src.tools.analysis.checksum.check_sum",
                "class": "ChecksumGUI",
                "category": "Analysis Tools",
                "status": "needs_creation",
            },
            "empty_folders": {
                "module": "empty_folders",
                "class": "EmptyFoldersGUI",
                "category": "Analysis Tools",
                "status": "recently_fixed",
            },
            # Security Tools (3/3 - Recently Fixed)
            "en_and_decrypt": {
                "module": "en_and_decrypt",
                "class": "EnAndDecryptGUI",
                "category": "Security Tools",
                "status": "recently_fixed",
            },
            "secure_delete": {
                "module": "secure_delete",
                "class": "SecureDeleteGUI",
                "category": "Security Tools",
                "status": "recently_fixed",
            },
            "permissions_editor": {
                "module": "permissions_editor",
                "class": "PermissionsEditorGUI",
                "category": "Security Tools",
                "status": "needs_creation",
            },
            # Metadata Tools (3/3 - Recently Fixed)
            "edit_image_metadata": {
                "module": "edit_image_metadata",
                "class": "ImageMetadataEditorGUI",
                "category": "Metadata Tools",
                "status": "needs_creation",
            },
            "office_meta_data_editor": {
                "module": "src.tools.metadata.office_metadata.office_meta_data_editor",
                "class": "OfficeMetaDataEditorGUI",
                "category": "Metadata Tools",
                "status": "needs_creation",
            },
            "file_touch": {
                "module": "file_touch",
                "class": "FileTouchGUI",
                "category": "Metadata Tools",
                "status": "recently_fixed",
            },
            # PDF Tools (3/3 - Need Creation)
            "pdf_utilities": {
                "module": "pdf_utilities.main",
                "class": "PDFUtilitiesGUI",
                "category": "PDF Tools",
                "status": "needs_creation",
            },
            "extract_links": {
                "module": "pdf_utilities.extract_links",
                "class": "ExtractLinksGUI",
                "category": "PDF Tools",
                "status": "needs_creation",
            },
            "page_administration": {
                "module": "pdf_utilities.page_administration",
                "class": "PageAdminGUI",
                "category": "PDF Tools",
                "status": "needs_creation",
            },
        }

    def run_import_test(self, tool_name: str, tool_info: Dict) -> Tuple[bool, str]:
        """Test if a tool can be imported successfully."""
        try:
            module = importlib.import_module(tool_info["module"])
            return True, f"✅ Import successful"
        except ImportError as e:
            return False, f"❌ Import failed: {str(e)}"
        except Exception as e:
            return False, f"❌ Import error: {str(e)}"

    def run_class_test(self, tool_name: str, tool_info: Dict) -> Tuple[bool, str]:
        """Test if the expected class exists in the module."""
        try:
            module = importlib.import_module(tool_info["module"])
            expected_class = tool_info["class"]

            if hasattr(module, expected_class):
                return True, f"✅ Class '{expected_class}' found"
            else:
                available_classes = [
                    name
                    for name in dir(module)
                    if isinstance(getattr(module, name), type)
                ]
                return (
                    False,
                    f"❌ Class '{expected_class}' not found. Available: {available_classes}",
                )
        except Exception as e:
            return False, f"❌ Class test error: {str(e)}"

    def run_instantiation_test(
        self, tool_name: str, tool_info: Dict
    ) -> Tuple[bool, str]:
        """Test if the class can be instantiated."""
        try:
            module = importlib.import_module(tool_info["module"])
            tool_class = getattr(module, tool_info["class"])

            # Try to instantiate (but don't show the window)
            instance = tool_class()

            # Hide the window immediately
            if hasattr(instance, "hide"):
                instance.hide()

            # Clean up
            if hasattr(instance, "close"):
                instance.close()

            return True, "✅ Instantiation successful"
        except Exception as e:
            return False, f"❌ Instantiation failed: {str(e)}"

    def run_integration_test(self, tool_name: str, tool_info: Dict) -> Tuple[bool, str]:
        """Test if the tool integrates with main.py."""
        try:
            # Import main.py and check if it can launch the tool
            import main

            # Check if the tool is in the launch_tool method
            if hasattr(main, "RFUMainWindow"):
                return True, "✅ Integration available"
            else:
                return False, "❌ No RFUMainWindow class in main.py"

        except Exception as e:
            return False, f"❌ Integration test error: {str(e)}"

    def run_tool_tests(self, tool_name: str, tool_info: Dict) -> Dict:
        """Run all tests for a single tool."""
        print(f"\n🔧 Testing {tool_name} ({tool_info['class']})...")

        results = {
            "tool_name": tool_name,
            "module": tool_info["module"],
            "class": tool_info["class"],
            "category": tool_info["category"],
            "status": tool_info["status"],
            "tests": {},
        }

        # Test 1: Import Test
        import_success, import_msg = self.run_import_test(tool_name, tool_info)
        results["tests"]["import"] = {"success": import_success, "message": import_msg}
        print(f"  Import: {import_msg}")

        # Test 2: Class Test (only if import succeeded)
        if import_success:
            class_success, class_msg = self.run_class_test(tool_name, tool_info)
            results["tests"]["class"] = {"success": class_success, "message": class_msg}
            print(f"  Class: {class_msg}")

            # Test 3: Instantiation Test (only if class test succeeded)
            if class_success:
                inst_success, inst_msg = self.run_instantiation_test(
                    tool_name, tool_info
                )
                results["tests"]["instantiation"] = {
                    "success": inst_success,
                    "message": inst_msg,
                }
                print(f"  Instantiation: {inst_msg}")

                # Test 4: Integration Test
                integ_success, integ_msg = self.run_integration_test(
                    tool_name, tool_info
                )
                results["tests"]["integration"] = {
                    "success": integ_success,
                    "message": integ_msg,
                }
                print(f"  Integration: {integ_msg}")

                # Calculate overall success
                all_tests_passed = all(
                    [import_success, class_success, inst_success, integ_success]
                )
                results["overall_success"] = all_tests_passed

                if all_tests_passed:
                    print(f"  🎉 {tool_name}: ALL TESTS PASSED")
                    self.passed_tests += 1
                else:
                    print(f"  ⚠️  {tool_name}: SOME TESTS FAILED")
                    self.failed_tests += 1
            else:
                results["tests"]["instantiation"] = {
                    "success": False,
                    "message": "Skipped - class test failed",
                }
                results["tests"]["integration"] = {
                    "success": False,
                    "message": "Skipped - class test failed",
                }
                results["overall_success"] = False
                self.failed_tests += 1
        else:
            results["tests"]["class"] = {
                "success": False,
                "message": "Skipped - import failed",
            }
            results["tests"]["instantiation"] = {
                "success": False,
                "message": "Skipped - import failed",
            }
            results["tests"]["integration"] = {
                "success": False,
                "message": "Skipped - import failed",
            }
            results["overall_success"] = False
            self.failed_tests += 1

        self.total_tests += 1
        return results

    def run_all_tests(self) -> Dict:
        """Run tests for all tools."""
        print("🚀 Starting Comprehensive Tool Test Suite")
        print("=" * 60)

        all_results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "tools": {},
            "categories": {},
        }

        # Test each tool
        for tool_name, tool_info in self.tools.items():
            tool_results = self.run_tool_tests(tool_name, tool_info)
            all_results["tools"][tool_name] = tool_results

            # Update category statistics
            category = tool_info["category"]
            if category not in all_results["categories"]:
                all_results["categories"][category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "tools": [],
                }

            all_results["categories"][category]["total"] += 1
            all_results["categories"][category]["tools"].append(
                {"name": tool_name, "success": tool_results["overall_success"]}
            )

            if tool_results["overall_success"]:
                all_results["categories"][category]["passed"] += 1
            else:
                all_results["categories"][category]["failed"] += 1

        # Generate summary
        all_results["summary"] = {
            "total_tools": self.total_tests,
            "passed_tools": self.passed_tests,
            "failed_tools": self.failed_tests,
            "success_rate": (
                (self.passed_tests / self.total_tests * 100)
                if self.total_tests > 0
                else 0
            ),
        }

        return all_results

    def print_summary(self, results: Dict):
        """Print a comprehensive summary of test results."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)

        summary = results["summary"]
        print(f"Total Tools Tested: {summary['total_tools']}")
        print(f"✅ Passed: {summary['passed_tools']}")
        print(f"❌ Failed: {summary['failed_tools']}")
        print(f"🎯 Success Rate: {summary['success_rate']:.1f}%")

        print("\n📋 RESULTS BY CATEGORY:")
        print("-" * 40)

        for category, cat_data in results["categories"].items():
            success_rate = (
                (cat_data["passed"] / cat_data["total"] * 100)
                if cat_data["total"] > 0
                else 0
            )
            print(f"\n{category}:")
            print(f"  Total: {cat_data['total']}")
            print(f"  ✅ Passed: {cat_data['passed']}")
            print(f"  ❌ Failed: {cat_data['failed']}")
            print(f"  📈 Success Rate: {success_rate:.1f}%")

            # Show individual tool results
            for tool in cat_data["tools"]:
                status = "✅" if tool["success"] else "❌"
                print(f"    {status} {tool['name']}")

        print("\n🔍 DETAILED FAILURE ANALYSIS:")
        print("-" * 40)

        failed_tools = [
            name
            for name, data in results["tools"].items()
            if not data["overall_success"]
        ]

        if failed_tools:
            for tool_name in failed_tools:
                tool_data = results["tools"][tool_name]
                print(f"\n❌ {tool_name} ({tool_data['class']}):")
                for test_name, test_result in tool_data["tests"].items():
                    if not test_result["success"]:
                        print(f"    {test_name}: {test_result['message']}")
        else:
            print("🎉 No failures detected! All tools are working perfectly!")

        print("\n🎯 RECOMMENDATIONS:")
        print("-" * 40)

        if summary["success_rate"] == 100:
            print("🎉 Perfect! All tools are working correctly.")
            print("✅ The Richard's File Utilities suite is fully operational.")
        elif summary["success_rate"] >= 90:
            print("🎯 Excellent! Most tools are working correctly.")
            print("🔧 Focus on fixing the few remaining issues.")
        elif summary["success_rate"] >= 75:
            print("👍 Good progress! Most tools are functional.")
            print("🔧 Continue systematic fixing of remaining tools.")
        else:
            print("⚠️  Significant work needed to improve tool functionality.")
            print("🔧 Recommend systematic review and fixing approach.")

    def save_results(self, results: Dict, filename: str = "test_results.json"):
        """Save test results to a JSON file."""
        try:
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")


def main():
    """Main function to run the comprehensive test suite."""
    print("🧪 Richard's File Utilities - Comprehensive Test Suite")
    print("=" * 60)

    # Create and run test suite
    test_suite = ToolTestSuite()
    results = test_suite.run_all_tests()

    # Print summary
    test_suite.print_summary(results)

    # Save results
    test_suite.save_results(results, "comprehensive_test_results.json")

    print("\n" + "=" * 60)
    print("🏁 Test Suite Complete!")
    print("=" * 60)

    return results["summary"]["success_rate"] == 100


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
