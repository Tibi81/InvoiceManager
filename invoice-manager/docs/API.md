# API Documentation

Invoice Manager REST API reference.

**Base URL:** `http://localhost:5000`

**Response Format:**
```json
{
  "data": { ... },  // or array
  "error": null     // or error message string
}
```

---

## Health Check

### GET /health

Check if API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0-dev"
}
```

---

## Gmail Accounts

### GET /api/accounts

List all Gmail accounts.

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "email": "personal@gmail.com",
      "is_active": true,
      "last_sync": "2026-02-15T10:30:00Z",
      "created_at": "2026-02-01T08:00:00Z"
    }
  ],
  "error": null
}
```

### POST /api/accounts

Add a new Gmail account (OAuth flow).

**Request Body:**
```json
{
  "email": "personal@gmail.com"
}
```

**Response:**
```json
{
  "data": {
    "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
    "state": "random-state-token"
  },
  "error": null
}
```

**Notes:**
- Client must redirect user to `auth_url`
- After authorization, Google redirects back with code
- Exchange code for tokens in callback endpoint

### DELETE /api/accounts/:id

Remove Gmail account.

**Response:**
```json
{
  "data": {
    "deleted": true,
    "id": 1
  },
  "error": null
}
```

### POST /api/accounts/sync

Trigger manual sync for all active accounts.

**Response:**
```json
{
  "data": {
    "synced_accounts": 2,
    "new_invoices": 5
  },
  "error": null
}
```

---

## Invoices

### GET /api/invoices

List invoices with optional filtering.

**Query Parameters:**
- `status` (optional): `unpaid`, `paid`, or `all` (default: `all`)
- `account_id` (optional): Filter by Gmail account ID
- `limit` (optional): Number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Examples:**
```
GET /api/invoices?status=unpaid
GET /api/invoices?status=paid&account_id=1
GET /api/invoices?limit=20&offset=40
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "gmail_account_id": 1,
      "gmail_account_email": "personal@gmail.com",
      "name": "Telekom számla",
      "amount": 8500.00,
      "currency": "HUF",
      "due_date": "2026-02-20",
      "paid": false,
      "paid_date": null,
      "payment_link": "https://simplepay.hu/...",
      "pdf_path": "invoices/telekom_202602.pdf",
      "iban": "HU42117730161111101800000000",
      "is_recurring": false,
      "recurring_invoice_id": null,
      "created_at": "2026-02-15T08:30:00Z",
      "has_qr": true,
      "has_payment_link": true
    }
  ],
  "error": null
}
```

### GET /api/invoices/:id

Get single invoice details.

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "Telekom számla",
    "amount": 8500.00,
    "currency": "HUF",
    "due_date": "2026-02-20",
    "paid": false,
    "payment_link": "https://simplepay.hu/...",
    "iban": "HU42117730161111101800000000",
    "has_qr": true,
    "has_payment_link": true
  },
  "error": null
}
```

### POST /api/invoices/:id/pay

Mark invoice as paid.

**Response:**
```json
{
  "data": {
    "id": 1,
    "paid": true,
    "paid_date": "2026-02-15T11:00:00Z"
  },
  "error": null
}
```

### GET /api/invoices/:id/qr

Generate QR code for invoice payment.

**Response:**
- Content-Type: `image/png`
- Binary PNG image data

**Error Response (if no IBAN):**
```json
{
  "error": "No IBAN available for this invoice"
}
```

**Notes:**
- QR code follows EPC standard
- Compatible with European banking apps

### DELETE /api/invoices/:id

Delete an invoice.

**Response:**
```json
{
  "data": {
    "deleted": true,
    "id": 1
  },
  "error": null
}
```

---

## Recurring Invoices

### GET /api/recurring

List all recurring invoice templates.

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Netflix előfizetés",
      "amount": 3990.00,
      "currency": "HUF",
      "day_of_month": 1,
      "is_active": true,
      "last_generated": "2026-02-01",
      "created_at": "2026-01-15T10:00:00Z"
    }
  ],
  "error": null
}
```

### POST /api/recurring

Create a new recurring invoice.

**Request Body:**
```json
{
  "name": "Netflix előfizetés",
  "amount": 3990.00,
  "day_of_month": 1
}
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "Netflix előfizetés",
    "amount": 3990.00,
    "currency": "HUF",
    "day_of_month": 1,
    "is_active": true,
    "last_generated": null,
    "created_at": "2026-02-15T12:00:00Z"
  },
  "error": null
}
```

**Validation:**
- `name`: Required, max 255 characters
- `amount`: Required, positive decimal
- `day_of_month`: Required, 1-31

### GET /api/recurring/:id

Get recurring invoice details.

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "Netflix előfizetés",
    "amount": 3990.00,
    "day_of_month": 1,
    "is_active": true
  },
  "error": null
}
```

### PUT /api/recurring/:id

Update recurring invoice.

**Request Body:**
```json
{
  "name": "Netflix Premium",
  "amount": 4990.00,
  "day_of_month": 5
}
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "name": "Netflix Premium",
    "amount": 4990.00,
    "day_of_month": 5,
    "is_active": true
  },
  "error": null
}
```

### POST /api/recurring/:id/pause

Pause or unpause recurring invoice.

**Response:**
```json
{
  "data": {
    "id": 1,
    "is_active": false
  },
  "error": null
}
```

**Notes:**
- Toggles `is_active` status
- Paused invoices won't generate new invoices

### DELETE /api/recurring/:id

Delete recurring invoice.

**Response:**
```json
{
  "data": {
    "deleted": true,
    "id": 1
  },
  "error": null
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "data": null,
  "error": "Validation error: amount must be positive"
}
```

### 404 Not Found
```json
{
  "data": null,
  "error": "Invoice not found"
}
```

### 500 Internal Server Error
```json
{
  "data": null,
  "error": "Internal server error"
}
```

---

## Status Codes

- `200 OK` - Successful GET, PUT, POST
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Authentication (Future)

Currently, the API has no authentication (local use only).

Future versions will implement:
- JWT tokens
- API keys
- Rate limiting

---

## Rate Limiting (Future)

Not implemented in MVP. Future considerations:
- 100 requests per minute per client
- Gmail API has its own limits (quota)

---

## Webhooks (Future)

Not implemented in MVP. Future features:
- Notify on new invoice
- Notify on payment due
- Custom webhook URLs

---

**Last Updated:** 2026-02-15
