"""Gmail accounts API endpoints."""

from __future__ import annotations

import re
from urllib.parse import urlencode

from flask import Blueprint, current_app, jsonify, redirect, request

from extensions import db
from models.database import GmailAccount
from services.gmail_filters import (
    DEFAULT_GMAIL_QUERY,
    DEFAULT_LABEL_NAME,
    embed_filter_settings,
    extract_filter_settings,
    has_oauth_credentials,
    normalize_filter_settings,
)
from services.gmail_service import (
    GmailServiceError,
    complete_oauth_callback,
    connect_account_local_oauth,
    create_oauth_authorization_url,
    sync_account_messages,
)

accounts_bp = Blueprint("accounts", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _account_to_dict(account: GmailAccount) -> dict:
    base = account.to_dict()
    label_name, gmail_query = extract_filter_settings(account.credentials_json)
    base["label_name"] = label_name
    base["gmail_query"] = gmail_query
    base["oauth_connected"] = has_oauth_credentials(account.credentials_json)
    return base


@accounts_bp.route("", methods=["GET"])
def get_accounts():
    """List all Gmail accounts with invoice filter settings."""
    try:
        accounts = GmailAccount.query.order_by(GmailAccount.email).all()
        return jsonify({
            "data": [_account_to_dict(a) for a in accounts],
            "error": None,
        })
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500


@accounts_bp.route("/defaults", methods=["GET"])
def get_account_defaults():
    """Return default filter settings used for new accounts."""
    return jsonify({
        "data": {
            "default_label_name": DEFAULT_LABEL_NAME,
            "default_gmail_query": DEFAULT_GMAIL_QUERY,
            "note": "Use a dedicated Gmail label and keep query focused on invoices/payment links.",
        },
        "error": None,
    })


@accounts_bp.route("", methods=["POST"])
def create_account():
    """Create a Gmail account settings record (OAuth data can be added later)."""
    try:
        data = request.get_json() or {}

        email = str(data.get("email", "")).strip().lower()
        if not email:
            return jsonify({"data": None, "error": "Email is required"}), 400
        if not EMAIL_RE.match(email):
            return jsonify({"data": None, "error": "Invalid email format"}), 400

        label_name, gmail_query = normalize_filter_settings(
            data.get("label_name"),
            data.get("gmail_query"),
        )

        if len(label_name) > 120:
            return jsonify({"data": None, "error": "Label name is too long (max 120)"}), 400
        if len(gmail_query) > 1000:
            return jsonify({"data": None, "error": "Gmail query is too long (max 1000)"}), 400

        account = GmailAccount.query.filter_by(email=email).first()
        if account:
            account.credentials_json = embed_filter_settings(account.credentials_json, label_name, gmail_query)
            if "is_active" in data:
                account.is_active = bool(data.get("is_active"))
        else:
            account = GmailAccount(
                email=email,
                is_active=bool(data.get("is_active", True)),
                credentials_json=embed_filter_settings("{}", label_name, gmail_query),
            )
            db.session.add(account)

        db.session.commit()

        return jsonify({
            "data": _account_to_dict(account),
            "error": None,
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500


@accounts_bp.route("/<int:account_id>/filters", methods=["PUT"])
def update_account_filters(account_id: int):
    """Update label/query filters for one Gmail account."""
    try:
        account = GmailAccount.query.get_or_404(account_id)
        data = request.get_json() or {}

        current_label, current_query = extract_filter_settings(account.credentials_json)
        label_name, gmail_query = normalize_filter_settings(
            data.get("label_name", current_label),
            data.get("gmail_query", current_query),
        )

        if len(label_name) > 120:
            return jsonify({"data": None, "error": "Label name is too long (max 120)"}), 400
        if len(gmail_query) > 1000:
            return jsonify({"data": None, "error": "Gmail query is too long (max 1000)"}), 400

        account.credentials_json = embed_filter_settings(account.credentials_json, label_name, gmail_query)

        if "is_active" in data:
            account.is_active = bool(data.get("is_active"))

        db.session.commit()

        return jsonify({
            "data": _account_to_dict(account),
            "error": None,
        })
    except GmailServiceError as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500


@accounts_bp.route("/<int:account_id>/oauth/start", methods=["POST"])
def start_account_oauth(account_id: int):
    """Start OAuth for one Gmail account."""
    try:
        account = GmailAccount.query.get_or_404(account_id)
        oauth_mode = str(current_app.config.get("GMAIL_OAUTH_MODE", "desktop")).strip().lower()
        if oauth_mode == "desktop":
            connected = connect_account_local_oauth(account)
            return jsonify({
                "data": {
                    "account_id": connected.id,
                    "email": connected.email,
                    "mode": "desktop",
                    "connected": True,
                },
                "error": None,
            })

        auth_url = create_oauth_authorization_url(account)
        return jsonify({
            "data": {
                "account_id": account.id,
                "email": account.email,
                "mode": "web",
                "authorization_url": auth_url,
            },
            "error": None,
        })
    except GmailServiceError as e:
        return jsonify({"data": None, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500


@accounts_bp.route("/oauth/callback", methods=["GET"])
def oauth_callback():
    """Handle Google OAuth callback and redirect back to frontend."""
    oauth_mode = str(current_app.config.get("GMAIL_OAUTH_MODE", "desktop")).strip().lower()
    if oauth_mode == "desktop":
        query = urlencode({"gmail_oauth": "error", "error": "Callback endpoint is not used in desktop mode"})
        frontend_base = current_app.config.get("FRONTEND_BASE_URL", "http://localhost:5173")
        return redirect(f"{frontend_base}/?{query}")

    frontend_base = current_app.config.get("FRONTEND_BASE_URL", "http://localhost:5173")
    error = request.args.get("error")
    code = request.args.get("code")
    state = request.args.get("state")

    if error:
        query = urlencode({"gmail_oauth": "error", "error": error})
        return redirect(f"{frontend_base}/?{query}")

    try:
        account = complete_oauth_callback(state=state or "", code=code or "")
        query = urlencode({
            "gmail_oauth": "success",
            "account_id": account.id,
            "email": account.email,
        })
        return redirect(f"{frontend_base}/?{query}")
    except GmailServiceError as e:
        query = urlencode({"gmail_oauth": "error", "error": str(e)})
        return redirect(f"{frontend_base}/?{query}")
    except Exception:
        query = urlencode({"gmail_oauth": "error", "error": "Unexpected OAuth callback error"})
        return redirect(f"{frontend_base}/?{query}")


@accounts_bp.route("/<int:account_id>/sync", methods=["POST"])
def sync_account(account_id: int):
    """Run Gmail sync preview using saved filters for one account."""
    try:
        account = GmailAccount.query.get_or_404(account_id)
        payload = request.get_json(silent=True) or {}
        try:
            max_results = int(payload.get("max_results", current_app.config.get("GMAIL_SYNC_MAX_RESULTS", 50)))
        except (TypeError, ValueError):
            return jsonify({"data": None, "error": "max_results must be an integer"}), 400
        result = sync_account_messages(account, max_results=max_results)
        return jsonify({"data": result, "error": None})
    except GmailServiceError as e:
        return jsonify({"data": None, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500


@accounts_bp.route("/<int:account_id>", methods=["DELETE"])
def delete_account(account_id: int):
    """Delete Gmail account settings record."""
    try:
        account = GmailAccount.query.get_or_404(account_id)
        db.session.delete(account)
        db.session.commit()

        return jsonify({
            "data": {"deleted": True, "id": account_id},
            "error": None,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500
