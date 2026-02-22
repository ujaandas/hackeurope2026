import { useState } from "react";
import { Calculator } from "lucide-react";
import { calculateROI } from "../../lib/api";

const ROICalculator = () => {
    const [kwhPrice, setKwhPrice] = useState(0.25);
    const [runsPerDay, setRunsPerDay] = useState(1000);
    const [result, setResult] = useState<{
        annual_kwh_saved: number;
        annual_co2_saved: number;
        annual_eur_saved: number;
    } | null>(null);
    const [loading, setLoading] = useState(false);

    const handleCalculate = async () => {
        setLoading(true);
        try {
            const data = await calculateROI(kwhPrice, runsPerDay);
            setResult(data);
        } catch {
            setResult(null);
        }
        setLoading(false);
    };

    return (
        <div className="rounded-xl border border-border bg-gradient-card p-6 shadow-card h-full">
            <div className="flex items-center gap-2 mb-5">
                <Calculator className="w-4 h-4 text-primary/60" />
                <h2 className="text-sm uppercase tracking-wider text-muted-foreground font-medium">
                    ROI Calculator
                </h2>
            </div>
            <div className="space-y-4">
                <div>
                    <label className="block text-xs text-muted-foreground mb-1.5">
                        Electricity Cost (EUR/kWh)
                    </label>
                    <input
                        type="number"
                        step="0.01"
                        value={kwhPrice}
                        onChange={(e) => setKwhPrice(parseFloat(e.target.value) || 0)}
                        className="w-full bg-input border border-border rounded-lg px-3 py-2 text-sm font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    />
                </div>
                <div>
                    <label className="block text-xs text-muted-foreground mb-1.5">
                        Estimated Runs/Day
                    </label>
                    <input
                        type="number"
                        value={runsPerDay}
                        onChange={(e) => setRunsPerDay(parseInt(e.target.value) || 0)}
                        className="w-full bg-input border border-border rounded-lg px-3 py-2 text-sm font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
                    />
                </div>
                <button
                    onClick={handleCalculate}
                    disabled={loading}
                    className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                    {loading ? "Calculating..." : "Calculate ROI"}
                </button>
                {result && (
                    <div className="space-y-2 pt-2 border-t border-border">
                        <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Annual Energy Saved</span>
                            <span className="font-mono text-foreground">{result.annual_kwh_saved.toFixed(4)} kWh</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Annual CO₂ Reduced</span>
                            <span className="font-mono text-foreground">{result.annual_co2_saved.toFixed(4)} kg</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Annual Cost Saved</span>
                            <span className="font-mono text-primary font-semibold">{result.annual_eur_saved.toFixed(4)} EUR</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ROICalculator;
