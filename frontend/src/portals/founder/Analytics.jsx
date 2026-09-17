import { useState, useEffect } from "react";
import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { analyticsAPI } from "../../config/api";
import StatCard from "../../components/StatCard";
import { BarChart3, Target, DollarSign, Map, Users } from "lucide-react";

export default function FounderAnalytics() {
  const [data, setData] = useState({});

  useEffect(() => {
    Promise.all([analyticsAPI.leads(), analyticsAPI.revenue(), analyticsAPI.visits(), analyticsAPI.employees(), analyticsAPI.investments()])
      .then(([l, r, v, e, i]) => setData({ leads: l.data, revenue: r.data, visits: v.data, employees: e.data, investments: i.data }))
      .catch(() => {});
  }, []);

  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-8">
        <div>
          <h1 className="page-header">Analytics & Reports</h1>
          <p className="text-[#8fac9a] mt-1">Company-wide performance metrics and drill-down</p>
        </div>

        <div>
          <h2 className="section-title">Lead Metrics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard title="Total Leads" value={data.leads?.total_leads ?? "—"} icon={Target} />
            <StatCard title="Won" value={data.leads?.won ?? "—"} icon={Target} color="green" />
            <StatCard title="Lost" value={data.leads?.lost ?? "—"} icon={Target} color="red" />
            <StatCard title="Conversion Rate" value={`${data.leads?.conversion_rate_pct ?? 0}%`} icon={BarChart3} color="accent" />
          </div>
        </div>

        <div>
          <h2 className="section-title">Operations</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard title="Visits Done" value={data.visits?.completed ?? "—"} icon={Map} color="green" />
            <StatCard title="Pending Visits" value={data.visits?.pending ?? "—"} icon={Map} />
            <StatCard title="Failed Visits" value={data.visits?.failed ?? "—"} icon={Map} color="red" />
            <StatCard title="Farm Employees" value={data.employees?.total_farm_employees ?? "—"} icon={Users} />
          </div>
        </div>

        <div>
          <h2 className="section-title">Financial</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard title="Total Revenue" value={data.revenue?.grand_total ? `₹${Number(data.revenue.grand_total).toLocaleString()}` : "—"} icon={DollarSign} color="accent" />
            <StatCard title="Investments" value={data.investments?.total_invested ? `₹${Number(data.investments.total_invested).toLocaleString()}` : "—"} icon={DollarSign} color="green" />
            <StatCard title="Active Investments" value={data.investments?.active_investments ?? "—"} icon={BarChart3} />
            <StatCard title="Settled Returns" value={data.investments?.total_settled ? `₹${Number(data.investments.total_settled).toLocaleString()}` : "—"} icon={DollarSign} color="green" />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
