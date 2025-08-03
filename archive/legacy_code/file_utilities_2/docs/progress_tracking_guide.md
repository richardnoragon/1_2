# Progress Tracking System Documentation

## Overview

The File Utilities 2 checksum system includes a comprehensive real-time progress tracking system that provides detailed feedback during checksum calculations and verifications. This system is designed to enhance user experience by providing:

- Real-time percentage completion
- Detailed status messages
- Milestone tracking for different operation phases
- Time estimates for completion
- Cancellation support for long-running operations

## Architecture

### Core Components

#### 1. ChecksumLogic (Core Engine)
Located in `file_utilities_2/core/check_sum.py`

**Enhanced Signals:**
- `progress_percentage(int)` - Emits percentage completion (0-100)
- `progress_message(str)` - Emits detailed status messages
- `milestone_reached(str, int)` - Emits milestone name and percentage
- `time_estimate(str)` - Emits estimated time remaining
- `progress_updated(int, int)` - Emits current/total bytes processed

**Key Features:**
- Byte-level progress tracking for file operations
- Automatic time estimation based on processing rate
- Milestone reporting for operation phases
- Thread-safe cancellation support

#### 2. Enhanced GUI Components

##### ChecksumWindow (Standardized GUI)
Located in `file_utilities_2/gui/check_sum_standardized.py`

**Progress UI Elements:**
- Progress bar with percentage display
- Real-time status messages
- Time estimate labels
- Cancel button for operation termination

##### ChecksumGUI (Legacy GUI)
Located in `file_utilities_2/gui/check_sum_gui.py`

**Enhanced with:**
- Multiple progress signal connections
- Status bar integration
- Progress widget updates

## Usage Examples

### Basic Progress Tracking

```python
from file_utilities_2.core.check_sum import ChecksumLogic
from PyQt5.QtCore import QThread

# Create checksum logic instance
checksummer = ChecksumLogic(
    target_path="/path/to/file.txt",
    algorithm="sha256",
    mode="calculate_file"
)

# Connect progress signals
checksummer.progress_percentage.connect(update_progress_bar)
checksummer.progress_message.connect(update_status_label)
checksummer.milestone_reached.connect(log_milestone)
checksummer.time_estimate.connect(update_eta_display)

# Run in thread
thread = QThread()
checksummer.moveToThread(thread)
thread.started.connect(checksummer.run)
thread.start()
```

### GUI Integration

```python
# In your GUI class
def _connect_thread_signals(self):
    """Connect enhanced thread signals."""
    self.checksum_thread.progress_percentage.connect(
        self.progress_bar.setValue
    )
    self.checksum_thread.progress_message.connect(
        self.progress_message.setText
    )
    self.checksum_thread.milestone_reached.connect(
        self._on_milestone_reached
    )
    self.checksum_thread.time_estimate.connect(
        self.time_estimate_label.setText
    )

def _on_milestone_reached(self, milestone, percentage):
    """Handle milestone updates."""
    self.status_bar.showMessage(f"{milestone} ({percentage}%)")
```

## Progress Tracking Phases

### File Checksum Calculation

1. **Initialization (0-10%)**
   - File validation
   - Size calculation
   - Algorithm setup

2. **Reading and Processing (10-95%)**
   - Byte-by-byte file reading
   - Hash algorithm updates
   - Real-time progress updates

3. **Finalization (95-100%)**
   - Final hash calculation
   - Result formatting
   - Cleanup operations

### Directory Operations

1. **Directory Scanning (0-20%)**
   - File enumeration
   - Path validation
   - Size calculation

2. **File Processing (20-90%)**
   - Individual file checksums
   - Progress aggregation
   - Error handling

3. **Result Compilation (90-100%)**
   - Result formatting
   - Final validation
   - Output generation

## Cancellation Support

### Implementation

```python
# In ChecksumLogic
def stop(self):
    """Stop the current operation."""
    self._is_running = False
    self.progress_message.emit("Operation cancelled by user")

# In GUI
def cancel_operation(self):
    """Cancel the current operation."""
    if self.checksum_thread and self.checksum_thread.isRunning():
        self.checksum_thread.cancel()
        self.status_bar.showMessage("Cancelling operation...", 2000)
```

### Thread Safety

- All progress updates are thread-safe using Qt signals
- Cancellation checks are performed at regular intervals
- No blocking operations in GUI thread

## Performance Considerations

### Update Frequency

- Progress updates are throttled to prevent GUI overwhelming
- Updates occur every 0.1 seconds or at significant milestones
- Byte-level tracking with configurable chunk sizes

### Memory Efficiency

- Streaming file processing with 8KB chunks
- Minimal memory footprint for large files
- Efficient signal/slot connections

## Error Handling

### Progress During Errors

- Error states are reported through progress system
- Partial progress is preserved on errors
- User-friendly error messages with context

### Recovery Mechanisms

- Graceful degradation on signal connection failures
- Fallback to basic progress reporting
- Automatic cleanup on operation termination

## Testing

### Unit Tests

Located in `file_utilities_2/tests/test_checksum.py`

**Test Coverage:**
- Progress callback functionality
- Milestone reporting accuracy
- Time estimation algorithms
- Cancellation behavior

### Integration Tests

**GUI Testing:**
- Signal/slot connections
- UI responsiveness during operations
- Cancel button functionality
- Progress display accuracy

## Best Practices

### For Developers

1. **Always connect error signals** before starting operations
2. **Implement cancellation support** for long-running operations
3. **Use throttled updates** to prevent GUI freezing
4. **Provide meaningful milestone names** for user clarity

### For Users

1. **Monitor progress messages** for operation details
2. **Use cancel button** for unwanted long operations
3. **Check time estimates** for planning purposes
4. **Review milestone updates** for operation phases

## Troubleshooting

### Common Issues

1. **Progress not updating**
   - Check signal connections
   - Verify thread setup
   - Ensure GUI event loop is running

2. **Inaccurate time estimates**
   - File size variations
   - System performance changes
   - Network storage delays

3. **Cancel not working**
   - Thread state verification
   - Signal connection issues
   - Operation already completed

### Debug Information

Enable debug logging to track:
- Signal emission frequency
- Thread state changes
- Progress calculation accuracy
- Error propagation paths

## Future Enhancements

### Planned Features

1. **Batch Operation Progress**
   - Multi-file progress aggregation
   - Individual file status tracking
   - Overall completion estimates

2. **Advanced Time Estimation**
   - Historical performance data
   - Adaptive algorithms
   - System load consideration

3. **Progress Persistence**
   - Resume interrupted operations
   - Progress state saving
   - Recovery mechanisms

### API Extensions

1. **Custom Progress Callbacks**
   - User-defined progress handlers
   - External system integration
   - Custom milestone definitions

2. **Progress Analytics**
   - Performance metrics collection
   - Operation timing analysis
   - Efficiency reporting