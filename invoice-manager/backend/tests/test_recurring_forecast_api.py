"""API tests for recurring forecast endpoint."""

from __future__ import annotations

from datetime import datetime, timezone

from extensions import db
from models.database import RecurringInvoice


def test_forecast_returns_next_due_dates(client, app):
    with app.app_context():
        recurring = RecurringInvoice(
            name="Forecast plan",
            amount=3900,
            currency="HUF",
            day_of_month=15,
            is_active=True,
            created_at=datetime(2026, 1, 1),
        )
        db.session.add(recurring)
        db.session.commit()
        recurring_id = recurring.id

    response = client.get(
        f"/api/recurring/{recurring_id}/forecast?months=3&from_date=2026-02-01"
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["error"] is None
    assert payload["data"]["months"] == 3
    assert [item["due_date"] for item in payload["data"]["forecast"]] == [
        "2026-02-15",
        "2026-03-15",
        "2026-04-15",
    ]


def test_forecast_marks_already_generated(client):
    run_date = datetime.now(timezone.utc).date()
    created = client.post(
        "/api/recurring",
        json={"name": "Already generated", "amount": 4500, "day_of_month": run_date.day},
    )
    recurring_id = created.get_json()["data"]["id"]

    client.post("/api/recurring/run-now", json={"run_date": run_date.isoformat()})

    response = client.get(
        f"/api/recurring/{recurring_id}/forecast?months=1&from_date={run_date.isoformat()}"
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["error"] is None
    assert payload["data"]["forecast"][0]["due_date"] == run_date.isoformat()
    assert payload["data"]["forecast"][0]["already_generated"] is True


def test_forecast_for_paused_template_returns_data(client):
    created = client.post(
        "/api/recurring",
        json={"name": "Paused forecast", "amount": 5000, "day_of_month": 8},
    )
    recurring_id = created.get_json()["data"]["id"]
    client.post(f"/api/recurring/{recurring_id}/pause")

    response = client.get(
        f"/api/recurring/{recurring_id}/forecast?months=2&from_date=2026-02-01"
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["error"] is None
    assert payload["data"]["is_active"] is False
    assert len(payload["data"]["forecast"]) == 2


def test_forecast_rejects_invalid_months(client):
    created = client.post(
        "/api/recurring",
        json={"name": "Invalid months", "amount": 2500, "day_of_month": 6},
    )
    recurring_id = created.get_json()["data"]["id"]

    response = client.get(f"/api/recurring/{recurring_id}/forecast?months=abc")
    payload = response.get_json()
    assert response.status_code == 400
    assert payload["error"] == "months must be an integer"

    response = client.get(f"/api/recurring/{recurring_id}/forecast?months=0")
    payload = response.get_json()
    assert response.status_code == 400
    assert payload["error"] == "months must be between 1 and 24"


def test_forecast_rejects_invalid_from_date(client):
    created = client.post(
        "/api/recurring",
        json={"name": "Invalid date", "amount": 3200, "day_of_month": 10},
    )
    recurring_id = created.get_json()["data"]["id"]

    response = client.get(
        f"/api/recurring/{recurring_id}/forecast?months=2&from_date=01-02-2026"
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error"] == "from_date must be YYYY-MM-DD"
