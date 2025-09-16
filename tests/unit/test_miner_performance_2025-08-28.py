"""
Performance and Stress Tests for miner.py
Created: 2025-08-28
Tests performance characteristics and stress conditions
"""

import pytest
import time
import sys
import os
import threading
import multiprocessing
from unittest.mock import Mock, patch
from memory_profiler import profile
import gc

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.tools.pdf_tools.pdf_view_analysis.miner import PDFMiner, MainWindow


class TestPDFMinerPerformance:
    """Performance tests for PDFMiner class"""
    
    def setup_method(self):
        """Setup performance test environment"""
        self.large_pdf_pages = 1000
        self.stress_iterations = 100
        
    @pytest.mark.slow
    @pytest.mark.performance
    def test_large_pdf_initialization_performance(self):
        """Test PDFMiner initialization with large PDF"""
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        mock_pdf_doc.load_page.return_value = mock_first_page
        mock_pdf_doc.page_count = self.large_pdf_pages
        
        with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz:
            mock_fitz.return_value = mock_pdf_doc
            
            start_time = time.time()
            miner = PDFMiner("large_test.pdf")
            end_time = time.time()
            
            initialization_time = end_time - start_time
            assert initialization_time < 5.0, f"Initialization took too long: {initialization_time:.2f}s"
            assert miner.pdf == mock_pdf_doc
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_metadata_extraction_performance(self):
        """Test metadata extraction performance with large dataset"""
        mock_pdf_doc = Mock()
        large_metadata = {f"field_{i}": f"value_{i}" * 100 for i in range(1000)}
        mock_pdf_doc.metadata = large_metadata
        mock_pdf_doc.page_count = self.large_pdf_pages
        
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        mock_pdf_doc.load_page.return_value = mock_first_page
        
        with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz:
            mock_fitz.return_value = mock_pdf_doc
            miner = PDFMiner("test.pdf")
            
            start_time = time.time()
            metadata, num_pages = miner.get_metadata()
            end_time = time.time()
            
            extraction_time = end_time - start_time
            assert extraction_time < 1.0, f"Metadata extraction took too long: {extraction_time:.2f}s"
            assert len(metadata) == 1000
            assert num_pages == self.large_pdf_pages
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_page_rendering_performance(self):
        """Test page rendering performance"""
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.samples = b'\\x00' * (1920 * 1080 * 3)  # Large image data
        mock_pixmap.width = 1920
        mock_pixmap.height = 1080
        mock_pixmap.stride = 1920 * 3
        mock_page.get_pixmap.return_value = mock_pixmap
        
        mock_pdf_doc.load_page.side_effect = lambda page_num: mock_first_page if page_num == 0 else mock_page
        
        with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz, \\
             patch('src.tools.pdf_tools.pdf_view_analysis.miner.QImage') as mock_qimage:
            
            mock_fitz.return_value = mock_pdf_doc
            mock_qimage.return_value = Mock()
            
            miner = PDFMiner("test.pdf")
            
            # Test multiple page renders
            start_time = time.time()
            for i in range(10):
                miner.get_page(i % 5)
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = total_time / 10
            assert avg_time < 0.5, f"Average page render time too slow: {avg_time:.3f}s"
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_text_extraction_performance(self):
        """Test text extraction performance with large text"""
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        
        large_text = "Sample text content. " * 10000  # Large text block
        mock_page = Mock()
        mock_page.getText.return_value = large_text
        
        mock_pdf_doc.load_page.side_effect = lambda page_num: mock_first_page if page_num == 0 else mock_page
        
        with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz:
            mock_fitz.return_value = mock_pdf_doc
            miner = PDFMiner("test.pdf")
            
            start_time = time.time()
            for i in range(50):
                text = miner.get_text(i % 10)
                assert len(text) > 0
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = total_time / 50
            assert avg_time < 0.1, f"Average text extraction time too slow: {avg_time:.3f}s"


class TestPDFMinerStress:
    """Stress tests for PDFMiner class"""
    
    @pytest.mark.slow
    @pytest.mark.stress
    def test_concurrent_pdf_access(self):
        """Test concurrent access to PDFMiner instances"""
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        mock_pdf_doc.load_page.return_value = mock_first_page
        mock_pdf_doc.metadata = {"title": "Concurrent Test"}
        mock_pdf_doc.page_count = 10
        
        results = []
        errors = []
        
        def create_and_use_miner(thread_id):
            try:
                with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz:
                    mock_fitz.return_value = mock_pdf_doc
                    miner = PDFMiner(f"test_{thread_id}.pdf")
                    
                    # Perform various operations
                    metadata, pages = miner.get_metadata()
                    text = miner.get_text(0)
                    
                    results.append((thread_id, len(metadata), pages, len(text)))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_and_use_miner, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(errors) == 0, f"Errors in concurrent access: {errors}"
        assert len(results) == 10, f"Not all threads completed: {len(results)}"
    
    @pytest.mark.slow
    @pytest.mark.stress
    def test_memory_usage_with_multiple_pdfs(self):
        """Test memory usage when creating multiple PDFMiner instances"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        miners = []
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        mock_pdf_doc.load_page.return_value = mock_first_page
        mock_pdf_doc.metadata = {"title": "Memory Test"}
        mock_pdf_doc.page_count = 100
        
        try:
            with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz:
                mock_fitz.return_value = mock_pdf_doc
                
                # Create multiple PDFMiner instances
                for i in range(50):
                    miner = PDFMiner(f"test_{i}.pdf")
                    miners.append(miner)
                    
                    # Use the miner to ensure it's active in memory
                    miner.get_metadata()
                
                current_memory = process.memory_info().rss
                memory_increase = current_memory - initial_memory
                memory_per_instance = memory_increase / len(miners)
                
                # Memory increase should be reasonable (less than 50MB total)
                assert memory_increase < 50 * 1024 * 1024, \\
                    f"Memory usage too high: {memory_increase / 1024 / 1024:.1f}MB"
                
                print(f"Memory per instance: {memory_per_instance / 1024:.1f}KB")
                
        finally:
            # Cleanup
            del miners
            gc.collect()
    
    @pytest.mark.slow
    @pytest.mark.stress
    def test_repeated_operations_stress(self):
        """Test repeated operations for memory leaks and stability"""
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.samples = b'\\x00' * 1000
        mock_pixmap.width = 800
        mock_pixmap.height = 600
        mock_pixmap.stride = 2400
        mock_page.get_pixmap.return_value = mock_pixmap
        mock_page.getText.return_value = "Sample text content"
        
        mock_pdf_doc.load_page.side_effect = lambda page_num: mock_first_page if page_num == 0 else mock_page
        mock_pdf_doc.metadata = {"title": "Stress Test"}
        mock_pdf_doc.page_count = 10
        
        with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz, \\
             patch('src.tools.pdf_tools.pdf_view_analysis.miner.QImage') as mock_qimage:
            
            mock_fitz.return_value = mock_pdf_doc
            mock_qimage.return_value = Mock()
            
            miner = PDFMiner("stress_test.pdf")
            
            # Perform repeated operations
            for iteration in range(1000):
                # Get metadata
                metadata, pages = miner.get_metadata()
                assert pages == 10
                
                # Extract text
                text = miner.get_text(iteration % 10)
                assert text == "Sample text content"
                
                # Render page
                if iteration % 10 == 0:  # Reduce frequency to avoid timeout
                    page_image = miner.get_page(iteration % 10)
                    assert page_image is not None
                
                # Check for basic functionality every 100 iterations
                if iteration % 100 == 0:
                    assert miner.width == 800
                    assert miner.height == 600


class TestMainWindowPerformance:
    """Performance tests for MainWindow class"""
    
    @pytest.fixture(autouse=True)
    def setup_qapp(self):
        """Setup QApplication for GUI tests"""
        from PyQt5.QtWidgets import QApplication
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
    
    @pytest.mark.slow
    @pytest.mark.performance
    @pytest.mark.gui
    def test_main_window_creation_performance(self):
        """Test MainWindow creation performance"""
        creation_times = []
        
        for i in range(10):
            with patch('src.tools.pdf_tools.pdf_view_analysis.miner.uic.loadUi'), \\
                 patch.object(MainWindow, 'actionExit') as mock_exit, \\
                 patch.object(MainWindow, 'actionOpen') as mock_open:
                
                mock_exit.triggered = Mock()
                mock_open.triggered = Mock()
                
                start_time = time.time()
                window = MainWindow()
                end_time = time.time()
                
                creation_time = end_time - start_time
                creation_times.append(creation_time)
                
                # Cleanup
                window.deleteLater()
        
        avg_creation_time = sum(creation_times) / len(creation_times)
        max_creation_time = max(creation_times)
        
        assert avg_creation_time < 1.0, f"Average window creation too slow: {avg_creation_time:.3f}s"
        assert max_creation_time < 2.0, f"Maximum window creation too slow: {max_creation_time:.3f}s"
        
        print(f"Average creation time: {avg_creation_time:.3f}s")
        print(f"Maximum creation time: {max_creation_time:.3f}s")


class TestPerformanceBenchmarks:
    """Benchmark tests for comparing performance"""
    
    @pytest.mark.slow
    @pytest.mark.benchmark
    def test_pdf_miner_initialization_benchmark(self, benchmark):
        """Benchmark PDFMiner initialization"""
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        mock_pdf_doc.load_page.return_value = mock_first_page
        
        def initialize_miner():
            with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz:
                mock_fitz.return_value = mock_pdf_doc
                return PDFMiner("benchmark_test.pdf")
        
        result = benchmark(initialize_miner)
        assert result is not None
    
    @pytest.mark.slow
    @pytest.mark.benchmark
    def test_metadata_extraction_benchmark(self, benchmark):
        """Benchmark metadata extraction"""
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        mock_pdf_doc.load_page.return_value = mock_first_page
        mock_pdf_doc.metadata = {"title": "Benchmark Test", "author": "Test Author"}
        mock_pdf_doc.page_count = 100
        
        with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz:
            mock_fitz.return_value = mock_pdf_doc
            miner = PDFMiner("benchmark_test.pdf")
            
            result = benchmark(miner.get_metadata)
            assert result[1] == 100  # page count
    
    @pytest.mark.slow
    @pytest.mark.benchmark
    def test_page_rendering_benchmark(self, benchmark):
        """Benchmark page rendering"""
        mock_pdf_doc = Mock()
        mock_first_page = Mock()
        mock_first_page.rect.width = 800
        mock_first_page.rect.height = 600
        
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.samples = b'\\x00' * 1000
        mock_pixmap.width = 800
        mock_pixmap.height = 600
        mock_pixmap.stride = 2400
        mock_page.get_pixmap.return_value = mock_pixmap
        
        mock_pdf_doc.load_page.side_effect = lambda page_num: mock_first_page if page_num == 0 else mock_page
        
        with patch('src.tools.pdf_tools.pdf_view_analysis.miner.fitz.open') as mock_fitz, \\
             patch('src.tools.pdf_tools.pdf_view_analysis.miner.QImage') as mock_qimage:
            
            mock_fitz.return_value = mock_pdf_doc
            mock_qimage.return_value = Mock()
            
            miner = PDFMiner("benchmark_test.pdf")
            
            result = benchmark(miner.get_page, 1)
            assert result is not None


if __name__ == '__main__':
    # Run performance tests
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'performance or stress or benchmark',
        '--durations=0'
    ])