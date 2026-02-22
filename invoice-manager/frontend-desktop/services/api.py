"""
Invoice Manager API client for desktop app.
"""
import requests

API_BASE = "http://localhost:5000/api"


def _handle_response(response: requests.Response):
    """Handle API response, raise on error."""
    if response.headers.get("content-type", "").startswith("application/json"):
        data = response.json()
        if data.get("error"):
            raise Exception(data["error"])
        return data.get("data")
    return response


def get_health():
    """Check backend health."""
    response = requests.get("http://localhost:5000/health", timeout=2)
    return response.json()


def get_invoices(status="all"):
    """Fetch invoices with status filter (unpaid, paid, all)."""
    response = requests.get(f"{API_BASE}/invoices", params={"status": status}, timeout=5)
    response.raise_for_status()
    return _handle_response(response)


def create_invoice(data: dict):
    """Create a new invoice."""
    response = requests.post(
        f"{API_BASE}/invoices",
        json=data,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )
    response.raise_for_status()
    return _handle_response(response)


def mark_paid(invoice_id: int):
    """Mark invoice as paid."""
    response = requests.post(f"{API_BASE}/invoices/{invoice_id}/pay", timeout=5)
    response.raise_for_status()
    return _handle_response(response)


def delete_invoice(invoice_id: int):
    """Delete an invoice."""
    response = requests.delete(f"{API_BASE}/invoices/{invoice_id}", timeout=5)
    response.raise_for_status()
    return _handle_response(response)


def get_qr_url(invoice_id: int) -> str:
    """Get URL for invoice QR code image."""
    return f"{API_BASE}/invoices/{invoice_id}/qr"


def get_recurring():
    """Fetch all recurring invoice templates."""
    response = requests.get(f"{API_BASE}/recurring", timeout=5)
    response.raise_for_status()
    return _handle_response(response)


def create_recurring(data: dict):
    """Create a new recurring invoice template."""
    response = requests.post(
        f"{API_BASE}/recurring",
        json=data,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )
    response.raise_for_status()
    return _handle_response(response)


def update_recurring(recurring_id: int, data: dict):
    """Update a recurring invoice template."""
    response = requests.put(
        f"{API_BASE}/recurring/{recurring_id}",
        json=data,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )
    response.raise_for_status()
    return _handle_response(response)


def delete_recurring(recurring_id: int):
    """Delete a recurring invoice template."""
    response = requests.delete(f"{API_BASE}/recurring/{recurring_id}", timeout=5)
    response.raise_for_status()
    return _handle_response(response)


def pause_recurring(recurring_id: int):
    """Toggle pause/unpause for recurring invoice."""
    response = requests.post(f"{API_BASE}/recurring/{recurring_id}/pause", timeout=5)
    response.raise_for_status()
    return _handle_response(response)


def get_accounts():
    """Fetch Gmail account settings."""
    response = requests.get(f"{API_BASE}/accounts", timeout=10)
    response.raise_for_status()
    return _handle_response(response)


def get_account_defaults():
    """Fetch default Gmail filter settings."""
    response = requests.get(f"{API_BASE}/accounts/defaults", timeout=10)
    response.raise_for_status()
    return _handle_response(response)


def create_account(data: dict):
    """Create Gmail account settings."""
    response = requests.post(
        f"{API_BASE}/accounts",
        json=data,
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    response.raise_for_status()
    return _handle_response(response)


def update_account_filters(account_id: int, data: dict):
    """Update Gmail account filter settings."""
    response = requests.put(
        f"{API_BASE}/accounts/{account_id}/filters",
        json=data,
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    response.raise_for_status()
    return _handle_response(response)


def delete_account(account_id: int):
    """Delete Gmail account settings."""
    response = requests.delete(f"{API_BASE}/accounts/{account_id}", timeout=10)
    response.raise_for_status()
    return _handle_response(response)


def start_account_oauth(account_id: int):
    """Start OAuth connection for one Gmail account."""
    response = requests.post(f"{API_BASE}/accounts/{account_id}/oauth/start", timeout=180)
    response.raise_for_status()
    return _handle_response(response)


def sync_account(account_id: int, max_results: int = 50, import_invoices: bool = True):
    """Run Gmail sync preview for one account."""
    response = requests.post(
        f"{API_BASE}/accounts/{account_id}/sync",
        json={"max_results": max_results, "import_invoices": import_invoices},
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    response.raise_for_status()
    return _handle_response(response)
