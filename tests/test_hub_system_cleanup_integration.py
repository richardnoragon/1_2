"""HUB integration tests for system_cleanup -- HUB-1 through HUB-5.

Verifies that the system_cleanup tool is correctly registered and wired inside
``src/tabbed_hub.py`` according to the Phase 3 Per-Tool Migration Template
HUB checklist.

All tests run headlessly via source-code static analysis and targeted imports --
no Qt application loop is required.

HUB-1: Tab registration check
HUB-2: Launch / teardown safety
HUB-3: Theme inheritance
HUB-4: Global preferences propagation
HUB-5: Error isolation (UtilityWindow / HubErrorScreen wiring)
"""

import ast
import inspect
import os
import pathlib
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_HUB_PATH = pathlib.Path("src/tabbed_hub.py")
_GUI_PATH = pathlib.Path("src/tools/system/system_cleanup/system_cleanup_gui.py")


def _hub_src() -> str:
    return _HUB_PATH.read_text(encoding="utf-8")


def _gui_src() -> str:
    return _GUI_PATH.read_text(encoding="utf-8")


def _method_segment(source: str, method_name: str) -> str:
    """Return the source text of the first function named *method_name*."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            seg = ast.get_source_segment(source, node)
            if seg:
                return seg
    return ""


# ---------------------------------------------------------------------------
# HUB-1  Tab registration check
# ---------------------------------------------------------------------------


class TestHUB1TabRegistration:
    """HUB-1: system_cleanup entry exists in the Hub tool grid."""

    def test_hub1a_open_system_cleanup_wired_in_create_system_tab(self):
        """HUB-1a: create_system_tab references open_system_cleanup callback."""
        seg = _method_segment(_hub_src(), "create_system_tab")
        assert seg, "create_system_tab method not found in tabbed_hub.py"
        assert "open_system_cleanup" in seg, (
            "open_system_cleanup callback not found in create_system_tab -- "
            "HUB-1a: tool tab entry missing"
        )

    def test_hub1b_label_derives_from_ui_strings(self):
        """HUB-1b: The button label is derived from _ui_strings.SystemCleanup.TITLE."""
        src = _hub_src()
        assert "_ui_strings.SystemCleanup.TITLE" in src, (
            "tabbed_hub.py does not reference _ui_strings.SystemCleanup.TITLE -- "
            "HUB-1b: label not sourced from ui_strings"
        )

    def test_hub1b_ui_strings_import_with_fallback(self):
        """HUB-1b: tabbed_hub.py imports ui_strings with a graceful fallback."""
        src = _hub_src()
        assert "_ui_strings" in src, "ui_strings alias _ui_strings not found"
        assert (
            "_UI_STRINGS_AVAILABLE" in src
        ), "_UI_STRINGS_AVAILABLE guard missing -- import lacks graceful fallback"

    def test_hub1b_ui_strings_title_value(self):
        """HUB-1b (value): ui_strings.SystemCleanup.TITLE == 'System Cleanup'."""
        from src.rfu.ui_strings import SystemCleanup

        assert SystemCleanup.TITLE == "System Cleanup"

    def test_hub1c_no_local_relative_icon_path_in_system_tab(self):
        """HUB-1c: System tab uses inline emoji -- no local-relative QIcon() path."""
        seg = _method_segment(_hub_src(), "create_system_tab")
        if "QIcon(" in seg:
            assert "assets/" in seg, (
                "create_system_tab uses QIcon() with a non-assets path -- "
                "HUB-1c: icon must come from shared assets/ directory"
            )


# ---------------------------------------------------------------------------
# HUB-2  Launch / teardown safety
# ---------------------------------------------------------------------------


class TestHUB2LaunchTeardown:
    """HUB-2: Launcher creates a UtilityWindow-backed tool safely."""

    def test_hub2a_launcher_uses_utility_window(self):
        """HUB-2a: open_system_cleanup wraps the tool in UtilityWindow."""
        seg = _method_segment(_hub_src(), "open_system_cleanup")
        assert "UtilityWindow(" in seg, (
            "open_system_cleanup does not use UtilityWindow -- "
            "HUB-2a: tool opens as a plain window, HubErrorScreen support absent"
        )

    def test_hub2a_launcher_does_not_touch_hub_geometry(self):
        """HUB-2a: open_system_cleanup must not resize or reposition the Hub."""
        seg = _method_segment(_hub_src(), "open_system_cleanup")
        assert "self.resize(" not in seg, "launcher calls self.resize()"
        assert "self.setGeometry(" not in seg, "launcher calls self.setGeometry()"
        assert "self.move(" not in seg, "launcher calls self.move()"

    def test_hub2b_launcher_stores_window_reference(self):
        """HUB-2b: launcher keeps reference so window is not garbage-collected."""
        seg = _method_segment(_hub_src(), "open_system_cleanup")
        assert "_system_cleanup_window" in seg, (
            "open_system_cleanup does not store the window reference -- "
            "HUB-2b: UtilityWindow may be GC after launch"
        )

    def test_hub2c_fresh_instance_on_each_call(self):
        """HUB-2c: Each open call creates a new SystemCleanupGUI."""
        seg = _method_segment(_hub_src(), "open_system_cleanup")
        assert "SystemCleanupGUI(" in seg, (
            "open_system_cleanup does not instantiate SystemCleanupGUI -- "
            "HUB-2c: tool may reuse stale state"
        )

    def test_hub2_launcher_has_except_block(self):
        """HUB-2: launch errors are caught so the Hub remains operational."""
        seg = _method_segment(_hub_src(), "open_system_cleanup")
        assert "except Exception" in seg or "except ImportError" in seg, (
            "open_system_cleanup has no except clause -- "
            "HUB-2: launch failure could propagate and break the Hub"
        )


# ---------------------------------------------------------------------------
# HUB-3  Theme inheritance
# ---------------------------------------------------------------------------


class TestHUB3ThemeInheritance:
    """HUB-3: SystemCleanupGUI inherits Hub theme via ThemeManager."""

    def test_hub3a_theme_callback_registered(self):
        """HUB-3a: __init__ registers _on_theme_changed with ThemeManager."""
        src = _gui_src()
        assert "ThemeManager.add_theme_changed_callback" in src, (
            "SystemCleanupGUI does not register a ThemeManager callback -- "
            "HUB-3a: tool will not update on Hub theme switch"
        )

    def test_hub3b_on_theme_changed_defined(self):
        """HUB-3b: _on_theme_changed is implemented."""
        src = _gui_src()
        assert "def _on_theme_changed" in src, (
            "SystemCleanupGUI._on_theme_changed not found -- "
            "HUB-3b: no handler to re-apply styles on theme switch"
        )

    def test_hub3c_no_independent_theme_variant(self):
        """HUB-3c: Tool does not define its own _active_variant."""
        src = _gui_src()
        assert "_active_variant" not in src, (
            "SystemCleanupGUI stores _active_variant -- "
            "HUB-3c: tool has independent theme state"
        )

    def test_hub3c_uses_token_function(self):
        """HUB-3c: token() used for color references."""
        src = _gui_src()
        assert "token(" in src, (
            "SystemCleanupGUI never calls token() -- "
            "HUB-3c: colors may be hard-coded"
        )


# ---------------------------------------------------------------------------
# HUB-4  Global preferences propagation
# ---------------------------------------------------------------------------


class TestHUB4PreferencesPropagation:
    """HUB-4: actor_username resolved dynamically on each telemetry call."""

    def test_hub4a_actor_username_reflects_env_var_change(self):
        """HUB-4a: _resolve_actor_username() reads RFU_USER_ID fresh every call."""
        os.environ["RFU_USER_ID"] = "hub4a_user_alpha"
        try:
            from src.gui.telemetry import _resolve_actor_username

            assert _resolve_actor_username() == "hub4a_user_alpha"
            os.environ["RFU_USER_ID"] = "hub4a_user_beta"
            assert (
                _resolve_actor_username() == "hub4a_user_beta"
            ), "_resolve_actor_username returned stale value -- HUB-4a: caching detected"
        finally:
            del os.environ["RFU_USER_ID"]

    def test_hub4b_tool_does_not_cache_actor_username(self):
        """HUB-4b: SystemCleanupGUI contains no cached identity attribute."""
        src = _gui_src()
        for attr in (
            "self._actor_username",
            "self.actor_username",
            "self._cached_username",
            "self._username",
        ):
            assert attr not in src, (
                f"{attr} found in system_cleanup_gui.py -- "
                "HUB-4b: actor_username may be cached"
            )

    def test_hub4b_emit_telemetry_calls_resolve(self):
        """HUB-4b: emit_telemetry calls _resolve_actor_username() for dynamic resolution."""
        from src.gui.telemetry import emit_telemetry

        src_text = inspect.getsource(emit_telemetry)
        assert "_resolve_actor_username()" in src_text, (
            "emit_telemetry does not call _resolve_actor_username() -- "
            "HUB-4b: identity may be captured once and never updated"
        )


# ---------------------------------------------------------------------------
# HUB-5  Error isolation
# ---------------------------------------------------------------------------


class TestHUB5ErrorIsolation:
    """HUB-5: UtilityWindow/HubErrorScreen wiring keeps Hub functional on failure."""

    def test_hub5a_launcher_exception_absorbed(self):
        """HUB-5a: open_system_cleanup try/except prevents tool crashes reaching Hub."""
        seg = _method_segment(_hub_src(), "open_system_cleanup")
        has_try = False
        for node in ast.walk(ast.parse(seg)):
            if isinstance(node, (ast.Try, ast.ExceptHandler)):
                has_try = True
                break
        assert has_try, (
            "open_system_cleanup has no try/except -- "
            "HUB-5a: tool failures propagate to Hub"
        )

    def test_hub5b_hub_error_screen_imported(self):
        """HUB-5b: HubErrorScreen is present in tabbed_hub.py."""
        src = _hub_src()
        assert (
            "_HubErrorScreen" in src or "HubErrorScreen" in src
        ), "HubErrorScreen not imported in tabbed_hub.py -- HUB-5b incomplete"

    def test_hub5b_utility_window_wires_retry_signal(self):
        """HUB-5b: UtilityWindow wires retry_requested and go_home_requested."""
        src = _hub_src()
        assert (
            "retry_requested" in src
        ), "UtilityWindow does not wire retry_requested -- HUB-5b incomplete"
        assert (
            "go_home_requested" in src
        ), "UtilityWindow does not wire go_home_requested -- HUB-5b incomplete"

    def test_hub5b_launcher_uses_utility_window_for_isolation(self):
        """HUB-5b: open_system_cleanup uses UtilityWindow for HubErrorScreen isolation."""
        seg = _method_segment(_hub_src(), "open_system_cleanup")
        assert "UtilityWindow(" in seg, (
            "open_system_cleanup does not use UtilityWindow -- "
            "HUB-5b: HubErrorScreen isolation not active"
        )

    def test_hub5c_relaunch_tool_window_defined(self):
        """HUB-5c: TabbedRFUHub defines relaunch_tool_window for HubErrorScreen retry."""
        src = _hub_src()
        assert "def relaunch_tool_window(" in src, (
            "relaunch_tool_window not defined -- " "HUB-5c: Retry button has no handler"
        )

    def test_hub5c_relaunch_dispatches_system_cleanup(self):
        """HUB-5c: relaunch_tool_window maps SystemCleanup title to open_system_cleanup."""
        seg = _method_segment(_hub_src(), "relaunch_tool_window")
        assert "open_system_cleanup" in seg, (
            "relaunch_tool_window does not dispatch to open_system_cleanup -- "
            "HUB-5c: Retry would not re-launch System Cleanup"
        )

    def test_hub5c_retry_signal_wired_to_relaunch(self):
        """HUB-5c: UtilityWindow __init__ connects retry_requested to relaunch_tool_window."""
        seg = _method_segment(_hub_src(), "__init__")
        assert "relaunch_tool_window" in seg, (
            "UtilityWindow.__init__ does not wire retry to relaunch_tool_window -- "
            "HUB-5c: Retry button wiring incomplete"
        )
