# Coding Guidelines

## Python
- Follow PEP 8 and use type hints.
- Add docstrings for public functions.
- Handle runtime failures with explicit `try/except` and clear error propagation.
- Keep secrets in environment variables, never in code.

## Backend
- Use SQLAlchemy ORM for persistence.
- Validate request payloads before DB writes.
- Return consistent JSON response structure (`data` + `error`).
- Keep route modules focused by domain (`invoices`, `recurring`, `accounts`).

## React/Web
- Prefer functional components and hooks.
- Use async/await for API access.
- Keep component and style concerns separated.

## Desktop/Flet
- Keep view composition separate from API calls where possible.
- Use reusable dialog and card builders for repeated UI patterns.
- Always surface backend errors to the user.

## File Size Policy
- Target: `50-150` lines per file.
- Soft upper bound: `200` lines.
- Hard upper bound: `300` lines only when unavoidable.
- Above `300` lines is not allowed in normal development.
- Split by responsibility (view, dialog, service, formatter, handler).

