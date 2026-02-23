"""
Database models for Invoice Manager.
"""
from datetime import datetime, timezone
from extensions import db


def _utc_now_naive() -> datetime:
    """Return UTC now as naive datetime for DB fields."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class GmailAccount(db.Model):
    """Gmail account for fetching invoices."""
    
    __tablename__ = 'gmail_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_sync = db.Column(db.DateTime, nullable=True)
    credentials_json = db.Column(db.Text, nullable=False)  # Encrypted OAuth tokens
    created_at = db.Column(db.DateTime, default=_utc_now_naive, nullable=False)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='gmail_account', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'is_active': self.is_active,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<GmailAccount {self.email}>'


class Invoice(db.Model):
    """Invoice from email or recurring template."""
    
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    gmail_account_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='HUF', nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid = db.Column(db.Boolean, default=False, nullable=False)
    paid_date = db.Column(db.DateTime, nullable=True)
    payment_link = db.Column(db.Text, nullable=True)
    pdf_path = db.Column(db.String(500), nullable=True)
    iban = db.Column(db.String(34), nullable=True)  # For QR code generation
    is_recurring = db.Column(db.Boolean, default=False, nullable=False)
    recurring_invoice_id = db.Column(db.Integer, db.ForeignKey('recurring_invoices.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=_utc_now_naive, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'gmail_account_id': self.gmail_account_id,
            'gmail_account_email': self.gmail_account.email if self.gmail_account else None,
            'name': self.name,
            'amount': float(self.amount),
            'currency': self.currency,
            'due_date': self.due_date.isoformat(),
            'paid': self.paid,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'payment_link': self.payment_link,
            'pdf_path': self.pdf_path,
            'iban': self.iban,
            'is_recurring': self.is_recurring,
            'recurring_invoice_id': self.recurring_invoice_id,
            'created_at': self.created_at.isoformat(),
            'has_qr': self.iban is not None,
            'has_payment_link': self.payment_link is not None
        }
    
    def __repr__(self):
        return f'<Invoice {self.name} - {self.amount} {self.currency}>'


class RecurringInvoice(db.Model):
    """Recurring invoice template."""
    
    __tablename__ = 'recurring_invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='HUF', nullable=False)
    day_of_month = db.Column(db.Integer, nullable=False)  # 1-31
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_generated = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=_utc_now_naive, nullable=False)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='recurring_template', lazy=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'amount': float(self.amount),
            'currency': self.currency,
            'day_of_month': self.day_of_month,
            'is_active': self.is_active,
            'last_generated': self.last_generated.isoformat() if self.last_generated else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<RecurringInvoice {self.name} - Day {self.day_of_month}>'
