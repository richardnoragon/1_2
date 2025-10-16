#!/usr/bin/env python3
"""
RFU Analytics Module with PyVisualizer Integration
=================================================

This module demonstrates how to integrate PyVisualizer into the RFU project
for creating analytics and reporting capabilities.

Author: GitHub Copilot
Date: September 29, 2025
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# PyVisualizer imports
try:
    from PyVisualizer.CommonUtilities import CommonUtilities
    from PyVisualizer.Visualizer import Visualizer

    PYVISUALIZER_AVAILABLE = True
except ImportError:
    PYVISUALIZER_AVAILABLE = False
    print("⚠️  PyVisualizer not available. Install with: pip install pyvisualizer")

# RFU imports (would be actual imports in your project)
# from src.rfu.config_manager import ConfigManager
# from src.rfu.core.log_manager import get_log_manager


class RFUAnalytics:
    """
    Analytics and reporting system for Richard's File Utilities using PyVisualizer.
    """

    def __init__(self, rfu_data_dir: str = "data/analytics"):
        """
        Initialize RFU Analytics system.

        Args:
            rfu_data_dir: Directory to store analytics data
        """
        self.data_dir = Path(rfu_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize visualizer if available
        if PYVISUALIZER_AVAILABLE:
            self.visualizer = Visualizer()
            self.common_utils = CommonUtilities()
        else:
            self.visualizer = None
            self.common_utils = None

        # Sample data for demonstration
        self.operations_log = self.data_dir / "operations.json"
        self.tool_usage_log = self.data_dir / "tool_usage.json"

    def log_operation(
        self,
        operation_type: str,
        file_count: int,
        size_mb: float,
        duration_seconds: float,
    ):
        """
        Log a file operation for analytics.

        Args:
            operation_type: Type of operation (copy, move, delete, etc.)
            file_count: Number of files processed
            size_mb: Total size in MB
            duration_seconds: Time taken for operation
        """

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "file_count": file_count,
            "size_mb": size_mb,
            "duration_seconds": duration_seconds,
            "files_per_second": file_count / max(duration_seconds, 0.1),
        }

        # Load existing logs
        logs = []
        if self.operations_log.exists():
            with open(self.operations_log, "r") as f:
                logs = json.load(f)

        # Add new entry
        logs.append(log_entry)

        # Save updated logs
        with open(self.operations_log, "w") as f:
            json.dump(logs, f, indent=2)

    def log_tool_usage(self, tool_name: str, success: bool, execution_time: float):
        """
        Log tool usage for analytics.

        Args:
            tool_name: Name of the RFU tool used
            success: Whether the operation succeeded
            execution_time: Time taken to execute
        """

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "success": success,
            "execution_time": execution_time,
        }

        # Load existing logs
        logs = []
        if self.tool_usage_log.exists():
            with open(self.tool_usage_log, "r") as f:
                logs = json.load(f)

        # Add new entry
        logs.append(log_entry)

        # Save updated logs
        with open(self.tool_usage_log, "w") as f:
            json.dump(logs, f, indent=2)

    def get_operations_dataframe(self) -> Optional[pd.DataFrame]:
        """Get operations data as pandas DataFrame."""

        if not self.operations_log.exists():
            return None

        with open(self.operations_log, "r") as f:
            data = json.load(f)

        if not data:
            return None

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["unix_timestamp"] = df["timestamp"].astype("int64") // 10**9

        # Add columns expected by PyVisualizer
        df["average_sales"] = df["file_count"] * 100  # Mock sales data

        return df

    def get_tool_usage_dataframe(self) -> Optional[pd.DataFrame]:
        """Get tool usage data as pandas DataFrame."""

        if not self.tool_usage_log.exists():
            return None

        with open(self.tool_usage_log, "r") as f:
            data = json.load(f)

        if not data:
            return None

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df

    def create_operations_visualizations(self, output_dir: str = "reports"):
        """
        Create visualizations for file operations using PyVisualizer.

        Args:
            output_dir: Directory to save visualization files
        """

        if not PYVISUALIZER_AVAILABLE:
            print("❌ PyVisualizer not available. Cannot create visualizations.")
            return

        # Get data
        df = self.get_operations_dataframe()
        if df is None or df.empty:
            print("⚠️  No operations data available for visualization.")
            return

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Change to output directory for PyVisualizer
        original_cwd = os.getcwd()
        os.chdir(output_path)

        try:
            print("📊 Creating operations visualizations...")

            # Yearly operations chart
            self.visualizer.barPlotSalesByYear(
                pandasDataframe=df,
                xColName="unix_timestamp",
                yColName="average_sales",
                sSaveWithFileName="operations_by_year.png",
            )
            print("   ✅ Created operations_by_year.png")

            # Monthly operations chart
            self.visualizer.barPlotSalesByMonth(
                pandasDataframe=df,
                xColName="unix_timestamp",
                yColName="average_sales",
                sSaveWithFileName="operations_by_month.png",
            )
            print("   ✅ Created operations_by_month.png")

        except Exception as e:
            print(f"❌ Error creating visualizations: {e}")
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    def generate_sample_data(self, days: int = 30):
        """
        Generate sample analytics data for demonstration.

        Args:
            days: Number of days of sample data to generate
        """

        print(f"🔧 Generating {days} days of sample analytics data...")

        # Generate sample operations
        operations = ["copy", "move", "delete", "compress", "encrypt", "duplicate_scan"]

        for day in range(days):
            date = datetime.now() - timedelta(days=days - day)

            # Generate 1-5 operations per day
            num_ops = np.random.randint(1, 6)

            for _ in range(num_ops):
                operation = np.random.choice(operations)
                file_count = np.random.randint(1, 100)
                size_mb = np.random.uniform(0.1, 500.0)
                duration = np.random.uniform(0.5, 30.0)

                # Temporarily set timestamp for sample data
                original_time = datetime.now()
                datetime.now = lambda: date + timedelta(
                    hours=np.random.randint(0, 24), minutes=np.random.randint(0, 60)
                )

                self.log_operation(operation, file_count, size_mb, duration)

                # Restore original datetime
                datetime.now = lambda: original_time

        # Generate sample tool usage
        tools = [
            "FileFinderWindow",
            "SizeAnalyzerGUI",
            "DuplicateFinderApp",
            "EnAndDecryptGUI",
            "SecureDeleteGUI",
            "PDFToolsWidget",
            "NetworkConnectivityGUI",
        ]

        for day in range(days):
            date = datetime.now() - timedelta(days=days - day)

            # Generate 2-8 tool uses per day
            num_uses = np.random.randint(2, 9)

            for _ in range(num_uses):
                tool = np.random.choice(tools)
                success = np.random.random() > 0.1  # 90% success rate
                exec_time = np.random.uniform(0.1, 10.0)

                # Temporarily set timestamp for sample data
                original_time = datetime.now()
                datetime.now = lambda: date + timedelta(
                    hours=np.random.randint(0, 24), minutes=np.random.randint(0, 60)
                )

                self.log_tool_usage(tool, success, exec_time)

                # Restore original datetime
                datetime.now = lambda: original_time

        print(f"   ✅ Generated sample data saved to {self.data_dir}")

    def print_analytics_summary(self):
        """Print a summary of available analytics data."""

        print("\n📈 RFU Analytics Summary")
        print("=" * 30)

        # Operations summary
        ops_df = self.get_operations_dataframe()
        if ops_df is not None:
            print(f"📁 Operations logged: {len(ops_df)}")
            print(
                f"   - Date range: {ops_df['timestamp'].min().date()} to {ops_df['timestamp'].max().date()}"
            )
            print(f"   - Total files processed: {ops_df['file_count'].sum():,}")
            print(f"   - Total data processed: {ops_df['size_mb'].sum():.1f} MB")
            print(
                f"   - Most common operation: {ops_df['operation_type'].mode().iloc[0]}"
            )
        else:
            print("📁 No operations data available")

        # Tool usage summary
        tool_df = self.get_tool_usage_dataframe()
        if tool_df is not None:
            print(f"\n🔧 Tool usage logged: {len(tool_df)}")
            print(f"   - Success rate: {tool_df['success'].mean():.1%}")
            print(
                f"   - Average execution time: {tool_df['execution_time'].mean():.2f} seconds"
            )
            print(f"   - Most used tool: {tool_df['tool_name'].mode().iloc[0]}")
        else:
            print("\n🔧 No tool usage data available")


def main():
    """Main demonstration function."""

    print("🚀 RFU Analytics with PyVisualizer Integration")
    print("=" * 50)

    # Initialize analytics system
    analytics = RFUAnalytics()

    # Generate sample data if none exists
    if not analytics.operations_log.exists():
        analytics.generate_sample_data(30)

    # Print summary
    analytics.print_analytics_summary()

    # Create visualizations
    if PYVISUALIZER_AVAILABLE:
        print("\n📊 Creating visualizations...")
        analytics.create_operations_visualizations()
        print("   ✅ Visualizations saved to 'reports' directory")
    else:
        print("\n⚠️  PyVisualizer not available - skipping visualizations")

    print(f"\n💡 Integration Tips:")
    print("   1. Add analytics.log_operation() calls to your file operation tools")
    print("   2. Add analytics.log_tool_usage() calls to your tool launchers")
    print("   3. Create a menu item for 'Generate Analytics Report'")
    print("   4. Set up automatic daily/weekly report generation")


if __name__ == "__main__":
    main()
