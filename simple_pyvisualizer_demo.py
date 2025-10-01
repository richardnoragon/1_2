#!/usr/bin/env python3
"""
Simple PyVisualizer Demo for RFU Integration
============================================

A simplified demonstration of PyVisualizer integration.

Author: GitHub Copilot
Date: September 29, 2025
"""

import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Check PyVisualizer availability
try:
    from PyVisualizer.Visualizer import Visualizer

    PYVISUALIZER_AVAILABLE = True
    print("✅ PyVisualizer is available!")
except ImportError:
    PYVISUALIZER_AVAILABLE = False
    print("❌ PyVisualizer not found in Python path")


def create_rfu_demo_data():
    """Create sample data for RFU operations."""

    print("📊 Creating sample RFU operations data...")

    # Create 365 days of sample data
    np.random.seed(42)
    dates = []
    start_date = datetime(2024, 1, 1)

    for i in range(365):
        dates.append(start_date + timedelta(days=i))

    # Convert to timestamps for PyVisualizer
    timestamps = [int(date.timestamp()) for date in dates]

    # Sample operations data
    data = {
        "timestamp": timestamps,
        "files_processed": np.random.randint(10, 500, 365),
        "duplicates_found": np.random.randint(0, 50, 365),
        "storage_saved_mb": np.random.randint(100, 5000, 365),
        "operations_count": np.random.randint(1, 20, 365),
        "average_sales": np.random.randint(
            1000, 10000, 365
        ),  # Required by PyVisualizer
    }

    df = pd.DataFrame(data)
    print(f"   ✅ Created {len(df)} records of sample data")
    return df


def demo_pyvisualizer_with_rfu_data():
    """Demonstrate PyVisualizer with RFU-style data."""

    if not PYVISUALIZER_AVAILABLE:
        print("❌ Cannot run PyVisualizer demo - not installed properly")
        return

    print("\n🎯 Running PyVisualizer Demo")
    print("=" * 30)

    # Create sample data
    data = create_rfu_demo_data()

    # Initialize PyVisualizer
    visualizer = Visualizer()

    # Create output directory
    output_dir = "rfu_reports"
    os.makedirs(output_dir, exist_ok=True)
    original_dir = os.getcwd()

    try:
        os.chdir(output_dir)

        print("\n📈 Generating yearly visualization...")
        visualizer.barPlotSalesByYear(
            pandasDataframe=data,
            xColName="timestamp",
            yColName="average_sales",
            sSaveWithFileName="rfu_operations_yearly.png",
        )
        print("   ✅ Created: rfu_operations_yearly.png")

        print("\n📈 Generating monthly visualization...")
        visualizer.barPlotSalesByMonth(
            pandasDataframe=data,
            xColName="timestamp",
            yColName="average_sales",
            sSaveWithFileName="rfu_operations_monthly.png",
        )
        print("   ✅ Created: rfu_operations_monthly.png")

    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
    finally:
        os.chdir(original_dir)

    print(f"\n📁 Visualizations saved to: {os.path.abspath(output_dir)}")


def show_integration_guide():
    """Show how to integrate PyVisualizer with RFU project."""

    print("\n🔧 RFU Integration Guide")
    print("=" * 25)

    print("1. 📋 Add to requirements.txt:")
    print("   pyvisualizer>=1.0.9")

    print("\n2. 🏗️  Create analytics module:")
    print("   src/rfu/analytics/visualizer.py")

    print("\n3. 📊 Add logging to RFU tools:")
    print("   - Log file operations (copy, move, delete)")
    print("   - Track duplicate detection results")
    print("   - Monitor tool usage statistics")
    print("   - Record performance metrics")

    print("\n4. 🖥️  Add GUI menu items:")
    print("   - 'Generate Reports' in main menu")
    print("   - 'View Analytics' in tools menu")
    print("   - 'Export Charts' option")

    print("\n5. 📈 Sample integration code:")
    integration_code = """
# In your RFU tool classes:
from src.rfu.analytics.visualizer import RFUVisualizer

class FileOperationTool:
    def __init__(self):
        self.analytics = RFUVisualizer()
    
    def copy_files(self, files):
        start_time = time.time()
        # ... perform copy operation ...
        duration = time.time() - start_time
        
        # Log for analytics
        self.analytics.log_operation(
            operation='copy',
            file_count=len(files),
            size_mb=total_size_mb,
            duration=duration
        )
"""
    print(integration_code)


def main():
    """Main function."""

    print("🚀 PyVisualizer + RFU Integration Demo")
    print("=" * 40)

    # Check if PyVisualizer is properly set up
    if PYVISUALIZER_AVAILABLE:
        # Run the demonstration
        demo_pyvisualizer_with_rfu_data()

        print("\n🎉 PyVisualizer demo completed successfully!")
    else:
        print("⚠️  PyVisualizer not properly installed.")
        print("   Run: pip install pyvisualizer")

    # Show integration guide
    show_integration_guide()

    print(f"\n✅ Demo finished! Check the generated visualization files.")


if __name__ == "__main__":
    main()
