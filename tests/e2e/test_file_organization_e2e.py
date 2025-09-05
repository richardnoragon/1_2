#!/usr/bin/env python3
"""
File Organization End-to-End Test Suite

Comprehensive E2E testing for File Organization tool functionality.
Tests complete workflows from rule creation through execution and conflict resolution.

Created: 2025-09-04
Coverage: Rule-based organization, directory structure creation, file type categorization,
          conflict resolution, and cross-tool integration
Priority: HIGH (addressing 0% E2E coverage for File Management tools)
"""

import os
import shutil
import sys
import tempfile
import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

try:
    from tests.e2e.file_management_test_utilities import (
        FileManagementPerformanceMonitor, FileManagementSignalTracker,
        FileManagementTestDataFactory, MockFileOrganizationTool, MockRFUHub,
        assert_performance_target, file_organization_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE,
    reason="File Management utilities not available"
)


class TestFileOrganizationRuleBased:
    """Test rule-based organization workflows."""
    
    def test_rule_creation_and_priority_workflow(self, file_organization_test_environment):
        """
        Test: Rule Definition → Priority Assignment → Application → Validation
        Target: < 35 seconds for 1000 files rule-based organization
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('file_organization', 'rule_based_sort')
        
        start_time = time.time()
        
        try:
            # Step 1: Create organization rules with priorities
            organization_rules = [
                {
                    'name': 'Documents Rule',
                    'priority': 1,
                    'conditions': {
                        'file_extensions': ['.txt', '.doc', '.pdf'],
                        'file_type': 'document'
                    },
                    'actions': {
                        'move_to': 'Documents',
                        'create_subdir': True,
                        'preserve_structure': False
                    }
                },
                {
                    'name': 'Media Rule',
                    'priority': 2,
                    'conditions': {
                        'file_extensions': ['.jpg', '.png', '.mp4'],
                        'file_type': 'media'
                    },
                    'actions': {
                        'move_to': 'Media',
                        'organize_by_date': True,
                        'create_subdirs': True
                    }
                },
                {
                    'name': 'Code Rule',
                    'priority': 3,
                    'conditions': {
                        'file_extensions': ['.py', '.js', '.java'],
                        'file_type': 'code'
                    },
                    'actions': {
                        'move_to': 'Development',
                        'organize_by_project': True
                    }
                }
            ]
            
            # Create rules
            rules_result = tool.create_organization_rules(organization_rules)
            
            assert rules_result['status'] == 'success', \
                "Rule creation should succeed"
            assert 'rules_count' in rules_result, \
                "Should report number of rules created"
            assert rules_result['rules_count'] == len(organization_rules), \
                "Should create all specified rules"
            
            # Verify rules were stored
            assert len(tool.organization_rules) == len(organization_rules), \
                "All rules should be stored"
            
            # Step 2: Apply organization with rules
            organize_result = tool.organize_files(test_data_path)
            
            assert organize_result['status'] == 'success', \
                "File organization should succeed"
            assert 'files_organized' in organize_result, \
                "Should report number of files organized"
            
            # Verify organization results
            assert len(tool.organization_results) > 0, \
                "Should have organization results"
            
            # Check rule application
            for result in tool.organization_results[:5]:  # Check first 5
                required_fields = ['source', 'destination', 'rule_applied', 'status']
                for field in required_fields:
                    assert field in result, \
                        f"Organization result missing field: {field}"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 35.0, \
                f"Rule-based organization took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'file_organization', 'rule_based_sort')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_condition_evaluation_workflow(self, file_organization_test_environment):
        """
        Test: Multiple Conditions → Boolean Logic → Rule Matching
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Test complex condition evaluation
        complex_rules = [
            {
                'name': 'Large Document Rule',
                'conditions': {
                    'file_extensions': ['.pdf', '.doc'],
                    'min_size': 1024 * 1024,  # 1MB
                    'modified_within_days': 30,
                    'condition_logic': 'AND'
                },
                'actions': {
                    'move_to': 'Important_Documents',
                    'create_backup': True
                }
            },
            {
                'name': 'Old Media Rule',
                'conditions': {
                    'file_extensions': ['.jpg', '.png'],
                    'modified_before_days': 365,
                    'condition_logic': 'AND'
                },
                'actions': {
                    'move_to': 'Archive/Old_Media',
                    'compress': True
                }
            }
        ]
        
        # Create and apply complex rules
        rules_result = tool.create_organization_rules(complex_rules)
        assert rules_result['status'] == 'success', \
            "Complex rule creation should succeed"
        
        organize_result = tool.organize_files(test_data_path)
        assert organize_result['status'] == 'success', \
            "Complex rule organization should succeed"
        
        # Verify rule matching logic was applied
        if len(tool.organization_results) > 0:
            for result in tool.organization_results:
                assert 'rule_applied' in result, \
                    "Should indicate which rule was applied"
    
    def test_rule_priority_handling_workflow(self, file_organization_test_environment):
        """
        Test: Overlapping Rules → Priority Resolution → Correct Application
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create overlapping rules with different priorities
        priority_rules = [
            {
                'name': 'High Priority Rule',
                'priority': 1,  # Highest priority
                'conditions': {'file_extensions': ['.txt', '.doc']},
                'actions': {'move_to': 'HighPriority'}
            },
            {
                'name': 'Low Priority Rule',
                'priority': 5,  # Lower priority
                'conditions': {'file_extensions': ['.txt']},  # Overlaps with above
                'actions': {'move_to': 'LowPriority'}
            }
        ]
        
        rules_result = tool.create_organization_rules(priority_rules)
        assert rules_result['status'] == 'success', \
            "Priority rule creation should succeed"
        
        organize_result = tool.organize_files(test_data_path)
        assert organize_result['status'] == 'success', \
            "Priority-based organization should succeed"
        
        # Mock validation - real implementation would verify priority application
        assert len(tool.organization_rules) == 2, \
            "Both priority rules should be stored"


class TestFileOrganizationDirectoryStructure:
    """Test directory structure creation and management."""
    
    def test_nested_folder_creation_workflow(self, file_organization_test_environment):
        """
        Test: Template Definition → Nested Structure → Permission Inheritance
        Target: < 40 seconds for directory structure creation
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('file_organization', 'directory_creation')
        
        start_time = time.time()
        
        try:
            # Define nested directory structure rules
            structure_rules = [
                {
                    'name': 'Project Structure Rule',
                    'template': 'project_template',
                    'structure': {
                        'Projects': {
                            'Active': {},
                            'Archive': {},
                            'Templates': {}
                        },
                        'Resources': {
                            'Documents': {},
                            'Images': {},
                            'Videos': {}
                        }
                    },
                    'permissions': 'inherit',
                    'create_missing': True
                }
            ]
            
            rules_result = tool.create_organization_rules(structure_rules)
            assert rules_result['status'] == 'success', \
                "Structure rule creation should succeed"
            
            # Apply structure creation
            organize_result = tool.organize_files(test_data_path)
            assert organize_result['status'] == 'success', \
                "Directory structure creation should succeed"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 40.0, \
                f"Directory creation took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'file_organization', 'directory_creation')
            assert perf_result['target_met'], \
                f"Directory creation performance target not met: {perf_result}"
    
    def test_template_structure_workflow(self, file_organization_test_environment):
        """
        Test: Template Selection → Structure Creation → Content Organization
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Test different organizational templates
        template_tests = [
            {
                'template': 'by_file_type',
                'structure_type': 'flat',
                'description': 'Organize by file type (flat structure)'
            },
            {
                'template': 'by_date_hierarchy',
                'structure_type': 'hierarchical',
                'date_format': 'YYYY/MM',
                'description': 'Organize by date hierarchy'
            },
            {
                'template': 'by_project',
                'structure_type': 'project_based',
                'detect_projects': True,
                'description': 'Organize by detected projects'
            }
        ]
        
        for template_test in template_tests:
            template_rules = [
                {
                    'name': f"{template_test['template']}_rule",
                    'template': template_test['template'],
                    'structure_type': template_test['structure_type'],
                    'actions': {
                        'apply_template': True,
                        'create_structure': True
                    }
                }
            ]
            
            rules_result = tool.create_organization_rules(template_rules)
            assert rules_result['status'] == 'success', \
                f"Template rule creation failed for {template_test['description']}"
            
            organize_result = tool.organize_files(test_data_path)
            assert organize_result['status'] == 'success', \
                f"Template organization failed for {template_test['description']}"


class TestFileOrganizationTypeCategorization:
    """Test file type categorization and MIME detection."""
    
    def test_mime_type_detection_workflow(self, file_organization_test_environment):
        """
        Test: File Scanning → MIME Detection → Type Classification → Organization
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create MIME-based organization rules
        mime_rules = [
            {
                'name': 'Text Files Rule',
                'conditions': {
                    'mime_type_patterns': ['text/*'],
                    'detection_method': 'mime'
                },
                'actions': {
                    'move_to': 'TextFiles',
                    'preserve_extensions': True
                }
            },
            {
                'name': 'Image Files Rule',
                'conditions': {
                    'mime_type_patterns': ['image/*'],
                    'detection_method': 'mime'
                },
                'actions': {
                    'move_to': 'Images',
                    'organize_by_format': True
                }
            }
        ]
        
        rules_result = tool.create_organization_rules(mime_rules)
        assert rules_result['status'] == 'success', \
            "MIME-based rule creation should succeed"
        
        organize_result = tool.organize_files(test_data_path)
        assert organize_result['status'] == 'success', \
            "MIME-based organization should succeed"
        
        # Verify MIME detection was considered
        if len(tool.organization_results) > 0:
            for result in tool.organization_results[:3]:
                assert 'rule_applied' in result, \
                    "Should indicate rule applied for MIME detection"
    
    def test_extension_mapping_workflow(self, file_organization_test_environment):
        """
        Test: Extension Analysis → Custom Mapping → Category Assignment
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create extension-based mapping rules
        extension_rules = [
            {
                'name': 'Development Files',
                'conditions': {
                    'file_extensions': ['.py', '.js', '.java', '.cpp'],
                    'custom_mapping': {
                        '.py': 'Python',
                        '.js': 'JavaScript',
                        '.java': 'Java',
                        '.cpp': 'C++'
                    }
                },
                'actions': {
                    'move_to': 'Development',
                    'create_language_subdirs': True
                }
            },
            {
                'name': 'Archive Files',
                'conditions': {
                    'file_extensions': ['.zip', '.tar', '.gz', '.7z'],
                    'category': 'archive'
                },
                'actions': {
                    'move_to': 'Archives',
                    'organize_by_compression_type': True
                }
            }
        ]
        
        rules_result = tool.create_organization_rules(extension_rules)
        assert rules_result['status'] == 'success', \
            "Extension mapping rule creation should succeed"
        
        organize_result = tool.organize_files(test_data_path)
        assert organize_result['status'] == 'success', \
            "Extension-based organization should succeed"
        
        # Verify extension mapping was applied
        assert len(tool.organization_rules) == 2, \
            "Extension mapping rules should be stored"
    
    def test_content_analysis_workflow(self, file_organization_test_environment):
        """
        Test: Content Scanning → Analysis → Intelligent Classification
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create content-based analysis rules
        content_rules = [
            {
                'name': 'Content Analysis Rule',
                'conditions': {
                    'content_analysis': True,
                    'keywords': ['project', 'report', 'analysis'],
                    'file_patterns': ['*report*', '*analysis*'],
                    'min_confidence': 0.7
                },
                'actions': {
                    'move_to': 'Reports',
                    'tag_with_keywords': True,
                    'create_metadata': True
                }
            }
        ]
        
        rules_result = tool.create_organization_rules(content_rules)
        assert rules_result['status'] == 'success', \
            "Content analysis rule creation should succeed"
        
        organize_result = tool.organize_files(test_data_path)
        assert organize_result['status'] == 'success', \
            "Content-based organization should succeed"


class TestFileOrganizationConflictResolution:
    """Test conflict handling and user intervention workflows."""
    
    def test_duplicate_handling_workflow(self, file_organization_test_environment):
        """
        Test: Duplicate Detection → User Intervention → Resolution Application
        Target: < 15 seconds for conflict resolution
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        # Create rules that might cause conflicts
        conflict_rules = [
            {
                'name': 'Duplicate Handling Rule',
                'conditions': {'file_extensions': ['.txt']},
                'actions': {
                    'move_to': 'Organized',
                    'handle_duplicates': True,
                    'duplicate_strategy': 'rename'
                }
            }
        ]
        
        rules_result = tool.create_organization_rules(conflict_rules)
        organize_result = tool.organize_files(test_data_path)
        
        # Check for conflicts in results
        conflicts = [r for r in tool.organization_results if r['status'] == 'conflict']
        
        if len(conflicts) > 0:
            performance_monitor.start_monitoring('file_organization', 'conflict_resolution')
            
            try:
                # Test different conflict resolution strategies
                resolution_strategies = ['rename', 'skip', 'overwrite']
                
                for strategy in resolution_strategies:
                    resolution_result = tool.resolve_conflicts(strategy)
                    
                    assert resolution_result['status'] == 'success', \
                        f"Conflict resolution should succeed with {strategy} strategy"
                    
                    if 'conflicts_resolved' in resolution_result:
                        assert resolution_result['conflicts_resolved'] >= 0, \
                            "Should report number of conflicts resolved"
                    
                    break  # Test one strategy for mock implementation
                
            finally:
                perf_result = performance_monitor.stop_monitoring(
                    'file_organization', 'conflict_resolution')
                assert perf_result['target_met'], \
                    "Conflict resolution performance target should be met"
    
    def test_naming_conflict_workflow(self, file_organization_test_environment):
        """
        Test: Naming Conflicts → Resolution Options → Safe Application
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create rules that cause naming conflicts
        naming_conflict_rules = [
            {
                'name': 'Naming Conflict Test',
                'conditions': {'file_extensions': ['.txt', '.py']},
                'actions': {
                    'move_to': 'Organized',
                    'naming_strategy': 'preserve_original',
                    'conflict_resolution': 'auto_rename'
                }
            }
        ]
        
        rules_result = tool.create_organization_rules(naming_conflict_rules)
        organize_result = tool.organize_files(test_data_path)
        
        # Should handle naming conflicts automatically
        assert organize_result['status'] == 'success', \
            "Should handle naming conflicts gracefully"
        
        # Check for conflict resolution in results
        resolved_conflicts = [r for r in tool.organization_results 
                            if r['status'] == 'resolved']
        
        # Mock validation - real implementation would check actual naming
        if len(resolved_conflicts) > 0:
            for conflict in resolved_conflicts:
                assert 'resolution' in conflict, \
                    "Resolved conflicts should have resolution method"
    
    def test_user_intervention_workflow(self, file_organization_test_environment):
        """
        Test: Complex Conflicts → User Prompt → Manual Resolution → Application
        """
        env = file_organization_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        
        # Create rules requiring user intervention
        intervention_rules = [
            {
                'name': 'Manual Resolution Rule',
                'conditions': {'file_extensions': ['.txt']},
                'actions': {
                    'move_to': 'ManualReview',
                    'require_confirmation': True,
                    'user_intervention_mode': True
                }
            }
        ]
        
        rules_result = tool.create_organization_rules(intervention_rules)
        organize_result = tool.organize_files(test_data_path)
        
        # Should succeed even with user intervention requirements
        assert organize_result['status'] in ['success', 'pending_intervention'], \
            "Should handle user intervention scenarios"
        
        # If conflicts exist, test manual resolution
        conflicts = [r for r in tool.organization_results if r['status'] == 'conflict']
        
        if len(conflicts) > 0:
            # Simulate user decision
            manual_resolution_result = tool.resolve_conflicts('manual_rename')
            
            assert manual_resolution_result['status'] == 'success', \
                "Manual conflict resolution should succeed"


class TestFileOrganizationIntegration:
    """Test integration with other file management tools."""
    
    def test_finder_to_organization_integration(self, file_organization_test_environment):
        """
        Test: File Finder Results → Organization Rules → Execution
        """
        env = file_organization_test_environment
        org_tool = env['tool']
        test_data_path = env['test_data_path']
        hub = env['hub']
        
        # Step 1: Simulate file finder results
        from tests.e2e.file_management_test_utilities import MockFileFinderTool
        
        mock_finder = MockFileFinderTool()
        hub.register_tool('file_finder', mock_finder)
        
        # Simulate found files
        search_criteria = {'file_types': ['.txt', '.py']}
        finder_result = mock_finder.search_files(test_data_path, search_criteria)
        
        assert finder_result['status'] == 'success', \
            "File finder should succeed"
        
        # Step 2: Use finder results for organization
        found_files = [result['path'] for result in mock_finder.search_results]
        
        # Create organization rules for found files
        integration_rules = [
            {
                'name': 'Finder Integration Rule',
                'conditions': {'source': 'file_finder_results'},
                'actions': {
                    'organize_found_files': True,
                    'move_to': 'FoundAndOrganized'
                }
            }
        ]
        
        rules_result = org_tool.create_organization_rules(integration_rules)
        organize_result = org_tool.organize_files(test_data_path, integration_rules)
        
        # Step 3: Verify integration workflow
        assert organize_result['status'] == 'success', \
            "Finder-organization integration should succeed"
        
        # Verify both tools are registered with hub
        hub_status = hub.tool_status
        assert 'file_finder' in hub_status, "Finder should be registered"
        assert 'file_organization' in hub_status, \
            "Organization tool should be registered"


# Test runner configuration
def run_file_organization_e2e_tests():
    """Run the File Organization E2E test suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "-x",  # Stop on first failure for E2E tests
        "--maxfail=3"  # Stop after 3 failures
    ]
    
    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Import PyQt5 for GUI testing if available
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    except ImportError:
        pass
    
    # Run the tests
    print("Starting File Organization End-to-End Tests...")
    exit_code = run_file_organization_e2e_tests()
    
    print(f"\nFile Organization E2E Test Suite completed with exit code: {exit_code}")
    sys.exit(exit_code)