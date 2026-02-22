import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from "recharts";
import type { OptimizationRecord } from "../../lib/api";


interface EnergyChartProps {
    history: OptimizationRecord[];
}

const EnergyChart = ({ history }: EnergyChartProps) => {
    if (!history || history.length === 0) {
        return (
            <p className="text-muted-foreground text-sm">
                No optimization data yet. Analyze some code to see results.
            </p>
        );
    }

    const chartData = history
        .slice(0, 10)
        .reverse()
        .map((r) => ({
            name: r.filename.split("/").pop() ?? r.filename,
            Before: r.energy_before,
            After: r.energy_after,
        }));

    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(200 18% 20%)" />
                <XAxis
                    dataKey="name"
                    tick={{ fill: "hsl(200 12% 55%)", fontSize: 11 }}
                    angle={-20}
                    textAnchor="end"
                    height={60}
                />
                <YAxis
                    tick={{ fill: "hsl(200 12% 55%)" }}
                    label={{
                        value: "Energy Score",
                        angle: -90,
                        position: "insideLeft",
                        fill: "hsl(200 12% 55%)",
                        style: { fontSize: 12 },
                    }}
                />
                <Tooltip
                    contentStyle={{
                        background: "hsl(200 22% 11%)",
                        border: "1px solid hsl(200 18% 20%)",
                        borderRadius: 8,
                        fontSize: 13,
                    }}
                    labelStyle={{ color: "hsl(180 10% 90%)" }}
                />
                <Legend
                    wrapperStyle={{ fontSize: 12, color: "hsl(200 12% 55%)" }}
                />
                <Bar
                    dataKey="Before"
                    fill="hsl(0 72% 51%)"
                    radius={[4, 4, 0, 0]}
                />
                <Bar
                    dataKey="After"
                    fill="hsl(142 71% 45%)"
                    radius={[4, 4, 0, 0]}
                />
            </BarChart>
        </ResponsiveContainer>
    );
};

export default EnergyChart;
