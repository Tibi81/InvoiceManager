"""Gmail OAuth and sync helpers."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from flask import current_app
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from itsdangerous import BadSignature, URLSafeSerializer

from extensions import db
from models.database import GmailAccount
from services.gmail_filters import (
    embed_oauth_credentials,
    extract_filter_settings,
    extract_oauth_credentials,
)

_URL_RE = re.compile(r"https?://", re.IGNORECASE)
_INVOICE_HINT_RE = re.compile(r"(szamla|invoice|fizetesi link|payment link)", re.IGNORECASE)


class GmailServiceError(Exception):
    """Domain error for Gmail integration."""


def _serializer() -> URLSafeSerializer:
    secret = current_app.config.get("SECRET_KEY")
    return URLSafeSerializer(secret, salt="gmail-oauth-state")


def _get_client_config() -> dict[str, Any]:
    client_id = current_app.config.get("GMAIL_CLIENT_ID")
    client_secret = current_app.config.get("GMAIL_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise GmailServiceError("GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be configured")

    oauth_mode = str(current_app.config.get("GMAIL_OAUTH_MODE", "desktop")).strip().lower()
    client_kind = "installed" if oauth_mode == "desktop" else "web"
    return {
        client_kind: {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


def _serialize_credentials(creds: Credentials) -> dict[str, Any]:
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes or []),
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
    }


def _load_credentials(account: GmailAccount) -> Credentials:
    oauth = extract_oauth_credentials(account.credentials_json)
    if not oauth:
        raise GmailServiceError("Gmail account is not connected yet. Start OAuth first.")

    scopes = current_app.config.get("GMAIL_SCOPES", [])
    creds = Credentials.from_authorized_user_info(oauth, scopes=scopes)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        account.credentials_json = embed_oauth_credentials(account.credentials_json, _serialize_credentials(creds))
        db.session.commit()

    if not creds.valid:
        raise GmailServiceError("Stored Gmail token is invalid. Reconnect the account.")

    return creds


def create_oauth_authorization_url(account: GmailAccount) -> str:
    """Create Google OAuth authorization URL for one account."""
    redirect_uri = current_app.config.get("GMAIL_REDIRECT_URI")
    flow = Flow.from_client_config(_get_client_config(), scopes=current_app.config.get("GMAIL_SCOPES", []))
    flow.redirect_uri = redirect_uri

    state = _serializer().dumps({"account_id": account.id, "email": account.email})
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
        login_hint=account.email,
    )
    return auth_url


def connect_account_local_oauth(account: GmailAccount) -> GmailAccount:
    """Run installed-app OAuth flow locally and persist credentials."""
    oauth_mode = str(current_app.config.get("GMAIL_OAUTH_MODE", "desktop")).strip().lower()
    if oauth_mode != "desktop":
        raise GmailServiceError("Local OAuth connect is only available in desktop mode")

    scopes = current_app.config.get("GMAIL_SCOPES", [])
    flow = InstalledAppFlow.from_client_config(_get_client_config(), scopes=scopes)
    try:
        creds = flow.run_local_server(
            host="127.0.0.1",
            port=0,
            open_browser=True,
            authorization_prompt_message="Opening browser for Gmail authorization...",
            success_message="Gmail authorization completed. You can close this tab.",
        )
    except Exception as exc:
        raise GmailServiceError(
            "Desktop OAuth failed. Verify Desktop client credentials and retry."
        ) from exc

    account.credentials_json = embed_oauth_credentials(
        account.credentials_json,
        _serialize_credentials(creds),
    )
    account.is_active = True
    db.session.commit()
    return account


def complete_oauth_callback(state: str, code: str) -> GmailAccount:
    """Exchange OAuth callback code and persist credentials for account in state."""
    if not state or not code:
        raise GmailServiceError("OAuth callback is missing required parameters")

    try:
        payload = _serializer().loads(state)
    except BadSignature as exc:
        raise GmailServiceError("Invalid OAuth state") from exc

    account_id = payload.get("account_id")
    if not account_id:
        raise GmailServiceError("OAuth state did not include account id")

    account = GmailAccount.query.get(account_id)
    if not account:
        raise GmailServiceError("Gmail account not found for OAuth callback")

    flow = Flow.from_client_config(_get_client_config(), scopes=current_app.config.get("GMAIL_SCOPES", []))
    flow.redirect_uri = current_app.config.get("GMAIL_REDIRECT_URI")
    flow.fetch_token(code=code)

    account.credentials_json = embed_oauth_credentials(
        account.credentials_json,
        _serialize_credentials(flow.credentials),
    )
    account.is_active = True
    db.session.commit()
    return account


def _build_effective_query(label_name: str, gmail_query: str) -> str:
    safe_label = label_name.replace('"', "")
    label_query = f'label:"{safe_label}"' if safe_label else ""
    if label_query and gmail_query:
        return f"({label_query}) ({gmail_query})"
    return label_query or gmail_query


def _extract_header(headers: list[dict[str, str]] | None, name: str) -> str:
    if not headers:
        return ""
    lower_name = name.lower()
    for header in headers:
        if str(header.get("name", "")).lower() == lower_name:
            return str(header.get("value", ""))
    return ""


def sync_account_messages(account: GmailAccount, max_results: int = 50) -> dict[str, Any]:
    """Run a lightweight Gmail sync for one account and return a summary preview."""
    creds = _load_credentials(account)
    gmail = build("gmail", "v1", credentials=creds, cache_discovery=False)

    label_name, gmail_query = extract_filter_settings(account.credentials_json)
    effective_query = _build_effective_query(label_name, gmail_query)
    limit = max(1, min(int(max_results), 100))

    refs: list[dict[str, str]] = []
    page_token = None
    while len(refs) < limit:
        response = (
            gmail.users()
            .messages()
            .list(
                userId="me",
                q=effective_query,
                maxResults=min(25, limit - len(refs)),
                includeSpamTrash=False,
                pageToken=page_token,
            )
            .execute()
        )
        refs.extend(response.get("messages", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    previews: list[dict[str, Any]] = []
    payment_link_hits = 0
    invoice_hint_hits = 0

    for ref in refs:
        msg = (
            gmail.users()
            .messages()
            .get(
                userId="me",
                id=ref["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        subject = _extract_header(headers, "Subject")
        sender = _extract_header(headers, "From")
        date_header = _extract_header(headers, "Date")
        snippet = msg.get("snippet", "")

        combined_text = f"{subject}\n{snippet}"
        has_payment_link = bool(_URL_RE.search(combined_text))
        has_invoice_hint = bool(_INVOICE_HINT_RE.search(combined_text))
        if has_payment_link:
            payment_link_hits += 1
        if has_invoice_hint:
            invoice_hint_hits += 1

        previews.append(
            {
                "id": msg.get("id"),
                "thread_id": msg.get("threadId"),
                "subject": subject,
                "from": sender,
                "date": date_header,
                "snippet": snippet,
                "has_payment_link": has_payment_link,
                "has_invoice_hint": has_invoice_hint,
            }
        )

    account.last_sync = datetime.now(timezone.utc).replace(tzinfo=None)
    db.session.commit()

    return {
        "account_id": account.id,
        "email": account.email,
        "label_name": label_name,
        "gmail_query": gmail_query,
        "effective_query": effective_query,
        "scanned_messages": len(refs),
        "payment_link_hits": payment_link_hits,
        "invoice_hint_hits": invoice_hint_hits,
        "sample_messages": previews[:20],
        "synced_at": account.last_sync.isoformat(),
    }
