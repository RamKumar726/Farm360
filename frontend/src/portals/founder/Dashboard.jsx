import { useEffect, useState } from "react";
import { LayoutDashboard, GitBranch, Map, Users, Target, DollarSign, AlertTriangle, FolderKanban, BarChart3, CheckSquare } from "lucide-react";
import AppLayout from "../../components/AppLayout";
import StatCard from "../../components/StatCard";
import ZoneMap from "../../components/ZoneMap";
import { analyticsAPI } from "../../config/api";

const NAV = [
  { path: "/founder/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/founder/branches", icon: GitBranch, label: "Branches" },
  { path: "/founder/zones", icon: Map, label: "Zones" },
  { path: "/founder/employees", icon: Users, label: "Employees" },
  { path: "/founder/leads", icon: Target, label: "Leads" },
  { path: "/founder/revenue", icon: DollarSign, label: "Revenue" },
  { path: "/founder/risk", icon: AlertTriangle, label: "Risk & Fraud" },
  { path: "/founder/projects", icon: FolderKanban, label: "Projects" },
  { path: "/founder/analytics", icon: BarChart3, label: "Analytics" },
  { path: "/founder/approvals", icon: CheckSquare, label: "Approvals" },
];

export default function FounderDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    Promise.all([
      analyticsAPI.leads(),
      analyticsAPI.revenue(),
      analyticsAPI.visits(),
      analyticsAPI.employees(),
    ]).then(([leads, revenue, visits, employees]) => {
      setStats({ leads: leads.data, revenue: revenue.data, visits: visits.data, employees: employees.data });
    }).catch(() => {});
  }, []);

  return (
    <AppLayout navItems={NAV}>
      <div className="space-y-8 animate-slide-up">
        {/* Header */}
        <div>
          <h1 className="page-header">Founder Dashboard</h1>
          <p className="text-[#8fac9a] mt-1">Complete company visibility across all branches and zones</p>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard title="Total Leads" value={stats?.leads?.total_leads ?? "—"} trend={12} trendLabel="vs last month" icon={Target} />
          <StatCard title="Won Leads" value={stats?.leads?.won ?? "—"} subtitle={`${stats?.leads?.conversion_rate_pct ?? 0}% conversion`} icon={CheckSquare} color="green" />
          <StatCard title="Total Revenue" value={stats?.revenue ? `₹${(stats.revenue.grand_total/100000).toFixed(1)}L` : "—"} icon={DollarSign} color="accent" />
          <StatCard title="Farm Employees" value={stats?.employees?.total_farm_employees ?? "—"} subtitle={`${stats?.employees?.available ?? 0} available today`} icon={Users} />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard title="Visits Completed" value={stats?.visits?.completed ?? "—"} icon={Map} color="green" />
          <StatCard title="Failed Visits" value={stats?.visits?.failed ?? "—"} icon={AlertTriangle} color="red" />
          <StatCard title="Lost Leads" value={stats?.leads?.lost ?? "—"} subtitle="Stored for reference" icon={Target} color="red" />
          <StatCard title="Agri Officers" value={stats?.employees?.total_agri_officers ?? "—"} icon={Users} color="blue" />
        </div>

        {/* Zone Map */}
        <div className="card">
          <h2 className="section-title">Zone Overview Map</h2>
          <ZoneMap className="h-64 w-full" />
        </div>

        {/* Quick actions */}
        <div className="grid md:grid-cols-3 gap-4">
          <div className="card">
            <h3 className="font-semibold text-[#f0ede4] mb-4">Lead Pipeline</h3>
            <div className="space-y-2">
              {[
                { label: "New", value: stats?.leads?.pending, color: "bg-blue-400" },
                { label: "Won", value: stats?.leads?.won, color: "bg-green-400" },
                { label: "Lost", value: stats?.leads?.lost, color: "bg-red-400" },
              ].map((s) => (
                <div key={s.label} className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full ${s.color}`} />
                  <span className="text-sm text-[#8fac9a] flex-1">{s.label}</span>
                  <span className="font-semibold text-[#f0ede4]">{s.value ?? "—"}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold text-[#f0ede4] mb-4">Visit Summary</h3>
            <div className="space-y-2">
              {[
                { label: "Completed", value: stats?.visits?.completed, color: "bg-green-400" },
                { label: "Pending", value: stats?.visits?.pending, color: "bg-yellow-400" },
                { label: "Failed", value: stats?.visits?.failed, color: "bg-red-400" },
              ].map((s) => (
                <div key={s.label} className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full ${s.color}`} />
                  <span className="text-sm text-[#8fac9a] flex-1">{s.label}</span>
                  <span className="font-semibold text-[#f0ede4]">{s.value ?? "—"}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold text-[#f0ede4] mb-4">Revenue Breakdown</h3>
            <div className="space-y-2">
              {[
                { label: "Agreements", value: stats?.revenue?.total_agreement_revenue },
                { label: "Investments", value: stats?.revenue?.total_investment_amount },
                { label: "Projects", value: stats?.revenue?.total_project_revenue },
              ].map((s) => (
                <div key={s.label} className="flex items-center gap-3">
                  <span className="text-sm text-[#8fac9a] flex-1">{s.label}</span>
                  <span className="font-semibold text-accent">
                    {s.value !== undefined ? `₹${Number(s.value).toLocaleString()}` : "—"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
