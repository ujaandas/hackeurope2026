import React, { useState } from 'react'
import { calculateROI } from '../api'

function ROICalculator() {
  const [kwhPrice, setKwhPrice] = useState(0.25)
  const [runsPerDay, setRunsPerDay] = useState(1000)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleCalculate = async () => {
    setLoading(true)
    try {
      const data = await calculateROI(kwhPrice, runsPerDay)
      setResult(data)
    } catch (e) {
      setResult(null)
    }
    setLoading(false)
  }

  return (
    <div className="panel">
      <h2>ROI Calculator</h2>
      <div className="roi-form">
        <div>
          <label>Electricity Cost (EUR/kWh)</label>
          <input
            type="number"
            step="0.01"
            value={kwhPrice}
            onChange={(e) => setKwhPrice(parseFloat(e.target.value) || 0)}
          />
        </div>
        <div>
          <label>Estimated Runs/Day</label>
          <input
            type="number"
            value={runsPerDay}
            onChange={(e) => setRunsPerDay(parseInt(e.target.value) || 0)}
          />
        </div>
        <button className="btn" onClick={handleCalculate} disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate ROI'}
        </button>
        {result && (
          <div className="roi-result">
            <p><strong>Annual Energy Saved:</strong> {result.annual_kwh_saved.toFixed(4)} kWh</p>
            <p><strong>Annual CO2 Reduced:</strong> {result.annual_co2_saved.toFixed(4)} kg</p>
            <p><strong>Annual Cost Saved:</strong> {result.annual_eur_saved.toFixed(4)} EUR</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ROICalculator
