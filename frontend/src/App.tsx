import { useState, useEffect } from "react";

import { AlertTriangle } from "lucide-react";
import { fetchDashboard, type DashboardData, type OptimizationRecord } from "./lib/api";
import Header from "./components/header";
import CodeDiff from "./components/dashboard/CodeDiff";
import EnergyChart from "./components/dashboard/EnergyChart";
import KPICards from "./components/dashboard/KPICards";
import OptimizationHistory from "./components/dashboard/OptimizationHistory";
import ROICalculator from "./components/dashboard/ROICalculator";
import SustainabilityScore from "./components/dashboard/SustainabilityScore";
import TryIt from "./components/dashboard/TryIt";

const Index = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<OptimizationRecord | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "analyze">("overview");

  const loadDashboard = async () => {
    try {
      const data = await fetchDashboard();
      setDashboardData(data);
      setError(null);
    } catch {
      setError("Could not connect to GreenLinter API.");
    } finally {
      setIsLoading(false); // End loading state
    }
  };

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      if (isMounted) await loadDashboard();
    };

    fetchData();

    const interval = setInterval(fetchData, 10000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  if (isLoading && !dashboardData) {
    return <div className="min-h-screen bg-background flex items-center justify-center text-primary">Loading GreenLinter Dashboard...</div>;
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="fixed inset-0 bg-gradient-glow pointer-events-none" />

      <div className="relative z-10">
        <Header score={dashboardData?.sustainability_score} isConnected={!error} />

        {/* Tab Navigation */}
        <div className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-[73px] z-40">
          <div className="container mx-auto px-6 flex gap-1">
            {(["overview", "analyze"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-5 py-3 text-sm font-medium capitalize transition-colors border-b-2 ${activeTab === tab
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
              >
                {tab === "overview" ? "Dashboard Overview" : "Analyze Code"}
              </button>
            ))}
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="container mx-auto px-6 pt-6">
            <div className="rounded-xl border border-accent/30 bg-accent/5 p-4 flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-accent shrink-0" />
              <p className="text-sm text-accent">{error}</p>
            </div>
          </div>
        )}

        <main className="container mx-auto px-6 py-8">
          {activeTab === "overview" ? (
            <div className="space-y-8">
              {/* KPI + Score: horizontal strip */}
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                <div className="lg:col-span-4">
                  <KPICards
                    totalOptimizations={dashboardData?.total_optimizations ?? 0}
                    totalKwhSaved={dashboardData?.total_kwh_saved ?? 0}
                    totalCo2Saved={dashboardData?.total_co2_saved ?? 0}
                    totalEurSaved={dashboardData?.total_eur_saved ?? 0}
                  />
                </div>
                <div className="lg:col-span-1">
                  <SustainabilityScore score={dashboardData?.sustainability_score ?? 0} />
                </div>
              </div>

              {/* Chart + ROI side by side */}
              <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
                <div className="xl:col-span-3 rounded-xl border border-border bg-gradient-card p-6 shadow-card">
                  <h2 className="text-sm uppercase tracking-wider text-muted-foreground font-medium mb-4">
                    Energy Impact
                  </h2>
                  <EnergyChart history={dashboardData?.history ?? []} />
                </div>
                <div className="xl:col-span-2">
                  <ROICalculator />
                </div>
              </div>

              {/* History + Code Diff stacked */}
              <div className="rounded-xl border border-border bg-gradient-card p-6 shadow-card">
                <h2 className="text-sm uppercase tracking-wider text-muted-foreground font-medium mb-4">
                  Optimization History
                </h2>
                <OptimizationHistory
                  history={dashboardData?.history ?? []}
                  onSelect={setSelectedRecord}
                />
              </div>

              {selectedRecord && (
                <div className="rounded-xl border border-border bg-gradient-card p-6 shadow-card animate-fade-in-up">
                  <h2 className="text-sm uppercase tracking-wider text-muted-foreground font-medium mb-4">
                    Code Comparison — {selectedRecord.filename}
                  </h2>
                  <CodeDiff record={selectedRecord} />
                </div>
              )}
            </div>
          ) : (
            <TryIt onOptimized={loadDashboard} />
          )}
        </main>
      </div>
    </div>
  );
};

export default Index;
