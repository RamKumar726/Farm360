import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import LeadCard from "../../components/LeadCard";
import { leadsAPI } from "../../config/api";

export default function ZoneAdminLeads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const params = filter !== "all" ? { status: filter } : {};
    leadsAPI.list(params).then((r) => { if (r.success) setLeads(r.data.items); setLoading(false); }).catch(() => setLoading(false));
  }, [filter]);

  return (
    <PortalPage title="Leads" subtitle="All leads in your branch" navItems={ZONE_ADMIN_NAV}>
      <div className="flex gap-2 flex-wrap">
        {["all", "new", "site_visit", "won", "lost"].map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-all ${filter === f ? "bg-accent text-primary-900 font-semibold" : "bg-white/5 text-[#8fac9a] hover:bg-white/10"}`}>
            {f === "all" ? "All" : f.replace("_", " ")}
          </button>
        ))}
      </div>
      {loading ? <p className="text-[#8fac9a] text-center py-8">Loading...</p> : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {leads.map((l) => <LeadCard key={l.id} lead={l} />)}
          {leads.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No leads found</p>}
        </div>
      )}
    </PortalPage>
  );
}
