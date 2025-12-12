# PyVisualizer Integration Guide for RFU

## Richard's File Utilities Analytics & Visualization

### ✅ Installation Status

PyVisualizer has been successfully installed and tested in your RFU project environment.

**Package Details:**

- **Name:** PyVisualizer
- **Version:** 1.0.9
- **Location:** Global Python installation
- **Dependencies:** matplotlib, pandas, seaborn, gspread, requests

---

## 🚀 Quick Start

### 1. Basic Usage

```python
from PyVisualizer.Visualizer import Visualizer
import pandas as pd

# Create visualizer
visualizer = Visualizer()

# Your data must have these columns:
# - timestamp (Unix timestamp)
# - average_sales (numeric values)

# Create yearly chart
visualizer.barPlotSalesByYear(
    pandasDataframe=your_dataframe,
    xColName='timestamp',
    yColName='average_sales',
    sSaveWithFileName='output_yearly.png'
)

# Create monthly chart
visualizer.barPlotSalesByMonth(
    pandasDataframe=your_dataframe,
    xColName='timestamp',
    yColName='average_sales',
    sSaveWithFileName='output_monthly.png'
)
```

### 2. Integration Files Created

**Demo Scripts:**

- `demo_pyvisualizer.py` - Comprehensive demonstration
- `simple_pyvisualizer_demo.py` - Simple demo with RFU data
- `src/analytics/analytics.py` - Advanced analytics system
- `src/analytics/pyvisualizer_integration.py` - PyQt5 integration

**Generated Reports:**

- `rfu_yearly_operations.png` - Yearly operations chart
- `rfu_monthly_operations.png` - Monthly operations chart
- `rfu_analytics_dashboard.png` - Comprehensive dashboard
- `reports/` directory - Additional visualizations

---

## 🔧 RFU Integration Steps

### Step 1: Add to Requirements

Add to your `requirements.txt`:

```
pyvisualizer>=1.0.9
```

### Step 2: Add Analytics Logging

In your RFU tools, add operation logging:

```python
from src.analytics.pyvisualizer_integration import RFUAnalyticsLogger

class YourRFUTool:
    def __init__(self):
        self.analytics = RFUAnalyticsLogger()

    def perform_operation(self):
        start_time = time.time()
        # ... your operation code ...
        duration = time.time() - start_time

        # Log the operation
        self.analytics.log_operation(
            tool_name="YourRFUTool",
            operation="file_processing",
            file_count=processed_files,
            size_mb=total_size,
            duration_seconds=duration,
            success=operation_succeeded
        )
```

### Step 3: Add GUI Integration

In your main hub (`src/rfu/main.py`), add analytics menu:

```python
from src.analytics.pyvisualizer_integration import integrate_with_main_hub

class MainWindow:
    def __init__(self):
        # ... existing code ...

        # Add analytics integration
        integrate_with_main_hub(self)
```

### Step 4: Create Analytics Widget

The PyQt5 widget is ready to use:

```python
from src.analytics.pyvisualizer_integration import RFUVisualizerWidget

# Create and show analytics widget
analytics_widget = RFUVisualizerWidget()
analytics_widget.show()
```

---

## 📊 What PyVisualizer Provides

### Core Functionality

1. **Bar Charts by Year** - Shows data trends over years
2. **Bar Charts by Month** - Shows seasonal patterns
3. **Data Pivot Tables** - For cross-tabular analysis

### Data Requirements

- **timestamp**: Unix timestamp column
- **average_sales**: Numeric column (can represent any metric)
- **Additional columns**: Can include any RFU-specific data

### Generated Output

- High-quality PNG charts
- Matplotlib-based visualizations
- Customizable styling via seaborn

---

## 🎯 RFU-Specific Use Cases

### 1. File Operations Analytics

Track and visualize:

- Files copied/moved/deleted over time
- Storage space processed
- Operation success rates
- Performance metrics

### 2. Tool Usage Statistics

Monitor:

- Which RFU tools are used most
- Peak usage times
- User workflow patterns
- Tool performance metrics

### 3. Duplicate Detection Reports

Visualize:

- Duplicates found over time
- Storage space saved
- Scan efficiency improvements
- File type distribution

### 4. Security Operations

Track:

- Encryption/decryption operations
- Secure delete operations
- Security tool usage patterns

---

## 🔍 Advanced Features

### Google Sheets Integration

PyVisualizer includes Google Sheets connectivity:

```python
from PyVisualizer.CommonUtilities import CommonUtilities

utils = CommonUtilities()
connection = utils.connectAndAutorizeToServiceAccount("service_account.json")
sheet = utils.read_google_sheet(connection, "sheet_name", "worksheet_name")
```

### Custom Visualizations

Extend beyond PyVisualizer's built-in charts:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Use the data from PyVisualizer with custom matplotlib code
# See the dashboard example in demo_pyvisualizer.py
```

---

## 📁 File Structure

```
your_project/
├── src/
│   └── analytics/
│       └── pyvisualizer_integration.py        # Main integration
├── data/
│   └── analytics/                             # Analytics data storage
├── reports/                                   # Generated visualizations
├── demo_pyvisualizer.py                      # Demo script
├── simple_pyvisualizer_demo.py              # Simple demo
└── requirements.txt                          # Updated with pyvisualizer
```

---

## 🎉 Testing & Validation

### Run Demonstrations

1. **Basic Demo:** `python demo_pyvisualizer.py`
2. **Simple Demo:** `python simple_pyvisualizer_demo.py`
3. **GUI Integration:** `python src/analytics/pyvisualizer_integration.py`

### Expected Outputs

- ✅ PNG visualization files generated
- ✅ No import errors
- ✅ PyQt5 analytics widget opens
- ✅ Sample data generation works

---

## 🚨 Troubleshooting

### Common Issues

**Import Error:** `ModuleNotFoundError: No module named 'pyvisualizer'`

- **Solution:** Ensure virtual environment is activated: `activate_env.bat`
- **Alternative:** Install globally: `pip install pyvisualizer`

**Missing Dependencies:** matplotlib, seaborn, pandas not found

- **Solution:** These should be in your requirements.txt already
- **Check:** Run `python -c "import matplotlib, seaborn, pandas; print('OK')"`

**Charts Not Displaying:** Plots don't show in GUI mode

- **Solution:** Set matplotlib backend: `plt.switch_backend('TkAgg')`

### Environment Notes

- PyVisualizer was installed in global Python (Python 3.13.5)
- All dependencies are available
- PyQt5 integration tested and working

---

## 🎯 Next Steps

1. **Test the Integration:** Run the demo scripts to verify everything works
2. **Add Analytics Logging:** Integrate logging calls into your existing RFU tools
3. **Customize Visualizations:** Adapt the charts for your specific metrics
4. **Add Menu Integration:** Connect the analytics widget to your main GUI
5. **Create Scheduled Reports:** Set up automatic report generation

---

## 📞 Support Resources

- **PyVisualizer GitHub:** [github.com/vishalkashyap95/PyVisualizer_Task2](https://github.com/vishalkashyap95/PyVisualizer_Task2)
- **Demo Files:** All created in your project directory
- **Integration Code:** Ready-to-use in `src/analytics/`

**Status:** ✅ PyVisualizer successfully installed and integrated with RFU!
