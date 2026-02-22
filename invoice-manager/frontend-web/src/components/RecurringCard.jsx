import React from 'react'
import './RecurringCard.css'

const formatAmount = (amount, currency = 'HUF') => {
  return new Intl.NumberFormat('hu-HU').format(amount) + ' ' + currency
}

const formatDate = (dateInput) => {
  return new Date(dateInput).toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const getClampedDate = (year, month, dayOfMonth) => {
  const lastDayOfMonth = new Date(year, month + 1, 0).getDate()
  const safeDay = Math.min(dayOfMonth, lastDayOfMonth)
  return new Date(year, month, safeDay)
}

const getNextDueDate = (dayOfMonth) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  let nextDue = getClampedDate(today.getFullYear(), today.getMonth(), dayOfMonth)
  if (nextDue < today) {
    nextDue = getClampedDate(today.getFullYear(), today.getMonth() + 1, dayOfMonth)
  }

  return nextDue
}

const getDaysUntilDate = (targetDate) => {
  const date = new Date(targetDate)
  const today = new Date()
  date.setHours(0, 0, 0, 0)
  today.setHours(0, 0, 0, 0)
  return Math.floor((date - today) / (1000 * 60 * 60 * 24))
}

const getDueStatusText = (dayOfMonth, isActive) => {
  if (!isActive) return null

  const nextDue = getNextDueDate(dayOfMonth)
  const days = getDaysUntilDate(nextDue)

  if (days > 0) return `${days} nap van hatra`
  return 'Ma esedekes'
}

const RecurringCard = ({ recurring, onPause, onDelete, onEdit }) => {
  const nextDueDate = getNextDueDate(recurring.day_of_month)
  const dueStatusText = getDueStatusText(recurring.day_of_month, recurring.is_active)

  return (
    <div className="recurring-card">
      <div className="recurring-card-header">
        <h3>{recurring.name}</h3>
        {!recurring.is_active && (
          <span className="badge paused">Szüneteltetve</span>
        )}
      </div>
      <div className="recurring-card-body">
        <p className="amount">{formatAmount(recurring.amount, recurring.currency)}</p>
        <p className="day">Hónap {recurring.day_of_month}. napján</p>
        <p className="due-date">Következő esedékesség: {formatDate(nextDueDate)}</p>
        {dueStatusText && <p className="due-status">{dueStatusText}</p>}
      </div>
      <div className="recurring-card-actions">
        <button
          className="btn btn-secondary"
          onClick={() => onPause(recurring.id)}
        >
          {recurring.is_active ? 'Szüneteltetés' : 'Folytatás'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => onEdit(recurring)}
        >
          Szerkesztés
        </button>
        <button
          className="btn btn-danger"
          onClick={() => onDelete(recurring.id)}
        >
          🗑️ Törlés
        </button>
      </div>
    </div>
  )
}

export default RecurringCard
