import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { EMPLOYEE_NAV } from "./_nav";
import LeadCard from "../../components/LeadCard";
import { leadsAPI } from "../../config/api";
import { Plus } from "lucide-react";
import toast from "react-hot-toast";

export default function EmployeeLeadPipeline() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ type: "site_management", source: "employee", farm_details: "", site_visit_date: "" });

  useEffect(() => {
    leadsAPI.list().then((r) => { if (r.success) setLeads(r.data.items); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await leadsAPI.create(form);
      if (res.success) { setLeads((p) => [res.data, ...p]); setShowForm(false); toast.success("Lead added!"); }
    } catch (err) { toast.error(err?.detail || "Failed"); }
  };

  const advanceLead = async (lead) => {
    const transitions = { new: "site_visit", site_visit: "advance_paid", advance_paid: "won", won: "completed" };
    if (!transitions[lead.status]) return toast.error("No further transition available");
    try {
      const res = await leadsAPI.updateStatus(lead.id, { status: transitions[lead.status] });
      if (res.success) setLeads((p) => p.map((l) => l.id === lead.id ? res.data : l));
    } catch (err) { toast.error(err?.detail || "Transition failed"); }
  };

  return (
    <PortalPage title="Lead Pipeline" subtitle="Manage and advance your assigned leads" navItems={EMPLOYEE_NAV}>
      <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}><Plus size={16} /> New Lead</button>

      {showForm && (
        <div className="card animate-slide-up">
          <h2 className="section-title">Add New Lead</h2>
          <form onSubmit={handleCreate} className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">Type</label>
              <select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                <option value="site_management">Site Management</option>
                <option value="farm_lease">Farm Lease</option>
                <option value="farm_manage">Farm Manage</option>
                <option value="farm_management">Farm Management</option>
              </select>
            </div>
            <div>
              <label className="label">Source</label>
              <select className="input" value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })}>
                <option value="employee">Employee</option>
                <option value="website">Website</option>
                <option value="referral">Referral</option>
                <option value="call_message">Call/Message</option>
                <option value="digital_marketing">Digital Marketing</option>
              </select>
            </div>
            <div className="md:col-span-2"><label className="label">Farm Details</label><textarea className="input min-h-[80px]" value={form.farm_details} onChange={(e) => setForm({ ...form, farm_details: e.target.value })} /></div>
            <div><label className="label">Site Visit Date</label><input type="date" className="input" value={form.site_visit_date} onChange={(e) => setForm({ ...form, site_visit_date: e.target.value })} /></div>
            <div className="flex items-end gap-3">
              <button type="submit" className="btn-primary">Create Lead</button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {loading ? <p className="text-center text-[#8fac9a] py-8">Loading...</p> : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {leads.map((lead) => (
            <div key={lead.id}>
              <LeadCard lead={lead} />
              {!["won", "completed", "lost"].includes(lead.status) && (
                <button onClick={() => advanceLead(lead)} className="btn-secondary w-full mt-2 text-sm">
                  → Advance to next stage
                </button>
              )}
            </div>
          ))}
          {leads.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No leads yet</p>}
        </div>
      )}
    </PortalPage>
  );
}
