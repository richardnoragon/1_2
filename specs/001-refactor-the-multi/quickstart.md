# Quickstart: Multi-Pane Explorer Testing

**Feature**: Multi-Pane Explorer Hub Interface Refactor
**Date**: October 1, 2025
**Purpose**: Validate the Multi-Pane Explorer implementation against specification requirements

## Prerequisites

- RFU application installed and configured
- Python 3.8+ environment
- pytest and pytest-qt installed
- Sample test data (provided in `tests/fixtures/`)

## Test Execution Order

### Phase 1: Smoke Tests (5 minutes)

**Objective**: Verify basic functionality works

```bash
# Run quick smoke tests
pytest tests/file_explorer/ui/test_smoke.py -v

# Expected: All pass
# - Application launches
# - Multi-Pane Explorer loads with 4 panes
# - Quick-toggle button present
# - Left/right panes visible
```

**Manual Verification**:

1. Launch RFU
2. Verify Multi-Pane Explorer is default interface
3. Count panes: 1 left + 2 center + 1 right = 4 total
4. Check left pane has tabs: Bookmarks, Recent (selected), Tools
5. Check right pane has tabs: Preview (selected), Properties

---

### Phase 2: Core Functionality (15 minutes)

#### Test 1: Hub Interface Toggle

**Objective**: Verify switching between Multi-Pane and Tabbed interfaces

```bash
pytest tests/file_explorer/integration/test_hub_toggle.py -v
```

**Manual Steps**:

1. Note current directory in center pane (e.g., C:\\Projects)
2. Click quick-toggle button
3. Verify interface switches to tabbed mode
4. Click quick-toggle button again
5. Verify interface switches back to Multi-Pane Explorer
6. Verify center pane still shows C:\\Projects (context preserved)

**Expected Results**:

- Toggle takes <200ms (feels instant)
- No error messages
- File selections preserved

---

#### Test 2: Pane Count Configuration

**Objective**: Verify 1-4 pane configurations

```bash
pytest tests/file_explorer/integration/test_pane_layout_changes.py -v
```

**Manual Steps**:

1. Open pane configuration menu (View → Pane Count)
2. Select "1 Pane"
   - Verify only 1 center pane visible
   - Verify layout options disabled
3. Select "2 Panes"
   - Verify 2 center panes visible
   - Verify layout options: Horizontal, Vertical
4. Select "3 Panes"
   - Verify 3 center panes visible
   - Verify layout options: Horizontal, Vertical, Grid
5. Select "4 Panes"
   - Verify 4 center panes visible (2x2 grid by default)
   - Verify layout options: Horizontal, Vertical, Grid

**Expected Results**:

- Each pane count renders correctly
- Layout options update appropriately
- Left and right panes always visible

---

#### Test 3: Bookmark Management

**Objective**: Verify bookmark creation, display, and deletion

```bash
pytest tests/file_explorer/unit/test_bookmark_service.py -v
pytest tests/file_explorer/ui/test_bookmarks_widget.py -v
```

**Manual Steps**:

1. Navigate to C:\\Projects in a center pane
2. Right-click folder → "Bookmark this location"
3. Switch to Bookmarks tab in left pane
4. Verify "Projects" appears in bottom half (locations section)
5. Go to Tools tab in left pane
6. Right-click "Duplicate Finder" → "Bookmark this tool"
7. Switch back to Bookmarks tab
8. Verify "Duplicate Finder" appears in top half (tools section)
9. Right-click bookmarked location → "Remove bookmark"
10. Verify it disappears from list

**Expected Results**:

- Bookmarks persist across app restarts
- Tools and locations in correct sections
- Deletion works immediately

---

#### Test 4: Recent Items Tracking

**Objective**: Verify recent items are tracked and displayed

```bash
pytest tests/file_explorer/unit/test_recent_items_service.py -v
pytest tests/file_explorer/ui/test_recent_widget.py -v
```

**Manual Steps**:

1. Launch "File Finder" tool
2. Close tool
3. Switch to Recent tab in left pane
4. Verify "File Finder" in top half (recent tools)
5. Navigate to C:\\Documents in center pane
6. Navigate to D:\\Backup in center pane
7. Check Recent tab
8. Verify both paths in bottom half (recent locations)
9. Launch 10 more different tools
10. Verify oldest tool evicted (only 10 shown)

**Expected Results**:

- Most recent items at top
- Max 10 tools, 10 locations
- LRU eviction works correctly

---

#### Test 5: Preview and Properties

**Objective**: Verify right pane displays file info

```bash
pytest tests/file_explorer/ui/test_preview_widget.py -v
pytest tests/file_explorer/ui/test_properties_widget.py -v
```

**Manual Steps**:

1. Navigate to `tests/fixtures/sample_files/` in center pane
2. Select `sample.txt` file
3. Verify Preview tab shows text content
4. Switch to Properties tab
5. Verify file metadata displayed (size, modified date, permissions)
6. Select `sample.jpg` image
7. Switch to Preview tab
8. Verify image preview shown
9. Select unsupported file type (e.g., `.bin`)
10. Verify Preview tab shows "Cannot preview this file type" message

**Expected Results**:

- Text files preview content (first 100KB)
- Images scale to fit
- Unsupported types show friendly message
- Properties always show available metadata

---

### Phase 3: Edge Cases (10 minutes)

#### Test 6: Empty States

**Objective**: Verify empty state messages

```bash
pytest tests/file_explorer/integration/test_empty_states.py -v
```

**Manual Steps**:

1. Reset configuration to defaults (no bookmarks/recent items)
2. Go to Bookmarks tab
3. Verify tools section shows: "No bookmarked tools yet. Right-click a tool in the Tools tab to bookmark it."
4. Verify locations section shows: "No bookmarked locations yet. Right-click a folder in the file explorer to bookmark it."
5. Go to Recent tab
6. Verify sections show appropriate "No recent..." messages

**Expected Results**:

- Helpful, actionable messages
- No blank sections
- Clear call-to-action

---

#### Test 7: Unavailable Drive Fallback

**Objective**: Verify graceful handling of missing default drive

```bash
pytest tests/file_explorer/integration/test_fallback_behavior.py -v
```

**Manual Steps** (simulated):

1. Set default drive to E:\\ (removable USB)
2. "Eject" drive (unmount or set config to non-existent drive)
3. Restart app
4. Verify center panes default to C:\\ (system root)
5. Verify notification shown: "Drive E:\\ is unavailable. Defaulted to C:\\ instead."

**Expected Results**:

- No crash or error dialog
- Fallback to system root
- Notification informs user

---

### Phase 4: Performance (5 minutes)

#### Test 8: Large Directory Handling

**Objective**: Verify UI remains responsive with 10k+ files

```bash
pytest tests/performance/test_large_directory_load.py -v
```

**Manual Steps**:

1. Generate test directory with 10,000 files:
   ```bash
   python scripts/generate_test_files.py --count 10000 --output /tmp/large_dir
   ```
2. Navigate to `/tmp/large_dir` in center pane
3. Observe loading time
4. Scroll through list
5. Select multiple files
6. Switch between panes

**Expected Results**:

- Initial load <2 seconds
- Scrolling smooth (60fps)
- UI never freezes
- Selection responsive

---

#### Test 9: Layout Switching Speed

**Objective**: Verify layout changes are perceived as instant

```bash
pytest tests/performance/test_layout_switching_speed.py -v
```

**Manual Steps**:

1. Start with 4-pane grid layout
2. Switch to 2-pane horizontal
3. Measure perceived latency
4. Switch to 2-pane vertical
5. Switch back to 4-pane grid

**Expected Results**:

- Each switch <200ms
- No flicker or visual glitches
- Smooth transitions

---

### Phase 5: Integration (10 minutes)

#### Test 10: End-to-End User Workflow

**Objective**: Validate complete user story

**Scenario**: User organizes project work

**Steps**:

1. Launch RFU (Multi-Pane Explorer default)
2. Configure 3-pane grid layout
3. Navigate panes to:
   - Pane 1: C:\\Projects\\RFU
   - Pane 2: C:\\Documents\\Specs
   - Pane 3: D:\\Backup
4. Bookmark all three locations
5. Launch "Duplicate Finder" tool
6. Close tool (should appear in Recent)
7. Select a file in Pane 1
8. Verify preview in right pane
9. Switch to Properties tab
10. Quick-toggle to tabbed interface
11. Quick-toggle back to Multi-Pane Explorer
12. Verify:
    - Layout preserved (3 panes, grid)
    - Pane paths preserved
    - Bookmarks still present
    - Recent tool shown
13. Restart application
14. Verify all preferences persisted

**Expected Results**:

- All actions complete without errors
- Preferences survive restart
- Context preserved across toggle
- Smooth, responsive experience

---

## Success Criteria

### Must Pass

- [ ] All automated tests pass (pytest exit code 0)
- [ ] All manual steps complete without crashes
- [ ] Performance requirements met:
  - [ ] Hub toggle <200ms
  - [ ] Large directory load <2s
  - [ ] Layout switch <200ms
- [ ] Preferences persist across restarts
- [ ] Empty states show helpful messages
- [ ] Fallback behaviors work (unavailable drives)

### Quality Metrics

- [ ] Test coverage ≥85% for new modules
- [ ] No mypy type errors
- [ ] No flake8 lint errors
- [ ] All edge cases handled gracefully

---

## Troubleshooting

### Issue: Preferences not persisting

**Check**:

- `config/rfu_config.json` exists and is writable
- No permission errors in logs
- ConfigManager properly initialized

**Fix**:

```bash
# Reset configuration
rm config/rfu_config.json
python -m src.rfu.main --reset-config
```

---

### Issue: Tools not appearing in Tools tab

**Check**:

- RFU tool registry populated (main.py)
- ToolsDiscoveryService has reference to main app
- Tool discovery cache not stale

**Fix**:

```python
# Refresh tool cache
tools_service.invalidate_cache()
tools_service.get_all_tools()
```

---

### Issue: Layout switching crashes

**Check**:

- Splitter state serialization
- Widget parenting
- Signal/slot connections

**Debug**:

```bash
# Run with debug logging
python -m src.rfu.main --log-level DEBUG
```

---

## Automated Test Invocation

### Run All Tests

```bash
pytest tests/file_explorer/ -v --cov=src/file_explorer --cov-report=html
```

### Run Specific Categories

```bash
# Unit tests only
pytest tests/file_explorer/unit/ -v

# Integration tests only
pytest tests/file_explorer/integration/ -v

# UI tests only (requires display)
pytest tests/file_explorer/ui/ -v

# Performance tests only
pytest tests/performance/ -v -m performance
```

### Generate Coverage Report

```bash
pytest --cov=src/file_explorer --cov-report=html
open htmlcov/index.html  # View in browser
```

---

## Continuous Integration

**CI Pipeline** (GitHub Actions / GitLab CI):

```yaml
test:
  script:
    - pip install -r requirements.txt
    - pytest tests/file_explorer/ --cov=src/file_explorer --junitxml=junit.xml
    - coverage report --fail-under=85
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

---

## Sign-Off Checklist

Before marking feature complete:

- [ ] All quickstart tests pass
- [ ] Code review completed
- [ ] Documentation updated (user guide + API reference)
- [ ] Performance benchmarks meet requirements
- [ ] Cross-platform testing completed (Windows/macOS/Linux)
- [ ] Accessibility testing completed (keyboard navigation)
- [ ] Constitution compliance verified
- [ ] Stakeholder approval obtained

**Approved By**: ******\_\_\_\_******  
**Date**: ******\_\_\_\_******
