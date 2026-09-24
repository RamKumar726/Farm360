import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { FOUNDER_NAV } from "./_nav";
import { leadsAPI } from "../../config/api";
import LeadCard from "../../components/LeadCard";

const SERVICE_STAGE_FILTERS = [
  { key: "all",              label: "All Leads" },
  { key: "prospecting",      label: "🌱 Prospecting" },
  { key: "qualification",    label: "🔍 Qualification" },
  { key: "need_analysis",    label: "📋 Need Analysis" },
  { key: "value_proposition",label: "💡 Value Prop" },
  { key: "decision_makers",  label: "👥 Decision Makers" },
  { key: "proposal_price",   label: "📄 Proposal / Price" },
  { key: "negotiation",      label: "🤝 Negotiation" },
  { key: "register_user",    label: "📲 Register User" },
  { key: "payment",          label: "💳 Payment" },
  { key: "closed_won",       label: "🏆 Closed Won" },
  { key: "closed_lost",      label: "❌ Closed Lost" },
  // Lease only
  { key: "land_verification",label: "🗺️ Land Verification" },
  { key: "feasibility",      label: "🔬 Feasibility" },
  { key: "agreement",        label: "📜 Agreement" },
  { key: "approval",         label: "✅ Approval" },
];

export default function FounderLeads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    const params = filter !== "all" ? { status: filter } : {};
    leadsAPI
      .list(params)
      .then((res) => { if (res.success) setLeads(res.data.items); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [filter]);

  const displayed = leads.filter((l) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      l.farm_details?.toLowerCase().includes(q) ||
      l.type?.toLowerCase().includes(q) ||
      l.source?.toLowerCase().includes(q) ||
      l.id?.toLowerCase().includes(q)
    );
  });

  const wonCount   = leads.filter((l) => l.status === "closed_won").length;
  const lostCount  = leads.filter((l) => l.status === "closed_lost").length;
  const activeCount= leads.filter((l) => l.status !== "closed_won" && l.status !== "closed_lost").length;

  return (
    <PortalPage
      title="Lead Pipeline — Full View"
      subtitle="Complete CRM lead pipeline across all branches, zones &amp; sources"
      navItems={FOUNDER_NAV}
    >
      <div className="space-y-6">

        {/* KPI row */}
        <div className="grid grid-cols-3 gap-4">
          <div className="card text-center">
            <p className="text-2xl font-bold text-accent">{activeCount}</p>
            <p className="text-xs text-[#8fac9a] mt-1">Active Leads</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-emerald-400">{wonCount}</p>
            <p className="text-xs text-[#8fac9a] mt-1">Closed Won</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-red-400">{lostCount}</p>
            <p className="text-xs text-[#8fac9a] mt-1">Closed Lost</p>
          </div>
        </div>

        {/* Search */}
        <input
          type="text"
          className="input w-full md:w-96"
          placeholder="Search by client name, type, source or ID…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {/* Stage filter chips */}
        <div className="flex gap-2 flex-wrap">
          {SERVICE_STAGE_FILTERS.map((f) => (
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

        {/* Lead grid */}
        {loading ? (
          <p className="text-center text-[#8fac9a] py-10">Loading pipeline…</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {displayed.map((lead) => (
              <LeadCard key={lead.id} lead={lead} />
            ))}
            {displayed.length === 0 && (
              <p className="col-span-3 text-center text-[#8fac9a] py-12">
                No leads found {filter !== "all" ? `at stage "${filter.replace(/_/g, " ")}"` : ""}
              </p>
            )}
          </div>
        )}
      </div>
    </PortalPage>
  );
}
