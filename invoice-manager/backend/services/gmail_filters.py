"""Helpers for Gmail invoice-focused filtering settings."""

from __future__ import annotations

import json
from typing import Any

DEFAULT_LABEL_NAME = "InvoiceManager"
DEFAULT_GMAIL_QUERY = (
    '(has:attachment filename:pdf) OR '
    '("fizetesi link" OR "payment link" OR "invoice" OR "szamla") '
    '-in:spam -in:trash'
)


def parse_credentials_json(raw_value: str | None) -> dict[str, Any]:
    """Parse credentials JSON safely while preserving legacy non-JSON values."""
    if not raw_value:
        return {}

    try:
        parsed = json.loads(raw_value)
    except Exception:
        return {"_raw_credentials": raw_value}

    if isinstance(parsed, dict):
        return parsed
    return {"_wrapped_credentials": parsed}


def extract_filter_settings(credentials_json: str | None) -> tuple[str, str]:
    """Read label/query settings from stored credentials payload."""
    parsed = parse_credentials_json(credentials_json)
    settings = parsed.get("_invoice_manager", {}) if isinstance(parsed, dict) else {}

    label_name = settings.get("label_name") if isinstance(settings, dict) else None
    gmail_query = settings.get("gmail_query") if isinstance(settings, dict) else None

    label_name = str(label_name).strip() if label_name else DEFAULT_LABEL_NAME
    gmail_query = str(gmail_query).strip() if gmail_query else DEFAULT_GMAIL_QUERY
    return label_name, gmail_query


def embed_filter_settings(
    existing_credentials_json: str | None,
    label_name: str,
    gmail_query: str,
) -> str:
    """Store label/query settings without discarding existing OAuth credential keys."""
    parsed = parse_credentials_json(existing_credentials_json)
    settings = parsed.get("_invoice_manager") if isinstance(parsed, dict) else None
    if not isinstance(settings, dict):
        settings = {}

    settings["label_name"] = label_name
    settings["gmail_query"] = gmail_query
    parsed["_invoice_manager"] = settings

    return json.dumps(parsed, ensure_ascii=False)


def normalize_filter_settings(label_name: str | None, gmail_query: str | None) -> tuple[str, str]:
    """Normalize label/query values with defaults and basic sanitation."""
    normalized_label = (label_name or DEFAULT_LABEL_NAME).strip()
    normalized_query = (gmail_query or DEFAULT_GMAIL_QUERY).strip()

    if not normalized_label:
        normalized_label = DEFAULT_LABEL_NAME
    if not normalized_query:
        normalized_query = DEFAULT_GMAIL_QUERY

    return normalized_label, normalized_query


def extract_oauth_credentials(credentials_json: str | None) -> dict[str, Any] | None:
    """Extract persisted OAuth credentials if present."""
    parsed = parse_credentials_json(credentials_json)
    oauth = parsed.get("oauth_credentials") if isinstance(parsed, dict) else None
    if isinstance(oauth, dict) and oauth.get("client_id"):
        return oauth
    return None


def has_oauth_credentials(credentials_json: str | None) -> bool:
    """Return whether an account has saved OAuth credentials."""
    return extract_oauth_credentials(credentials_json) is not None


def embed_oauth_credentials(existing_credentials_json: str | None, oauth_credentials: dict[str, Any]) -> str:
    """Store OAuth credentials while preserving filter settings and unknown keys."""
    parsed = parse_credentials_json(existing_credentials_json)
    parsed["oauth_credentials"] = oauth_credentials
    return json.dumps(parsed, ensure_ascii=False)
