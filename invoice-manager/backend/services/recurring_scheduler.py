"""Background scheduler for recurring invoice generation."""

from __future__ import annotations

import threading
from datetime import datetime, timezone

from services.recurring_generator import generate_due_recurring_invoices


class _RecurringRunState:
    """Thread-safe in-memory state for recurring generation runs."""

    def __init__(self):
        self._lock = threading.Lock()
        self._state = {
            "total_runs": 0,
            "last_run_at": None,
            "last_run_date": None,
            "last_result": None,
            "last_error": None,
        }

    def mark_success(self, run_date, result: dict):
        with self._lock:
            self._state["total_runs"] += 1
            self._state["last_run_at"] = datetime.now(timezone.utc).isoformat()
            self._state["last_run_date"] = run_date.isoformat()
            self._state["last_result"] = result
            self._state["last_error"] = None

    def mark_error(self, run_date, error: Exception):
        with self._lock:
            self._state["total_runs"] += 1
            self._state["last_run_at"] = datetime.now(timezone.utc).isoformat()
            self._state["last_run_date"] = run_date.isoformat()
            self._state["last_error"] = str(error)

    def snapshot(self) -> dict:
        with self._lock:
            return dict(self._state)

    def reset(self):
        with self._lock:
            self._state = {
                "total_runs": 0,
                "last_run_at": None,
                "last_run_date": None,
                "last_result": None,
                "last_error": None,
            }


_run_state = _RecurringRunState()


def run_recurring_generation_for_date(run_date):
    """Execute one recurring generation run and update run-state."""
    try:
        result = generate_due_recurring_invoices(run_date)
        _run_state.mark_success(run_date, result)
        return result
    except Exception as exc:
        _run_state.mark_error(run_date, exc)
        raise


def get_recurring_run_status() -> dict:
    """Return snapshot of recurring generation run status."""
    return _run_state.snapshot()


def reset_recurring_run_status():
    """Reset recurring generation run status (used by tests)."""
    _run_state.reset()


class RecurringScheduler:
    """Small background loop that runs recurring generation periodically."""

    def __init__(self, app, interval_seconds: int):
        self._app = app
        self._interval_seconds = max(30, int(interval_seconds))
        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="recurring-scheduler",
        )

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join(timeout=2)

    def _run_loop(self):
        while not self._stop_event.is_set():
            today = datetime.now(timezone.utc).date()
            with self._app.app_context():
                run_recurring_generation_for_date(today)
            self._stop_event.wait(self._interval_seconds)
