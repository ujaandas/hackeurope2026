import { Leaf, Zap, Activity } from "lucide-react";

interface HeaderProps {
    score?: number;
    isConnected: boolean;
}

const Header = ({ score, isConnected }: HeaderProps) => {
    return (
        <header className="border-b border-border bg-card/80 backdrop-blur-md sticky top-0 z-50">
            <div className="container mx-auto flex items-center justify-between py-4 px-6">
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center shadow-glow">
                            <Leaf className="w-5 h-5 text-primary" />
                        </div>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold font-display tracking-tight text-foreground">
                            green<span className="text-primary">lint</span>
                        </h1>
                        <p className="text-xs text-muted-foreground tracking-wide uppercase">
                            Sustainable Code Analysis
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    {score !== undefined && isConnected && (
                        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 animate-fade-in">
                            <Activity className="w-4 h-4 text-primary" />
                            <span className="text-sm font-mono font-semibold text-primary">
                                {score}/100
                            </span>
                        </div>
                    )}

                    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors duration-300 ${isConnected ? "bg-secondary" : "bg-destructive/10 border border-destructive/20"
                        }`}>
                        <Zap className={`w-4 h-4 transition-colors ${isConnected ? "text-cyan-accent" : "text-destructive"
                            }`} />
                        <span className={`text-sm font-medium ${isConnected ? "text-secondary-foreground" : "text-destructive"
                            }`}>
                            {isConnected ? "Live" : "Offline"}
                        </span>
                        <span className={`w-2 h-2 rounded-full transition-colors ${isConnected
                            ? "bg-primary animate-pulse"
                            : "bg-destructive shadow-[0_0_8px_rgba(239,68,68,0.5)]"
                            }`} />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;