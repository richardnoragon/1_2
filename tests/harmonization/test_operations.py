import pytest

from src.core.operations import operation
from src.core.error_codes import resolve_error


def test_nested_operations_share_correlation_and_fail_once():
    events = []
    def emit(event, **fields):
        events.append(fields)
    with pytest.raises(PermissionError):
        with operation("tool", "outer", emit=emit) as correlation:
            with operation("tool", "inner", emit=emit):
                raise PermissionError("sensitive path")
    assert {event["correlation_id"] for event in events} == {correlation}
    assert [event["marker"] for event in events] == ["perf_start", "perf_start", "perf_fail", "perf_fail"]
    assert events[-1]["error_code"] == "RFU-PERMISSION"
    assert "sensitive path" not in repr(events)


def test_telemetry_failure_does_not_break_work():
    def fail(*args, **kwargs):
        raise RuntimeError("offline")
    with operation("tool", "inspect", emit=fail):
        pass


def test_unknown_error_is_actionable_without_exception_details():
    assert resolve_error("legacy-code").code == "RFU-INTERNAL"
    assert resolve_error(FileNotFoundError("secret")).code == "RFU-NOT-FOUND"
