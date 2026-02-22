"""
QR code generation for SEPA/EPC payments.
"""
import io
from segno import helpers


def generate_payment_qr(
    iban: str,
    amount: float,
    name: str,
    reference: str = "",
    scale: int = 5,
) -> bytes:
    """
    Generate EPC QR code for SEPA payment.

    Args:
        iban: Recipient IBAN (without spaces)
        amount: Payment amount
        name: Recipient name
        reference: Payment reference (optional)
        scale: QR code scale/size (default 5)

    Returns:
        PNG image as bytes
    """
    # Clean IBAN - remove spaces
    iban_clean = iban.replace(" ", "").strip()

    # EPC QR requires text or reference (ISO 11649) - use name as fallback
    ref_text = reference.strip() if reference else name

    qr = helpers.make_epc_qr(
        name=name,
        iban=iban_clean,
        amount=amount,
        text=ref_text,
    )

    buffer = io.BytesIO()
    qr.save(buffer, kind="png", scale=scale)
    return buffer.getvalue()
