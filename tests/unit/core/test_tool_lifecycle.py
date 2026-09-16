from types import ModuleType
from unittest.mock import Mock, patch

from src.core.tool_lifecycle import (
    ToolRuntimeTracker,
    resolve_tool_class,
    resolve_tool_launch_request,
)
from src.core.tool_manifest import ToolManifestRegistry


def test_resolve_tool_launch_request_uses_manifest_lookup():
    request = resolve_tool_launch_request("File Finder")

    assert request is not None
    assert request.module_name == "src.tools.file_management.finder.file_finder"
    assert request.class_name == "FileFinderWindow"


def test_resolve_tool_class_uses_standard_import_strategy():
    mock_module = ModuleType("test.module")
    mock_class = Mock()
    setattr(mock_module, "TestClass", mock_class)

    with patch("builtins.__import__", return_value=mock_module):
        resolved = resolve_tool_class("test.module", "TestClass")

    assert resolved is mock_class


def test_tool_runtime_tracker_register_update_and_unregister():
    tracker = ToolRuntimeTracker()
    tool_instance = Mock()

    record = tracker.register("Demo Tool", tool_instance)
    assert record.tool_instance is tool_instance
    assert tracker.snapshot("Demo Tool")["status"] == "registered"

    updated = tracker.update_progress("Demo Tool", 75, "Working")
    assert updated is not None
    assert updated.progress == 75
    assert updated.current_operation == "Working"

    removed = tracker.unregister("Demo Tool")
    assert removed is not None
    assert tracker.snapshot("Demo Tool") is None


def test_manifest_lookup_matches_display_name():
    entry = ToolManifestRegistry.lookup("File Finder")

    assert entry is not None
    assert entry.tool_id == "file-finder"


def test_tool_runtime_tracker_propagates_actor_and_session_context():
    audit_trail = Mock()
    tracker = ToolRuntimeTracker(audit_trail=audit_trail)
    tool_instance = Mock()

    tracker.register(
        "Alpha Tool",
        tool_instance,
        actor="qa-admin",
        session_id="session-123",
        metadata={"role": "admin"},
    )
    tracker.update_progress(
        "Alpha Tool",
        50,
        "Halfway",
        actor="qa-admin",
        session_id="session-123",
        metadata={"role": "admin"},
    )
    tracker.unregister(
        "Alpha Tool",
        actor="qa-admin",
        session_id="session-123",
        metadata={"role": "admin"},
    )

    assert audit_trail.log_event.call_count == 3
    first_call = audit_trail.log_event.call_args_list[0]
    assert first_call.kwargs["actor"] == "qa-admin"
    assert first_call.kwargs["session_id"] == "session-123"
    assert first_call.kwargs["metadata"]["role"] == "admin"