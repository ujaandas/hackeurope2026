const BASE_URL = import.meta.env.VITE_API_URL || '';

export async function fetchDashboard() {
  const res = await fetch(`${BASE_URL}/api/dashboard`);
  if (!res.ok) throw new Error('Failed to fetch dashboard');
  return res.json();
}

export async function analyzeCode(filename, code, language = 'cpp') {
  const res = await fetch(`${BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, code, language }),
  });
  if (!res.ok) throw new Error('Failed to analyze code');
  return res.json();
}

export async function optimizeCode(filename, code, patterns, language = 'cpp', provider = 'ollama') {
  const res = await fetch(`${BASE_URL}/api/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, code, patterns, language, provider }),
  });
  if (!res.ok) throw new Error('Failed to optimize code');
  return res.json();
}

export async function calculateROI(kwhPriceEur = 0.25, runsPerDay = 1000) {
  const res = await fetch(`${BASE_URL}/api/roi`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kwh_price_eur: kwhPriceEur, runs_per_day: runsPerDay }),
  });
  if (!res.ok) throw new Error('Failed to calculate ROI');
  return res.json();
}
