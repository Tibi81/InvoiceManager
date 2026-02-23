"""API tests for recurring run-now and run-status endpoints."""

from __future__ import annotations

from datetime import date, datetime, timezone

from models.database import Invoice


def test_run_now_generates_due_recurring_invoice(client, app):
    run_date = datetime.now(timezone.utc).date()
    created = client.post(
        "/api/recurring",
        json={"name": "Cloud storage", "amount": 4990, "day_of_month": run_date.day},
    )
    recurring_id = created.get_json()["data"]["id"]

    response = client.post(
        "/api/recurring/run-now",
        json={"run_date": run_date.isoformat()},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["error"] is None
    assert payload["data"]["run_date"] == run_date.isoformat()
    assert payload["data"]["result"]["generated"] == 1

    with app.app_context():
        invoice = Invoice.query.filter_by(
            recurring_invoice_id=recurring_id,
            is_recurring=True,
        ).one()
        assert invoice.due_date == run_date


def test_run_now_rejects_invalid_date(client):
    response = client.post("/api/recurring/run-now", json={"run_date": "08-02-2026"})
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["data"] is None
    assert payload["error"] == "run_date must be YYYY-MM-DD"


def test_run_status_returns_last_run_details(client):
    client.post(
        "/api/recurring",
        json={"name": "Streaming", "amount": 2990, "day_of_month": 5},
    )
    client.post("/api/recurring/run-now", json={"run_date": "2026-02-05"})

    response = client.get("/api/recurring/run-status")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["error"] is None
    assert payload["data"]["total_runs"] == 1
    assert payload["data"]["last_run_date"] == "2026-02-05"
    assert payload["data"]["last_result"] is not None
    assert payload["data"]["scheduler_enabled"] is False


def test_run_now_returns_500_when_generation_fails(client, monkeypatch):
    def fake_run(_run_date):
        raise RuntimeError("forced-failure")

    monkeypatch.setattr("api.recurring.run_recurring_generation_for_date", fake_run)

    response = client.post("/api/recurring/run-now", json={"run_date": "2026-02-10"})
    payload = response.get_json()

    assert response.status_code == 500
    assert payload["data"] is None
    assert payload["error"] == "forced-failure"
