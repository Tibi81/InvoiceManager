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

/** Napok száma a határidő és ma között. Pozitív = még hátra van, negatív = lejárt. */
function getDaysUntilDue(dueDateStr) {
  const due = new Date(dueDateStr)
  const today = new Date()
  due.setHours(0, 0, 0, 0)
  today.setHours(0, 0, 0, 0)
  return Math.floor((due - today) / (1000 * 60 * 60 * 24))
}

function getDueStatusText(dueDateStr, paid) {
  if (paid) return null
  const days = getDaysUntilDue(dueDateStr)
  if (days > 0) return `${days} nap van hátra`
  if (days < 0) return `${Math.abs(days)} nappal járt le`
  return 'Ma esedékes'
}

const InvoiceCard = ({ invoice, onMarkPaid, onDelete, isMarkingPaid }) => {
  const [showQr, setShowQr] = useState(false)
  const dueStatusText = getDueStatusText(invoice.due_date, invoice.paid)

  return (
    <div className="invoice-card">
      <div className="invoice-card-header">
        <h3>{invoice.name}</h3>
        <span className={`badge status-${invoice.paid ? 'paid' : 'unpaid'}`}>
          {invoice.paid ? 'Fizetve' : 'Fizetetlen'}
        </span>
        {invoice.is_recurring && <span className="badge recurring">Ismétlődő</span>}
      </div>
      <div className="invoice-card-body">
        <p className="amount">{formatAmount(invoice.amount, invoice.currency)}</p>
        <p className="due-date">Esedékesség: {formatDate(invoice.due_date)}</p>
        {dueStatusText && (
          <p className={`due-status ${getDaysUntilDue(invoice.due_date) < 0 ? 'overdue' : ''}`}>
            {dueStatusText}
          </p>
        )}
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
