import { useEffect, useState } from "react";
import AppLayout from "../../components/AppLayout";
import { ZONE_ADMIN_NAV } from "./_nav";
import StatCard from "../../components/StatCard";
import { Target, Users, Map, DollarSign } from "lucide-react";
import { analyticsAPI, leadsAPI, visitsAPI } from "../../config/api";

export default function ZoneAdminDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    Promise.all([analyticsAPI.leads(), analyticsAPI.visits(), analyticsAPI.employees()])
      .then(([l, v, e]) => setStats({ leads: l.data, visits: v.data, employees: e.data }))
      .catch(() => {});
  }, []);

  return (
    <AppLayout navItems={ZONE_ADMIN_NAV}>
      <div className="space-y-6 animate-slide-up">
        <h1 className="page-header">Branch Dashboard</h1>
        <p className="text-[#8fac9a]">Scoped to your assigned branch — all zones visible</p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard title="Total Leads" value={stats?.leads?.total_leads ?? "—"} icon={Target} />
          <StatCard title="Won Leads" value={stats?.leads?.won ?? "—"} icon={Target} color="green" />
          <StatCard title="Completed Visits" value={stats?.visits?.completed ?? "—"} icon={Map} color="green" />
          <StatCard title="Farm Employees" value={stats?.employees?.total_farm_employees ?? "—"} icon={Users} />
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="section-title">Quick Actions</h2>
            <div className="space-y-2">
              {[
                { label: "Assign Outsourcing Team", href: "/zone-admin/work" },
                { label: "Review Failed Visits", href: "/zone-admin/visits" },
                { label: "Manage Brokers", href: "/zone-admin/brokers" },
                { label: "Escalate to Founder", href: "/zone-admin/escalations" },
              ].map((a) => (
                <a key={a.label} href={a.href} className="block px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-sm text-[#8fac9a] hover:text-[#f0ede4] transition-colors">
                  → {a.label}
                </a>
              ))}
            </div>
          </div>
          <div className="card">
            <h2 className="section-title">Lead Performance</h2>
            <div className="space-y-3">
              {[
                { label: "Conversion Rate", val: `${stats?.leads?.conversion_rate_pct ?? 0}%`, bar: stats?.leads?.conversion_rate_pct || 0 },
                { label: "Won / Total", val: `${stats?.leads?.won ?? 0} / ${stats?.leads?.total_leads ?? 0}`, bar: stats?.leads?.won && stats?.leads?.total_leads ? (stats.leads.won / stats.leads.total_leads) * 100 : 0 },
              ].map((r) => (
                <div key={r.label}>
                  <div className="flex justify-between text-sm mb-1"><span className="text-[#8fac9a]">{r.label}</span><span className="text-accent font-semibold">{r.val}</span></div>
                  <div className="h-1.5 bg-white/10 rounded-full"><div className="h-full bg-accent rounded-full" style={{ width: `${r.bar}%` }} /></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
