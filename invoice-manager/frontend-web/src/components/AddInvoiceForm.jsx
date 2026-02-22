import { useState } from 'react'

const AddInvoiceForm = ({ onSubmit, onCancel }) => {
  const today = new Date().toISOString().slice(0, 10)
  const [name, setName] = useState('')
  const [amount, setAmount] = useState('')
  const [dueDate, setDueDate] = useState(today)
  const [iban, setIban] = useState('')
  const [paymentLink, setPaymentLink] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      name: name.trim(),
      amount: parseFloat(amount),
      due_date: dueDate,
      iban: iban.trim() || undefined,
      payment_link: paymentLink.trim() || undefined,
    })
  }

  return (
    <form className="add-invoice-form" onSubmit={handleSubmit}>
      <h3>Új számla hozzáadása</h3>
      <div className="form-group">
        <label htmlFor="name">Számla neve *</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="pl. Telekom számla"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="amount">Összeg (Ft) *</label>
        <input
          id="amount"
          type="number"
          min="1"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="8500"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="dueDate">Esedékesség *</label>
        <input
          id="dueDate"
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="iban">IBAN (QR kódhoz)</label>
        <input
          id="iban"
          type="text"
          value={iban}
          onChange={(e) => setIban(e.target.value)}
          placeholder="HU42 1177 3016 1111 1018 0000 0000"
        />
      </div>
      <div className="form-group">
        <label htmlFor="paymentLink">Fizetési link</label>
        <input
          id="paymentLink"
          type="url"
          value={paymentLink}
          onChange={(e) => setPaymentLink(e.target.value)}
          placeholder="https://..."
        />
      </div>
      <div className="form-actions">
        <button type="submit" className="btn btn-primary">
          Hozzáadás
        </button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Mégse
        </button>
      </div>
    </form>
  )
}

export default AddInvoiceForm
