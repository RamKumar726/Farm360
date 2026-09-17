import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { investmentsAPI, projectsAPI } from "../../config/api";
import StatusBadge from "../../components/StatusBadge";
import { TrendingUp } from "lucide-react";
import toast from "react-hot-toast";

export default function CustomerInvestments() {
  const [investments, setInvestments] = useState([]);
  const [projects, setProjects] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ project_id: "", type: "project_investment", amount: "" });

  useEffect(() => {
    investmentsAPI.list().then((r) => { if (r.success) setInvestments(r.data.items); });
    projectsAPI.list({ status: "open" }).then((r) => { if (r.success) setProjects(r.data.items); });
  }, []);

  const handleInvest = async (e) => {
    e.preventDefault();
    try {
      const res = await investmentsAPI.create({ ...form, amount: parseFloat(form.amount), customer_id: "self" });
      if (res.success) { setInvestments((p) => [res.data, ...p]); setShowForm(false); toast.success("Investment created! Revenue share calculated."); }
    } catch (err) { toast.error(err?.detail || "Failed"); }
  };

  return (
    <PortalPage title="My Investments" subtitle="Track your investment portfolio and returns" navItems={CUSTOMER_NAV}>
      <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}><TrendingUp size={16} /> New Investment</button>

      {showForm && (
        <div className="card animate-slide-up">
          <form onSubmit={handleInvest} className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">Project</label>
              <select className="input" value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })} required>
                <option value="">-- Select project --</option>
                {projects.map((p) => <option key={p.id} value={p.id}>{p.name} (₹{Number(p.total_amount).toLocaleString()})</option>)}
              </select>
            </div>
            <div><label className="label">Amount (₹)</label><input className="input" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required /></div>
            <div>
              <label className="label">Type</label>
              <select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                <option value="project_investment">Project Investment</option>
                <option value="agricultural_investment">Agricultural Investment</option>
                <option value="fixed_return">Fixed Return Bond</option>
              </select>
            </div>
            <div className="flex items-end gap-3">
              <button type="submit" className="btn-primary">💰 Invest</button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {investments.map((inv) => (
          <div key={inv.id} className="card">
            <div className="flex justify-between items-start mb-3">
              <span className="font-semibold text-[#f0ede4] capitalize">{inv.type?.replace("_", " ")}</span>
              <StatusBadge status={inv.status} />
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-[#8fac9a]">Invested</span><span className="font-semibold text-[#f0ede4]">₹{Number(inv.amount).toLocaleString()}</span></div>
              <div className="flex justify-between"><span className="text-[#8fac9a]">Revenue Share</span><span className="text-accent font-semibold">{inv.revenue_share_percentage?.toFixed(2) || 0}%</span></div>
              <div className="flex justify-between"><span className="text-[#8fac9a]">Expected Return</span><span className="text-green-400 font-semibold">{inv.expected_return ? `₹${Number(inv.expected_return).toLocaleString()}` : "—"}</span></div>
              {inv.actual_return && <div className="flex justify-between"><span className="text-[#8fac9a]">Actual Return</span><span className="text-green-400 font-bold">₹{Number(inv.actual_return).toLocaleString()}</span></div>}
            </div>
          </div>
        ))}
        {investments.length === 0 && <div className="col-span-2 card text-center py-10"><TrendingUp size={40} className="mx-auto mb-2 opacity-20" /><p className="text-[#8fac9a]">No investments yet</p></div>}
      </div>
    </PortalPage>
  );
}
