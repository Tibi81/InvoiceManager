"""Formatting helpers used by desktop UI."""

from __future__ import annotations

import calendar
from datetime import date, datetime


def format_date(date_str: str) -> str:
    """Format date for Hungarian-style display."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y. %b %d.").replace("Jan", "jan").replace("Feb", "feb")
    except Exception:
        return date_str


def format_amount(amount: float, currency: str = "HUF") -> str:
    """Format amount with thousand separators."""
    return f"{amount:,.0f}".replace(",", " ") + " " + currency


def get_days_until_due(due_date_str: str) -> int:
    """Days until due (positive=future, negative=overdue)."""
    try:
        due = datetime.fromisoformat(due_date_str.replace("Z", "+00:00")).date()
    except Exception:
        return 0
    today = datetime.utcnow().date()
    return (due - today).days


def get_due_status_text(due_date_str: str, paid: bool) -> str | None:
    """Return due status label."""
    if paid:
        return None
    days = get_days_until_due(due_date_str)
    if days > 0:
        return f"{days} nap van hatra"
    if days < 0:
        return f"{abs(days)} nappal jart le"
    return "Ma esedekes"


def _clamped_day(year: int, month: int, day_of_month: int) -> date:
    """Return date in given month clamped to month end (e.g. 31 -> 30/28/29)."""
    last_day = calendar.monthrange(year, month)[1]
    safe_day = min(max(int(day_of_month), 1), last_day)
    return date(year, month, safe_day)


def get_next_recurring_due_date(day_of_month: int) -> date:
    """Compute next recurring due date from day-of-month rule."""
    today = datetime.utcnow().date()
    this_month_due = _clamped_day(today.year, today.month, day_of_month)
    if this_month_due >= today:
        return this_month_due

    if today.month == 12:
        return _clamped_day(today.year + 1, 1, day_of_month)
    return _clamped_day(today.year, today.month + 1, day_of_month)


def get_recurring_due_status_text(day_of_month: int, is_active: bool) -> str | None:
    """Return recurring due status label (active only)."""
    if not is_active:
        return None

    days = (get_next_recurring_due_date(day_of_month) - datetime.utcnow().date()).days
    if days > 0:
        return f"{days} nap van hatra"
    return "Ma esedekes"
