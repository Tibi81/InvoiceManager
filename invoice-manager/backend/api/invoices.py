"""
Invoices API endpoints.
"""
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file
import io

from extensions import db
from models.database import Invoice
from services.qr_generator import generate_payment_qr

invoices_bp = Blueprint("invoices", __name__)


@invoices_bp.route("", methods=["GET"])
def get_invoices():
    """List invoices with optional status filter."""
    try:
        status = request.args.get("status", "all")
        account_id = request.args.get("account_id", type=int)
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)

        query = Invoice.query

        if status == "unpaid":
            query = query.filter_by(paid=False)
        elif status == "paid":
            query = query.filter_by(paid=True)

        if account_id:
            query = query.filter_by(gmail_account_id=account_id)

        query = query.order_by(Invoice.due_date.desc())
        invoices = query.limit(limit).offset(offset).all()

        return jsonify({
            "data": [inv.to_dict() for inv in invoices],
            "error": None,
        })
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500


@invoices_bp.route("/<int:invoice_id>", methods=["GET"])
def get_invoice(invoice_id: int):
    """Get single invoice details."""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        return jsonify({
            "data": invoice.to_dict(),
            "error": None,
        })
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500


@invoices_bp.route("", methods=["POST"])
def create_invoice():
    """Create a manual invoice (for testing / manual entry)."""
    try:
        data = request.get_json() or {}

        name = data.get("name")
        if not name or not str(name).strip():
            return jsonify({
                "data": None,
                "error": "Name is required",
            }), 400

        amount = data.get("amount")
        if amount is None:
            return jsonify({
                "data": None,
                "error": "Amount is required",
            }), 400
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return jsonify({
                "data": None,
                "error": "Amount must be a valid number",
            }), 400
        if amount <= 0:
            return jsonify({
                "data": None,
                "error": "Amount must be positive",
            }), 400

        due_date_str = data.get("due_date")
        if not due_date_str:
            return jsonify({
                "data": None,
                "error": "Due date is required",
            }), 400
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({
                "data": None,
                "error": "Due date must be YYYY-MM-DD format",
            }), 400

        invoice = Invoice(
            name=str(name).strip(),
            amount=amount,
            currency=data.get("currency", "HUF"),
            due_date=due_date,
            paid=False,
            gmail_account_id=data.get("gmail_account_id"),
            payment_link=data.get("payment_link"),
            iban=data.get("iban"),
            is_recurring=False,
        )
        db.session.add(invoice)
        db.session.commit()

        return jsonify({
            "data": invoice.to_dict(),
            "error": None,
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500


@invoices_bp.route("/<int:invoice_id>/pay", methods=["POST"])
def mark_paid(invoice_id: int):
    """Mark invoice as paid."""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        invoice.paid = True
        invoice.paid_date = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "data": {
                "id": invoice.id,
                "paid": invoice.paid,
                "paid_date": invoice.paid_date.isoformat(),
            },
            "error": None,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500


@invoices_bp.route("/<int:invoice_id>/qr", methods=["GET"])
def get_qr_code(invoice_id: int):
    """Generate QR code for invoice payment."""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        if not invoice.iban:
            return jsonify({
                "data": None,
                "error": "No IBAN available for this invoice",
            }), 400

        qr_bytes = generate_payment_qr(
            iban=invoice.iban,
            amount=float(invoice.amount),
            name=invoice.name,
        )

        return send_file(
            io.BytesIO(qr_bytes),
            mimetype="image/png",
            as_attachment=False,
            download_name=f"invoice_{invoice_id}_qr.png",
        )
    except Exception as e:
        return jsonify({"data": None, "error": str(e)}), 500


@invoices_bp.route("/<int:invoice_id>", methods=["DELETE"])
def delete_invoice(invoice_id: int):
    """Delete an invoice."""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        db.session.delete(invoice)
        db.session.commit()

        return jsonify({
            "data": {"deleted": True, "id": invoice_id},
            "error": None,
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"data": None, "error": str(e)}), 500
