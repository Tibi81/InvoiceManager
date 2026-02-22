# Architecture

## High-level Components
- `backend/`: Flask API, business logic, persistence
- `frontend-web/`: browser UI
- `frontend-desktop/`: desktop UI
- `docs/`: setup and API docs

## Backend Layout
- `backend/app.py`: Flask app bootstrap
- `backend/models/database.py`: SQLAlchemy models
- `backend/api/`: route modules (`invoices.py`, `accounts.py`, `recurring.py`)
- `backend/services/`: integration/helpers (QR, Gmail parsing in future)

## Frontend Layout
- Web: component-driven React app
- Desktop: Flet app, API client in `frontend-desktop/services/api.py`

## Integration Contract
- Frontends only talk to backend HTTP API
- Backend owns validation and persistence rules
- Shared concepts: invoice, recurring template, account, payment metadata

