import type { ReactNode } from "react";
import logo from "@/terraviz.png";
import { Activity } from "lucide-react";

interface EmptySidebarProps {
    title: string;
    subtitle: string;
    className?: string;
    children: ReactNode;
}

export function EmptySidebar({ title, subtitle, className, children }: EmptySidebarProps) {
    return (
        <div className={`flex flex-col h-full bg-sidebar border-r border-sidebar-border max-w-[420px] min-w-[420px] ${className}`}>
            {/* Header with branding */}
            <div className="flex items-center justify-between w-full px-6 py-4 border-b border-sidebar-border bg-sidebar-accent/50">
                <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center">
                        <Activity className="h-5 w-5 text-primary-foreground" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold tracking-tight text-sidebar-foreground">TerraViz</h1>
                        <p className="text-[10px] text-sidebar-foreground/60 tracking-wider uppercase">Analytics Platform</p>
                    </div>
                </div>
                <div className="flex items-center gap-1.5">
                    <div className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
                    <span className="text-[10px] text-sidebar-foreground/60 uppercase tracking-wider">Live</span>
                </div>
            </div>

            {/* Title Section */}
            <div className="px-6 py-5 border-b border-sidebar-border bg-sidebar">
                <h2 className="text-xl font-bold text-sidebar-foreground text-balance leading-tight">{title}</h2>
                <p className="text-sm text-sidebar-foreground/70 mt-1.5 leading-relaxed font-mono">
                    {subtitle}
                </p>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden">
                {children}
            </div>
        </div>
    );
}
