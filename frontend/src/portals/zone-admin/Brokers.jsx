import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import { brokersAPI } from "../../config/api";
import { Plus } from "lucide-react";
import toast from "react-hot-toast";

export default function ZoneAdminBrokers() {
  const [brokers, setBrokers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", contact: "" });

  useEffect(() => { brokersAPI.list().then((r) => { if (r.success) setBrokers(r.data.items); }); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await brokersAPI.create(form);
      if (res.success) { setBrokers((p) => [...p, res.data]); setShowForm(false); toast.success("Broker added"); }
    } catch { toast.error("Failed"); }
  };

  return (
    <PortalPage title="Broker Network" navItems={ZONE_ADMIN_NAV}>
      <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}><Plus size={16} /> Add Broker</button>
      {showForm && (
        <div className="card animate-slide-up">
          <form onSubmit={handleCreate} className="grid md:grid-cols-2 gap-4">
            <div><label className="label">Name</label><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
            <div><label className="label">Contact</label><input className="input" value={form.contact} onChange={(e) => setForm({ ...form, contact: e.target.value })} /></div>
            <div className="flex gap-3"><button type="submit" className="btn-primary">Add</button><button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button></div>
          </form>
        </div>
      )}
      <div className="grid md:grid-cols-3 gap-4">
        {brokers.map((b) => (
          <div key={b.id} className="card">
            <p className="font-semibold text-[#f0ede4]">{b.name}</p>
            <p className="text-sm text-[#8fac9a]">{b.contact || "No contact"}</p>
            <p className="text-xs text-accent mt-1">Zone: {b.zone_id?.slice(0, 8) || "Unassigned"}</p>
          </div>
        ))}
      </div>
    </PortalPage>
  );
}
