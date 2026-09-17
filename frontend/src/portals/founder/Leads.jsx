import { useState, useEffect } from "react";
import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { leadsAPI } from "../../config/api";
import LeadCard from "../../components/LeadCard";
import StatusBadge from "../../components/StatusBadge";

export default function FounderLeads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const params = filter !== "all" ? { status: filter } : {};
    leadsAPI.list(params).then((res) => { if (res.success) setLeads(res.data.items); setLoading(false); }).catch(() => setLoading(false));
  }, [filter]);

  const FILTERS = ["all", "new", "site_visit", "advance_paid", "won", "completed", "lost"];

  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-6">
        <div>
          <h1 className="page-header">All Leads</h1>
          <p className="text-[#8fac9a] mt-1">Complete lead pipeline across all branches</p>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 flex-wrap">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${filter === f ? "bg-accent text-primary-900" : "bg-white/5 text-[#8fac9a] hover:bg-white/10"}`}
            >
              {f === "all" ? "All" : f.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase())}
            </button>
          ))}
        </div>

        {loading ? <div className="text-center text-[#8fac9a] py-8">Loading leads...</div> : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {leads.map((lead) => <LeadCard key={lead.id} lead={lead} />)}
            {leads.length === 0 && <div className="col-span-3 text-center text-[#8fac9a] py-12">No leads found</div>}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
