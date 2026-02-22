# Models And API

## Core Models

### `GmailAccount`
- email address
- active flag
- sync metadata
- credentials/token storage

### `Invoice`
- source account (nullable for manual entries)
- name, amount, currency
- due date and paid status
- optional payment link and IBAN
- optional recurring source reference

### `RecurringInvoice`
- name, amount, currency
- day of month
- active flag
- last generated marker

## REST Endpoints

### Accounts
- `GET /api/accounts`
- `POST /api/accounts`
- `DELETE /api/accounts/:id`
- `POST /api/accounts/sync`

### Invoices
- `GET /api/invoices?status=unpaid|paid|all`
- `GET /api/invoices/:id`
- `POST /api/invoices/:id/pay`
- `GET /api/invoices/:id/qr`
- `DELETE /api/invoices/:id`

### Recurring
- `GET /api/recurring`
- `POST /api/recurring`
- `GET /api/recurring/:id`
- `PUT /api/recurring/:id`
- `DELETE /api/recurring/:id`
- `POST /api/recurring/:id/pause`

## API Response Shape
Success:
```json
{ "data": {}, "error": null }
```

Error:
```json
{ "data": null, "error": "Error message" }
```

