import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import LeadCard from "../../components/LeadCard";
import { leadsAPI } from "../../config/api";
import InvestmentPipeline from "../../components/InvestmentPipeline";
import { apiFetch } from "../../config/api";
import toast from "react-hot-toast";

const FILTERS = [
  { key: "all",              label: "All" },
  { key: "prospecting",      label: "🌱 Prospecting" },
  { key: "qualification",    label: "🔍 Qualification" },
  { key: "need_analysis",    label: "📋 Need Analysis" },
  { key: "proposal_price",   label: "📄 Proposal" },
  { key: "negotiation",      label: "🤝 Negotiation" },
  { key: "payment",          label: "💳 Payment" },
  { key: "closed_won",       label: "🏆 Won" },
  { key: "closed_lost",      label: "❌ Lost" },
  // Lease stages
  { key: "land_verification",label: "🗺️ Land Verify" },
  { key: "feasibility",      label: "🔬 Feasibility" },
  { key: "agreement",        label: "📜 Agreement" },
  { key: "approval",         label: "✅ Approval" },
];

export default function ZoneAdminLeads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  const reviewLease = async (leadId, approved) => {
    try {
      await apiFetch(`/leads/${leadId}/approval?approved=${approved}`, { method: "POST" });
      toast.success(approved ? "Zone approval recorded; sent for Founder review" : "Lease opportunity rejected");
      const params = filter !== "all" ? { status: filter } : {};
      const result = await leadsAPI.list(params);
      if (result.success) setLeads(result.data.items);
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not record zone approval"); }
  };

  useEffect(() => {
    setLoading(true);
    const params = filter !== "all" ? { status: filter } : {};
    leadsAPI
      .list(params)
      .then((r) => { if (r.success) setLeads(r.data.items); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [filter]);

  return (
    <PortalPage title="Leads" subtitle="All leads in your branch" navItems={ZONE_ADMIN_NAV}>
      <InvestmentPipeline />
      <div className="space-y-4">
        {/* Filter chips */}
        <div className="flex gap-2 flex-wrap">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                filter === f.key
                  ? "bg-accent text-primary-900 font-semibold"
                  : "bg-white/5 text-[#8fac9a] hover:bg-white/10"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="text-[#8fac9a] text-center py-8">Loading leads…</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {leads.map((l) => <div key={l.id} className="space-y-2"><LeadCard lead={l} />{l.status === "approval" && (l.type === "farm_lease" || l.type === "sell_land") && <div className="card flex gap-2"><button className="btn-secondary flex-1 text-red-300" onClick={() => reviewLease(l.id, false)}>Reject</button><button className="btn-primary flex-1" onClick={() => reviewLease(l.id, true)}>Approve and send to Founder</button></div>}</div>)}
            {leads.length === 0 && (
              <p className="col-span-3 text-center text-[#8fac9a] py-10">No leads found</p>
            )}
          </div>
        )}
      </div>
    </PortalPage>
  );
}
