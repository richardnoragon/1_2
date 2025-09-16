"""
Simplified Network GUI Test - Initial Validation
Test file: test_network_gui_simple_2025-08-29.py
Target module: src/utilities/network/gui.py
Generated: 2025-08-29

This is a simplified test to validate the testing environment setup.
"""

import sys

import pytest

# Add the source directory to the Python path
sys.path.insert(0, r'c:\Users\richardi\1_2\src')

def test_imports():
    """Test that all required modules can be imported."""
    try:
        from utilities.network.gui import (DEFAULT_SPEED_LABEL, BandwidthData,
                                           NetworkScanResult)
        assert DEFAULT_SPEED_LABEL == "0 KB/s"
        print("✅ Basic imports successful")
    except ImportError as e:
        pytest.skip(f"Cannot import network GUI module: {e}")

def test_network_scan_result():
    """Test NetworkScanResult dataclass creation."""
    from utilities.network.gui import NetworkScanResult
    
    result = NetworkScanResult(
        target="127.0.0.1",
        port=80,
        state="open", 
        service="HTTP"
    )
    
    assert result.target == "127.0.0.1"
    assert result.port == 80
    assert result.state == "open"
    assert result.service == "HTTP"
    print("✅ NetworkScanResult test passed")

def test_bandwidth_data():
    """Test BandwidthData dataclass creation."""
    from datetime import datetime

    from utilities.network.gui import BandwidthData
    
    timestamp = datetime.now()
    data = BandwidthData(
        timestamp=timestamp,
        download_speed=1024.0,
        upload_speed=512.0,
        total_download=1048576,
        total_upload=524288
    )
    
    assert data.timestamp == timestamp
    assert data.download_speed == 1024.0
    assert data.upload_speed == 512.0
    print("✅ BandwidthData test passed")

if __name__ == "__main__":
    test_imports()
    test_network_scan_result()
    test_bandwidth_data()
    print("🎉 All simple tests passed!")