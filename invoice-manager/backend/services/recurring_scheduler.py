"""Background scheduler for recurring invoice generation."""

from __future__ import annotations

import threading
from datetime import datetime, timezone

from services.recurring_generator import generate_due_recurring_invoices


class RecurringScheduler:
    """Small background loop that runs recurring generation periodically."""

    def __init__(self, app, interval_seconds: int):
        self._app = app
        self._interval_seconds = max(30, int(interval_seconds))
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="recurring-scheduler")

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join(timeout=2)

    def _run_loop(self):
        while not self._stop_event.is_set():
            with self._app.app_context():
                today = datetime.now(timezone.utc).date()
                generate_due_recurring_invoices(today)
            self._stop_event.wait(self._interval_seconds)
