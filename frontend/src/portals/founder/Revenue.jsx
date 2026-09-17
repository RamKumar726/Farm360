import { useState, useEffect } from "react";
import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { analyticsAPI } from "../../config/api";
import StatCard from "../../components/StatCard";
import { DollarSign, TrendingUp, FolderKanban, Handshake } from "lucide-react";

export default function FounderRevenue() {
  const [data, setData] = useState(null);
  const [invData, setInvData] = useState(null);

  useEffect(() => {
    analyticsAPI.revenue().then((r) => { if (r.success) setData(r.data); });
    analyticsAPI.investments().then((r) => { if (r.success) setInvData(r.data); });
  }, []);

  const fmt = (n) => n !== undefined ? `₹${Number(n).toLocaleString("en-IN")}` : "—";

  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-6">
        <h1 className="page-header">Revenue Overview</h1>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard title="Agreement Revenue" value={fmt(data?.total_agreement_revenue)} icon={Handshake} color="accent" />
          <StatCard title="Investment Capital" value={fmt(data?.total_investment_amount)} icon={TrendingUp} color="green" />
          <StatCard title="Project Revenue" value={fmt(data?.total_project_revenue)} icon={FolderKanban} color="blue" />
          <StatCard title="Grand Total" value={fmt(data?.grand_total)} icon={DollarSign} color="accent" />
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="card">
            <h2 className="section-title">Investment Summary</h2>
            <div className="space-y-3">
              {[
                { label: "Total Invested", val: fmt(invData?.total_invested) },
                { label: "Total Settled Returns", val: fmt(invData?.total_settled) },
                { label: "Active Investments", val: invData?.active_investments ?? "—" },
                { label: "Settled Investments", val: invData?.settled_investments ?? "—" },
              ].map((r) => (
                <div key={r.label} className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-[#8fac9a]">{r.label}</span>
                  <span className="font-semibold text-[#f0ede4]">{r.val}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="card">
            <h2 className="section-title">Revenue Channels</h2>
            <div className="space-y-4">
              {[
                { label: "Farm Agreements", value: data?.total_agreement_revenue || 0, total: data?.grand_total || 1, color: "bg-accent" },
                { label: "Investments", value: data?.total_investment_amount || 0, total: data?.grand_total || 1, color: "bg-green-400" },
                { label: "Projects", value: data?.total_project_revenue || 0, total: data?.grand_total || 1, color: "bg-blue-400" },
              ].map((r) => (
                <div key={r.label}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-[#8fac9a]">{r.label}</span>
                    <span className="text-[#f0ede4]">{Math.round((r.value / r.total) * 100) || 0}%</span>
                  </div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div className={`h-full ${r.color} rounded-full transition-all duration-1000`}
                         style={{ width: `${Math.round((r.value / r.total) * 100) || 0}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
