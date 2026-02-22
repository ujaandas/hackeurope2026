import type { OptimizationRecord } from "../../lib/api";



interface CodeDiffProps {
    record: OptimizationRecord;
}

const CodeDiff = ({ record }: CodeDiffProps) => {
    return (
        <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <div className="text-xs uppercase tracking-wider text-muted-foreground font-medium mb-2">
                        Original Code
                    </div>
                    <pre className="bg-[hsl(200_30%_6%)] rounded-lg p-4 text-sm text-foreground overflow-x-auto border border-border font-mono leading-relaxed">
                        {record.original_code || "No original code available"}
                    </pre>
                </div>
                <div>
                    <div className="text-xs uppercase tracking-wider text-primary font-medium mb-2">
                        Optimized Code
                    </div>
                    <pre className="bg-[hsl(200_30%_6%)] rounded-lg p-4 text-sm text-foreground overflow-x-auto border border-primary/20 font-mono leading-relaxed">
                        {record.optimized_code || "No optimized code available"}
                    </pre>
                </div>
            </div>
            {record.chain_of_thought && (
                <div>
                    <h3 className="text-sm font-medium text-primary mb-2">
                        AI Chain of Thought
                    </h3>
                    <div className="bg-secondary rounded-lg p-4 text-sm text-secondary-foreground leading-relaxed border border-border">
                        {record.chain_of_thought}
                    </div>
                </div>
            )}
        </div>
    );
};

export default CodeDiff;
