import React, { useState, useEffect } from 'react'
import { fetchDashboard } from './api'
import Dashboard from './components/Dashboard'
import TryIt from './components/TryIt'

function App() {
  const [dashboardData, setDashboardData] = useState(null)
  const [error, setError] = useState(null)

  const loadDashboard = async () => {
    try {
      const data = await fetchDashboard()
      setDashboardData(data)
      setError(null)
    } catch (e) {
      setError('Could not connect to GreenLinter API. Is the backend running?')
    }
  }

  useEffect(() => {
    loadDashboard()
    const interval = setInterval(loadDashboard, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>GreenLinter Dashboard</h1>
        {dashboardData && (
          <div className="score-badge">
            Score: {dashboardData.sustainability_score}/100
          </div>
        )}
      </header>

      {error && (
        <div className="panel" style={{ borderColor: '#f59e0b', marginBottom: 20 }}>
          <p style={{ color: '#f59e0b' }}>{error}</p>
        </div>
      )}

      <Dashboard data={dashboardData} />
      <TryIt onOptimized={loadDashboard} />
    </div>
  )
}

export default App
