import { useState } from 'react'
import { getQrUrl } from '../services/api'

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatAmount = (amount, currency = 'HUF') => {
  return new Intl.NumberFormat('hu-HU').format(amount) + ' ' + currency
}

const InvoiceCard = ({ invoice, onMarkPaid, onDelete, isMarkingPaid }) => {
  const [showQr, setShowQr] = useState(false)

  return (
    <div className="invoice-card">
      <div className="invoice-card-header">
        <h3>{invoice.name}</h3>
        {invoice.is_recurring && <span className="badge recurring">Ismétlődő</span>}
      </div>
      <div className="invoice-card-body">
        <p className="amount">{formatAmount(invoice.amount, invoice.currency)}</p>
        <p className="due-date">Esedékesség: {formatDate(invoice.due_date)}</p>
        {invoice.gmail_account_email && (
          <p className="account">📧 {invoice.gmail_account_email}</p>
        )}
      </div>
      <div className="invoice-card-actions">
        {!invoice.paid && (
          <button
            className="btn btn-primary"
            onClick={() => onMarkPaid(invoice.id)}
            disabled={isMarkingPaid}
          >
            Fizetve
          </button>
        )}
        {invoice.has_payment_link && (
          <a
            href={invoice.payment_link}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary"
          >
            Fizetési link
          </a>
        )}
        {invoice.has_qr && (
          <button
            className="btn btn-secondary"
            onClick={() => setShowQr(!showQr)}
          >
            {showQr ? 'QR elrejtése' : 'QR kód'}
          </button>
        )}
        <button
          className="btn btn-danger"
          onClick={() => onDelete(invoice.id)}
          title="Törlés"
        >
          🗑️
        </button>
      </div>
      {showQr && invoice.has_qr && (
        <div className="invoice-qr">
          <img
            src={getQrUrl(invoice.id)}
            alt={`QR kód: ${invoice.name}`}
            width={200}
            height={200}
          />
        </div>
      )}
    </div>
  )
}

export default InvoiceCard
