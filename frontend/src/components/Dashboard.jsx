import React, { useState } from 'react'
import EnergyChart from './EnergyChart'
import SustainabilityScore from './SustainabilityScore'
import OptimizationHistory from './OptimizationHistory'
import ROICalculator from './ROICalculator'
import CodeDiff from './CodeDiff'

function Dashboard({ data }) {
  const [selectedRecord, setSelectedRecord] = useState(null)

  if (!data) {
    return (
      <div className="panel">
        <p>Loading dashboard data...</p>
      </div>
    )
  }

  return (
    <>
      <div className="kpi-row">
        <div className="kpi-card">
          <div className="label">Total Optimizations</div>
          <div className="value">{data.total_optimizations}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Energy Saved</div>
          <div className="value">
            {data.total_kwh_saved.toFixed(2)}
            <span className="unit">kWh</span>
          </div>
        </div>
        <div className="kpi-card">
          <div className="label">CO2 Reduced</div>
          <div className="value">
            {data.total_co2_saved.toFixed(2)}
            <span className="unit">kg</span>
          </div>
        </div>
        <div className="kpi-card">
          <div className="label">Cost Saved</div>
          <div className="value">
            {data.total_eur_saved.toFixed(2)}
            <span className="unit">EUR</span>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="panel">
          <h2>Energy Impact</h2>
          <EnergyChart history={data.history} />
        </div>
        <div>
          <SustainabilityScore score={data.sustainability_score} />
          <ROICalculator />
        </div>
      </div>

      <div className="panel">
        <h2>Optimization History</h2>
        <OptimizationHistory
          history={data.history}
          onSelect={setSelectedRecord}
        />
      </div>

      {selectedRecord && (
        <div className="panel" style={{ marginTop: 20 }}>
          <h2>Code Comparison - {selectedRecord.filename}</h2>
          <CodeDiff record={selectedRecord} />
        </div>
      )}
    </>
  )
}

export default Dashboard
