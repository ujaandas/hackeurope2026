export type PatternSeverity = "low" | "medium" | "high";

export interface DetectedPattern {
    pattern_id: string;
    name: string;
    severity: PatternSeverity;
    line_start: number;
    line_end: number;
    description: string;
    suggestion: string;
    estimated_energy_cost: number;
    estimated_energy_saved: number;
}

export interface OptimizationRecord {
    id: number;
    timestamp: string;
    filename: string;
    // language: string;
    patterns_found: number;
    energy_before: number;
    energy_after: number;
    savings_kwh: number;
    savings_co2_kg: number;
    savings_eur: number;
    original_code?: string;
    optimized_code?: string;
    chain_of_thought?: string;
}

export interface DashboardData {
    total_optimizations: number;
    total_kwh_saved: number;
    total_co2_saved: number;
    total_eur_saved: number;
    sustainability_score: number;
    history: OptimizationRecord[];
}

export interface AnalyzeResponse {
    filename: string;
    patterns: DetectedPattern[];
    total_energy_score: number;
    optimized_energy_score: number;
    estimated_kwh: number;
    estimated_co2_kg: number;
    estimated_cost_eur: number;
}

export interface OptimizeResponse {
    filename: string;
    original_code: string;
    optimized_code: string;
    changes_summary: string;
    chain_of_thought: string;
    energy_before: number;
    energy_after: number;
    savings_kwh: number;
    savings_co2_kg: number;
    savings_eur: number;
}

export interface ROIResponse {
    annual_kwh_saved: number;
    annual_co2_saved: number;
    annual_eur_saved: number;
}

const BASE_URL = import.meta.env.BACKEND_URL || "";

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    const res = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });

    if (!res.ok) {
        throw new Error(`API Error (${res.status}): Failed to fetch ${endpoint}`);
    }

    return res.json();
}

export function fetchDashboard(): Promise<DashboardData> {
    return fetchApi<DashboardData>("/api/dashboard");
}

export function analyzeCode(
    filename: string,
    code: string,
    language: string = "cpp"
): Promise<AnalyzeResponse> {
    return fetchApi<AnalyzeResponse>("/api/analyze", {
        method: "POST",
        body: JSON.stringify({ filename, code, language }),
    });
}

export function optimizeCode(
    filename: string,
    code: string,
    patterns: DetectedPattern[],
    language: string = "cpp",
    provider: string = "ollama"
): Promise<OptimizeResponse> {
    return fetchApi<OptimizeResponse>("/api/optimize", {
        method: "POST",
        body: JSON.stringify({ filename, code, patterns, language, provider }),
    });
}

export function calculateROI(
    kwhPriceEur: number = 0.25,
    runsPerDay: number = 1000
): Promise<ROIResponse> {
    return fetchApi<ROIResponse>("/api/roi", {
        method: "POST",
        body: JSON.stringify({ kwh_price_eur: kwhPriceEur, runs_per_day: runsPerDay }),
    });
}