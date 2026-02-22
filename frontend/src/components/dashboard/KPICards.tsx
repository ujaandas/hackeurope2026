import { Zap, Cloud, DollarSign, BarChart3 } from "lucide-react";

interface KPICardsProps {
    totalOptimizations: number;
    totalKwhSaved: number;
    totalCo2Saved: number;
    totalEurSaved: number;
}

const KPICards = ({ totalOptimizations, totalKwhSaved, totalCo2Saved, totalEurSaved }: KPICardsProps) => {
    const cards = [
        {
            label: "Total Optimizations",
            value: totalOptimizations.toString(),
            unit: "",
            icon: BarChart3,
            delay: "animate-delay-100",
        },
        {
            label: "Energy Saved",
            value: totalKwhSaved.toFixed(2),
            unit: "kWh",
            icon: Zap,
            delay: "animate-delay-200",
        },
        {
            label: "CO₂ Reduced",
            value: totalCo2Saved.toFixed(2),
            unit: "kg",
            icon: Cloud,
            delay: "animate-delay-300",
        },
        {
            label: "Cost Saved",
            value: totalEurSaved.toFixed(2),
            unit: "EUR",
            icon: DollarSign,
            delay: "animate-delay-400",
        },
    ];

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {cards.map((card) => (
                <div
                    key={card.label}
                    className={`opacity-0 animate-fade-in-up ${card.delay} rounded-xl border border-border bg-gradient-card p-5 shadow-card hover:shadow-glow transition-shadow duration-300`}
                >
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-xs uppercase tracking-wider text-muted-foreground font-medium">
                            {card.label}
                        </span>
                        <card.icon className="w-4 h-4 text-primary/60" />
                    </div>
                    <div className="flex items-baseline gap-1.5">
                        <span className="text-3xl font-bold font-mono text-foreground">
                            {card.value}
                        </span>
                        {card.unit && (
                            <span className="text-sm text-muted-foreground font-mono">
                                {card.unit}
                            </span>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default KPICards;
