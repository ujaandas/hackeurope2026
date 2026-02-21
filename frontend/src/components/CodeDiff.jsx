import React from 'react'

function CodeDiff({ record }) {
  return (
    <div>
      <div className="code-diff">
        <div>
          <div className="label">Original Code</div>
          <pre>{record.original_code || 'No original code available'}</pre>
        </div>
        <div>
          <div className="label">Optimized Code</div>
          <pre>{record.optimized_code || 'No optimized code available'}</pre>
        </div>
      </div>
      {record.chain_of_thought && (
        <div style={{ marginTop: 16 }}>
          <h3 style={{ color: '#4ade80', fontSize: '0.95rem', marginBottom: 8 }}>
            AI Chain of Thought
          </h3>
          <div className="chain-of-thought">
            {record.chain_of_thought}
          </div>
        </div>
      )}
    </div>
  )
}

export default CodeDiff
