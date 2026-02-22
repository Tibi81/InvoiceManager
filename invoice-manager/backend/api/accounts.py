"""
Gmail accounts API endpoints.
Placeholder for Phase 2 - Gmail integration.
"""
from flask import Blueprint, jsonify

from models.database import GmailAccount

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("", methods=["GET"])
def get_accounts():
    """List all Gmail accounts."""
    try:
        accounts = GmailAccount.query.order_by(GmailAccount.email).all()
        return jsonify({
            "data": [a.to_dict() for a in accounts],
            "error": None,
        })
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500
