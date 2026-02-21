import React from 'react'

function SustainabilityScore({ score }) {
  let colorClass = 'green'
  let grade = 'A'
  if (score < 30) { colorClass = 'red'; grade = 'C' }
  else if (score < 70) { colorClass = 'yellow'; grade = 'B' }

  return (
    <div className="panel" style={{ marginBottom: 20 }}>
      <h2>Sustainability Score</h2>
      <div className="score-gauge">
        <div className={`score-circle ${colorClass}`}>
          {score}
        </div>
        <div className="score-label">Grade: {grade}</div>
      </div>
    </div>
  )
}

export default SustainabilityScore
