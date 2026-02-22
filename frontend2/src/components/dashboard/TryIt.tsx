import { useState } from "react";
import { Code2, Play, Sparkles, AlertTriangle } from "lucide-react"; import { analyzeCode, optimizeCode, type AnalyzeResponse, type OptimizeResponse } from "../../lib/api";
;

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
}`;

interface TryItProps {
    onOptimized?: () => void;
}

const TryIt = ({ onOptimized }: TryItProps) => {
    const [code, setCode] = useState(SAMPLE_CODE);
    const [language, setLanguage] = useState("cpp");
    const [patterns, setPatterns] = useState<AnalyzeResponse | null>(null);
    const [optimized, setOptimized] = useState<OptimizeResponse | null>(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [optimizing, setOptimizing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleAnalyze = async () => {
        setAnalyzing(true);
        setError(null);
        setOptimized(null);
        try {
            const result = await analyzeCode("input.cpp", code, language);
            setPatterns(result);
        } catch {
            setError("Analysis failed. Is the backend running?");
        }
        setAnalyzing(false);
    };

    const handleOptimize = async () => {
        if (!patterns || patterns.patterns.length === 0) return;
        setOptimizing(true);
        setError(null);
        try {
            const result = await optimizeCode("input.cpp", code, patterns.patterns, language);
            setOptimized(result);
            if (onOptimized) onOptimized();
        } catch {
            setError("Optimization failed. Check AI provider availability.");
        }
        setOptimizing(false);
    };

    return (
        <div className="space-y-6">
            {/* Code Input Panel */}
            <div className="rounded-xl border border-border bg-gradient-card p-6 shadow-card">
                <div className="flex items-center gap-2 mb-5">
                    <Code2 className="w-5 h-5 text-primary" />
                    <h2 className="text-lg font-semibold text-foreground">Analyze Code</h2>
                </div>

                <div className="flex gap-3 mb-4 items-center">
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="bg-input border border-border text-foreground px-3 py-2 rounded-lg text-sm font-mono focus:outline-none focus:ring-1 focus:ring-ring"
                    >
                        <option value="cpp">C++</option>
                        <option value="python">Python</option>
                    </select>
                    <button
                        onClick={() => setCode(SAMPLE_CODE)}
                        className="text-xs px-3 py-2 rounded-lg bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors"
                    >
                        Load Sample
                    </button>
                </div>

                <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="Paste your code here..."
                    className="w-full h-64 bg-[hsl(200_30%_6%)] border border-border rounded-lg p-4 text-sm font-mono text-foreground resize-none focus:outline-none focus:ring-1 focus:ring-ring leading-relaxed"
                />

                <div className="flex gap-3 mt-4">
                    <button
                        onClick={handleAnalyze}
                        disabled={analyzing || !code}
                        className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Play className="w-4 h-4" />
                        {analyzing ? "Analyzing..." : "Analyze"}
                    </button>
                    <button
                        onClick={handleOptimize}
                        disabled={optimizing || !patterns || patterns.patterns.length === 0}
                        className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-secondary text-secondary-foreground font-medium text-sm hover:bg-secondary/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Sparkles className="w-4 h-4" />
                        {optimizing ? "Optimizing..." : "Optimize with AI"}
                    </button>
                </div>

                {error && <p className="text-destructive text-sm mt-3">{error}</p>}
            </div>

            {/* Analysis Results */}
            {patterns && (
                <div className="rounded-xl border border-border bg-gradient-card p-6 shadow-card animate-fade-in-up">
                    <div className="flex items-center gap-4 flex-wrap mb-4">
                        <h3 className="text-sm font-semibold text-primary">
                            Energy Score: {patterns.total_energy_score}/100
                        </h3>
                        <div className="flex gap-4 text-xs font-mono text-muted-foreground">
                            <span>{patterns.estimated_kwh.toFixed(4)} kWh/yr</span>
                            <span>{patterns.estimated_co2_kg.toFixed(4)} kg CO₂/yr</span>
                            <span>{patterns.estimated_cost_eur.toFixed(4)} EUR/yr</span>
                        </div>
                    </div>

                    {patterns.patterns.length === 0 ? (
                        <p className="text-primary text-sm">No energy anti-patterns detected! 🎉</p>
                    ) : (
                        <div className="space-y-3">
                            {patterns.patterns.map((p, i) => (
                                <div
                                    key={i}
                                    className={`rounded-lg border p-4 ${p.severity === "high"
                                        ? "border-destructive/30 bg-destructive/5"
                                        : "border-border bg-secondary/30"
                                        }`}
                                >
                                    <div className="flex items-center gap-2 mb-1">
                                        {p.severity === "high" && (
                                            <AlertTriangle className="w-4 h-4 text-destructive" />
                                        )}
                                        <span className="text-sm font-semibold text-foreground">{p.name}</span>
                                        <span className="text-xs font-mono text-muted-foreground">
                                            Lines {p.line_start}–{p.line_end}
                                        </span>
                                    </div>
                                    <p className="text-sm text-muted-foreground mb-1">{p.description}</p>
                                    <p className="text-sm text-primary/80">💡 {p.suggestion}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Optimized Result */}
            {optimized && (
                <div className="rounded-xl border border-border bg-gradient-card p-6 shadow-card animate-fade-in-up">
                    <h3 className="text-sm font-semibold text-primary mb-2">
                        Optimized — Energy: {optimized.energy_before} → {optimized.energy_after}
                    </h3>
                    <div className="flex gap-4 text-xs font-mono text-muted-foreground mb-4">
                        <span>Saved: {optimized.savings_kwh.toFixed(4)} kWh</span>
                        <span>{optimized.savings_co2_kg.toFixed(4)} kg CO₂</span>
                        <span>{optimized.savings_eur.toFixed(4)} EUR</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <div className="text-xs uppercase tracking-wider text-muted-foreground font-medium mb-2">Original</div>
                            <pre className="bg-[hsl(200_30%_6%)] rounded-lg p-4 text-sm text-foreground overflow-x-auto border border-border font-mono leading-relaxed">
                                {optimized.original_code}
                            </pre>
                        </div>
                        <div>
                            <div className="text-xs uppercase tracking-wider text-primary font-medium mb-2">Optimized</div>
                            <pre className="bg-[hsl(200_30%_6%)] rounded-lg p-4 text-sm text-foreground overflow-x-auto border border-primary/20 font-mono leading-relaxed">
                                {optimized.optimized_code}
                            </pre>
                        </div>
                    </div>
                    {optimized.chain_of_thought && (
                        <div className="mt-4">
                            <h4 className="text-xs uppercase tracking-wider text-muted-foreground font-medium mb-2">AI Chain of Thought</h4>
                            <div className="bg-secondary rounded-lg p-4 text-sm text-secondary-foreground leading-relaxed border border-border">
                                {optimized.chain_of_thought}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default TryIt;
