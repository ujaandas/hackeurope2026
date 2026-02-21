import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function EnergyChart({ history }) {
  if (!history || history.length === 0) {
    return <p style={{ color: '#8899aa' }}>No optimization data yet. Analyze some code to see results.</p>
  }

  const chartData = history.slice(0, 10).reverse().map((r, i) => ({
    name: r.filename.split('/').pop(),
    before: r.energy_before,
    after: r.energy_after,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e3a4a" />
        <XAxis dataKey="name" tick={{ fill: '#8899aa', fontSize: 12 }} angle={-20} textAnchor="end" height={60} />
        <YAxis tick={{ fill: '#8899aa' }} label={{ value: 'Energy Score', angle: -90, position: 'insideLeft', fill: '#8899aa' }} />
        <Tooltip
          contentStyle={{ background: '#162530', border: '1px solid #1e3a4a', borderRadius: 8 }}
          labelStyle={{ color: '#e0e0e0' }}
        />
        <Legend />
        <Bar dataKey="before" name="Before" fill="#ef4444" radius={[4, 4, 0, 0]} />
        <Bar dataKey="after" name="After" fill="#4ade80" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default EnergyChart
