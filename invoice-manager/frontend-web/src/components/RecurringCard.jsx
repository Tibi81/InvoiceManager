import React from 'react'
import './RecurringCard.css'

const formatAmount = (amount, currency = 'HUF') => {
  return new Intl.NumberFormat('hu-HU').format(amount) + ' ' + currency
}

const RecurringCard = ({ recurring, onPause, onDelete, onEdit }) => {
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
