# Debugging And Resources

## Debugging
- Backend logs: run `python app.py` in `backend/`.
- Desktop app: run `python main.py` in `frontend-desktop/`.
- Web app: run `npm run dev` in `frontend-web/`.

## Typical Failure Points
- backend not running or wrong port
- malformed invoice payload (date/amount/type errors)
- missing IBAN for QR generation
- recurring template with invalid day-of-month

## Docs
- `docs/SETUP.md`
- `docs/API.md`
- repository `README.md`

