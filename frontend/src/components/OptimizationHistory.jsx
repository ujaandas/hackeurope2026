import React from 'react'

function OptimizationHistory({ history, onSelect }) {
  if (!history || history.length === 0) {
    return <p style={{ color: '#8899aa' }}>No optimizations recorded yet.</p>
  }

  return (
    <table className="history-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>File</th>
          <th>Patterns</th>
          <th>Before</th>
          <th>After</th>
          <th>kWh Saved</th>
          <th>CO2 (kg)</th>
        </tr>
      </thead>
      <tbody>
        {history.map((r) => (
          <tr key={r.id} onClick={() => onSelect(r)}>
            <td>{new Date(r.timestamp).toLocaleDateString()}</td>
            <td>{r.filename}</td>
            <td>{r.patterns_found}</td>
            <td style={{ color: '#ef4444' }}>{r.energy_before.toFixed(1)}</td>
            <td style={{ color: '#4ade80' }}>{r.energy_after.toFixed(1)}</td>
            <td>{r.savings_kwh.toFixed(4)}</td>
            <td>{r.savings_co2_kg.toFixed(4)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default OptimizationHistory
