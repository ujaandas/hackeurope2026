import React, { useState } from 'react'
import { analyzeCode, optimizeCode } from '../api'

const SAMPLE_CODE = `#include <vector>
#include <iostream>

void bubbleSort(std::vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main() {
    std::vector<int> data = {64, 34, 25, 12, 22, 11, 90};
    bubbleSort(data);
    for (int x : data) {
        std::cout << x << " ";
    }
    return 0;
}`

function TryIt({ onOptimized }) {
  const [code, setCode] = useState(SAMPLE_CODE)
  const [language, setLanguage] = useState('cpp')
  const [patterns, setPatterns] = useState(null)
  const [optimized, setOptimized] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [optimizing, setOptimizing] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    setAnalyzing(true)
    setError(null)
    setOptimized(null)
    try {
      const result = await analyzeCode('input.cpp', code, language)
      setPatterns(result)
    } catch (e) {
      setError('Analysis failed. Is the backend running?')
    }
    setAnalyzing(false)
  }

  const handleOptimize = async () => {
    if (!patterns || patterns.patterns.length === 0) return
    setOptimizing(true)
    setError(null)
    try {
      const result = await optimizeCode('input.cpp', code, patterns.patterns, language)
      setOptimized(result)
      if (onOptimized) onOptimized()
    } catch (e) {
      setError('Optimization failed. Check AI provider availability.')
    }
    setOptimizing(false)
  }

  return (
    <div className="panel try-it">
      <h2>Try It - Analyze Code</h2>
      <div style={{ display: 'flex', gap: 12, marginBottom: 12, alignItems: 'center' }}>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          style={{
            background: '#0f1923', border: '1px solid #1e3a4a', color: '#e0e0e0',
            padding: '8px 12px', borderRadius: 6,
          }}
        >
          <option value="cpp">C++</option>
          <option value="python">Python</option>
        </select>
        <button
          className="btn btn-secondary"
          onClick={() => setCode(SAMPLE_CODE)}
          style={{ fontSize: '0.8rem', padding: '6px 12px' }}
        >
          Load Sample
        </button>
      </div>
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Paste your code here..."
      />
      <div className="buttons">
        <button className="btn" onClick={handleAnalyze} disabled={analyzing || !code}>
          {analyzing ? 'Analyzing...' : 'Analyze'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={handleOptimize}
          disabled={optimizing || !patterns || patterns.patterns.length === 0}
        >
          {optimizing ? 'Optimizing...' : 'Optimize with AI'}
        </button>
      </div>

      {error && <p style={{ color: '#ef4444', marginTop: 12 }}>{error}</p>}

      {patterns && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ color: '#4ade80', marginBottom: 8 }}>
            Analysis Results - Energy Score: {patterns.total_energy_score}/100
          </h3>
          <div style={{ display: 'flex', gap: 16, marginBottom: 12 }}>
            <span>Estimated: {patterns.estimated_kwh.toFixed(4)} kWh/year</span>
            <span>{patterns.estimated_co2_kg.toFixed(4)} kg CO2/year</span>
            <span>{patterns.estimated_cost_eur.toFixed(4)} EUR/year</span>
          </div>
          {patterns.patterns.length === 0 ? (
            <p style={{ color: '#4ade80' }}>No energy anti-patterns detected!</p>
          ) : (
            <div className="pattern-list">
              {patterns.patterns.map((p, i) => (
                <div key={i} className={`pattern-item ${p.severity === 'high' ? 'high' : ''}`}>
                  <div className="name">
                    {p.name} (Lines {p.line_start}-{p.line_end})
                  </div>
                  <div className="desc">{p.description}</div>
                  <div className="suggestion">{p.suggestion}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {optimized && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ color: '#4ade80', marginBottom: 8 }}>
            Optimized - Energy: {optimized.energy_before} &rarr; {optimized.energy_after}
          </h3>
          <div style={{ display: 'flex', gap: 16, marginBottom: 12, fontSize: '0.9rem' }}>
            <span>Saved: {optimized.savings_kwh.toFixed(4)} kWh</span>
            <span>{optimized.savings_co2_kg.toFixed(4)} kg CO2</span>
            <span>{optimized.savings_eur.toFixed(4)} EUR</span>
          </div>
          <div className="code-diff">
            <div>
              <div className="label">Original</div>
              <pre>{optimized.original_code}</pre>
            </div>
            <div>
              <div className="label">Optimized</div>
              <pre>{optimized.optimized_code}</pre>
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            <h4 style={{ color: '#8899aa', fontSize: '0.9rem', marginBottom: 8 }}>
              AI Chain of Thought
            </h4>
            <div className="chain-of-thought">{optimized.chain_of_thought}</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TryIt
