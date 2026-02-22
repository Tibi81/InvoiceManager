import { useState, useEffect } from 'react'
import {
  getHealth,
  getInvoices,
  createInvoice,
  markPaid,
  deleteInvoice,
  getRecurring,
  createRecurring,
  updateRecurring,
  deleteRecurring,
  pauseRecurring,
} from './services/api'
import InvoiceCard from './components/InvoiceCard'
import AddInvoiceForm from './components/AddInvoiceForm'
import RecurringCard from './components/RecurringCard'
import RecurringForm from './components/RecurringForm'
import './App.css'
import './components/InvoiceCard.css'
import './components/AddInvoiceForm.css'

const INVOICE_TABS = [
  { id: 'unpaid', label: 'Fizetetlen', status: 'unpaid' },
  { id: 'paid', label: 'Fizetett', status: 'paid' },
  { id: 'all', label: 'Összes', status: 'all' },
]

const MAIN_VIEWS = [
  { id: 'invoices', label: 'Számlák' },
  { id: 'recurring', label: 'Ismétlődő számlák' },
]

function App() {
  const [apiStatus, setApiStatus] = useState(null)
  const [mainView, setMainView] = useState('invoices')
  const [invoices, setInvoices] = useState([])
  const [recurring, setRecurring] = useState([])
  const [activeTab, setActiveTab] = useState('unpaid')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [markingPaidId, setMarkingPaidId] = useState(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [showRecurringForm, setShowRecurringForm] = useState(false)
  const [editingRecurring, setEditingRecurring] = useState(null)

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
      const status = INVOICE_TABS.find((t) => t.id === activeTab)?.status || 'all'
      const data = await getInvoices(status)
      setInvoices(data || [])
    } catch (err) {
      setError(err.message)
      setInvoices([])
    } finally {
      setLoading(false)
    }
  }

  const loadRecurring = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getRecurring()
      setRecurring(data || [])
    } catch (err) {
      setError(err.message)
      setRecurring([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHealth()
  }, [])

  useEffect(() => {
    if (apiStatus) {
      if (mainView === 'invoices') loadInvoices()
      else loadRecurring()
    }
  }, [apiStatus, activeTab, mainView])

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

  const handleAddRecurring = async (data) => {
    setError(null)
    try {
      await createRecurring(data)
      setShowRecurringForm(false)
      await loadRecurring()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleUpdateRecurring = async (data) => {
    if (!editingRecurring) return
    setError(null)
    try {
      await updateRecurring(editingRecurring.id, data)
      setShowRecurringForm(false)
      setEditingRecurring(null)
      await loadRecurring()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleRecurringSubmit = (data) => {
    if (editingRecurring) handleUpdateRecurring(data)
    else handleAddRecurring(data)
  }

  const handlePauseRecurring = async (id) => {
    setError(null)
    try {
      await pauseRecurring(id)
      await loadRecurring()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeleteRecurring = async (id) => {
    if (!window.confirm('Biztosan törölni szeretnéd ezt az ismétlődő számlát?')) return
    setError(null)
    try {
      await deleteRecurring(id)
      await loadRecurring()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleEditRecurring = (rec) => {
    setEditingRecurring(rec)
    setShowRecurringForm(true)
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

        <div className="main-tabs">
          {MAIN_VIEWS.map((view) => (
            <button
              key={view.id}
              className={`main-tab ${mainView === view.id ? 'active' : ''}`}
              onClick={() => setMainView(view.id)}
            >
              {view.label}
            </button>
          ))}
        </div>

        {mainView === 'invoices' && (
          <>
            <div className="tabs">
              {INVOICE_TABS.map((tab) => (
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
          </>
        )}

        {mainView === 'recurring' && (
          <>
            <div className="actions">
              <button
                className="btn btn-primary"
                onClick={() => {
                  setEditingRecurring(null)
                  setShowRecurringForm(!showRecurringForm)
                }}
              >
                {showRecurringForm ? 'Mégse' : '+ Új ismétlődő'}
              </button>
              <button className="btn btn-secondary" onClick={loadRecurring}>
                🔄 Frissítés
              </button>
            </div>

            {showRecurringForm && (
              <RecurringForm
                recurring={editingRecurring}
                onSubmit={handleRecurringSubmit}
                onCancel={() => {
                  setShowRecurringForm(false)
                  setEditingRecurring(null)
                }}
              />
            )}

            <div className="invoice-list">
              {loading ? (
                <p>Betöltés...</p>
              ) : recurring.length === 0 ? (
                <p className="empty-state">Nincs ismétlődő számla</p>
              ) : (
                recurring.map((rec) => (
                  <RecurringCard
                    key={rec.id}
                    recurring={rec}
                    onPause={handlePauseRecurring}
                    onDelete={handleDeleteRecurring}
                    onEdit={handleEditRecurring}
                  />
                ))
              )}
            </div>
          </>
        )}

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}
      </header>
    </div>
  )
}

export default App
