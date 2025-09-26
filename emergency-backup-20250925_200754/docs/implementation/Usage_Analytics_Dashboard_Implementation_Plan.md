# Usage Analytics Dashboard - Comprehensive Implementation Plan

## Overview

This document provides a detailed implementation plan for the `UsageAnalyticsDashboard` component that will integrate with the existing Richard's File Utilities (RFU) application as a new tab in the main window. The dashboard will leverage the current SQLite database infrastructure and provide comprehensive usage insights through interactive data visualizations.

## 1. Database Schema Extensions ✅

### Current Database Analysis
The existing database already provides excellent foundations:
- `file_history` table for file access tracking
- `app_logs` table for application events  
- `app_settings` table for configuration
- Tool usage tracking capabilities in main window

### Required Additional Tables

```sql
-- User Sessions Table
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    tools_used INTEGER DEFAULT 0,
    files_accessed INTEGER DEFAULT 0,
    operations_count INTEGER DEFAULT 0,
    session_metadata TEXT -- JSON
);

-- Tool Usage Analytics (Enhanced)
CREATE TABLE IF NOT EXISTS tool_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    session_id TEXT,
    user_id TEXT,
    usage_count INTEGER DEFAULT 1,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    total_execution_time_ms INTEGER DEFAULT 0,
    first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performance_metrics TEXT, -- JSON
    UNIQUE(tool_name, operation_type)
);

-- Feature Adoption Metrics
CREATE TABLE IF NOT EXISTS feature_adoption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_name TEXT NOT NULL,
    category TEXT NOT NULL,
    first_adoption TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_users INTEGER DEFAULT 1,
    usage_frequency TEXT, -- daily, weekly, monthly
    adoption_rate REAL DEFAULT 0.0,
    retention_rate REAL DEFAULT 0.0,
    metadata TEXT -- JSON
);

-- Performance Metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL, -- cpu, memory, disk, network
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    context TEXT, -- tool_name, operation
    session_id TEXT,
    metadata TEXT -- JSON
);

-- User Behavior Patterns
CREATE TABLE IF NOT EXISTS user_behavior_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL, -- workflow, sequence, preference
    pattern_data TEXT NOT NULL, -- JSON
    frequency INTEGER DEFAULT 1,
    confidence_score REAL DEFAULT 0.0,
    first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dashboard Reports
CREATE TABLE IF NOT EXISTS dashboard_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_name TEXT NOT NULL,
    report_type TEXT NOT NULL, -- scheduled, manual, export
    parameters TEXT, -- JSON
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT,
    format TEXT, -- pdf, csv, excel, md
    status TEXT DEFAULT 'completed'
);

-- Directory History (extends existing tracking)
CREATE TABLE IF NOT EXISTS directory_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directory_path TEXT NOT NULL,
    tool_name TEXT,
    access_count INTEGER DEFAULT 1,
    first_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(directory_path)
);
```

### Database Indexes for Performance

```sql
-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_tool_usage_tool_name ON tool_usage(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_usage_timestamp ON tool_usage(last_used DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_feature_adoption_category ON feature_adoption(category);
CREATE INDEX IF NOT EXISTS idx_directory_history_accessed ON directory_history(last_accessed DESC);
```

## 2. Dashboard Architecture & Component Structure

### Directory Structure
```
src/rfu/gui/analytics/
├── __init__.py
├── usage_analytics_dashboard.py          # Main dashboard widget
├── components/
│   ├── __init__.py
│   ├── chart_widgets.py                  # Chart components
│   ├── heatmap_widget.py                 # Interactive heatmaps
│   ├── metrics_cards.py                  # KPI metric cards
│   ├── filter_panel.py                   # Date/user filters
│   ├── export_dialog.py                  # Export functionality
│   └── drill_down_dialog.py              # Detailed views
├── data/
│   ├── __init__.py
│   ├── analytics_service.py              # Data service layer
│   ├── query_builder.py                  # SQL query builder
│   ├── data_aggregator.py                # Data aggregation
│   └── cache_manager.py                  # Performance caching
├── visualization/
│   ├── __init__.py
│   ├── chart_factory.py                  # Chart creation
│   ├── color_schemes.py                  # Theming
│   └── interactive_plots.py              # Interactive features
├── export/
│   ├── __init__.py
│   ├── pdf_exporter.py                   # PDF generation
│   ├── excel_exporter.py                 # Excel export
│   ├── csv_exporter.py                   # CSV export
│   └── markdown_exporter.py              # Markdown export
└── utils/
    ├── __init__.py
    ├── date_utils.py                     # Date handling
    ├── user_segmentation.py              # User analysis
    └── performance_monitor.py            # Real-time monitoring
```

### Core Architecture Components

#### Main Dashboard Widget
```python
class UsageAnalyticsDashboard(QWidget):
    """
    Main analytics dashboard widget that integrates with RFU main window.
    Provides comprehensive usage insights through interactive visualizations.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = get_database_manager()
        self.analytics_service = AnalyticsService(self.db_manager)
        self.cache_manager = CacheManager()
        self.real_time_updater = RealTimeUpdater()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the dashboard UI layout"""
        # Top metrics cards row (4 KPI cards)
        # Chart grid (2x2 or 3x2 layout)
        # Bottom heatmap section
        # Side filter panel
        # Export controls
        
    def setup_connections(self):
        """Setup signal/slot connections"""
        # Real-time update connections
        # Filter change connections
        # Export action connections
```

## 3. Data Visualization Library Integration Strategy

### Primary Technology Stack
- **matplotlib**: Core charting library (already in requirements.txt)
- **matplotlib.backends.backend_qt5agg**: PyQt5 integration
- **numpy**: Data processing (already available)
- **pandas**: Data manipulation (already available)

### Secondary Libraries (Optional Enhancements)
- **seaborn**: Statistical visualizations
- **PyQtGraph**: Real-time performance monitoring
- **plotly**: Advanced interactive features (future enhancement)

### Chart Types Implementation

```python
class ChartFactory:
    """Factory for creating different chart types"""
    
    @staticmethod
    def create_line_chart(data, title, **kwargs):
        """Usage trends over time"""
        
    @staticmethod
    def create_bar_chart(data, title, **kwargs):
        """Tool usage comparisons"""
        
    @staticmethod
    def create_pie_chart(data, title, **kwargs):
        """Feature adoption distribution"""
        
    @staticmethod
    def create_area_chart(data, title, **kwargs):
        """Cumulative usage data"""
        
    @staticmethod
    def create_heatmap(data, title, **kwargs):
        """User activity patterns"""
        
    @staticmethod
    def create_scatter_plot(data, title, **kwargs):
        """Performance correlations"""
```

## 4. Core Analytics Data Models & Services

### Analytics Service Layer
```python
class AnalyticsService:
    """Core service for analytics data processing"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.cache_manager = CacheManager()
        self.query_builder = QueryBuilder()
        
    def get_usage_trends(self, date_range, granularity='daily'):
        """Get usage trends with caching"""
        cache_key = f"usage_trends_{date_range}_{granularity}"
        cached_data = self.cache_manager.get_cached_data(cache_key)
        if cached_data:
            return cached_data
            
        query = self.query_builder.build_usage_trends_query(date_range, granularity)
        data = self.db_manager.execute_query(query)
        
        self.cache_manager.cache_data(cache_key, data)
        return data
        
    def get_tool_popularity(self, date_range):
        """Get most/least used tools"""
        
    def get_user_segments(self):
        """Analyze user behavior patterns"""
        
    def get_performance_metrics(self, date_range):
        """Get system performance data"""
        
    def get_feature_adoption_rates(self):
        """Calculate feature adoption metrics"""
        
    def get_session_analytics(self, date_range):
        """Get session-based analytics"""
        
    def get_file_access_patterns(self, date_range):
        """Analyze file access patterns"""
```

### Data Aggregation Service
```python
class DataAggregator:
    """Handles data aggregation and statistical calculations"""
    
    def aggregate_by_time_period(self, data, period='daily'):
        """Aggregate data by time periods"""
        
    def calculate_growth_rates(self, data):
        """Calculate period-over-period growth"""
        
    def identify_usage_patterns(self, data):
        """Identify recurring usage patterns"""
        
    def calculate_user_segments(self, data):
        """Segment users based on behavior"""
```

## 5. Dashboard Widget Components

### Metrics Cards Component
```python
class MetricsCards(QWidget):
    """KPI metrics display cards"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_cards()
        
    def setup_cards(self):
        """Setup 4 main KPI cards"""
        # Total Sessions
        # Active Tools
        # Files Processed
        # System Performance
        
    def update_metrics(self, metrics_data):
        """Update card values with animation"""
```

### Chart Widgets Component
```python
class ChartWidget(QWidget):
    """Individual chart widget with matplotlib integration"""
    
    def __init__(self, chart_type, parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.setup_ui()
        
    def update_chart(self, data, title, **kwargs):
        """Update chart with new data"""
        
    def export_chart(self, filename, format='png'):
        """Export chart to file"""
```

### Interactive Heatmap Widget
```python
class HeatmapWidget(QWidget):
    """Interactive heatmap for user activity patterns"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_heatmap()
        
    def update_heatmap(self, activity_data):
        """Update heatmap with activity data"""
        # Time of day vs. day of week
        # Tool usage vs. time periods
        # Feature usage hotspots
```

### Filter Panel Component
```python
class FilterPanel(QWidget):
    """Dashboard filter controls"""
    
    filter_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_filters()
        
    def setup_filters(self):
        """Setup filter controls"""
        # Date range picker
        # User segment selector
        # Tool category filter
        # Performance metric filter
        
    def get_current_filters(self):
        """Get current filter values"""
        return {
            'date_range': self.date_range_picker.get_range(),
            'user_segment': self.user_segment_combo.currentText(),
            'tool_categories': self.get_selected_categories(),
            'metrics': self.get_selected_metrics()
        }
```

## 6. User Segmentation & Role-Based Access Control

### User Role System
```python
from enum import Enum

class UserRole(Enum):
    REGULAR_USER = "regular"
    POWER_USER = "power"
    ADMINISTRATOR = "admin"

class AccessControlManager:
    """Manages role-based access to dashboard features"""
    
    def __init__(self):
        self.permissions = self._define_permissions()
        
    def _define_permissions(self):
        return {
            UserRole.REGULAR_USER: {
                'view_personal_stats': True,
                'view_org_stats': False,
                'export_data': True,
                'schedule_reports': False,
                'view_performance_metrics': False,
                'access_user_behavior': False
            },
            UserRole.POWER_USER: {
                'view_personal_stats': True,
                'view_org_stats': True,
                'export_data': True,
                'schedule_reports': True,
                'view_performance_metrics': True,
                'access_user_behavior': False
            },
            UserRole.ADMINISTRATOR: {
                'view_personal_stats': True,
                'view_org_stats': True,
                'export_data': True,
                'schedule_reports': True,
                'view_performance_metrics': True,
                'access_user_behavior': True,
                'user_management': True,
                'system_configuration': True
            }
        }
        
    def get_user_permissions(self, user_role):
        """Get permissions for a user role"""
        return self.permissions.get(user_role, {})
        
    def can_access_feature(self, user_role, feature):
        """Check if user can access specific feature"""
        permissions = self.get_user_permissions(user_role)
        return permissions.get(feature, False)
```

### User Segmentation Analysis
```python
class UserSegmentationAnalyzer:
    """Analyzes user behavior to create segments"""
    
    def __init__(self, analytics_service):
        self.analytics_service = analytics_service
        
    def segment_by_usage_frequency(self, data):
        """Segment users by usage frequency"""
        # Heavy users (daily)
        # Regular users (weekly)
        # Occasional users (monthly)
        # Inactive users
        
    def segment_by_tool_preference(self, data):
        """Segment users by preferred tools"""
        # File management focused
        # Security focused
        # Analysis focused
        # Multi-tool users
        
    def segment_by_session_patterns(self, data):
        """Segment users by session behavior"""
        # Long session users
        # Frequent short sessions
        # Weekend users
        # Business hours users
```

## 7. Real-Time Data Update Mechanisms

### Real-Time Updater
```python
class RealTimeUpdater(QObject):
    """Handles real-time data updates for the dashboard"""
    
    data_updated = pyqtSignal(dict)
    performance_updated = pyqtSignal(dict)
    
    def __init__(self, analytics_service):
        super().__init__()
        self.analytics_service = analytics_service
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.update_interval = 30000  # 30 seconds
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance)
        self.performance_interval = 5000  # 5 seconds
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.timer.start(self.update_interval)
        self.performance_timer.start(self.performance_interval)
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.timer.stop()
        self.performance_timer.stop()
        
    def update_data(self):
        """Update dashboard data"""
        try:
            # Fetch latest usage metrics
            latest_data = self.analytics_service.get_latest_metrics()
            self.data_updated.emit(latest_data)
        except Exception as e:
            logging.error(f"Real-time data update failed: {e}")
            
    def update_performance(self):
        """Update performance metrics"""
        try:
            # Fetch current performance data
            perf_data = self.analytics_service.get_current_performance()
            self.performance_updated.emit(perf_data)
        except Exception as e:
            logging.error(f"Performance update failed: {e}")
```

## 8. Export Functionality Implementation

### Export Manager
```python
class ExportManager:
    """Manages data export in multiple formats"""
    
    def __init__(self, analytics_service):
        self.analytics_service = analytics_service
        self.exporters = {
            'pdf': PDFExporter(),
            'excel': ExcelExporter(),
            'csv': CSVExporter(),
            'markdown': MarkdownExporter()
        }
        
    def export_dashboard(self, format_type, date_range, filters, output_path):
        """Export dashboard data in specified format"""
        try:
            # Gather all dashboard data
            data = self._gather_export_data(date_range, filters)
            
            # Use appropriate exporter
            exporter = self.exporters.get(format_type)
            if not exporter:
                raise ValueError(f"Unsupported export format: {format_type}")
                
            return exporter.export(data, output_path)
            
        except Exception as e:
            logging.error(f"Export failed: {e}")
            raise
            
    def _gather_export_data(self, date_range, filters):
        """Gather all data needed for export"""
        return {
            'usage_trends': self.analytics_service.get_usage_trends(date_range),
            'tool_popularity': self.analytics_service.get_tool_popularity(date_range),
            'performance_metrics': self.analytics_service.get_performance_metrics(date_range),
            'session_analytics': self.analytics_service.get_session_analytics(date_range),
            'file_access_patterns': self.analytics_service.get_file_access_patterns(date_range),
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'date_range': date_range,
                'filters': filters
            }
        }
```

### PDF Exporter
```python
class PDFExporter:
    """Export dashboard data to PDF format"""
    
    def export(self, data, output_path):
        """Create comprehensive PDF report"""
        # Use reportlab or matplotlib for PDF generation
        # Include charts, tables, and summary statistics
        # Professional formatting with headers/footers
```

### Excel Exporter
```python
class ExcelExporter:
    """Export dashboard data to Excel format"""
    
    def export(self, data, output_path):
        """Create Excel workbook with multiple sheets"""
        # Use openpyxl (already in requirements)
        # Multiple sheets for different data types
        # Embedded charts and formatting
        # Data validation and formulas
```

## 9. Integration with Main Window Tab System

### Main Window Integration
```python
# Integration point in main.py init_ui() method (around line 644)

def init_ui(self):
    """Initialize the user interface."""
    # ... existing code ...
    
    # Add Analytics Dashboard Tab
    analytics_tab = self.create_analytics_dashboard_tab()
    tab_widget.addTab(analytics_tab, "📊 Analytics")
    
    # Store reference for later access
    self.analytics_dashboard = analytics_tab
    
    # ... rest of existing code ...

def create_analytics_dashboard_tab(self):
    """Create the usage analytics dashboard tab."""
    try:
        from src.rfu.gui.analytics.usage_analytics_dashboard import UsageAnalyticsDashboard
        
        # Create dashboard with database integration
        dashboard = UsageAnalyticsDashboard(self)
        dashboard.set_database_manager(self.db_manager)
        
        # Connect to existing tracking systems
        if hasattr(self, 'track_tool_usage'):
            dashboard.tool_accessed.connect(
                lambda tool_name: self.track_tool_usage(tool_name, "analytics_view")
            )
            
        return dashboard
        
    except ImportError as e:
        self.logger.error(f"Failed to import UsageAnalyticsDashboard: {e}")
        return self.create_placeholder_tab("Analytics Dashboard", str(e))
        
def create_placeholder_tab(self, tab_name, error_message):
    """Create placeholder tab when component is not available"""
    placeholder = QWidget()
    layout = QVBoxLayout(placeholder)
    
    label = QLabel(f"{tab_name} is not available")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("font-size: 16px; color: #666;")
    
    error_label = QLabel(f"Error: {error_message}")
    error_label.setAlignment(Qt.AlignCenter)
    error_label.setStyleSheet("font-size: 12px; color: #999;")
    error_label.setWordWrap(True)
    
    layout.addWidget(label)
    layout.addWidget(error_label)
    
    return placeholder

def open_analytics_dashboard(self):
    """Open Analytics Dashboard tool."""
    self.track_tool_usage("Analytics Dashboard", "open")
    
    # Switch to analytics tab
    if hasattr(self, 'tab_widget'):
        analytics_tab_index = self.find_tab_by_name("📊 Analytics")
        if analytics_tab_index >= 0:
            self.tab_widget.setCurrentIndex(analytics_tab_index)
            
def find_tab_by_name(self, tab_name):
    """Find tab index by name"""
    if hasattr(self, 'tab_widget'):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == tab_name:
                return i
    return -1
```

### Menu Integration
```python
# Add to _add_tools_menu method in main.py

def _add_tools_menu(self, menubar):
    """Add tools-specific menu items."""
    if hasattr(self.menu_manager, 'tools_menu'):
        tools_menu = self.menu_manager.tools_menu
        
        # ... existing code ...
        
        # Analytics Tools submenu
        analytics_tools_menu = tools_menu.addMenu('📊 &Analytics')
        analytics_tools_menu.addAction('Usage Dashboard').triggered.connect(self.open_analytics_dashboard)
        analytics_tools_menu.addAction('Export Analytics...').triggered.connect(self.export_analytics_data)
        analytics_tools_menu.addAction('Schedule Reports...').triggered.connect(self.schedule_analytics_reports)
```

## 10. Performance Optimization & Caching

### Cache Manager
```python
class CacheManager:
    """Manages data caching for performance optimization"""
    
    def __init__(self):
        self.memory_cache = {}
        self.cache_ttl = 300  # 5 minutes default
        self.max_cache_size = 100  # Maximum cached items
        
    def get_cached_data(self, key):
        """Retrieve cached data if valid"""
        if key in self.memory_cache:
            cached_item = self.memory_cache[key]
            if self._is_cache_valid(cached_item):
                return cached_item['data']
            else:
                del self.memory_cache[key]
        return None
        
    def cache_data(self, key, data, ttl=None):
        """Cache data with TTL"""
        if ttl is None:
            ttl = self.cache_ttl
            
        # Implement LRU eviction if cache is full
        if len(self.memory_cache) >= self.max_cache_size:
            self._evict_oldest()
            
        self.memory_cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
    def invalidate_cache(self, pattern=None):
        """Clear cache entries matching pattern"""
        if pattern is None:
            self.memory_cache.clear()
        else:
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
                
    def _is_cache_valid(self, cached_item):
        """Check if cached item is still valid"""
        age = time.time() - cached_item['timestamp']
        return age < cached_item['ttl']
        
    def _evict_oldest(self):
        """Remove oldest cache entry"""
        if self.memory_cache:
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k]['timestamp'])
            del self.memory_cache[oldest_key]
```

### Performance Monitoring
```python
class PerformanceMonitor:
    """Monitors dashboard performance and optimization"""
    
    def __init__(self):
        self.query_times = {}
        self.render_times = {}
        
    def measure_query_time(self, query_name):
        """Decorator to measure query execution time"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                self.query_times[query_name] = execution_time
                if execution_time > 1.0:  # Log slow queries
                    logging.warning(f"Slow query detected: {query_name} took {execution_time:.2f}s")
                    
                return result
            return wrapper
        return decorator
        
    def get_performance_report(self):
        """Generate performance report"""
        return {
            'average_query_time': sum(self.query_times.values()) / len(self.query_times) if self.query_times else 0,
            'slowest_queries': sorted(self.query_times.items(), key=lambda x: x[1], reverse=True)[:5],
            'total_queries': len(self.query_times)
        }
```

## 11. Automated Report Scheduling

### Report Scheduler
```python
class ReportScheduler:
    """Handles automated report generation and scheduling"""
    
    def __init__(self, analytics_service, export_manager):
        self.analytics_service = analytics_service
        self.export_manager = export_manager
        self.scheduler = QTimer()
        self.scheduled_reports = []
        self.scheduler.timeout.connect(self.check_scheduled_reports)
        self.scheduler.start(60000)  # Check every minute
        
    def schedule_report(self, report_config):
        """Schedule a new report"""
        report = {
            'id': str(uuid.uuid4()),
            'name': report_config['name'],
            'frequency': report_config['frequency'],  # daily, weekly, monthly
            'format': report_config['format'],
            'filters': report_config.get('filters', {}),
            'output_path': report_config['output_path'],
            'next_run': self._calculate_next_run(report_config['frequency']),
            'enabled': True
        }
        
        self.scheduled_reports.append(report)
        self._save_scheduled_reports()
        
    def check_scheduled_reports(self):
        """Check and execute due reports"""
        current_time = datetime.now()
        
        for report in self.scheduled_reports:
            if report['enabled'] and current_time >= report['next_run']:
                try:
                    self._execute_report(report)
                    report['next_run'] = self._calculate_next_run(report['frequency'])
                    self._save_scheduled_reports()
                except Exception as e:
                    logging.error(f"Failed to execute scheduled report {report['name']}: {e}")
                    
    def _execute_report(self, report):
        """Execute a scheduled report"""
        # Calculate date range based on frequency
        date_range = self._get_report_date_range(report['frequency'])
        
        # Generate report
        output_file = self.export_manager.export_dashboard(
            report['format'],
            date_range,
            report['filters'],
            report['output_path']
        )
        
        # Log successful generation
        logging.info(f"Generated scheduled report: {report['name']} -> {output_file}")
        
        # Store report record in database
        self._store_report_record(report, output_file)
        
    def _calculate_next_run(self, frequency):
        """Calculate next run time based on frequency"""
        now = datetime.now()
        if frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(weeks=1)
        elif frequency == 'monthly':
            return now + timedelta(days=30)
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")
```

## 12. Accessibility & Mobile Responsiveness

### Accessibility Features
```python
class AccessibilityManager:
    """Manages accessibility features for the dashboard"""
    
    def __init__(self, dashboard_widget):
        self.dashboard = dashboard_widget
        self.setup_accessibility()
        
    def setup_accessibility(self):
        """Setup accessibility features"""
        # Keyboard navigation
        self._setup_keyboard_navigation()
        
        # Screen reader support
        self._setup_screen_reader_support()
        
        # High contrast mode
        self._setup_high_contrast_mode()
        
        # Font scaling
        self._setup_font_scaling()
        
    def _setup_keyboard_navigation(self):
        """Enable full keyboard navigation"""
        # Tab order for all interactive elements
        # Keyboard shortcuts for common actions
        # Focus indicators
        
    def _setup_screen_reader_support(self):
        """Add screen reader support"""
        # Proper ARIA labels
        # Descriptive text for charts
        # Status announcements
        
    def _setup_high_contrast_mode(self):
        """Implement high contrast theme"""
        # Alternative color schemes
        # Increased contrast ratios
        # Clear visual boundaries
        
    def _setup_font_scaling(self):
        """Enable configurable font scaling"""
        # Scalable font sizes
        # Responsive layout adjustments
        # User preference storage
```

### Responsive Layout
```python
class ResponsiveLayoutManager:
    """Manages responsive layout for different screen sizes"""
    
    def __init__(self, dashboard_widget):
        self.dashboard = dashboard_widget
        self.current_layout = 'desktop'
        self.setup_responsive_behavior()
        
    def setup_responsive_behavior(self):
        """Setup responsive layout behavior"""
        # Monitor window resize events
        self.dashboard.resizeEvent = self.handle_resize
        
    def handle_resize(self, event):
        """Handle window resize events"""
        new_size