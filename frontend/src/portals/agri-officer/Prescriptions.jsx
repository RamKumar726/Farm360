import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { AGRI_NAV } from "./_nav";
import { prescriptionsAPI } from "../../config/api";
import StatusBadge from "../../components/StatusBadge";
import { Plus } from "lucide-react";
import toast from "react-hot-toast";

export default function AgriPrescriptions() {
  const [prescriptions, setPrescriptions] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ farm_id: "", type: "direct", content: "", estimated_cost: "", items: "" });

  useEffect(() => { prescriptionsAPI.list().then((r) => { if (r.success) setPrescriptions(r.data.items); }); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await prescriptionsAPI.create({
        ...form,
        estimated_cost: parseFloat(form.estimated_cost) || 0,
        items: form.items.split(",").map((s) => s.trim()).filter(Boolean),
      });
      if (res.success) { setPrescriptions((p) => [res.data, ...p]); setShowForm(false); toast.success("Prescription created!"); }
    } catch { toast.error("Failed"); }
  };

  return (
    <PortalPage title="Prescriptions" subtitle="Create and manage farm care prescriptions" navItems={AGRI_NAV}>
      <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}><Plus size={16} /> New Prescription</button>
      {showForm && (
        <div className="card animate-slide-up">
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div><label className="label">Farm ID</label><input className="input" placeholder="Farm UUID" value={form.farm_id} onChange={(e) => setForm({ ...form, farm_id: e.target.value })} required /></div>
              <div>
                <label className="label">Type</label>
                <select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                  <option value="direct">Direct (Customer pays)</option>
                  <option value="lease">Lease (Prasad covers)</option>
                </select>
              </div>
              <div><label className="label">Estimated Cost (₹)</label><input className="input" type="number" value={form.estimated_cost} onChange={(e) => setForm({ ...form, estimated_cost: e.target.value })} /></div>
              <div><label className="label">Items (comma-separated)</label><input className="input" placeholder="fertilizer, seeds, labor" value={form.items} onChange={(e) => setForm({ ...form, items: e.target.value })} /></div>
            </div>
            <div><label className="label">Prescription Content</label><textarea className="input min-h-[100px]" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} /></div>
            <div className="flex gap-3">
              <button type="submit" className="btn-primary">Submit</button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        {prescriptions.map((rx) => (
          <div key={rx.id} className="card">
            <div className="flex justify-between items-start mb-2">
              <span className="badge-accent">{rx.type}</span>
              <StatusBadge status={rx.status} />
            </div>
            <p className="text-sm text-[#8fac9a] mt-2">{rx.content}</p>
            {rx.estimated_cost && <p className="text-accent font-semibold mt-2">₹{Number(rx.estimated_cost).toLocaleString()}</p>}
          </div>
        ))}
      </div>
    </PortalPage>
  );
}
