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
  getAccounts,
  createAccount,
  updateAccountFilters,
  deleteAccount,
  getAccountDefaults,
  startAccountOAuth,
  syncAccount,
} from './services/api'
import InvoiceCard from './components/InvoiceCard'
import AddInvoiceForm from './components/AddInvoiceForm'
import RecurringCard from './components/RecurringCard'
import RecurringForm from './components/RecurringForm'
import GmailAccountCard from './components/GmailAccountCard'
import './App.css'
import './components/InvoiceCard.css'
import './components/AddInvoiceForm.css'

const INVOICE_TABS = [
  { id: 'unpaid', label: 'Fizetetlen', status: 'unpaid' },
  { id: 'paid', label: 'Fizetett', status: 'paid' },
  { id: 'all', label: 'Osszes', status: 'all' },
]

const MAIN_VIEWS = [
  { id: 'invoices', label: 'Szamlak' },
  { id: 'recurring', label: 'Ismetlodo szamlak' },
  { id: 'gmail', label: 'Gmail szures' },
]

function App() {
  const [apiStatus, setApiStatus] = useState(null)
  const [mainView, setMainView] = useState('invoices')
  const [invoices, setInvoices] = useState([])
  const [recurring, setRecurring] = useState([])
  const [accounts, setAccounts] = useState([])
  const [accountDefaults, setAccountDefaults] = useState(null)
  const [activeTab, setActiveTab] = useState('unpaid')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [markingPaidId, setMarkingPaidId] = useState(null)
  const [savingAccountId, setSavingAccountId] = useState(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [showRecurringForm, setShowRecurringForm] = useState(false)
  const [showAddAccountForm, setShowAddAccountForm] = useState(false)
  const [newAccountEmail, setNewAccountEmail] = useState('')
  const [syncSummaries, setSyncSummaries] = useState({})
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

  const loadAccounts = async () => {
    setLoading(true)
    setError(null)
    try {
      const [accountsData, defaultsData] = await Promise.all([
        getAccounts(),
        getAccountDefaults(),
      ])
      setAccounts(accountsData || [])
      setAccountDefaults(defaultsData)
    } catch (err) {
      setError(err.message)
      setAccounts([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHealth()
  }, [])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const oauthStatus = params.get('gmail_oauth')
    if (!oauthStatus) return

    if (oauthStatus === 'success') {
      setError(null)
      loadAccounts()
    } else if (oauthStatus === 'error') {
      setError(params.get('error') || 'OAuth hiba')
    }

    const cleanUrl = `${window.location.pathname}${window.location.hash || ''}`
    window.history.replaceState({}, document.title, cleanUrl)
  }, [])

  useEffect(() => {
    if (!apiStatus) return

    if (mainView === 'invoices') loadInvoices()
    if (mainView === 'recurring') loadRecurring()
    if (mainView === 'gmail') loadAccounts()
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
    if (!window.confirm('Biztosan torolni szeretned ezt a szamlat?')) return
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
    if (!window.confirm('Biztosan torolni szeretned ezt az ismetlodo szamlat?')) return
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

  const handleAddAccount = async (event) => {
    event.preventDefault()
    const email = newAccountEmail.trim()
    if (!email) return

    setError(null)
    setSavingAccountId('new')
    try {
      await createAccount({
        email,
        label_name: accountDefaults?.default_label_name,
        gmail_query: accountDefaults?.default_gmail_query,
      })
      setNewAccountEmail('')
      setShowAddAccountForm(false)
      await loadAccounts()
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingAccountId(null)
    }
  }

  const handleSaveAccount = async (id, payload) => {
    setError(null)
    setSavingAccountId(id)
    try {
      await updateAccountFilters(id, payload)
      await loadAccounts()
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingAccountId(null)
    }
  }

  const handleToggleAccount = async (id, isActive) => {
    await handleSaveAccount(id, { is_active: isActive })
  }

  const handleDeleteAccount = async (id) => {
    if (!window.confirm('Biztosan torolni szeretned ezt a Gmail fiokot?')) return

    setError(null)
    setSavingAccountId(id)
    try {
      await deleteAccount(id)
      await loadAccounts()
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingAccountId(null)
    }
  }

  const handleConnectAccount = async (id) => {
    setError(null)
    setSavingAccountId(id)
    try {
      const data = await startAccountOAuth(id)
      if (data?.mode === 'desktop') {
        await loadAccounts()
        return
      }
      if (!data?.authorization_url) {
        throw new Error('Nem sikerult OAuth URL-t letrehozni')
      }
      window.location.href = data.authorization_url
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingAccountId(null)
    }
  }

  const handleSyncAccount = async (id) => {
    setError(null)
    setSavingAccountId(id)
    try {
      const result = await syncAccount(id, { max_results: 50, import_invoices: true })
      setSyncSummaries((prev) => ({ ...prev, [id]: result }))
      await loadAccounts()
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingAccountId(null)
    }
  }

  if (!apiStatus) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Szamla Kezelo</h1>
          <div className="status-card">
            <h2>Backend allapot</h2>
            <p>Backend nem erheto el</p>
            <p>Inditsd el a Flask API-t: <code>cd backend && python app.py</code></p>
            <button className="btn btn-secondary" onClick={loadHealth}>
              Ujraprobalas
            </button>
          </div>
        </header>
      </div>
    )
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Szamla Kezelo</h1>
        <p className="subtitle">Invoice Manager</p>

        <div className="status-badge">
          Backend elerheto · v{apiStatus.version}
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
                {showAddForm ? 'Megse' : '+ Uj szamla'}
              </button>
              <button className="btn btn-secondary" onClick={loadInvoices}>
                Frissites
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
                <p>Betoltes...</p>
              ) : invoices.length === 0 ? (
                <p className="empty-state">Nincs megjelenitheto szamla</p>
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
                {showRecurringForm ? 'Megse' : '+ Uj ismetlodo'}
              </button>
              <button className="btn btn-secondary" onClick={loadRecurring}>
                Frissites
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
                <p>Betoltes...</p>
              ) : recurring.length === 0 ? (
                <p className="empty-state">Nincs ismetlodo szamla</p>
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

        {mainView === 'gmail' && (
          <>
            <div className="actions">
              <button
                className="btn btn-primary"
                onClick={() => setShowAddAccountForm(!showAddAccountForm)}
              >
                {showAddAccountForm ? 'Megse' : '+ Uj Gmail fiok'}
              </button>
              <button className="btn btn-secondary" onClick={loadAccounts}>
                Frissites
              </button>
            </div>

            {showAddAccountForm && (
              <form className="account-add-form" onSubmit={handleAddAccount}>
                <input
                  type="email"
                  value={newAccountEmail}
                  onChange={(e) => setNewAccountEmail(e.target.value)}
                  placeholder="pelda@gmail.com"
                  required
                />
                <button className="btn btn-primary" type="submit" disabled={savingAccountId === 'new'}>
                  Hozzaadas
                </button>
              </form>
            )}

            <div className="gmail-guide">
              <strong>Javaslat:</strong> Gmail-ben hozz letre egy kulon cimket (pl. InvoiceManager),
              es csak azokra a levelekre alkalmazd, amik szamlat vagy fizetesi linket tartalmaznak.
            </div>

            <div className="invoice-list">
              {loading ? (
                <p>Betoltes...</p>
              ) : accounts.length === 0 ? (
                <p className="empty-state">Nincs Gmail fiok beallitva</p>
              ) : (
                accounts.map((account) => (
                  <div key={account.id}>
                    <GmailAccountCard
                      account={account}
                      onSave={handleSaveAccount}
                      onDelete={handleDeleteAccount}
                      onToggleActive={handleToggleAccount}
                      onConnect={handleConnectAccount}
                      onSync={handleSyncAccount}
                      isSaving={savingAccountId === account.id}
                    />
                    {syncSummaries[account.id] && (
                      <div className="gmail-sync-summary">
                        <strong>Utolso szinkron:</strong> {syncSummaries[account.id].synced_at}
                        <br />
                        Talalt levelek: {syncSummaries[account.id].scanned_messages}
                        {' | '}
                        Fizetesi link gyanus: {syncSummaries[account.id].payment_link_hits}
                        {' | '}
                        Szamla kulcsszo gyanus: {syncSummaries[account.id].invoice_hint_hits}
                        <br />
                        Importalt szamlak: {syncSummaries[account.id].imported_invoices || 0}
                        {' | '}
                        Kihagyva (nincs osszeg): {syncSummaries[account.id].skipped_no_amount || 0}
                        {' | '}
                        Kihagyva (duplikalt): {syncSummaries[account.id].skipped_duplicates || 0}
                        {(syncSummaries[account.id].sample_messages || []).length > 0 && (
                          <div className="gmail-sync-messages">
                            {(syncSummaries[account.id].sample_messages || []).map((msg) => (
                              <div className="gmail-sync-message" key={msg.id}>
                                <div className="gmail-sync-meta">
                                  <strong>{msg.subject || '(Nincs targy)'}</strong>
                                  {msg.from ? ` - ${msg.from}` : ''}
                                </div>
                                <div className="gmail-sync-snippet">{msg.snippet || '(Nincs kivonat)'}</div>
                                <div className="gmail-sync-snippet">
                                  Osszeg becsles: {msg.amount_guess || '-'} {msg.currency_guess || ''}
                                </div>
                                {msg.payment_link_guess && (
                                  <div className="gmail-sync-snippet">
                                    Link becsles: {msg.payment_link_guess}
                                  </div>
                                )}
                                <div className="gmail-sync-flags">
                                  {msg.has_payment_link ? 'Fizetesi link gyanus' : ''}
                                  {msg.has_payment_link && msg.has_invoice_hint ? ' | ' : ''}
                                  {msg.has_invoice_hint ? 'Szamla kulcsszo gyanus' : ''}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </header>
    </div>
  )
}

export default App
