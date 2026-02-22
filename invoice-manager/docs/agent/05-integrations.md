# Integrations

## Gmail/OAuth (Planned)
- OAuth flow stores account tokens securely.
- Poll/sync logic maps relevant emails to invoice candidates.
- Parse subject/body/attachments for provider, amount, due date, payment hints.

## PDF Parsing (Planned)
- Extract structured fields from attachments.
- Preserve original files and parsing trace for debugging.
- Fail gracefully when extraction confidence is low.

## QR Generation
- Generate transfer QR from invoice IBAN and amount when available.
- Keep QR generation in dedicated backend service layer.

## Recurring Generation
- Recurring templates produce real invoices on schedule.
- Generation must be idempotent for a period (avoid duplicates).
- Paused templates must be ignored by scheduler.

