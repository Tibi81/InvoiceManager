"""Recurring invoice generation logic."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date

from extensions import db
from models.database import Invoice, RecurringInvoice


@dataclass
class GenerationStats:
    generated: int = 0
    skipped_existing: int = 0
    skipped_paused: int = 0
    skipped_not_due: int = 0
    processed_templates: int = 0

    def to_dict(self) -> dict:
        return {
            "generated": self.generated,
            "skipped_existing": self.skipped_existing,
            "skipped_paused": self.skipped_paused,
            "skipped_not_due": self.skipped_not_due,
            "processed_templates": self.processed_templates,
        }


def _month_start(value: date) -> date:
    return value.replace(day=1)


def _next_month(value: date) -> date:
    year = value.year + (1 if value.month == 12 else 0)
    month = 1 if value.month == 12 else value.month + 1
    return date(year, month, 1)


def _due_date_for_month(year: int, month: int, day_of_month: int) -> date:
    last_day = monthrange(year, month)[1]
    return date(year, month, min(day_of_month, last_day))


def _iter_due_dates(template: RecurringInvoice, run_date: date):
    created_date = template.created_at.date()
    if template.last_generated is not None:
        cursor = _next_month(_month_start(template.last_generated))
    else:
        cursor = _month_start(created_date)
    end = _month_start(run_date)

    while cursor <= end:
        due_date = _due_date_for_month(cursor.year, cursor.month, template.day_of_month)
        if due_date >= created_date and due_date <= run_date:
            yield due_date
        cursor = _next_month(cursor)


def forecast_recurring_due_dates(
    template: RecurringInvoice,
    months: int,
    from_date: date,
) -> list[date]:
    """Forecast next due dates for recurring template from a given date."""
    if months <= 0:
        return []

    anchor_date = max(from_date, template.created_at.date())
    cursor = _month_start(anchor_date)
    due_dates: list[date] = []

    while len(due_dates) < months:
        due_date = _due_date_for_month(cursor.year, cursor.month, template.day_of_month)
        if due_date >= anchor_date:
            due_dates.append(due_date)
        cursor = _next_month(cursor)

    return due_dates


def generate_due_recurring_invoices(run_date: date) -> dict:
    """Generate missing recurring invoices up to run_date in an idempotent way."""
    stats = GenerationStats()
    templates = RecurringInvoice.query.order_by(RecurringInvoice.id).all()
    stats.processed_templates = len(templates)

    for template in templates:
        if not template.is_active:
            stats.skipped_paused += 1
            continue

        template_had_due = False
        latest_due = template.last_generated
        for due_date in _iter_due_dates(template, run_date):
            template_had_due = True
            latest_due = due_date if latest_due is None else max(latest_due, due_date)
            existing = Invoice.query.filter_by(
                recurring_invoice_id=template.id,
                due_date=due_date,
                is_recurring=True,
            ).first()
            if existing:
                stats.skipped_existing += 1
                continue

            db.session.add(
                Invoice(
                    name=template.name,
                    amount=template.amount,
                    currency=template.currency,
                    due_date=due_date,
                    paid=False,
                    is_recurring=True,
                    recurring_invoice_id=template.id,
                )
            )
            stats.generated += 1

        if template_had_due and latest_due is not None:
            template.last_generated = latest_due
        else:
            stats.skipped_not_due += 1

    db.session.commit()
    return stats.to_dict()
