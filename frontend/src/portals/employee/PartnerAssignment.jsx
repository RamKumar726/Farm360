import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { EMPLOYEE_NAV } from "./_nav";
import { workPartnersAPI, workOrdersAPI, zonesAPI } from "../../config/api";
import toast from "react-hot-toast";
import { Plus } from "lucide-react";
import useAppStore from "../../store/useAppStore";

export default function EmployeePartnerAssignment() {
  const { user } = useAppStore();
  const [partners, setPartners] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);
  const [zones, setZones] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", contact: "", work_types: "", user_email: "", zone_id: "" });
  const [linkEmails, setLinkEmails] = useState({});

  useEffect(() => {
    workPartnersAPI.list().then((r) => { if (r.success) setPartners(r.data.items); });
    workOrdersAPI.list({ status: "pending" }).then((r) => { if (r.success) setWorkOrders(r.data.items); });
    zonesAPI.list({ page_size: 100 }).then((r) => { if (r.success) setZones(r.data.items || []); });
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      const res = await workPartnersAPI.create({ ...form, zone_id: form.zone_id || user?.zone_id || null, user_email: form.user_email || null, work_types: form.work_types.split(",").map((s) => s.trim()).filter(Boolean) });
      if (res.success) { setPartners((p) => [...p, res.data]); setShowForm(false); toast.success("Partner added!"); }
    } catch { toast.error("Failed"); }
  };

  const assignPartner = async (workOrderId, partnerId) => {
    await workOrdersAPI.assignPartner(workOrderId, partnerId);
    toast.success("Partner assigned! Notifying via WhatsApp...");
  };

  const linkAccount = async (partnerId) => {
    try {
      const result = await workPartnersAPI.linkAccount(partnerId, linkEmails[partnerId]);
      setPartners((rows) => rows.map((row) => row.id === partnerId ? result.data : row));
      toast.success("Provider portal account linked");
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not link account"); }
  };

  return (
    <PortalPage title="Partner Assignment" subtitle="Assign outsourcing partners to pending work orders" navItems={EMPLOYEE_NAV}>
      <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}><Plus size={16} /> Add Partner</button>
      {showForm && (
        <div className="card animate-slide-up">
          <form onSubmit={handleAdd} className="grid md:grid-cols-2 gap-4">
            <div><label className="label">Partner Name</label><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
            <div><label className="label">Contact</label><input className="input" value={form.contact} onChange={(e) => setForm({ ...form, contact: e.target.value })} /></div>
            <div className="md:col-span-2"><label className="label">Provider login email (create a Work Partner account first)</label><input className="input" type="email" value={form.user_email} onChange={(e) => setForm({ ...form, user_email: e.target.value })} required /></div>
            <div><label className="label">Zone</label><select className="input" value={form.zone_id || user?.zone_id || ""} onChange={(e) => setForm({ ...form, zone_id: e.target.value })} required><option value="">Select zone</option>{zones.map((zone) => <option key={zone.id} value={zone.id}>{zone.name}</option>)}</select></div>
            <div className="md:col-span-2"><label className="label">Work Types (comma-separated)</label><input className="input" placeholder="cleaning, irrigation, harvest" value={form.work_types} onChange={(e) => setForm({ ...form, work_types: e.target.value })} /></div>
            <div className="flex gap-3"><button type="submit" className="btn-primary">Add Partner</button><button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button></div>
          </form>
        </div>
      )}
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h2 className="section-title">Available Partners ({partners.length})</h2>
          <div className="space-y-2">
            {partners.map((p) => (
              <div key={p.id} className="card p-4">
                <p className="font-semibold text-[#f0ede4]">{p.name}</p>
                <p className="text-sm text-[#8fac9a]">{p.contact}</p>
                <p className="text-xs text-accent">{p.work_types?.join(", ")}</p>
                <p className="text-xs text-[#8fac9a]">{p.user_id ? "Provider portal linked" : "No provider login linked"}</p>
                {!p.user_id && <div className="flex gap-2 mt-2"><input className="input" type="email" placeholder="Provider login email" value={linkEmails[p.id] || ""} onChange={(event) => setLinkEmails({ ...linkEmails, [p.id]: event.target.value })} /><button className="btn-secondary" onClick={() => linkAccount(p.id)}>Link</button></div>}
              </div>
            ))}
          </div>
        </div>
        <div>
          <h2 className="section-title">Pending Work Orders ({workOrders.length})</h2>
          <div className="space-y-2">
            {workOrders.map((w) => (
              <div key={w.id} className="card p-4">
                <p className="font-semibold text-[#f0ede4]">{w.type?.replace("_", " ")}</p>
                {partners[0] && (
                  <button onClick={() => assignPartner(w.id, partners[0].id)} className="btn-secondary text-sm mt-2 w-full">
                    Assign {partners[0].name}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </PortalPage>
  );
}
