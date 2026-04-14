# KEY_ACTIONS — Network

**Tool:** Network (Network Diagnostics)  
**Source:** `src/tools/network/gui.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Connectivity Test / Ping | `Tab` to target input field → type host → `Tab` to "Test Connectivity" button → `Enter` | No — ICMP/TCP probe; read-only |
| 2 | Port Scan | `Tab` to target input → type host → `Tab` to scan type `QComboBox` → arrow keys → `Tab` to "Port Scan" button → `Enter` | No — probes target ports; read-only (external host may log the probe) |
| 3 | Select Scan Type | `Tab` to scan type `QComboBox` → arrow keys (TCP Connect, UDP, etc.) | No — configuration only |
| 4 | Bandwidth Monitor | `Tab` to "Bandwidth Monitor" tab → `Tab` to "Start" button → `Enter` to begin monitoring | No — observes network traffic counters; read-only |
| 5 | WiFi Scan | `Tab` to "WiFi" tab → `Tab` to "Scan" button → `Enter` | No — lists available wireless networks; read-only |
| 6 | Network Discovery | `Tab` to "Discovery" tab → `Tab` to "Discover" button → `Enter` | No — ARP/ping sweep; read-only for local host |
| 7 | LAN File Transfer — Send | `Tab` to "LAN Transfer" tab → `Tab` to "Select File" → `Enter` → `Tab` to "Send" → `Enter` | Possible — transfers file over local network; file is read locally and written on remote |
| 8 | Stop Active Scan | `Tab` to "Stop" button → `Enter` (available during active operation) | No — cancels in-progress scan |

### Notes

- Action 7 (LAN File Transfer) is classified as "Possible" side effects — the local file is only read; the remote end has a write side effect. Confirmation should be required before initiating a transfer.
- Port scanning (Action 2) may be logged by the scanned host; ensure users are aware.
