import { EmptySidebar } from "./sidebar-empty";
import { TrendingUp, Target, BarChart3, Cpu, Sparkles } from "lucide-react";

export function SidebarInactive() {
    return (
        <EmptySidebar 
            title="Regional Commodity Analysis" 
            subtitle="Draw polygon to begin prediction"
        >
            <div className="h-full flex flex-col">
                {/* Instructions Panel */}
                <div className="p-6 bg-sidebar-accent/30 border-b border-sidebar-border">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="h-6 w-6 rounded bg-primary/10 flex items-center justify-center">
                            <Target className="h-3.5 w-3.5 text-primary" />
                        </div>
                        <h3 className="text-xs font-bold text-sidebar-foreground uppercase tracking-wider">Quick Start</h3>
                    </div>
                    <ol className="space-y-3 text-sm text-sidebar-foreground/80 leading-relaxed">
                        <li className="flex items-start gap-3">
                            <span className="font-mono text-primary font-bold flex-shrink-0">01</span>
                            <span>Click the <span className="font-semibold text-sidebar-foreground">polygon tool</span> in the bottom right corner</span>
                        </li>
                        <li className="flex items-start gap-3">
                            <span className="font-mono text-primary font-bold flex-shrink-0">02</span>
                            <span>Draw your region of interest on the map by clicking points</span>
                        </li>
                        <li className="flex items-start gap-3">
                            <span className="font-mono text-primary font-bold flex-shrink-0">03</span>
                            <span>Press <span className="font-semibold text-accent">✓</span> to complete and run analysis</span>
                        </li>
                    </ol>
                </div>

                {/* Features Grid */}
                <div className="p-6 space-y-4">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="h-6 w-6 rounded bg-accent/10 flex items-center justify-center">
                            <Sparkles className="h-3.5 w-3.5 text-accent" />
                        </div>
                        <h3 className="text-xs font-bold text-sidebar-foreground uppercase tracking-wider">Analysis Capabilities</h3>
                    </div>

                    <div className="grid gap-3">
                        <div className="group p-4 rounded-lg bg-sidebar-accent border border-sidebar-border hover:border-primary/50 transition-colors">
                            <div className="flex items-start gap-3">
                                <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center flex-shrink-0">
                                    <TrendingUp className="h-4 w-4 text-primary" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-bold text-sidebar-foreground text-sm mb-1">Price Predictions</h4>
                                    <p className="text-xs text-sidebar-foreground/70 leading-relaxed">Advanced ML models for commodity price forecasting</p>
                                </div>
                            </div>
                        </div>

                        <div className="group p-4 rounded-lg bg-sidebar-accent border border-sidebar-border hover:border-accent/50 transition-colors">
                            <div className="flex items-start gap-3">
                                <div className="h-8 w-8 rounded-md bg-accent/10 flex items-center justify-center flex-shrink-0">
                                    <BarChart3 className="h-4 w-4 text-accent" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-bold text-sidebar-foreground text-sm mb-1">Yield Analysis</h4>
                                    <p className="text-xs text-sidebar-foreground/70 leading-relaxed">Crop yield estimates and carbon sequestration data</p>
                                </div>
                            </div>
                        </div>

                        <div className="group p-4 rounded-lg bg-sidebar-accent border border-sidebar-border hover:border-chart-3/50 transition-colors">
                            <div className="flex items-start gap-3">
                                <div className="h-8 w-8 rounded-md bg-chart-3/10 flex items-center justify-center flex-shrink-0">
                                    <Cpu className="h-4 w-4 text-chart-3" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-bold text-sidebar-foreground text-sm mb-1">Risk Assessment</h4>
                                    <p className="text-xs text-sidebar-foreground/70 leading-relaxed">RUSLE erosion factors and environmental metrics</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Status Bar */}
                <div className="mt-auto p-4 border-t border-sidebar-border bg-sidebar-accent/20">
                    <div className="flex items-center justify-between text-[10px]">
                        <span className="text-sidebar-foreground/60 uppercase tracking-wider">System Status</span>
                        <div className="flex items-center gap-1.5">
                            <div className="h-1.5 w-1.5 rounded-full bg-accent" />
                            <span className="text-sidebar-foreground/80 font-mono">Ready</span>
                        </div>
                    </div>
                </div>
            </div>
        </EmptySidebar>
    )
}
