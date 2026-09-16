"""Correlated operation timing with one terminal event on success or failure."""

from contextlib import contextmanager
from contextvars import ContextVar
from time import perf_counter
from uuid import uuid4

from src.core.error_codes import resolve_error

_correlation = ContextVar("rfu_operation_correlation", default=None)


@contextmanager
def operation(tool_id, name, *, emit=None, correlation_id=None, dry_run=False):
    """Nested operations inherit correlation; exceptions retain their traceback."""
    if emit is None:
        from src.gui.telemetry import emit_telemetry
        emit = emit_telemetry
    correlation_id = correlation_id or _correlation.get() or str(uuid4())
    token = _correlation.set(correlation_id)
    start = perf_counter()

    def send(marker, **extra):
        # Observability cannot change the success/failure of an operation.
        try:
            emit("ui_performance_metric", tool_id=tool_id, schema_version=1,
                 operation=name, marker=marker, correlation_id=correlation_id,
                 dry_run=bool(dry_run), **extra)
        except Exception:
            pass

    send("perf_start")
    try:
        yield correlation_id
    except BaseException as exc:
        send("perf_fail", duration_ms=(perf_counter() - start) * 1000,
             error_code=resolve_error(exc).code)
        raise
    else:
        send("perf_end", duration_ms=(perf_counter() - start) * 1000)
    finally:
        _correlation.reset(token)
