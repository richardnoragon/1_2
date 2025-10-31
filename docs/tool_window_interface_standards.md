# Tool Window Interface Standards

This document records the minimum interface that every RFU tool window must
provide. The goal is to prevent regressions like missing exit actions and to
make expectations explicit for future development.

## Required attributes and behaviors

- Every tool subclassing `StandardWindow` **must** expose a callable
  `ensure_exit_action_reference()` method. This method is injected by the base
  class and guarantees that both legacy (`actionexit`) and modern (`actionExit`)
  exit actions are available.
- Tool windows should inherit from `StandardWindow` whenever possible. The base
  class now validates the interface contract at construction time and will
  raise an error if required attributes are missing.
- Tools that provide custom stand-alone fallbacks (such as simple utility
  wrappers) must implement the same exit action behavior. Use `StandardWindow`
  directly or replicate its helper method.

## Validation safeguards

- `StandardWindow` calls the tool interface validator during initialization to
  enforce compliance before the UI is built. Any violation is logged and raises
  an exception immediately.
- The reusable audit utility in `src/core/tool_interface_validator.py` scans
  all modules under `src.tools` and reports missing attributes or import
  failures.
- Automated tests in `tests/unit/test_tool_interface.py` run the audit and
  instantiate the Rename tool to guarantee that exit action references are
  available.

## Checklist for new tool windows

1. Subclass `StandardWindow` (or another validated base) and call
   `super().__init__()` first in `__init__`.
2. Confirm that the tool opens with both `actionExit` and `actionexit`
   attributes populated. The helper `ensure_exit_action_reference()` handles
   this automatically.
3. Add the tool module to the audit if it lives outside `src/tools/`.
4. Extend or add unit tests covering initialization or interface-specific
   behavior.

Following this checklist prevents silent regressions and keeps the launch hub
stable.
