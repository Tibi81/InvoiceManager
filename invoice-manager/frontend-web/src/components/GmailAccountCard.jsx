import { useEffect, useState } from 'react'
import './GmailAccountCard.css'

const GmailAccountCard = ({
  account,
  onSave,
  onDelete,
  onToggleActive,
  onConnect,
  onSync,
  isSaving,
}) => {
  const [labelName, setLabelName] = useState(account.label_name || 'InvoiceManager')
  const [gmailQuery, setGmailQuery] = useState(account.gmail_query || '')

  useEffect(() => {
    setLabelName(account.label_name || 'InvoiceManager')
    setGmailQuery(account.gmail_query || '')
  }, [account.id, account.label_name, account.gmail_query])

  const handleSave = () => {
    onSave(account.id, {
      label_name: labelName,
      gmail_query: gmailQuery,
    })
  }

  return (
    <div className="gmail-card">
      <div className="gmail-card-header">
        <h3>{account.email}</h3>
        <div className="gmail-card-statuses">
          <span className={`badge status-${account.is_active ? 'paid' : 'unpaid'}`}>
            {account.is_active ? 'Aktiv' : 'Inaktiv'}
          </span>
          <span className={`badge status-${account.oauth_connected ? 'paid' : 'unpaid'}`}>
            {account.oauth_connected ? 'Google kapcsolva' : 'Nincs kapcsolva'}
          </span>
        </div>
      </div>

      <p className="gmail-hint">
        Gmail oldalon hozz letre egy cimket ezzel a nevvel, es a szuroiddel tedd ide a relevans leveleket.
      </p>

      <div className="gmail-form-group">
        <label htmlFor={`label-${account.id}`}>Gmail cimke neve</label>
        <input
          id={`label-${account.id}`}
          type="text"
          value={labelName}
          onChange={(e) => setLabelName(e.target.value)}
          placeholder="InvoiceManager"
        />
      </div>

      <div className="gmail-form-group">
        <label htmlFor={`query-${account.id}`}>Kiegeszito Gmail query</label>
        <textarea
          id={`query-${account.id}`}
          value={gmailQuery}
          onChange={(e) => setGmailQuery(e.target.value)}
          rows={3}
        />
      </div>

      <div className="gmail-card-actions">
        <button
          className="btn btn-secondary"
          onClick={() => onConnect(account.id)}
          disabled={isSaving}
        >
          {account.oauth_connected ? 'Ujracsatlakozas' : 'Google csatlakozas'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => onSync(account.id)}
          disabled={isSaving || !account.oauth_connected}
          title={account.oauth_connected ? '' : 'Elobb csatlakoztasd a Google fiokot'}
        >
          Szinkron
        </button>
        <button className="btn btn-primary" onClick={handleSave} disabled={isSaving}>
          Mentes
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => onToggleActive(account.id, !account.is_active)}
          disabled={isSaving}
        >
          {account.is_active ? 'Inaktivalas' : 'Aktivalas'}
        </button>
        <button className="btn btn-danger" onClick={() => onDelete(account.id)} disabled={isSaving}>
          Torles
        </button>
      </div>
    </div>
  )
}

export default GmailAccountCard
