import { EmptySidebar } from "./sidebar-empty";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";
import { ScrollArea } from "./ui/scroll-area";
import { Separator } from "./ui/separator";
import { Badge } from "./ui/badge";
import { TrendingUp, TrendingDown, AlertTriangle, MapPin, Leaf, Sprout, Activity, BarChart2 } from "lucide-react";
import type { BackendResponse } from "@/lib/types";

interface SidebarActiveProps {
    data?: BackendResponse;
    area: string;
    isOcean: boolean;
    hasCountry: boolean;
}

function getErosionGrade(meanErosion: number): { 
    grade: string; 
    variant: "default" | "secondary" | "destructive" | "outline";
    severity: "low" | "medium" | "high" | "critical";
} {
    if (meanErosion < 5) return { grade: "Grade A", variant: "secondary", severity: "low" };
    if (meanErosion < 10) return { grade: "Grade B", variant: "default", severity: "medium" };
    if (meanErosion < 20) return { grade: "Grade C", variant: "outline", severity: "high" };
    return { grade: "Grade D", variant: "destructive", severity: "critical" };
}


export function SidebarActive({ data, area, isOcean, hasCountry }: SidebarActiveProps) {
    if (!data) {
        return (
            <EmptySidebar
                title={area}
                subtitle="Analysis unavailable">
                <div className="p-6 text-center">
                    <AlertTriangle className="h-12 w-12 text-destructive mx-auto mb-3 opacity-50" />
                    <p className="text-sm text-sidebar-foreground/70">Unable to load prediction data</p>
                </div>
            </EmptySidebar>
        )
    }
    const erosionGrade = getErosionGrade(data.erosion.mean);
    const coordinates = data.polygon_metadata.centroid;
    
    // Show RUSLE only if it's not ocean AND has a valid country
    const showRUSLE = !isOcean && hasCountry;

    return (
        <ScrollArea className="h-full">
            <EmptySidebar
                title={area}
                subtitle={`${coordinates[1].toFixed(4)}°N, ${coordinates[0].toFixed(4)}°E`}
            >
                <div className="p-6 space-y-6">
                    {/* Key Metrics Grid */}
                    <div className="grid grid-cols-2 gap-3">
                        <div className="p-4 rounded-lg bg-sidebar-accent border border-sidebar-border">
                            <div className="flex items-center gap-2 mb-2">
                                <MapPin className="h-3.5 w-3.5 text-primary" />
                                <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider font-bold">Area</span>
                            </div>
                            <p className="text-2xl font-bold text-sidebar-foreground font-mono">{data.polygon_metadata.area_km2.toFixed(1)}</p>
                            <p className="text-[10px] text-sidebar-foreground/60 mt-0.5">km² surveyed</p>
                        </div>

                        <div className="p-4 rounded-lg bg-sidebar-accent border border-sidebar-border">
                            <div className="flex items-center gap-2 mb-2">
                                <Activity className="h-3.5 w-3.5 text-accent" />
                                <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider font-bold">Vertices</span>
                            </div>
                            <p className="text-2xl font-bold text-sidebar-foreground font-mono">{data.polygon_metadata.num_vertices}</p>
                            <p className="text-[10px] text-sidebar-foreground/60 mt-0.5">data points</p>
                        </div>
                    </div>

                    {/* Carbon Sequestration */}
                    {data.carbon_sequestration && !data.carbon_sequestration.error && data.carbon_sequestration.carbon_rate_mg_ha_yr != null && (
                        <div className="space-y-3">
                            <div className="flex items-center gap-2">
                                <div className="h-6 w-6 rounded bg-accent/10 flex items-center justify-center">
                                    <Leaf className="h-3.5 w-3.5 text-accent" />
                                </div>
                                <h3 className="text-xs font-bold text-sidebar-foreground uppercase tracking-wider">Carbon Sequestration</h3>
                            </div>

                            <div className="p-4 rounded-lg bg-sidebar-accent border border-sidebar-border space-y-3">
                                {/* Main Rate Display */}
                                <div className="flex items-baseline justify-between">
                                    <span className="text-xs text-sidebar-foreground/60 uppercase tracking-wider">Sequestration Rate</span>
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-2xl font-bold text-accent font-mono">
                                            {data.carbon_sequestration.carbon_rate_mg_ha_yr.toFixed(2)}
                                        </span>
                                        <span className="text-[10px] text-sidebar-foreground/60">Mg/ha/yr</span>
                                    </div>
                                </div>

                                <Separator className="bg-sidebar-border" />

                                {/* Total */}
                                {data.carbon_sequestration.total_carbon_yr != null && (
                                    <div className="flex items-center justify-between">
                                        <span className="text-xs text-sidebar-foreground/70">Total Annual</span>
                                        <span className="font-mono text-sm font-bold text-sidebar-foreground">
                                            {data.carbon_sequestration.total_carbon_yr.toFixed(2)} <span className="text-[10px] text-sidebar-foreground/60">Mg/yr</span>
                                        </span>
                                    </div>
                                )}

                                {/* Soil Classification */}
                                {data.carbon_sequestration.soil?.classification && (
                                    <div className="pt-2 border-t border-sidebar-border">
                                        <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider">Soil Type</span>
                                        <p className="text-xs text-sidebar-foreground/90 mt-1">{data.carbon_sequestration.soil.classification}</p>
                                    </div>
                                )}

                                {/* Climate Conditions */}
                                {data.carbon_sequestration.climate && (
                                    <div className="grid grid-cols-2 gap-2 pt-2 border-t border-sidebar-border">
                                        <div>
                                            <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider block mb-1">Temp</span>
                                            <span className="font-mono text-sm font-bold text-sidebar-foreground">
                                                {data.carbon_sequestration.climate.annual_mean_temp_c.toFixed(1)}°C
                                            </span>
                                        </div>
                                        <div>
                                            <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider block mb-1">Precip</span>
                                            <span className="font-mono text-sm font-bold text-sidebar-foreground">
                                                {data.carbon_sequestration.climate.annual_mean_precip_mm.toFixed(0)}mm
                                            </span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Soil Erosion Assessment - Only show for land areas with valid country */}
                    {showRUSLE && (
                        <div className="space-y-3">
                            <div className="flex items-center gap-2">
                                <div className="h-6 w-6 rounded bg-destructive/10 flex items-center justify-center">
                                    <AlertTriangle className="h-3.5 w-3.5 text-destructive" />
                                </div>
                                <h3 className="text-xs font-bold text-sidebar-foreground uppercase tracking-wider">RUSLE Analysis</h3>
                                <Badge variant={erosionGrade.variant} className="ml-auto text-[10px] px-2 py-0.5">
                                    {erosionGrade.grade}
                                </Badge>
                            </div>

                            <div className="p-4 rounded-lg bg-sidebar-accent border border-sidebar-border space-y-3">
                                {/* Key Erosion Metrics */}
                                <div className="grid grid-cols-3 gap-3">
                                    <div>
                                        <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider block mb-1">Mean</span>
                                        <span className="font-mono text-base font-bold text-sidebar-foreground block">
                                            {data.erosion.mean.toFixed(1)}
                                        </span>
                                        <span className="text-[9px] text-sidebar-foreground/60">t/ha/yr</span>
                                    </div>
                                    <div>
                                        <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider block mb-1">Max</span>
                                        <span className="font-mono text-base font-bold text-destructive block">
                                            {data.erosion.max.toFixed(1)}
                                        </span>
                                        <span className="text-[9px] text-sidebar-foreground/60">t/ha/yr</span>
                                    </div>
                                    <div>
                                        <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider block mb-1">P95</span>
                                        <span className="font-mono text-base font-bold text-chart-3 block">
                                            {data.erosion.p95.toFixed(1)}
                                        </span>
                                        <span className="text-[9px] text-sidebar-foreground/60">t/ha/yr</span>
                                    </div>
                                </div>

                                {data.erosion.total_soil_loss_tonnes != null && (
                                    <>
                                        <Separator className="bg-sidebar-border" />
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs text-sidebar-foreground/70">Total Annual Loss</span>
                                            <span className="font-mono text-sm font-bold text-destructive">
                                                {data.erosion.total_soil_loss_tonnes.toLocaleString()} <span className="text-[10px]">tonnes</span>
                                            </span>
                                        </div>
                                    </>
                                )}
                            </div>

                            <Separator className="bg-sidebar-border" />

                            {/* RUSLE Factors */}
                            <div className="p-4 rounded-lg bg-sidebar-accent border border-sidebar-border">
                                <h4 className="text-[10px] font-bold text-sidebar-foreground/70 uppercase tracking-wider mb-3">Factor Contributions</h4>
                                <div className="space-y-3">
                                    {/* R Factor */}
                                    <div>
                                        <div className="flex items-center justify-between mb-1.5">
                                            <span className="text-xs text-sidebar-foreground/80 font-medium">R - Rainfall</span>
                                            <span className="font-mono text-xs font-bold text-sidebar-foreground">
                                                {data.factors.R.mean.toFixed(1)}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Progress
                                                value={data.factors.R.contribution_pct ?? 0}
                                                className="h-1.5 flex-1"
                                            />
                                            <span className="text-[10px] text-sidebar-foreground/60 font-mono w-10 text-right">
                                                {data.factors.R.contribution_pct?.toFixed(0) ?? 'N/A'}%
                                            </span>
                                        </div>
                                    </div>

                                    {/* K Factor */}
                                    <div>
                                        <div className="flex items-center justify-between mb-1.5">
                                            <span className="text-xs text-sidebar-foreground/80 font-medium">K - Soil</span>
                                            <span className="font-mono text-xs font-bold text-sidebar-foreground">
                                                {data.factors.K.mean.toFixed(3)}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Progress
                                                value={data.factors.K.contribution_pct ?? 0}
                                                className="h-1.5 flex-1"
                                            />
                                            <span className="text-[10px] text-sidebar-foreground/60 font-mono w-10 text-right">
                                                {data.factors.K.contribution_pct?.toFixed(0) ?? 'N/A'}%
                                            </span>
                                        </div>
                                    </div>

                                    {/* LS Factor */}
                                    <div>
                                        <div className="flex items-center justify-between mb-1.5">
                                            <span className="text-xs text-sidebar-foreground/80 font-medium">LS - Slope</span>
                                            <span className="font-mono text-xs font-bold text-sidebar-foreground">
                                                {data.factors.LS.mean.toFixed(2)}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Progress
                                                value={data.factors.LS.contribution_pct ?? 0}
                                                className="h-1.5 flex-1"
                                            />
                                            <span className="text-[10px] text-sidebar-foreground/60 font-mono w-10 text-right">
                                                {data.factors.LS.contribution_pct?.toFixed(0) ?? 'N/A'}%
                                            </span>
                                        </div>
                                    </div>

                                    {/* C Factor */}
                                    <div>
                                        <div className="flex items-center justify-between mb-1.5">
                                            <span className="text-xs text-sidebar-foreground/80 font-medium">C - Cover</span>
                                            <span className="font-mono text-xs font-bold text-sidebar-foreground">
                                                {data.factors.C.mean.toFixed(3)}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Progress
                                                value={data.factors.C.contribution_pct ?? 0}
                                                className="h-1.5 flex-1"
                                            />
                                            <span className="text-[10px] text-sidebar-foreground/60 font-mono w-10 text-right">
                                                {data.factors.C.contribution_pct?.toFixed(0) ?? 'N/A'}%
                                            </span>
                                        </div>
                                    </div>

                                    {/* P Factor - Optional */}
                                    {data.factors.P && (
                                        <div>
                                            <div className="flex items-center justify-between mb-1.5">
                                                <span className="text-xs text-sidebar-foreground/80 font-medium">P - Practice</span>
                                                <span className="font-mono text-xs font-bold text-sidebar-foreground">
                                                    {data.factors.P.mean.toFixed(2)}
                                                </span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Progress
                                                    value={data.factors.P.contribution_pct ?? 0}
                                                    className="h-1.5 flex-1"
                                                />
                                                <span className="text-[10px] text-sidebar-foreground/60 font-mono w-10 text-right">
                                                    {data.factors.P.contribution_pct?.toFixed(0) ?? 'N/A'}%
                                                </span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Crop Yield */}
                    {data.crop_yield && !data.crop_yield.error && data.crop_yield.yield_t_ha != null && (
                        <div className="space-y-3">
                            <div className="flex items-center gap-2">
                                <div className="h-6 w-6 rounded bg-chart-3/10 flex items-center justify-center">
                                    <Sprout className="h-3.5 w-3.5 text-chart-3" />
                                </div>
                                <h3 className="text-xs font-bold text-sidebar-foreground uppercase tracking-wider">Crop Yield</h3>
                            </div>

                            <div className="p-4 rounded-lg bg-sidebar-accent border border-sidebar-border">
                                <div className="flex items-baseline justify-between mb-2">
                                    <span className="text-xs text-sidebar-foreground/60 uppercase tracking-wider">Predicted Yield</span>
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-2xl font-bold text-chart-3 font-mono">
                                            {data.crop_yield.yield_t_ha.toFixed(2)}
                                        </span>
                                        <span className="text-[10px] text-sidebar-foreground/60">t/ha</span>
                                    </div>
                                </div>
                                <div className="pt-2 border-t border-sidebar-border">
                                    <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider">Crop Type</span>
                                    <p className="text-xs text-sidebar-foreground/90 mt-1">{data.crop_yield.crop_name}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Computation Metrics */}
                    <div className="pt-4 border-t border-sidebar-border">
                        <div className="flex items-center gap-2 mb-3">
                            <div className="h-6 w-6 rounded bg-primary/10 flex items-center justify-center">
                                <BarChart2 className="h-3.5 w-3.5 text-primary" />
                            </div>
                            <h3 className="text-xs font-bold text-sidebar-foreground uppercase tracking-wider">Analysis Metrics</h3>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                            <div className="p-3 rounded-lg bg-sidebar-accent border border-sidebar-border">
                                <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider block mb-1">Runtime</span>
                                <span className="font-mono text-sm font-bold text-sidebar-foreground">
                                    {data.computation_time_sec.toFixed(2)}s
                                </span>
                            </div>
                            <div className="p-3 rounded-lg bg-sidebar-accent border border-sidebar-border">
                                <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider block mb-1">Hotspots</span>
                                <span className="font-mono text-sm font-bold text-sidebar-foreground">
                                    {data.num_hotspots}
                                </span>
                            </div>
                        </div>
                        <div className="mt-2 p-3 rounded-lg bg-sidebar-accent/50 border border-sidebar-border">
                            <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider block mb-1">Timestamp</span>
                            <span className="font-mono text-[11px] text-sidebar-foreground/80">
                                {new Date(data.timestamp).toLocaleString()}
                            </span>
                        </div>
                    </div>
                </div>
            </EmptySidebar>
        </ScrollArea>
    );
}
