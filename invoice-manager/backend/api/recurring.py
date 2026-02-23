"""
Recurring invoices API endpoints.
"""
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

from extensions import db
from models.database import Invoice, RecurringInvoice
from services.recurring_generator import forecast_recurring_due_dates
from services.recurring_scheduler import (
    get_recurring_run_status,
    run_recurring_generation_for_date,
)

recurring_bp = Blueprint("recurring", __name__)


def _validate_recurring_data(
    data: dict,
    for_update: bool = False,
) -> tuple[dict | None, str | None]:
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


def _get_recurring_or_404(recurring_id: int):
    recurring = db.session.get(RecurringInvoice, recurring_id)
    if recurring is None:
        return None, (
            jsonify({"data": None, "error": "Recurring invoice not found"}),
            404,
        )
    return recurring, None


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
        recurring, err = _get_recurring_or_404(recurring_id)
        if err:
            return err
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
        if (
            "name" not in validated
            or "amount" not in validated
            or "day_of_month" not in validated
        ):
            return jsonify({
                "data": None,
                "error": "Name, amount and day_of_month are required",
            }), 400

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
        recurring, err = _get_recurring_or_404(recurring_id)
        if err:
            return err
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
        recurring, err = _get_recurring_or_404(recurring_id)
        if err:
            return err
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
        recurring, err = _get_recurring_or_404(recurring_id)
        if err:
            return err
        db.session.delete(recurring)
        db.session.commit()

        return jsonify({
            "data": {"deleted": True, "id": recurring_id},
            "error": None,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500


@recurring_bp.route("/<int:recurring_id>/forecast", methods=["GET"])
def recurring_forecast(recurring_id: int):
    """Forecast upcoming due dates for one recurring template."""
    try:
        recurring, err = _get_recurring_or_404(recurring_id)
        if err:
            return err

        months_raw = request.args.get("months", "3")
        try:
            months = int(months_raw)
        except (TypeError, ValueError):
            return jsonify({"data": None, "error": "months must be an integer"}), 400
        if months < 1 or months > 24:
            return jsonify({"data": None, "error": "months must be between 1 and 24"}), 400

        from_date_raw = request.args.get("from_date")
        if from_date_raw:
            try:
                from_date = datetime.strptime(from_date_raw, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"data": None, "error": "from_date must be YYYY-MM-DD"}), 400
        else:
            from_date = datetime.now(timezone.utc).date()

        due_dates = forecast_recurring_due_dates(
            template=recurring,
            months=months,
            from_date=from_date,
        )

        existing_dates = {
            inv.due_date.isoformat()
            for inv in Invoice.query.filter(
                Invoice.recurring_invoice_id == recurring.id,
                Invoice.is_recurring.is_(True),
                Invoice.due_date.in_(due_dates),
            ).all()
        }

        forecast = [
            {
                "due_date": due_date.isoformat(),
                "already_generated": due_date.isoformat() in existing_dates,
            }
            for due_date in due_dates
        ]

        return jsonify({
            "data": {
                "recurring_id": recurring.id,
                "is_active": recurring.is_active,
                "months": months,
                "from_date": from_date.isoformat(),
                "forecast": forecast,
            },
            "error": None,
        })
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500


@recurring_bp.route("/run-now", methods=["POST"])
def run_recurring_now():
    """Trigger recurring invoice generation immediately."""
    try:
        payload = request.get_json(silent=True) or {}
        run_date_raw = payload.get("run_date")
        if run_date_raw:
            try:
                run_date = datetime.strptime(str(run_date_raw), "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"data": None, "error": "run_date must be YYYY-MM-DD"}), 400
        else:
            run_date = datetime.now(timezone.utc).date()

        result = run_recurring_generation_for_date(run_date)
        return jsonify({
            "data": {
                "run_date": run_date.isoformat(),
                "result": result,
            },
            "error": None,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500


@recurring_bp.route("/run-status", methods=["GET"])
def recurring_run_status():
    """Return scheduler and last-run status for recurring generation."""
    status = get_recurring_run_status()
    status["scheduler_enabled"] = bool(
        current_app.config.get("RECURRING_SCHEDULER_ENABLED", True)
    )
    status["scheduler_interval_seconds"] = int(current_app.config.get(
        "RECURRING_SCHEDULER_INTERVAL_SECONDS",
        300,
    ))
    return jsonify({
        "data": status,
        "error": None,
    })
