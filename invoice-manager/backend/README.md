# Backend - Flask REST API

Invoice Manager backend API built with Flask.

## Setup

### 1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and add your Gmail API credentials
```

### 4. Run the application
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Testing

Test the API with curl:
```bash
# Health check
curl http://localhost:5000/health

# Root endpoint
curl http://localhost:5000/
```

Or use Postman/Insomnia for a better experience.

Run automated tests:
```bash
pytest -q
```

## Project Structure

```
backend/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── models/
│   ├── __init__.py
│   └── database.py     # SQLAlchemy models
├── services/           # Business logic (to be added)
│   ├── gmail_service.py
│   ├── pdf_parser.py
│   └── qr_generator.py
├── api/               # API blueprints (to be added)
│   ├── invoices.py
│   ├── accounts.py
│   └── recurring.py
└── tests/             # Unit tests (to be added)
```

## Next Steps

1. Implement Gmail API integration (`services/gmail_service.py`)
2. Implement PDF parsing (`services/pdf_parser.py`)
3. Implement QR code generation (`services/qr_generator.py`)
4. Create API endpoints (`api/` blueprints)
5. Add tests (`tests/`)

## Development Notes

- Database: SQLite (stored as `invoices.db`)
- All dates stored in UTC
- API responses follow format: `{"data": ..., "error": null}`
- CORS enabled for `localhost:3000` (React) and `localhost:5173` (Vite)
- Recurring scheduler runs in background by default
  - `RECURRING_SCHEDULER_ENABLED=true|false`
  - `RECURRING_SCHEDULER_INTERVAL_SECONDS=300`
