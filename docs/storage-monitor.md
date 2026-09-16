# Storage Monitor

Open **Storage Monitor** from the hub's Tools catalogue. It opens an independent,
resizable window; **Always on top** keeps it above other windows. Smaller windows
scroll their contents rather than clipping controls.

- **Drive or network path:** choose a mounted local volume or mapped/mounted
  network share. **Add path…** accepts another local folder or an accessible
  network path, including Windows UNC paths. The tool does not discover arbitrary
  servers or mount/authenticate shares. Refresh picks up mounted drives.
- **Capacity:** total, used and free bytes, formatted as binary units (GiB, etc.).
  Used percentage is used / total. Filesystem-reserved space can make used + free
  smaller than total. Offline/inaccessible paths show an unavailable state.
- **Activity:** current read/write bytes per second, highest observed rates during
  this window's lifetime, and a graph of recent samples. Rates are calculated from
  counter differences and elapsed monotonic time, not cumulative byte totals.
  Missing or reset counters establish a new baseline without a false spike.
- **Activity source:** Linux device paths are matched exactly when possible.
  Otherwise select an operating-system device explicitly. Its counters can cover
  several volumes; they are not attributed to an unrelated selected path. Other
  platforms may require manual activity-source selection. Most network shares do
  not expose per-share activity through these counters, so no speed is invented.
  Observed peaks are not rated maximum hardware or network throughput.

Polling is read-only and approximately once per second. A separate process isolates
mount/capacity queries; a five-second timeout prevents an unavailable network path
from blocking the GUI. Closing stops polling and terminates its query process.

## Optional benchmark

Enable **Enable optional speed benchmark**, then choose **Run 128 MiB benchmark**.
The button requires a writable selected directory and at least 192 MiB free.
Confirmation identifies the target before any test data is written.

The worker creates a uniquely named `.rfu-benchmark-*` file, writes 128 MiB, flushes
it, reads it back, then removes it. Existing files are not modified. Cancellation
is checked between I/O calls and cleans up the file; an in-progress operating-system
I/O call must return first. As with any temporary file, a process crash or lost
network connection during cleanup can leave a test file behind.

Benchmark results are separate from live activity peaks. Reads may come from a
cache, and a flush does not establish a device's manufacturer-rated maximum.
Results measure this filesystem/path under the current workload. Benchmarking
runs off the UI thread and is disabled by default.

## Verification

`tests/harmonization/test_storage_monitor.py` covers rates, reset/missing counters,
network discovery, unavailable capacity, benchmark success/cancellation/error
cleanup, confirmation, worker results, toggles, resizing, stale selection data,
probe timeouts and a real probe/close lifecycle. The inventory suite also covers
launch, health, degradation/retry, retained state and Return to Hub.

Linux Qt was exercised locally. Native Windows/macOS and a live remote network
share were not available for this local run; platform jobs are configured in CI.
