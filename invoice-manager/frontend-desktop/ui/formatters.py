"""Formatting helpers used by desktop UI."""

from __future__ import annotations

from datetime import datetime


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

