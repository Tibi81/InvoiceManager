import { useState, useEffect } from 'react'

const RecurringForm = ({ recurring, onSubmit, onCancel }) => {
  const [name, setName] = useState('')
  const [amount, setAmount] = useState('')
  const [dayOfMonth, setDayOfMonth] = useState('15')

  useEffect(() => {
    if (recurring) {
      setName(recurring.name)
      setAmount(String(recurring.amount))
      setDayOfMonth(String(recurring.day_of_month))
    }
  }, [recurring])

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      name: name.trim(),
      amount: parseFloat(amount),
      day_of_month: parseInt(dayOfMonth, 10),
    })
  }

  const days = Array.from({ length: 31 }, (_, i) => i + 1)

  return (
    <form className="add-invoice-form recurring-form" onSubmit={handleSubmit}>
      <h3>{recurring ? 'Ismétlődő számla szerkesztése' : 'Új ismétlődő számla'}</h3>
      <div className="form-group">
        <label htmlFor="recurring-name">Név *</label>
        <input
          id="recurring-name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="pl. Netflix előfizetés"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="recurring-amount">Összeg (Ft) *</label>
        <input
          id="recurring-amount"
          type="number"
          min="1"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="3990"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="recurring-day">Hónap napja (1-31) *</label>
        <select
          id="recurring-day"
          value={dayOfMonth}
          onChange={(e) => setDayOfMonth(e.target.value)}
          required
        >
          {days.map((d) => (
            <option key={d} value={d}>
              {d}. nap
            </option>
          ))}
        </select>
      </div>
      <div className="form-actions">
        <button type="submit" className="btn btn-primary">
          {recurring ? 'Mentés' : 'Hozzáadás'}
        </button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Mégse
        </button>
      </div>
    </form>
  )
}

export default RecurringForm
