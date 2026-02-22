import { useState, useEffect } from 'react'
import {
  getHealth,
  getInvoices,
  createInvoice,
  markPaid,
  deleteInvoice,
} from './services/api'
import InvoiceCard from './components/InvoiceCard'
import AddInvoiceForm from './components/AddInvoiceForm'
import './App.css'
import './components/InvoiceCard.css'
import './components/AddInvoiceForm.css'

const TABS = [
  { id: 'unpaid', label: 'Fizetetlen', status: 'unpaid' },
  { id: 'paid', label: 'Fizetett', status: 'paid' },
  { id: 'all', label: 'Összes', status: 'all' },
]

function App() {
  const [apiStatus, setApiStatus] = useState(null)
  const [invoices, setInvoices] = useState([])
  const [activeTab, setActiveTab] = useState('unpaid')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [markingPaidId, setMarkingPaidId] = useState(null)
  const [showAddForm, setShowAddForm] = useState(false)

  const loadHealth = async () => {
    try {
      const data = await getHealth()
      setApiStatus(data)
    } catch (err) {
      setApiStatus(null)
    }
  }

  const loadInvoices = async () => {
    setLoading(true)
    setError(null)
    try {
      const status = TABS.find((t) => t.id === activeTab)?.status || 'all'
      const data = await getInvoices(status)
      setInvoices(data || [])
    } catch (err) {
      setError(err.message)
      setInvoices([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHealth()
  }, [])

  useEffect(() => {
    if (apiStatus) {
      loadInvoices()
    }
  }, [apiStatus, activeTab])

  const handleMarkPaid = async (invoiceId) => {
    setMarkingPaidId(invoiceId)
    setError(null)
    try {
      await markPaid(invoiceId)
      await loadInvoices()
    } catch (err) {
      setError(err.message)
    } finally {
      setMarkingPaidId(null)
    }
  }

  const handleDelete = async (invoiceId) => {
    if (!window.confirm('Biztosan törölni szeretnéd ezt a számlát?')) return
    setError(null)
    try {
      await deleteInvoice(invoiceId)
      await loadInvoices()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleAddInvoice = async (data) => {
    setError(null)
    try {
      await createInvoice(data)
      setShowAddForm(false)
      await loadInvoices()
    } catch (err) {
      setError(err.message)
    }
  }

  if (!apiStatus) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>📧 Számla Kezelő</h1>
          <div className="status-card">
            <h2>Backend Állapot</h2>
            <p>❌ Backend nem elérhető</p>
            <p>Indítsd el a Flask API-t: <code>cd backend && python app.py</code></p>
            <button className="btn btn-secondary" onClick={loadHealth}>
              Újrapróbálás
            </button>
          </div>
        </header>
      </div>
    )
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>📧 Számla Kezelő</h1>
        <p className="subtitle">Invoice Manager</p>

        <div className="status-badge">
          ✅ Backend elérhető · v{apiStatus.version}
        </div>

        <div className="tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="actions">
          <button
            className="btn btn-primary"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? 'Mégse' : '+ Új számla'}
          </button>
          <button className="btn btn-secondary" onClick={loadInvoices}>
            🔄 Frissítés
          </button>
        </div>

        {showAddForm && (
          <AddInvoiceForm
            onSubmit={handleAddInvoice}
            onCancel={() => setShowAddForm(false)}
          />
        )}

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <div className="invoice-list">
          {loading ? (
            <p>Betöltés...</p>
          ) : invoices.length === 0 ? (
            <p className="empty-state">Nincs megjeleníthető számla</p>
          ) : (
            invoices.map((invoice) => (
              <InvoiceCard
                key={invoice.id}
                invoice={invoice}
                onMarkPaid={handleMarkPaid}
                onDelete={handleDelete}
                isMarkingPaid={markingPaidId === invoice.id}
              />
            ))
          )}
        </div>
      </header>
    </div>
  )
}

export default App
