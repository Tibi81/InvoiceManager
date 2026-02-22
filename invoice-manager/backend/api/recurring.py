"""
Recurring invoices API endpoints.
"""
from flask import Blueprint, jsonify, request

from extensions import db
from models.database import RecurringInvoice

recurring_bp = Blueprint("recurring", __name__)


def _validate_recurring_data(data: dict, for_update: bool = False) -> tuple[dict | None, str | None]:
    """Validate recurring invoice data. Returns (validated_data, error_message)."""
    result = {}

    if not for_update or "name" in data:
        name = data.get("name")
        if not for_update and (not name or not str(name).strip()):
            return None, "Name is required"
        if name is not None:
            if not str(name).strip():
                return None, "Name cannot be empty"
            result["name"] = str(name).strip()

    if not for_update or "amount" in data:
        amount = data.get("amount")
        if not for_update and amount is None:
            return None, "Amount is required"
        if amount is not None:
            try:
                amount = float(amount)
            except (TypeError, ValueError):
                return None, "Amount must be a valid number"
            if amount <= 0:
                return None, "Amount must be positive"
            result["amount"] = amount

    if not for_update or "day_of_month" in data:
        day_of_month = data.get("day_of_month")
        if not for_update and day_of_month is None:
            return None, "Day of month is required"
        if day_of_month is not None:
            try:
                day_of_month = int(day_of_month)
            except (TypeError, ValueError):
                return None, "Day of month must be 1-31"
            if not 1 <= day_of_month <= 31:
                return None, "Day of month must be between 1 and 31"
            result["day_of_month"] = day_of_month

    if "currency" in data:
        result["currency"] = data.get("currency", "HUF")

    return result, None


@recurring_bp.route("", methods=["GET"])
def get_recurring():
    """List all recurring invoice templates."""
    try:
        recurring = RecurringInvoice.query.order_by(RecurringInvoice.name).all()
        return jsonify({
            "data": [r.to_dict() for r in recurring],
            "error": None,
        })
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500


@recurring_bp.route("/<int:recurring_id>", methods=["GET"])
def get_recurring_one(recurring_id: int):
    """Get recurring invoice details."""
    try:
        recurring = RecurringInvoice.query.get_or_404(recurring_id)
        return jsonify({
            "data": recurring.to_dict(),
            "error": None,
        })
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500


@recurring_bp.route("", methods=["POST"])
def create_recurring():
    """Create a new recurring invoice template."""
    try:
        data = request.get_json() or {}
        validated, err = _validate_recurring_data(data, for_update=False)
        if err:
            return jsonify({"data": None, "error": err}), 400
        if "name" not in validated or "amount" not in validated or "day_of_month" not in validated:
            return jsonify({"data": None, "error": "Name, amount and day_of_month are required"}), 400

        recurring = RecurringInvoice(
            name=validated["name"],
            amount=validated["amount"],
            currency=validated.get("currency", "HUF"),
            day_of_month=validated["day_of_month"],
            is_active=True,
        )
        db.session.add(recurring)
        db.session.commit()

        return jsonify({
            "data": recurring.to_dict(),
            "error": None,
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500


@recurring_bp.route("/<int:recurring_id>", methods=["PUT"])
def update_recurring(recurring_id: int):
    """Update recurring invoice template."""
    try:
        recurring = RecurringInvoice.query.get_or_404(recurring_id)
        data = request.get_json() or {}

        validated, err = _validate_recurring_data(data, for_update=True)
        if err:
            return jsonify({"data": None, "error": err}), 400

        if "name" in validated:
            recurring.name = validated["name"]
        if "amount" in validated:
            recurring.amount = validated["amount"]
        if "day_of_month" in validated:
            recurring.day_of_month = validated["day_of_month"]
        if "currency" in validated:
            recurring.currency = validated["currency"]

        db.session.commit()

        return jsonify({
            "data": recurring.to_dict(),
            "error": None,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500


@recurring_bp.route("/<int:recurring_id>/pause", methods=["POST"])
def pause_recurring(recurring_id: int):
    """Toggle pause/unpause for recurring invoice."""
    try:
        recurring = RecurringInvoice.query.get_or_404(recurring_id)
        recurring.is_active = not recurring.is_active
        db.session.commit()

        return jsonify({
            "data": {
                "id": recurring.id,
                "is_active": recurring.is_active,
            },
            "error": None,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500


@recurring_bp.route("/<int:recurring_id>", methods=["DELETE"])
def delete_recurring(recurring_id: int):
    """Delete recurring invoice template."""
    try:
        recurring = RecurringInvoice.query.get_or_404(recurring_id)
        db.session.delete(recurring)
        db.session.commit()

        return jsonify({
            "data": {"deleted": True, "id": recurring_id},
            "error": None,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500
