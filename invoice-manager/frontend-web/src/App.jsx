import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Test backend connection
    fetch('http://localhost:5000/health')
      .then(res => res.json())
      .then(data => {
        setApiStatus(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Backend connection failed:', err)
        setLoading(false)
      })
  }, [])

  return (
    <div className="App">
      <header className="App-header">
        <h1>📧 Számla Kezelő</h1>
        <p>Invoice Manager - Web Interface</p>
        
        <div className="status-card">
          <h2>Backend Állapot</h2>
          {loading ? (
            <p>Kapcsolódás...</p>
          ) : apiStatus ? (
            <div>
              <p>✅ Backend elérhető</p>
              <p>Verzió: {apiStatus.version}</p>
            </div>
          ) : (
            <p>❌ Backend nem elérhető - Indítsd el a Flask API-t!</p>
          )}
        </div>

        <div className="info-card">
          <h3>🚧 Fejlesztés alatt</h3>
          <p>Az MVP fejlesztése folyamatban...</p>
          <ul style={{ textAlign: 'left', maxWidth: '400px' }}>
            <li>Backend API alapok ✅</li>
            <li>Gmail integráció ⏳</li>
            <li>PDF feldolgozás ⏳</li>
            <li>React UI ⏳</li>
          </ul>
        </div>
      </header>
    </div>
  )
}

export default App
