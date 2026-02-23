"""API tests for invoices blueprint."""

from __future__ import annotations

from datetime import date

from models.database import Invoice


def test_create_invoice_requires_name(client):
    response = client.post(
        "/api/invoices",
        json={"amount": 1200, "due_date": "2026-03-01"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["data"] is None
    assert payload["error"] == "Name is required"


def test_create_invoice_requires_positive_amount(client):
    response = client.post(
        "/api/invoices",
        json={"name": "Test", "amount": 0, "due_date": "2026-03-01"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Amount must be positive"


def test_create_invoice_requires_iso_due_date(client):
    response = client.post(
        "/api/invoices",
        json={"name": "Test", "amount": 1200, "due_date": "01-03-2026"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"] == "Due date must be YYYY-MM-DD format"


def test_create_invoice_success(client):
    response = client.post(
        "/api/invoices",
        json={
            "name": "Villanyszamla",
            "amount": 10990,
            "currency": "HUF",
            "due_date": "2026-03-01",
            "iban": "HU42117730161111101800000000",
        },
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["error"] is None
    assert payload["data"]["name"] == "Villanyszamla"
    assert payload["data"]["amount"] == 10990.0
    assert payload["data"]["has_qr"] is True


def test_mark_invoice_paid(client, app):
    with app.app_context():
        invoice = Invoice(name="Internet", amount=4990, due_date=date(2026, 3, 10), currency="HUF")
        invoice.paid = False
        invoice.is_recurring = False
        from extensions import db

        db.session.add(invoice)
        db.session.commit()
        invoice_id = invoice.id

    response = client.post(f"/api/invoices/{invoice_id}/pay")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["error"] is None
    assert payload["data"]["id"] == invoice_id
    assert payload["data"]["paid"] is True
    assert payload["data"]["paid_date"] is not None


def test_get_qr_requires_iban(client, app):
    with app.app_context():
        invoice = Invoice(name="Netflix", amount=3990, due_date=date(2026, 3, 15), currency="HUF")
        invoice.is_recurring = False
        from extensions import db

        db.session.add(invoice)
        db.session.commit()
        invoice_id = invoice.id

    response = client.get(f"/api/invoices/{invoice_id}/qr")
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["data"] is None
    assert payload["error"] == "No IBAN available for this invoice"


def test_delete_invoice(client, app):
    with app.app_context():
        invoice = Invoice(name="Delete me", amount=2500, due_date=date(2026, 3, 20), currency="HUF")
        invoice.is_recurring = False
        from extensions import db

        db.session.add(invoice)
        db.session.commit()
        invoice_id = invoice.id

    response = client.delete(f"/api/invoices/{invoice_id}")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["error"] is None
    assert payload["data"] == {"deleted": True, "id": invoice_id}
