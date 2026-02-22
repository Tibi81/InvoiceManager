"""Gmail OAuth and sync helpers."""

from __future__ import annotations

import base64
import binascii
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

from flask import current_app
from dateutil import parser as date_parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from itsdangerous import BadSignature, URLSafeSerializer

from extensions import db
from models.database import GmailAccount, Invoice
from services.gmail_filters import (
    embed_oauth_credentials,
    extract_filter_settings,
    extract_oauth_credentials,
)

_URL_RE = re.compile(r"https?://", re.IGNORECASE)
_INVOICE_HINT_RE = re.compile(r"(szamla|invoice|fizetesi link|payment link)", re.IGNORECASE)
_AMOUNT_RE = re.compile(
    r"(?<!\d)(\d{1,3}(?:[ .]\d{3})+|\d+)(?:[,.](\d{1,2}))?\s*(HUF|Ft|EUR|USD)?",
    re.IGNORECASE,
)
_PAYMENT_LINK_RE = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)
_DUE_DATE_KEYWORD_RE = re.compile(r"(hatarido|esedekes|fizetesi hatarido|due date)", re.IGNORECASE)
_AMOUNT_HINT_RE = re.compile(r"(fizetendo|osszeg|vegosszeg|total|amount|to pay)", re.IGNORECASE)
_ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_LOCAL_DATE_RE = re.compile(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b")


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


def _decode_part_data(encoded: str | None) -> str:
    if not encoded:
        return ""
    try:
        padded = encoded + "=" * (-len(encoded) % 4)
        return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8", errors="ignore")
    except (ValueError, binascii.Error):
        return ""


def _extract_body_text(payload: dict[str, Any]) -> str:
    body_texts: list[str] = []

    def visit(part: dict[str, Any]):
        mime_type = str(part.get("mimeType", "")).lower()
        body_data = _decode_part_data((part.get("body") or {}).get("data"))
        if mime_type == "text/plain" and body_data:
            body_texts.append(body_data)
        elif mime_type == "text/html" and body_data and not body_texts:
            html_as_text = re.sub(r"<[^>]+>", " ", body_data)
            body_texts.append(re.sub(r"\s+", " ", html_as_text))

        for child in part.get("parts", []) or []:
            visit(child)

    visit(payload)
    return "\n".join(t for t in body_texts if t).strip()


def _extract_payment_link(text: str) -> str | None:
    for match in _PAYMENT_LINK_RE.findall(text):
        url = match.strip().rstrip(".,)")
        if any(key in url.lower() for key in ("pay", "payment", "fizet", "stripe", "paypal", "simplepay", "barion", "revolut")):
            return url
    fallback = _PAYMENT_LINK_RE.search(text)
    return fallback.group(0).strip().rstrip(".,)") if fallback else None


def _extract_amount_and_currency(text: str) -> tuple[float | None, str]:
    candidates: list[tuple[float, str, int]] = []
    for line in text.splitlines():
        has_hint = bool(_AMOUNT_HINT_RE.search(line))
        for match in _AMOUNT_RE.finditer(line):
            int_part, decimal_part, currency = match.groups()
            normalized_int = int_part.replace(" ", "").replace(".", "")
            if not normalized_int.isdigit():
                continue
            amount = float(normalized_int)
            if decimal_part:
                amount = amount + float(f"0.{decimal_part}")
            if amount <= 0:
                continue

            # Filter common year-like false positives when no currency is present.
            if currency is None and amount < 100:
                continue
            if currency is None and 1900 <= amount <= 2100:
                continue

            normalized_currency = (currency or "HUF").upper()
            if normalized_currency == "FT":
                normalized_currency = "HUF"
            score = 10 if has_hint else 1
            if currency:
                score += 5
            candidates.append((amount, normalized_currency, score))

    if not candidates:
        return None, "HUF"
    best = max(candidates, key=lambda item: (item[2], item[0]))
    return best[0], best[1]


def _extract_due_date(text: str) -> date | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidate_lines = [line for line in lines if _DUE_DATE_KEYWORD_RE.search(line)]
    search_pool = candidate_lines if candidate_lines else lines[:20]

    for line in search_pool:
        iso = _ISO_DATE_RE.search(line)
        if iso:
            try:
                return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
            except ValueError:
                pass
        local = _LOCAL_DATE_RE.search(line)
        if local:
            try:
                return date(int(local.group(3)), int(local.group(2)), int(local.group(1)))
            except ValueError:
                pass
        try:
            parsed = date_parser.parse(line, dayfirst=True, fuzzy=True)
            if parsed:
                return parsed.date()
        except (ValueError, OverflowError):
            pass
    return None


def _build_invoice_name(subject: str, sender: str) -> str:
    clean_subject = (subject or "").strip()
    if clean_subject:
        return clean_subject[:255]
    clean_sender = (sender or "").strip()
    if clean_sender:
        return f"Gmail invoice - {clean_sender}"[:255]
    return "Gmail invoice"


def _find_existing_import(account_id: int, message_id: str) -> Invoice | None:
    return Invoice.query.filter_by(gmail_account_id=account_id, pdf_path=f"gmail:{message_id}").first()


def sync_account_messages(account: GmailAccount, max_results: int = 50, import_invoices: bool = True) -> dict[str, Any]:
    """Run Gmail sync and optionally import parsed messages as normal invoices."""
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
    imported_invoices = 0
    skipped_no_amount = 0
    skipped_duplicates = 0
    imported_preview: list[dict[str, Any]] = []

    for ref in refs:
        msg = (
            gmail.users()
            .messages()
            .get(
                userId="me",
                id=ref["id"],
                format="full",
            )
            .execute()
        )

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        subject = _extract_header(headers, "Subject")
        sender = _extract_header(headers, "From")
        date_header = _extract_header(headers, "Date")
        snippet = msg.get("snippet", "")
        body_text = _extract_body_text(payload)

        combined_text = f"{subject}\n{snippet}\n{body_text}".strip()
        has_payment_link = bool(_URL_RE.search(combined_text))
        has_invoice_hint = bool(_INVOICE_HINT_RE.search(combined_text))
        if has_payment_link:
            payment_link_hits += 1
        if has_invoice_hint:
            invoice_hint_hits += 1

        payment_link = _extract_payment_link(combined_text)
        amount, currency = _extract_amount_and_currency(combined_text)
        due_date = _extract_due_date(combined_text) or (datetime.utcnow().date() + timedelta(days=7))

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
                "amount_guess": amount,
                "currency_guess": currency,
                "payment_link_guess": payment_link,
            }
        )

        if not import_invoices:
            continue

        message_id = str(msg.get("id") or "")
        if message_id and _find_existing_import(account.id, message_id):
            skipped_duplicates += 1
            continue

        if amount is None:
            skipped_no_amount += 1
            continue

        invoice = Invoice(
            gmail_account_id=account.id,
            name=_build_invoice_name(subject, sender),
            amount=amount,
            currency=currency or "HUF",
            due_date=due_date,
            paid=False,
            payment_link=payment_link,
            pdf_path=f"gmail:{message_id}" if message_id else None,
            is_recurring=False,
        )
        db.session.add(invoice)
        db.session.flush()
        imported_invoices += 1
        imported_preview.append(invoice.to_dict())

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
        "import_invoices": import_invoices,
        "imported_invoices": imported_invoices,
        "skipped_no_amount": skipped_no_amount,
        "skipped_duplicates": skipped_duplicates,
        "imported_invoice_samples": imported_preview[:20],
        "sample_messages": previews[:20],
        "synced_at": account.last_sync.isoformat(),
    }
