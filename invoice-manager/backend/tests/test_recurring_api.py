"""API tests for recurring invoices blueprint."""

from __future__ import annotations


def test_create_recurring_requires_name(client):
    response = client.post(
        "/api/recurring",
        json={"amount": 3990, "day_of_month": 1},
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error"] == "Name is required"


def test_create_recurring_requires_positive_amount(client):
    response = client.post(
        "/api/recurring",
        json={"name": "Netflix", "amount": 0, "day_of_month": 1},
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error"] == "Amount must be positive"


def test_create_recurring_validates_day_of_month(client):
    response = client.post(
        "/api/recurring",
        json={"name": "Netflix", "amount": 3990, "day_of_month": 32},
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error"] == "Day of month must be between 1 and 31"


def test_create_recurring_success(client):
    response = client.post(
        "/api/recurring",
        json={"name": "Netflix", "amount": 3990, "day_of_month": 1},
    )
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["error"] is None
    assert payload["data"]["name"] == "Netflix"
    assert payload["data"]["amount"] == 3990.0
    assert payload["data"]["day_of_month"] == 1
    assert payload["data"]["is_active"] is True


def test_update_recurring_day_of_month(client):
    created = client.post(
        "/api/recurring",
        json={"name": "Spotify", "amount": 1990, "day_of_month": 10},
    )
    recurring_id = created.get_json()["data"]["id"]

    response = client.put(
        f"/api/recurring/{recurring_id}",
        json={"day_of_month": 15},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["error"] is None
    assert payload["data"]["id"] == recurring_id
    assert payload["data"]["day_of_month"] == 15


def test_pause_toggle_recurring(client):
    created = client.post(
        "/api/recurring",
        json={"name": "Dropbox", "amount": 4990, "day_of_month": 8},
    )
    recurring_id = created.get_json()["data"]["id"]

    pause_1 = client.post(f"/api/recurring/{recurring_id}/pause")
    payload_1 = pause_1.get_json()
    assert pause_1.status_code == 200
    assert payload_1["data"]["is_active"] is False

    pause_2 = client.post(f"/api/recurring/{recurring_id}/pause")
    payload_2 = pause_2.get_json()
    assert pause_2.status_code == 200
    assert payload_2["data"]["is_active"] is True
