# Tab Sorting Workflow

This guide explains how to keep the dialog hub tabs ordered alphabetically
while reserving priority slots for pinned categories.

## One-Time Alphabetical Reorganization

1. Open the **Tools** menu in the main RFU window.
2. Click **Refresh Tool List**. The hub invokes
   `AlphabeticalTabWidget.sort_tabs()` and rebuilds the tab order.
3. Confirm that pinned tabs (`File Management`, `File Operations` by default)
   stay in their leading positions.
4. If you prefer to automate this step in scripts, call
   `window.tab_widget.sort_tabs()` on an `RFUMainWindow` instance.

## Automatic Sorting for New or Renamed Tabs

- The hub now uses `AlphabeticalTabWidget`, which sorts tabs each time
  `addTab`, `insertTab`, or `setTabText` is called. No extra wiring is needed
  when new categories are registered through `_register_tab`.
- When a tab title changes, call `tab_widget.setTabText(index, new_label)`;
  the widget reorders the non pinned tabs immediately.
- To add a tab that should always stay near the front, either list its title in
  `RFUMainWindow.PINNED_TAB_TITLES` or set `widget.setProperty("rfuPinnedTab",
True)` before you add it.

## Maintaining Pinned or Priority Tabs

- Edit `RFUMainWindow.PINNED_TAB_TITLES` to control which labels remain fixed
  at the front. The order in that tuple is preserved.
- At runtime you can adjust pinning with `tab_widget.pin_tab(widget)` and
  `tab_widget.unpin_tab(widget)`. The sort logic runs after each change.
- Pinned widgets retain their slot even when the title changes; unpinning drops
  them back into the alphabetical pool on the next sort.
