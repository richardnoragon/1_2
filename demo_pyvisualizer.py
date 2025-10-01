#!/usr/bin/env python3
"""
PyVisualizer Demo for Richard's File Utilities (RFU)
====================================================

This script demonstrates how to use PyVisualizer for data visualization
in the RFU project. It shows various ways to visualize file system data,
usage statistics, and other metrics that would be relevant to a file
management utility.

Author: GitHub Copilot
Date: September 29, 2025
"""

import os
import sys
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from PyVisualizer.Visualizer import Visualizer

# Set up matplotlib backend for GUI display
plt.switch_backend("TkAgg")


def create_sample_data():
    """Create sample data that mimics RFU file operations and statistics."""

    # Create sample file operation data
    np.random.seed(42)  # For reproducible results

    # Generate timestamps for the last year
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range(365)]
    timestamps = [int(date.timestamp()) for date in dates]

    # Sample file operations data
    file_operations = {
        "timestamp": timestamps,
        "files_copied": np.random.randint(10, 100, 365),
        "files_moved": np.random.randint(5, 50, 365),
        "files_deleted": np.random.randint(1, 20, 365),
        "duplicate_files_found": np.random.randint(0, 30, 365),
        "average_sales": np.random.normal(5000, 1500, 365).astype(
            int
        ),  # PyVisualizer expects this column
    }

    return pd.DataFrame(file_operations)


def create_file_size_data():
    """Create sample file size distribution data."""

    file_types = ["PDF", "Images", "Documents", "Archives", "Videos", "Audio", "Other"]
    sizes_mb = [2500, 15000, 1200, 8500, 45000, 6800, 3200]  # Size in MB

    return pd.DataFrame({"file_type": file_types, "total_size_mb": sizes_mb})


def demo_pyvisualizer_basic():
    """Demonstrate basic PyVisualizer functionality."""

    print("🎯 PyVisualizer Demo - Basic Functionality")
    print("=" * 50)

    # Create sample data
    data = create_sample_data()
    print(f"✅ Generated sample data with {len(data)} records")

    # Initialize visualizer
    visualizer = Visualizer()

    print("\n📊 Creating visualizations...")

    try:
        # Create sales by year plot (repurposed for file operations)
        print("1. Creating yearly file operations chart...")
        visualizer.barPlotSalesByYear(
            pandasDataframe=data,
            xColName="timestamp",
            yColName="average_sales",
            sSaveWithFileName="rfu_yearly_operations.png",
        )
        print("   ✅ Saved as 'rfu_yearly_operations.png'")

    except Exception as e:
        print(f"   ❌ Error creating yearly chart: {e}")

    try:
        # Create sales by month plot
        print("2. Creating monthly file operations chart...")
        visualizer.barPlotSalesByMonth(
            pandasDataframe=data,
            xColName="timestamp",
            yColName="average_sales",
            sSaveWithFileName="rfu_monthly_operations.png",
        )
        print("   ✅ Saved as 'rfu_monthly_operations.png'")

    except Exception as e:
        print(f"   ❌ Error creating monthly chart: {e}")


def demo_custom_visualizations():
    """Create custom visualizations using matplotlib/seaborn directly."""

    print("\n🎨 Creating Custom RFU Visualizations")
    print("=" * 40)

    # File size distribution
    file_data = create_file_size_data()

    # Set up the plotting style
    plt.style.use("seaborn-v0_8")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle("Richard's File Utilities - System Analytics Dashboard", fontsize=16)

    # 1. File size distribution pie chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(file_data)))
    ax1.pie(
        file_data["total_size_mb"],
        labels=file_data["file_type"],
        autopct="%1.1f%%",
        colors=colors,
    )
    ax1.set_title("Storage Usage by File Type")

    # 2. File operations over time
    operations_data = create_sample_data()
    ax2.plot(
        operations_data.index[-30:],
        operations_data["files_copied"][-30:],
        label="Files Copied",
        marker="o",
    )
    ax2.plot(
        operations_data.index[-30:],
        operations_data["files_moved"][-30:],
        label="Files Moved",
        marker="s",
    )
    ax2.plot(
        operations_data.index[-30:],
        operations_data["files_deleted"][-30:],
        label="Files Deleted",
        marker="^",
    )
    ax2.set_title("File Operations (Last 30 Days)")
    ax2.legend()
    ax2.set_xlabel("Days")
    ax2.set_ylabel("Number of Files")

    # 3. Duplicate detection efficiency
    ax3.bar(
        ["Duplicates Found", "Files Processed"],
        [1250, 15800],
        color=["#ff6b6b", "#4ecdc4"],
    )
    ax3.set_title("Duplicate Detection Results")
    ax3.set_ylabel("Number of Files")

    # 4. System resource usage (simulated)
    resources = ["CPU Usage", "Memory Usage", "Disk I/O", "Network I/O"]
    usage_percent = [25, 45, 60, 15]
    bars = ax4.barh(
        resources, usage_percent, color=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"]
    )
    ax4.set_title("Resource Utilization")
    ax4.set_xlabel("Usage Percentage")
    ax4.set_xlim(0, 100)

    # Add percentage labels on bars
    for bar, pct in zip(bars, usage_percent):
        ax4.text(
            bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{pct}%",
            va="center",
        )

    plt.tight_layout()
    plt.savefig("rfu_analytics_dashboard.png", dpi=300, bbox_inches="tight")
    print("✅ Created comprehensive analytics dashboard: 'rfu_analytics_dashboard.png'")

    plt.show()


def demo_integration_with_rfu():
    """Show how PyVisualizer could integrate with your RFU project."""

    print("\n🔧 Integration Ideas for RFU Project")
    print("=" * 40)

    integration_ideas = [
        "📁 File Operation Statistics: Track copy, move, delete operations over time",
        "🔍 Duplicate File Analysis: Visualize duplicate detection results and savings",
        "📊 Storage Analysis: Show file type distribution and storage usage",
        "⚡ Performance Metrics: Display tool execution times and efficiency",
        "🔐 Security Dashboard: Visualize encryption/decryption operations",
        "📈 Usage Analytics: Track which tools are used most frequently",
        "🎯 Quality Metrics: Show test coverage, error rates, and performance",
        "🌐 Network Activity: Visualize network connectivity tool usage",
    ]

    for idea in integration_ideas:
        print(f"  {idea}")

    print(f"\n💡 Integration Steps:")
    print("  1. Add data logging to your RFU tools")
    print("  2. Create data collection utilities in your ConfigManager")
    print("  3. Use PyVisualizer to generate reports and dashboards")
    print("  4. Add visualization menu items to your GUI")


def main():
    """Main demonstration function."""

    print("🚀 PyVisualizer Integration Demo for RFU")
    print("=" * 50)
    print("This demo shows how PyVisualizer can be used with")
    print("Richard's File Utilities for data visualization.\n")

    try:
        # Run basic PyVisualizer demo
        demo_pyvisualizer_basic()

        # Run custom visualizations demo
        demo_custom_visualizations()

        # Show integration ideas
        demo_integration_with_rfu()

        print(f"\n🎉 Demo completed successfully!")
        print("Check the generated PNG files for visualizations.")
        print("\nGenerated files:")
        for filename in [
            "rfu_yearly_operations.png",
            "rfu_monthly_operations.png",
            "rfu_analytics_dashboard.png",
        ]:
            if os.path.exists(filename):
                print(f"  ✅ {filename}")
            else:
                print(f"  ❌ {filename} (not created)")

    except KeyboardInterrupt:
        print("\n⏸️  Demo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
