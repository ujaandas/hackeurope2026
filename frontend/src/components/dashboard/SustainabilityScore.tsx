interface SustainabilityScoreProps {
    score: number;
}

const SustainabilityScore = ({ score }: SustainabilityScoreProps) => {
    let grade = "A";
    let ringColor = "text-primary";
    // let bgRing = "border-primary/30";

    if (score < 30) {
        grade = "C";
        ringColor = "text-destructive";
        // bgRing = "border-destructive/30";
    } else if (score < 70) {
        grade = "B";
        ringColor = "text-yellow-400";
        // bgRing = "border-yellow-400/30";
    }

    const circumference = 2 * Math.PI * 58;
    const offset = circumference - (score / 100) * circumference;

    return (
        <div className="rounded-xl border border-border bg-gradient-card p-6 shadow-card text-center">
            <h2 className="text-sm uppercase tracking-wider text-muted-foreground font-medium mb-6">
                Sustainability Score
            </h2>
            <div className="relative inline-flex items-center justify-center">
                <svg width="140" height="140" className="-rotate-90">
                    <circle
                        cx="70"
                        cy="70"
                        r="58"
                        fill="none"
                        stroke="hsl(200 18% 20%)"
                        strokeWidth="8"
                    />
                    <circle
                        cx="70"
                        cy="70"
                        r="58"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="8"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        className={`${ringColor} transition-all duration-1000`}
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-3xl font-bold font-mono ${ringColor}`}>
                        {score}
                    </span>
                    <span className="text-xs text-muted-foreground mt-1">
                        Grade: {grade}
                    </span>
                </div>
            </div>
        </div>
    );
};

export default SustainabilityScore;
