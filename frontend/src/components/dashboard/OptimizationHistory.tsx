import type { OptimizationRecord } from "../../lib/api";


interface OptimizationHistoryProps {
    history: OptimizationRecord[];
    onSelect: (record: OptimizationRecord) => void;
}

const OptimizationHistory = ({ history, onSelect }: OptimizationHistoryProps) => {
    if (!history || history.length === 0) {
        return <p className="text-muted-foreground text-sm">No optimizations recorded yet.</p>;
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
                <thead>
                    <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-muted-foreground font-medium">Date</th>
                        <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-muted-foreground font-medium">File</th>
                        <th className="text-center py-3 px-4 text-xs uppercase tracking-wider text-muted-foreground font-medium">Patterns</th>
                        <th className="text-right py-3 px-4 text-xs uppercase tracking-wider text-muted-foreground font-medium">Before</th>
                        <th className="text-right py-3 px-4 text-xs uppercase tracking-wider text-muted-foreground font-medium">After</th>
                        <th className="text-right py-3 px-4 text-xs uppercase tracking-wider text-muted-foreground font-medium">kWh Saved</th>
                        <th className="text-right py-3 px-4 text-xs uppercase tracking-wider text-muted-foreground font-medium">CO₂ (kg)</th>
                    </tr>
                </thead>
                <tbody>
                    {history.map((r) => (
                        <tr
                            key={r.id}
                            onClick={() => onSelect(r)}
                            className="border-b border-border/50 hover:bg-secondary/50 cursor-pointer transition-colors"
                        >
                            <td className="py-3 px-4 text-muted-foreground font-mono text-xs">
                                {new Date(r.timestamp).toLocaleDateString()}
                            </td>
                            <td className="py-3 px-4 text-foreground font-mono text-xs">{r.filename}</td>
                            <td className="py-3 px-4 text-center">
                                <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-semibold">
                                    {r.patterns_found}
                                </span>
                            </td>
                            <td className="py-3 px-4 text-right text-destructive font-mono">{r.energy_before.toFixed(1)}</td>
                            <td className="py-3 px-4 text-right text-primary font-mono">{r.energy_after.toFixed(1)}</td>
                            <td className="py-3 px-4 text-right text-foreground font-mono">{r.savings_kwh.toFixed(4)}</td>
                            <td className="py-3 px-4 text-right text-foreground font-mono">{r.savings_co2_kg.toFixed(4)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default OptimizationHistory;
