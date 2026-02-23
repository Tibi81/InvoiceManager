"""API tests for Gmail accounts blueprint."""

from __future__ import annotations

from models.database import GmailAccount


def test_create_account_requires_email(client):
    response = client.post("/api/accounts", json={})
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["data"] is None
    assert payload["error"] == "Email is required"


def test_create_account_rejects_invalid_email(client):
    response = client.post("/api/accounts", json={"email": "not-an-email"})
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error"] == "Invalid email format"


def test_create_account_success_returns_defaults(client):
    response = client.post("/api/accounts", json={"email": "user@example.com"})
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["error"] is None
    assert payload["data"]["email"] == "user@example.com"
    assert payload["data"]["label_name"] == "InvoiceManager"
    assert payload["data"]["oauth_connected"] is False


def test_create_account_upserts_existing_email(client):
    first = client.post("/api/accounts", json={"email": "same@example.com"})
    first_payload = first.get_json()
    account_id = first_payload["data"]["id"]

    second = client.post(
        "/api/accounts",
        json={
            "email": "same@example.com",
            "label_name": "IM-Test",
            "gmail_query": "from:billing@example.com",
            "is_active": False,
        },
    )
    payload = second.get_json()

    assert second.status_code == 201
    assert payload["data"]["id"] == account_id
    assert payload["data"]["label_name"] == "IM-Test"
    assert payload["data"]["gmail_query"] == "from:billing@example.com"
    assert payload["data"]["is_active"] is False


def test_sync_account_rejects_non_integer_max_results(client, app):
    with app.app_context():
        from extensions import db

        account = GmailAccount(
            email="sync@example.com",
            is_active=True,
            credentials_json="{}",
        )
        db.session.add(account)
        db.session.commit()
        account_id = account.id

    response = client.post(
        f"/api/accounts/{account_id}/sync",
        json={"max_results": "abc"},
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error"] == "max_results must be an integer"


def test_sync_account_success_with_mocked_service(client, app, monkeypatch):
    with app.app_context():
        from extensions import db

        account = GmailAccount(
            email="ok@example.com",
            is_active=True,
            credentials_json="{}",
        )
        db.session.add(account)
        db.session.commit()
        account_id = account.id

    def fake_sync(account, max_results=50, import_invoices=True):
        return {
            "account_id": account.id,
            "scanned_messages": 2,
            "imported_invoices": 1,
            "max_results_received": max_results,
            "import_invoices_received": import_invoices,
        }

    monkeypatch.setattr("api.accounts.sync_account_messages", fake_sync)

    response = client.post(
        f"/api/accounts/{account_id}/sync",
        json={"max_results": 7, "import_invoices": False},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["error"] is None
    assert payload["data"]["scanned_messages"] == 2
    assert payload["data"]["max_results_received"] == 7
    assert payload["data"]["import_invoices_received"] is False
