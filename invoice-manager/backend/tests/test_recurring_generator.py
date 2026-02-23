"""Tests for recurring generation service."""

from __future__ import annotations

from datetime import date, datetime, timezone

from extensions import db
from models.database import Invoice, RecurringInvoice
from services.recurring_generator import generate_due_recurring_invoices


def _create_template(
    name: str,
    amount: float,
    day_of_month: int,
    created_at: datetime,
    is_active: bool = True,
    last_generated: date | None = None,
) -> RecurringInvoice:
    template = RecurringInvoice(
        name=name,
        amount=amount,
        currency="HUF",
        day_of_month=day_of_month,
        is_active=is_active,
        last_generated=last_generated,
        created_at=created_at.replace(tzinfo=None),
    )
    db.session.add(template)
    db.session.commit()
    return template


def test_generates_invoice_when_due(app):
    with app.app_context():
        template = _create_template(
            name="Netflix",
            amount=3990,
            day_of_month=5,
            created_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )

        stats = generate_due_recurring_invoices(date(2026, 2, 5))
        invoices = Invoice.query.filter_by(recurring_invoice_id=template.id, is_recurring=True).all()

        assert stats["generated"] == 1
        assert len(invoices) == 1
        assert invoices[0].due_date == date(2026, 2, 5)


def test_generation_is_idempotent(app):
    with app.app_context():
        template = _create_template(
            name="Spotify",
            amount=1990,
            day_of_month=10,
            created_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )

        first = generate_due_recurring_invoices(date(2026, 2, 10))
        second = generate_due_recurring_invoices(date(2026, 2, 10))
        count = Invoice.query.filter_by(recurring_invoice_id=template.id, is_recurring=True).count()

        assert first["generated"] == 1
        assert second["generated"] == 0
        assert second["skipped_not_due"] >= 1
        assert count == 1


def test_paused_template_is_ignored(app):
    with app.app_context():
        template = _create_template(
            name="Paused template",
            amount=5000,
            day_of_month=1,
            is_active=False,
            created_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )

        stats = generate_due_recurring_invoices(date(2026, 2, 1))
        count = Invoice.query.filter_by(recurring_invoice_id=template.id).count()

        assert stats["generated"] == 0
        assert stats["skipped_paused"] >= 1
        assert count == 0


def test_day_of_month_is_clamped_to_end_of_month(app):
    with app.app_context():
        template = _create_template(
            name="Month-end",
            amount=9990,
            day_of_month=31,
            created_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )

        stats = generate_due_recurring_invoices(date(2026, 2, 28))
        invoice = Invoice.query.filter_by(recurring_invoice_id=template.id, is_recurring=True).one()

        assert stats["generated"] == 1
        assert invoice.due_date == date(2026, 2, 28)


def test_catch_up_generates_missing_months(app):
    with app.app_context():
        template = _create_template(
            name="Catch-up",
            amount=2990,
            day_of_month=15,
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            last_generated=date(2026, 1, 15),
        )

        stats = generate_due_recurring_invoices(date(2026, 3, 20))
        due_dates = [
            inv.due_date
            for inv in Invoice.query.filter_by(recurring_invoice_id=template.id, is_recurring=True)
            .order_by(Invoice.due_date.asc())
            .all()
        ]

        assert stats["generated"] == 2
        assert due_dates == [date(2026, 2, 15), date(2026, 3, 15)]
