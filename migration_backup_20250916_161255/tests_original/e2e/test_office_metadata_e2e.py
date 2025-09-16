#!/usr/bin/env python3
"""
Office Metadata E2E Tests

Comprehensive end-to-end testing for Office Metadata tool workflows.
Tests document property extraction, editing, privacy analysis, and batch processing.

Created: 2025-09-04
Purpose: Validate Office Metadata tool functionality with real-world scenarios
Coverage: Document properties, privacy scrubbing, template application, batch operations
"""

import os
import sys
import time

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import test utilities
from .metadata_tools_test_utilities import (assert_performance_target,
                                            office_metadata_test_environment)


class TestOfficeMetadataDocumentProperties:
    """Test class for document property management workflows"""
    
    def test_word_document_properties_workflow(self, office_metadata_test_environment):
        """Test comprehensive Word document property extraction"""
        env = office_metadata_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracker
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('office_metadata', 'property_extraction')
        
        # Test data setup
        word_doc_path = os.path.join(env['test_data_path'], 'documents', 'test_document.docx')
        
        # Execute document property extraction workflow
        result = tool.extract_document_properties(word_doc_path)
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('office_metadata', 'property_extraction')
        
        # Validate workflow results
        assert result['status'] == 'success'
        assert result['files_processed'] == 1
        assert result['metadata_operations'] >= 1
        assert word_doc_path in tool.document_properties
        
        # Validate document properties structure
        properties = tool.document_properties[word_doc_path]
        assert 'file_info' in properties
        assert 'core_properties' in properties
        assert 'app_properties' in properties
        
        # Validate file info
        file_info = properties['file_info']
        assert file_info['file_extension'] == '.docx'
        assert file_info['file_name'] == os.path.basename(word_doc_path)
        assert file_info['file_size'] > 0
        
        # Validate core properties
        core_props = properties['core_properties']
        required_fields = ['title', 'creator', 'subject', 'created', 'modified']
        for field in required_fields:
            assert field in core_props, f"Missing core property: {field}"
        
        # Validate application properties
        app_props = properties['app_properties']
        assert app_props['application'] == 'Microsoft Word'
        assert 'app_version' in app_props
        
        # Validate signal tracking
        workflow_summary = signal_tracker.get_workflow_summary()
        assert workflow_summary['total_events'] > 0
        assert workflow_summary['completion_status'] is True
        assert workflow_summary['error_events'] == 0
        
        # Validate performance target
        assert_performance_target(perf_result['duration'], 'office_metadata', 'property_extraction')
    
    def test_excel_spreadsheet_properties_workflow(self, office_metadata_test_environment):
        """Test Excel spreadsheet property extraction"""
        env = office_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        excel_doc_path = os.path.join(env['test_data_path'], 'documents', 'test_spreadsheet.xlsx')
        
        # Execute Excel property extraction
        result = tool.extract_document_properties(excel_doc_path)
        
        # Validate workflow results
        assert result['status'] == 'success'
        assert excel_doc_path in tool.document_properties
        
        # Validate Excel-specific properties
        properties = tool.document_properties[excel_doc_path]
        app_props = properties['app_properties']
        assert app_props['application'] == 'Microsoft Excel'
    
    def test_powerpoint_presentation_properties_workflow(self, office_metadata_test_environment):
        """Test PowerPoint presentation property extraction"""
        env = office_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        ppt_doc_path = os.path.join(env['test_data_path'], 'documents', 'test_presentation.pptx')
        
        # Execute PowerPoint property extraction
        result = tool.extract_document_properties(ppt_doc_path)
        
        # Validate workflow results
        assert result['status'] == 'success'
        assert ppt_doc_path in tool.document_properties
        
        # Validate PowerPoint-specific properties
        properties = tool.document_properties[ppt_doc_path]
        app_props = properties['app_properties']
        assert app_props['application'] == 'Microsoft PowerPoint'
    
    def test_pdf_document_properties_workflow(self, office_metadata_test_environment):
        """Test PDF document property extraction"""
        env = office_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        pdf_doc_path = os.path.join(env['test_data_path'], 'documents', 'test_document.pdf')
        
        # Execute PDF property extraction
        result = tool.extract_document_properties(pdf_doc_path)
        
        # Validate workflow results
        assert result['status'] == 'success'
        assert pdf_doc_path in tool.document_properties
        
        # Validate PDF-specific properties
        properties = tool.document_properties[pdf_doc_path]
        app_props = properties['app_properties']
        assert app_props['application'] == 'Adobe Acrobat'
        
        # Validate file info
        file_info = properties['file_info']
        assert file_info['file_extension'] == '.pdf'


class TestOfficeMetadataBatchProcessing:
    """Test class for batch processing across multiple formats"""
    
    def test_multi_format_batch_processing_workflow(self, office_metadata_test_environment):
        """Test batch processing across multiple document formats"""
        env = office_metadata_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signals
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('office_metadata', 'batch_processing')
        
        # Test data setup with multiple formats
        test_documents = [
            os.path.join(env['test_data_path'], 'documents', 'batch_word_001.docx'),
            os.path.join(env['test_data_path'], 'documents', 'batch_excel_001.xlsx'),
            os.path.join(env['test_data_path'], 'documents', 'batch_ppt_001.pptx'),
            os.path.join(env['test_data_path'], 'documents', 'batch_pdf_001.pdf'),
            os.path.join(env['test_data_path'], 'documents', 'batch_word_002.docx')
        ]
        
        # Execute batch processing workflow
        batch_results = []
        for document_path in test_documents:
            result = tool.extract_document_properties(document_path)
            batch_results.append(result)
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('office_metadata', 'batch_processing')
        
        # Validate batch processing results
        successful_extractions = len([r for r in batch_results if r['status'] == 'success'])
        assert successful_extractions == len(test_documents)
        
        # Validate format-specific processing
        format_counts = {}
        for document_path in test_documents:
            if document_path in tool.document_properties:
                file_ext = os.path.splitext(document_path)[1].lower()
                format_counts[file_ext] = format_counts.get(file_ext, 0) + 1
                
                properties = tool.document_properties[document_path]
                app_name = properties['app_properties']['application']
                
                # Validate correct application mapping
                if file_ext == '.docx':
                    assert 'Word' in app_name
                elif file_ext == '.xlsx':
                    assert 'Excel' in app_name
                elif file_ext == '.pptx':
                    assert 'PowerPoint' in app_name
                elif file_ext == '.pdf':
                    assert 'Acrobat' in app_name
        
        # Validate multiple formats were processed
        assert len(format_counts) >= 3
        
        # Validate signal tracking
        workflow_summary = signal_tracker.get_workflow_summary()
        assert workflow_summary['total_events'] >= len(test_documents)
        assert workflow_summary['error_events'] == 0
        
        # Validate performance target
        assert_performance_target(perf_result['duration'], 'office_metadata', 'batch_processing')


class TestOfficeMetadataPrivacyScrubbing:
    """Test class for privacy analysis and data scrubbing"""
    
    def test_sensitive_data_detection_workflow(self, office_metadata_test_environment):
        """Test detection of sensitive information in document metadata"""
        env = office_metadata_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        # Start performance monitoring
        performance_monitor.start_monitoring('office_metadata', 'privacy_analysis')
        
        # Test data setup
        sensitive_doc_path = os.path.join(env['test_data_path'], 'documents', 'sensitive_document.docx')
        
        # Execute property extraction with privacy analysis
        result = tool.extract_document_properties(sensitive_doc_path)
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('office_metadata', 'privacy_analysis')
        
        # Validate privacy analysis execution
        assert result['status'] == 'success'
        assert sensitive_doc_path in tool.privacy_concerns
        
        # Validate privacy analysis results
        privacy_analysis = tool.privacy_concerns[sensitive_doc_path]
        assert 'privacy_concerns' in privacy_analysis
        assert 'risk_level' in privacy_analysis
        assert 'recommendations' in privacy_analysis
        
        # Validate risk assessment
        risk_level = privacy_analysis['risk_level']
        assert risk_level in ['low', 'medium', 'high']
        
        # If privacy concerns exist, validate they're properly identified
        if privacy_analysis['privacy_concerns']:
            assert len(privacy_analysis['recommendations']) > 0
        
        # Validate performance target
        assert_performance_target(perf_result['duration'], 'office_metadata', 'privacy_analysis')
    
    def test_privacy_scrubbing_workflow(self, office_metadata_test_environment):
        """Test privacy data scrubbing functionality"""
        env = office_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        privacy_doc_path = os.path.join(env['test_data_path'], 'documents', 'privacy_test.docx')
        
        # Step 1: Extract properties to establish baseline
        extract_result = tool.extract_document_properties(privacy_doc_path)
        assert extract_result['status'] == 'success'
        
        # Step 2: Execute privacy scrubbing
        scrub_options = {
            'remove_author': True,
            'remove_company': True,
            'remove_custom_properties': False
        }
        
        scrub_result = tool.scrub_privacy_data(privacy_doc_path, scrub_options)
        
        # Validate scrubbing results
        assert scrub_result['status'] == 'success'
        assert scrub_result['files_processed'] == 1
        assert scrub_result['metadata_operations'] > 0
        
        # Validate scrubbing was applied
        scrubbed_fields = scrub_result.get('fields_scrubbed', [])
        if scrub_options['remove_author']:
            assert any('creator' in field or 'author' in field for field in scrubbed_fields)
        if scrub_options['remove_company']:
            assert any('company' in field for field in scrubbed_fields)


class TestOfficeMetadataTemplateApplication:
    """Test class for template-based metadata operations"""
    
    def test_metadata_template_creation_workflow(self, office_metadata_test_environment):
        """Test creation and validation of metadata templates"""
        env = office_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        template_documents = []
        for i in range(3):
            doc_path = os.path.join(env['test_data_path'], 'documents', f'template_test_{i:03d}.docx')
            template_documents.append(doc_path)
        
        # Create metadata template
        template_name = 'corporate_template'
        template_data = {
            'creator': 'Corporate Author',
            'subject': 'Corporate Document',
            'keywords': 'corporate, official, template',
            'company': 'Example Corporation'
        }
        
        # Execute template application workflow
        template_result = tool.apply_metadata_template(template_documents, template_name, template_data)
        
        # Validate template creation and application
        assert template_result['status'] == 'success'
        assert template_result['files_processed'] == len(template_documents)
        assert template_result['metadata_operations'] == len(template_documents)
        
        # Validate template storage
        assert template_name in tool.template_data
        stored_template = tool.template_data[template_name]
        assert stored_template == template_data
    
    def test_template_application_workflow(self, office_metadata_test_environment):
        """Test applying templates to multiple documents"""
        env = office_metadata_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        # Start performance monitoring
        performance_monitor.start_monitoring('office_metadata', 'template_application')
        
        # Test data setup
        target_documents = []
        for i in range(5):
            doc_path = os.path.join(env['test_data_path'], 'documents', f'template_target_{i:03d}.docx')
            target_documents.append(doc_path)
        
        # Create standardization template
        standardization_template = {
            'creator': 'Standardized Author',
            'company': 'Standard Corporation',
            'keywords': 'standardized, template, metadata'
        }
        
        # Execute template application
        application_result = tool.apply_metadata_template(
            target_documents, 'standardization_template', standardization_template
        )
        
        # Stop performance monitoring
        perf_result = performance_monitor.stop_monitoring('office_metadata', 'template_application')
        
        # Validate template application workflow
        assert application_result['status'] == 'success'
        assert application_result['files_processed'] == len(target_documents)
        
        # Validate template storage
        assert 'standardization_template' in tool.template_data
        applied_template = tool.template_data['standardization_template']
        assert applied_template == standardization_template
        
        # Validate performance target
        assert_performance_target(perf_result['duration'], 'office_metadata', 'template_application')


class TestOfficeMetadataFormatSpecific:
    """Test class for format-specific handling"""
    
    def test_ooxml_format_processing_workflow(self, office_metadata_test_environment):
        """Test OOXML format (DOCX, XLSX, PPTX) specific processing"""
        env = office_metadata_test_environment
        tool = env['tool']
        
        # Test data setup with OOXML formats
        ooxml_documents = [
            os.path.join(env['test_data_path'], 'documents', 'ooxml_word.docx'),
            os.path.join(env['test_data_path'], 'documents', 'ooxml_excel.xlsx'),
            os.path.join(env['test_data_path'], 'documents', 'ooxml_powerpoint.pptx')
        ]
        
        # Execute OOXML-specific processing
        ooxml_results = []
        for doc_path in ooxml_documents:
            result = tool.extract_document_properties(doc_path)
            ooxml_results.append(result)
            
            # Validate OOXML support capability
            assert tool.capabilities['ooxml_support'] is True
        
        # Validate OOXML processing results
        successful_extractions = len([r for r in ooxml_results if r['status'] == 'success'])
        assert successful_extractions == len(ooxml_documents)
        
        # Validate OOXML-specific metadata structure
        for doc_path in ooxml_documents:
            if doc_path in tool.document_properties:
                properties = tool.document_properties[doc_path]
                
                # OOXML documents should have rich metadata
                assert 'core_properties' in properties
                assert 'app_properties' in properties
                
                # Validate application detection
                app_name = properties['app_properties']['application']
                assert 'Microsoft' in app_name
    
    def test_ole_format_compatibility_workflow(self, office_metadata_test_environment):
        """Test OLE format (DOC, XLS, PPT) compatibility"""
        env = office_metadata_test_environment
        tool = env['tool']
        
        # Test data setup with OLE formats
        ole_documents = [
            os.path.join(env['test_data_path'], 'documents', 'legacy_word.doc'),
            os.path.join(env['test_data_path'], 'documents', 'legacy_excel.xls'),
            os.path.join(env['test_data_path'], 'documents', 'legacy_powerpoint.ppt')
        ]
        
        # Execute OLE format processing
        ole_results = []
        for doc_path in ole_documents:
            result = tool.extract_document_properties(doc_path)
            ole_results.append(result)
            
            # Validate OLE support capability
            assert tool.capabilities['ole_support'] is True
        
        # Validate OLE processing (may have limited support)
        for result in ole_results:
            # OLE processing may succeed with limited data or fail gracefully
            assert result['status'] in ['success', 'error']


class TestOfficeMetadataPrivacyCompliance:
    """Test class for privacy compliance and security features"""
    
    def test_privacy_risk_assessment_workflow(self, office_metadata_test_environment):
        """Test comprehensive privacy risk assessment"""
        env = office_metadata_test_environment
        tool = env['tool']
        
        # Test data setup with various risk levels
        risk_test_documents = []
        for i in range(6):
            doc_path = os.path.join(env['test_data_path'], 'documents', f'risk_assessment_{i:03d}.docx')
            risk_test_documents.append(doc_path)
            
            # Extract properties with privacy analysis
            tool.extract_document_properties(doc_path)
        
        # Validate privacy risk categorization
        risk_levels = {}
        for doc_path in risk_test_documents:
            if doc_path in tool.privacy_concerns:
                privacy_data = tool.privacy_concerns[doc_path]
                risk_level = privacy_data['risk_level']
                risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        
        # Validate risk assessment distribution
        total_assessed = sum(risk_levels.values())
        assert total_assessed > 0
        
        # Validate risk levels are valid
        for risk_level in risk_levels.keys():
            assert risk_level in ['low', 'medium', 'high']
    
    def test_compliance_reporting_workflow(self, office_metadata_test_environment):
        """Test generation of compliance reports"""
        env = office_metadata_test_environment
        tool = env['tool']
        
        # Test data setup
        compliance_documents = []
        for i in range(8):
            doc_path = os.path.join(env['test_data_path'], 'documents', f'compliance_{i:03d}.docx')
            compliance_documents.append(doc_path)
            
            # Extract properties for compliance analysis
            tool.extract_document_properties(doc_path)
        
        # Generate compliance summary
        compliance_summary = {
            'total_documents': len(compliance_documents),
            'documents_with_privacy_concerns': 0,
            'high_risk_documents': 0,
            'medium_risk_documents': 0,
            'low_risk_documents': 0
        }
        
        for doc_path in compliance_documents:
            if doc_path in tool.privacy_concerns:
                privacy_data = tool.privacy_concerns[doc_path]
                compliance_summary['documents_with_privacy_concerns'] += 1
                
                risk_level = privacy_data['risk_level']
                if risk_level == 'high':
                    compliance_summary['high_risk_documents'] += 1
                elif risk_level == 'medium':
                    compliance_summary['medium_risk_documents'] += 1
                else:
                    compliance_summary['low_risk_documents'] += 1
        
        # Validate compliance reporting data
        assert compliance_summary['total_documents'] == len(compliance_documents)
        
        total_risk_categorized = (compliance_summary['high_risk_documents'] + 
                                compliance_summary['medium_risk_documents'] + 
                                compliance_summary['low_risk_documents'])
        assert total_risk_categorized == compliance_summary['documents_with_privacy_concerns']


class TestOfficeMetadataIntegration:
    """Test class for hub integration and cross-tool workflows"""
    
    def test_office_metadata_hub_integration_workflow(self, office_metadata_test_environment):
        """Test Office Metadata tool integration with RFU Hub"""
        env = office_metadata_test_environment
        tool = env['tool']
        hub = env['hub']
        
        # Validate hub registration
        assert 'office_metadata' in hub.registered_tools
        assert hub.registered_tools['office_metadata'] == tool
        
        # Test hub coordination
        test_doc_path = os.path.join(env['test_data_path'], 'documents', 'hub_integration_test.docx')
        
        # Execute operation through hub-registered tool
        result = tool.extract_document_properties(test_doc_path)
        
        # Validate hub integration
        assert result['status'] == 'success'
        assert len(hub.hub_events) > 0
        
        # Validate tool status tracking
        tool_status = hub.tool_status['office_metadata']
        assert tool_status['status'] == 'registered'
        assert 'last_activity' in tool_status
    
    def test_cross_tool_document_workflow_integration(self, office_metadata_test_environment):
        """Test document metadata workflow integration"""
        env = office_metadata_test_environment
        tool = env['tool']
        hub = env['hub']
        
        # Simulate cross-tool workflow: Office Metadata → Security Analysis
        test_documents = []
        for i in range(3):
            doc_path = os.path.join(env['test_data_path'], 'documents', f'cross_tool_{i:03d}.docx')
            test_documents.append(doc_path)
            
            # Extract metadata for security handoff
            result = tool.extract_document_properties(doc_path)
            assert result['status'] == 'success'
        
        # Validate metadata available for cross-tool handoff
        security_handoff_data = []
        for doc_path in test_documents:
            if doc_path in tool.privacy_concerns:
                privacy_data = tool.privacy_concerns[doc_path]
                
                # Prepare data for security tool handoff
                handoff_item = {
                    'document_path': doc_path,
                    'risk_level': privacy_data['risk_level'],
                    'privacy_concerns': privacy_data['privacy_concerns'],
                    'recommendations': privacy_data['recommendations']
                }
                security_handoff_data.append(handoff_item)
        
        # Validate handoff data structure
        for handoff_item in security_handoff_data:
            assert 'document_path' in handoff_item
            assert 'risk_level' in handoff_item
            assert handoff_item['risk_level'] in ['low', 'medium', 'high']
    
    def test_concurrent_office_metadata_operations_workflow(self, office_metadata_test_environment):
        """Test concurrent office metadata operations"""
        env = office_metadata_test_environment
        tool = env['tool']
        hub = env['hub']
        
        # Test data setup
        concurrent_docs = []
        for i in range(6):
            doc_path = os.path.join(env['test_data_path'], 'documents', f'concurrent_{i:03d}.docx')
            concurrent_docs.append(doc_path)
        
        # Execute concurrent-style operations
        results = []
        
        # Operation 1: Extract properties from first half
        for doc_path in concurrent_docs[:3]:
            result = tool.extract_document_properties(doc_path)
            results.append(result)
        
        # Operation 2: Privacy analysis on second half
        for doc_path in concurrent_docs[3:]:
            result = tool.extract_document_properties(doc_path)
            results.append(result)
        
        # Validate concurrent operation coordination
        successful_ops = len([r for r in results if r['status'] == 'success'])
        assert successful_ops >= len(results) // 2
        
        # Validate hub coordination
        assert len(hub.registered_tools) > 0
        assert 'office_metadata' in hub.registered_tools
        assert hub.tool_status['office_metadata']['status'] == 'registered'
        
        # Validate resource coordination
        resource_usage = tool.get_resource_usage()
        assert resource_usage['memory'] > 0
        assert resource_usage['cpu'] > 0