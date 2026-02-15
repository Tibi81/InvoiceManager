# Invoice Manager - AI Development Guide

## Project Overview

Personal invoice management system that automatically processes invoices from Gmail and manages recurring bills.

**Status:** 🚧 Under active development - MVP phase

**Tech Stack:**
- Backend: Flask REST API (Python 3.11+)
- Web Frontend: React + Vite
- Desktop Frontend: Flet (Python)
- Database: SQLite
- APIs: Gmail API, PDF parsing

---

## MVP Features (v1.0.0)

### 1. Email-based Invoice Processing 📧
- Gmail API monitors 2 accounts for new emails
- Automatic PDF attachment download and parsing
- Extract: amount, due date, service provider name, IBAN
- Payment link detection in email body
- Automatic invoice creation in database

### 2. Manual Recurring Invoices 🔄
- User creates recurring invoice templates (e.g., Netflix, rent)
- Parameters: name, amount, day of month, frequency
- Automatic invoice generation on due date
- Edit/delete/pause recurring invoices

### 3. Invoice List with Multiple Views 📋
- Three views: Unpaid / Paid / All
- Filter by date, Gmail account, category (optional)
- Mark invoices as paid
- QR code generation for bank transfers (EPC standard)
- Payment link button (opens in new tab)

---

## Architecture

```
┌─────────────────────────────────┐
│      Flask REST API (Backend)   │
│  - Gmail integration            │
│  - PDF parsing                  │
│  - SQLite database              │
│  - Business logic               │
└─────────────┬───────────────────┘
              │
      ┌───────┴────────┐
      │                │
┌─────▼─────┐    ┌────▼─────┐
│  React    │    │   Flet   │
│  Web UI   │    │ Desktop  │
│           │    │   App    │
└───────────┘    └──────────┘
```

### Directory Structure
```
invoice-manager/
├── backend/                 # Flask REST API
│   ├── app.py              # Main Flask app
│   ├── config.py           # Configuration
│   ├── models/
│   │   └── database.py     # SQLAlchemy models
│   ├── services/
│   │   ├── gmail_service.py
│   │   ├── pdf_parser.py
│   │   └── qr_generator.py
│   ├── api/
│   │   ├── invoices.py
│   │   ├── accounts.py
│   │   └── recurring.py
│   └── tests/
│
├── frontend-web/           # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│   └── package.json
│
├── frontend-desktop/       # Flet desktop app
│   ├── main.py
│   ├── components/
│   ├── services/
│   └── assets/
│
├── docs/
│   ├── SETUP.md
│   └── API.md
│
└── agent.md (this file)
```

---

## Database Models

### GmailAccount
```python
id: int (PK)
email: str                    # "personal@gmail.com"
is_active: bool               # True/False
last_sync: datetime           # Last sync timestamp
credentials_json: text        # OAuth token (encrypted)
created_at: datetime
```

### Invoice
```python
id: int (PK)
gmail_account_id: int (FK)    # Nullable if manual
name: str                     # "Telekom számla"
amount: decimal               # 8500.00
currency: str                 # "HUF" (only HUF in MVP)
due_date: date                # 2026-02-20
paid: bool                    # False
paid_date: datetime           # Nullable
payment_link: str             # Nullable
pdf_path: str                 # Nullable, local path
iban: str                     # Nullable, for QR generation
is_recurring: bool            # False if from email
recurring_invoice_id: int     # FK to RecurringInvoice (nullable)
created_at: datetime
```

### RecurringInvoice
```python
id: int (PK)
name: str                     # "Netflix előfizetés"
amount: decimal               # 3990.00
currency: str                 # "HUF"
day_of_month: int             # 1-31
is_active: bool               # True
last_generated: date          # Last time invoice was created
created_at: datetime
```

---

## API Endpoints

### Gmail Accounts
```
GET    /api/accounts              # List all accounts
POST   /api/accounts              # Add new account (OAuth flow)
DELETE /api/accounts/:id          # Remove account
POST   /api/accounts/sync         # Trigger sync for all accounts
```

### Invoices
```
GET    /api/invoices              # List invoices (query: ?status=unpaid)
GET    /api/invoices/:id          # Get invoice details
POST   /api/invoices/:id/pay      # Mark as paid
GET    /api/invoices/:id/qr       # Generate QR code (returns image)
DELETE /api/invoices/:id          # Delete invoice
```

### Recurring Invoices
```
GET    /api/recurring             # List all recurring invoices
POST   /api/recurring             # Create new recurring invoice
GET    /api/recurring/:id         # Get details
PUT    /api/recurring/:id         # Update recurring invoice
DELETE /api/recurring/:id         # Delete recurring invoice
POST   /api/recurring/:id/pause   # Pause/unpause
```

---

## Coding Guidelines

### Python (Backend & Desktop)

**Style:**
- Follow PEP 8
- Use type hints: `def get_invoice(invoice_id: int) -> Invoice:`
- Docstrings for all public functions
- Error handling with try/except blocks
- Never hardcode secrets (use environment variables)

**Database:**
- Use SQLAlchemy ORM
- Migrations with Alembic (if needed later)
- All dates in UTC, convert to local in frontend

**API Response Format:**
```python
# Success
{
    "data": {...},
    "error": null
}

# Error
{
    "data": null,
    "error": "Error message here"
}
```

**Example API endpoint:**
```python
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    try:
        status = request.args.get('status')  # unpaid, paid, all
        invoices = Invoice.query.filter_by(paid=(status == 'paid')).all()
        return jsonify({
            "data": [inv.to_dict() for inv in invoices],
            "error": None
        })
    except Exception as e:
        return jsonify({
            "data": None,
            "error": str(e)
        }), 500
```

### JavaScript/React (Web Frontend)

**Style:**
- Functional components with hooks
- Use `const` over `let`
- Async/await for API calls
- PropTypes for type checking (or TypeScript later)

**Component Structure:**
```jsx
// components/InvoiceCard/index.jsx
import React from 'react';
import './styles.css';

const InvoiceCard = ({ invoice, onMarkPaid }) => {
  return (
    <div className="invoice-card">
      <h3>{invoice.name}</h3>
      <p>{invoice.amount} {invoice.currency}</p>
      <button onClick={() => onMarkPaid(invoice.id)}>
        Fizetve
      </button>
    </div>
  );
};

export default InvoiceCard;
```

**API Calls:**
```javascript
// services/api.js
const API_BASE = 'http://localhost:5000/api';

export const getInvoices = async (status = 'all') => {
  const response = await fetch(`${API_BASE}/invoices?status=${status}`);
  const { data, error } = await response.json();
  if (error) throw new Error(error);
  return data;
};

export const markPaid = async (invoiceId) => {
  const response = await fetch(`${API_BASE}/invoices/${invoiceId}/pay`, {
    method: 'POST'
  });
  const { data, error } = await response.json();
  if (error) throw new Error(error);
  return data;
};
```

### Flet (Desktop Frontend)

**Style:**
- Material Design components
- Embed Flask backend as subprocess
- Handle backend lifecycle (start/stop)

**Example:**
```python
import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Számla Kezelő"
    page.window_icon = "assets/icon.png"
    
    def load_invoices():
        response = requests.get('http://localhost:5000/api/invoices')
        data = response.json()['data']
        
        invoice_list.controls.clear()
        for inv in data:
            invoice_list.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(inv['name']),
                        subtitle=ft.Text(f"{inv['amount']} Ft"),
                        trailing=ft.TextButton("Fizetve")
                    )
                )
            )
        page.update()
    
    invoice_list = ft.ListView()
    page.add(
        ft.AppBar(title=ft.Text("Számlák")),
        ft.ElevatedButton("Frissítés", on_click=lambda _: load_invoices()),
        invoice_list
    )
    
    load_invoices()

ft.app(target=main)
```

---

## Security & Best Practices

### Never Commit:
- ❌ `.env` files (use `.env.example` as template)
- ❌ `gmail_credentials.json` or OAuth tokens
- ❌ `*.db` database files
- ❌ API keys or passwords
- ❌ `__pycache__/`, `node_modules/`

### Environment Variables:
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
    GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
    DATABASE_URI = 'sqlite:///invoices.db'
```

### Input Validation:
```python
# Always validate user input
def create_recurring_invoice(data):
    if not data.get('name'):
        raise ValueError("Name is required")
    if data.get('amount', 0) <= 0:
        raise ValueError("Amount must be positive")
    if not (1 <= data.get('day_of_month', 0) <= 31):
        raise ValueError("Invalid day of month")
    # ... create invoice
```

---

## Gmail API Integration

### OAuth Flow:
1. User clicks "Add Gmail Account"
2. Backend redirects to Google OAuth consent screen
3. User authorizes
4. Backend receives authorization code
5. Exchange code for access token + refresh token
6. Store tokens encrypted in database

### Email Fetching:
```python
# services/gmail_service.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def fetch_new_emails(account: GmailAccount) -> list:
    """Fetch unread emails with attachments."""
    creds = Credentials.from_authorized_user_info(
        json.loads(account.credentials_json)
    )
    service = build('gmail', 'v1', credentials=creds)
    
    # Query: unread emails with attachments
    results = service.users().messages().list(
        userId='me',
        q='is:unread has:attachment'
    ).execute()
    
    messages = results.get('messages', [])
    return messages
```

### PDF Processing:
```python
# services/pdf_parser.py
import PyPDF2
import re

def extract_invoice_data(pdf_path: str) -> dict:
    """Extract amount, date, IBAN from PDF."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Extract amount (e.g., "15 000 Ft" or "15,000 Ft")
    amount_match = re.search(r'(\d+[\s,.]?\d+)\s*Ft', text)
    amount = float(amount_match.group(1).replace(' ', '').replace(',', '')) if amount_match else None
    
    # Extract IBAN
    iban_match = re.search(r'HU\d{2}\s?\d{3}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}', text)
    iban = iban_match.group(0).replace(' ', '') if iban_match else None
    
    return {
        'amount': amount,
        'iban': iban,
        'raw_text': text
    }
```

---

## QR Code Generation (EPC Standard)

```python
# services/qr_generator.py
import segno

def generate_payment_qr(iban: str, amount: float, name: str, reference: str = "") -> bytes:
    """Generate EPC QR code for SEPA payment."""
    qr = segno.make_epc_qr(
        name=name,
        iban=iban,
        amount=amount,
        text=reference,
        reference=reference
    )
    
    # Return as PNG bytes
    import io
    buffer = io.BytesIO()
    qr.save(buffer, kind='png', scale=5)
    return buffer.getvalue()
```

**API endpoint:**
```python
@app.route('/api/invoices/<int:invoice_id>/qr', methods=['GET'])
def get_qr_code(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    if not invoice.iban:
        return jsonify({"error": "No IBAN available"}), 400
    
    qr_bytes = generate_payment_qr(
        iban=invoice.iban,
        amount=float(invoice.amount),
        name=invoice.name
    )
    
    return send_file(
        io.BytesIO(qr_bytes),
        mimetype='image/png'
    )
```

---

## Recurring Invoice Auto-Generation

```python
# Background job (run daily via cron or APScheduler)
from datetime import date

def generate_due_recurring_invoices():
    """Create invoices for recurring bills due today."""
    today = date.today()
    recurring = RecurringInvoice.query.filter_by(
        is_active=True,
        day_of_month=today.day
    ).all()
    
    for rec in recurring:
        # Check if already generated this month
        if rec.last_generated and rec.last_generated.month == today.month:
            continue
        
        # Create new invoice
        invoice = Invoice(
            name=rec.name,
            amount=rec.amount,
            currency=rec.currency,
            due_date=today,
            paid=False,
            is_recurring=True,
            recurring_invoice_id=rec.id
        )
        db.session.add(invoice)
        
        # Update last generated
        rec.last_generated = today
    
    db.session.commit()
```

---

## Development Workflow

### Backend Development:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Fill in your values
python app.py             # Runs on http://localhost:5000
```

Test with Postman or curl:
```bash
curl http://localhost:5000/api/invoices
```

### Web Frontend Development:
```bash
cd frontend-web
npm install
npm run dev               # Runs on http://localhost:3000
```

### Desktop Development:
```bash
cd frontend-desktop
pip install -r requirements.txt
python main.py            # Opens desktop window
```

### Build Desktop App:
```bash
flet build windows --icon assets/icon.ico
# Output: build/invoice-manager.exe
```

---

## Testing

### Backend Tests (pytest):
```python
# tests/test_api.py
def test_get_invoices(client):
    response = client.get('/api/invoices')
    assert response.status_code == 200
    data = response.json['data']
    assert isinstance(data, list)

def test_mark_paid(client):
    # Create test invoice
    invoice = Invoice(name="Test", amount=100, due_date=date.today())
    db.session.add(invoice)
    db.session.commit()
    
    # Mark as paid
    response = client.post(f'/api/invoices/{invoice.id}/pay')
    assert response.status_code == 200
    assert response.json['data']['paid'] == True
```

Run tests:
```bash
cd backend
pytest
```

---

## Git Workflow

### Commit Message Format:
```
feat: add QR code generation
fix: Gmail token refresh issue
docs: update API documentation
refactor: improve PDF parsing logic
test: add invoice API tests
```

### Branch Strategy (if needed later):
```
main          → Stable releases
develop       → Active development
feature/xyz   → New features
fix/xyz       → Bug fixes
```

---

## Common Patterns & Snippets

### Error Handling (Backend):
```python
try:
    # Your code
    result = some_operation()
    return jsonify({"data": result, "error": None})
except ValueError as e:
    return jsonify({"data": None, "error": str(e)}), 400
except Exception as e:
    app.logger.error(f"Unexpected error: {e}")
    return jsonify({"data": None, "error": "Internal server error"}), 500
```

### Loading States (React):
```jsx
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

const loadInvoices = async () => {
  setLoading(true);
  setError(null);
  try {
    const data = await getInvoices();
    setInvoices(data);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

### Date Formatting (Hungarian):
```javascript
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};
```

---

## Project-Specific Notes

- **Language:** Hungarian UI (HUF currency only)
- **Timezone:** All dates stored in UTC, displayed in Europe/Budapest
- **Gmail Limits:** Max 2 accounts in MVP
- **PDF Storage:** Local filesystem, path stored in DB
- **QR Codes:** EPC standard (European banks)
- **Desktop:** Windows primary target (Mac/Linux later)

---

## When Making Changes

### Before Coding:
1. Is this an API change? → Update both frontends
2. Does this affect database? → Write migration
3. Is this sensitive? → Use environment variables
4. Does this need tests? → Write tests first (TDD optional)

### Checklist:
- [ ] Code follows style guidelines
- [ ] No secrets in code
- [ ] API response format correct
- [ ] Error handling included
- [ ] Tests written (if applicable)
- [ ] README updated (if feature added)
- [ ] Commit message descriptive

---

## DO NOT

- ❌ Hardcode API keys, credentials, or secrets
- ❌ Commit `.env` files or tokens
- ❌ Commit database files (`*.db`)
- ❌ Use `print()` for logging (use `logging` module)
- ❌ Directly mutate state in React (use setState)
- ❌ Make synchronous API calls (use async/await)
- ❌ Skip error handling
- ❌ Write endpoints without input validation

---

## Debugging Tips

### Backend:
- Enable Flask debug mode: `app.run(debug=True)`
- Check logs: `tail -f app.log`
- Use breakpoints: `import pdb; pdb.set_trace()`
- Test endpoints: Postman or curl

### Frontend:
- React DevTools (browser extension)
- Network tab in browser dev tools
- Console.log for debugging (remove before commit)
- Check API responses in Network tab

### Desktop:
- Flet prints to console
- Check backend subprocess logs
- Test API separately first

### Gmail API:
- Common issue: token expiry → refresh token logic
- Check scopes: `https://www.googleapis.com/auth/gmail.readonly`
- Test with Gmail API Explorer first

---

## Resources

- Flask docs: https://flask.palletsprojects.com/
- React docs: https://react.dev/
- Flet docs: https://flet.dev/
- Gmail API: https://developers.google.com/gmail/api
- EPC QR standard: https://en.wikipedia.org/wiki/EPC_QR_code
- Segno (QR lib): https://segno.readthedocs.io/

---

## Questions Before Starting

1. **Is this feature in MVP scope?** → Check feature list above
2. **Does backend API exist?** → Build backend first
3. **How will this work in both frontends?** → Design for both
4. **What happens if this fails?** → Add error handling
5. **Is this secure?** → Review security guidelines

---

**Last Updated:** 2026-02-15
**Version:** 0.1.0-dev
**Status:** MVP Development Phase
