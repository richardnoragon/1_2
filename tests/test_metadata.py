import unittest
import os
from tests.test_utils import TestUtils
from office_meta_data_editor import OfficeMetaEditor  # Update based on actual class name
from tag_viewer_editor import TagEditor  # Update based on actual class name

class TestMetadataManagement(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.office_editor = OfficeMetaEditor()
        self.tag_editor = TagEditor()
        
        # Create a simple DOCX file (minimal valid structure)
        self.docx_file = os.path.join(self.test_dir, "test.docx")
        self._create_minimal_docx(self.docx_file)
        
        # Create a simple MP3 file
        self.mp3_file = os.path.join(self.test_dir, "test.mp3")
        self._create_minimal_mp3(self.mp3_file)

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)

    def _create_minimal_docx(self, filepath):
        """Creates a minimal valid DOCX file"""
        from zipfile import ZipFile, ZIP_DEFLATED
        
        with ZipFile(filepath, 'w', ZIP_DEFLATED) as docx:
            # Add required Office Open XML files
            docx.writestr('[Content_Types].xml',
                '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
            docx.writestr('docProps/core.xml',
                '<?xml version="1.0" encoding="UTF-8"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"/>')

    def _create_minimal_mp3(self, filepath):
        """Creates a minimal valid MP3 file"""
        with open(filepath, 'wb') as f:
            # Write minimal MP3 header
            f.write(b'ID3\x03\x00\x00\x00\x00\x00\x00')
            # Write minimal MP3 frame
            f.write(b'\xFF\xFB\x90\x44\x00')  # MPEG-1 Layer 3

    def test_office_metadata_read(self):
        """Test reading Office document metadata"""
        metadata = self.office_editor.read_metadata(self.docx_file)
        self.assertIsNotNone(metadata)
        self.assertTrue(isinstance(metadata, dict))

    def test_office_metadata_write(self):
        """Test writing Office document metadata"""
        test_metadata = {
            'title': 'Test Document',
            'author': 'Test Author',
            'subject': 'Test Subject',
            'keywords': 'test, document'
        }
        
        # Write metadata
        self.office_editor.write_metadata(self.docx_file, test_metadata)
        
        # Read back and verify
        read_metadata = self.office_editor.read_metadata(self.docx_file)
        for key, value in test_metadata.items():
            self.assertEqual(read_metadata.get(key), value)

    def test_mp3_tags_read(self):
        """Test reading MP3 tags"""
        tags = self.tag_editor.read_tags(self.mp3_file)
        self.assertIsNotNone(tags)
        self.assertTrue(isinstance(tags, dict))

    def test_mp3_tags_write(self):
        """Test writing MP3 tags"""
        test_tags = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'album': 'Test Album',
            'year': '2025'
        }
        
        # Write tags
        self.tag_editor.write_tags(self.mp3_file, test_tags)
        
        # Read back and verify
        read_tags = self.tag_editor.read_tags(self.mp3_file)
        for key, value in test_tags.items():
            self.assertEqual(read_tags.get(key), value)

    def test_batch_metadata_update(self):
        """Test updating metadata for multiple files"""
        # Create multiple test files
        files = []
        for i in range(3):
            docx_file = os.path.join(self.test_dir, f"test_{i}.docx")
            self._create_minimal_docx(docx_file)
            files.append(docx_file)
        
        # Update metadata for all files
        common_metadata = {'company': 'Test Company', 'category': 'Test'}
        self.office_editor.batch_update(files, common_metadata)
        
        # Verify all files were updated
        for file in files:
            metadata = self.office_editor.read_metadata(file)
            self.assertEqual(metadata.get('company'), 'Test Company')
            self.assertEqual(metadata.get('category'), 'Test')

    def test_metadata_export_import(self):
        """Test exporting and importing metadata"""
        # Set initial metadata
        initial_metadata = {
            'title': 'Export Test',
            'author': 'Test Author'
        }
        self.office_editor.write_metadata(self.docx_file, initial_metadata)
        
        # Export metadata
        export_file = os.path.join(self.test_dir, "metadata.json")
        self.office_editor.export_metadata([self.docx_file], export_file)
        
        # Modify the original metadata
        self.office_editor.write_metadata(self.docx_file, {'title': 'Changed'})
        
        # Import metadata back
        self.office_editor.import_metadata(export_file)
        
        # Verify metadata was restored
        restored = self.office_editor.read_metadata(self.docx_file)
        self.assertEqual(restored.get('title'), 'Export Test')
        self.assertEqual(restored.get('author'), 'Test Author')

if __name__ == '__main__':
    unittest.main()