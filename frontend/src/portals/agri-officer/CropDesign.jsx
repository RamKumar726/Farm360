import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { AGRI_NAV } from "./_nav";
import { cropDesignsAPI } from "../../config/api";
import StatusBadge from "../../components/StatusBadge";
import { Plus, Check } from "lucide-react";
import toast from "react-hot-toast";

export default function AgriCropDesign() {
  const [designs, setDesigns] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ farm_id: "", best_practices: "", land_suitability: "", timing: "", crop_time: "", estimated_yearly_cost: "", intercrop_design: "", recommended_machines: "", research_notes: "" });

  useEffect(() => { cropDesignsAPI.list().then((r) => { if (r.success) setDesigns(r.data.items); }); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await cropDesignsAPI.create({ ...form, estimated_yearly_cost: parseFloat(form.estimated_yearly_cost) || 0 });
      if (res.success) { setDesigns((p) => [res.data, ...p]); setShowForm(false); toast.success("Crop design submitted!"); }
    } catch { toast.error("Failed"); }
  };

  return (
    <PortalPage title="Crop Design" subtitle="Design crop plans — approved designs auto-generate cycles" navItems={AGRI_NAV}>
      <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}><Plus size={16} /> New Crop Design</button>
      {showForm && (
        <div className="card animate-slide-up">
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div><label className="label">Farm ID</label><input className="input" value={form.farm_id} onChange={(e) => setForm({ ...form, farm_id: e.target.value })} required /></div>
              <div><label className="label">Land Suitability</label><input className="input" placeholder="Sandy loam, suitable for tomato" value={form.land_suitability} onChange={(e) => setForm({ ...form, land_suitability: e.target.value })} /></div>
              <div><label className="label">Crop Timing</label><input className="input" placeholder="Kharif / Rabi / Summer" value={form.timing} onChange={(e) => setForm({ ...form, timing: e.target.value })} /></div>
              <div><label className="label">Crop Time (months)</label><input className="input" placeholder="4 months" value={form.crop_time} onChange={(e) => setForm({ ...form, crop_time: e.target.value })} /></div>
              <div><label className="label">Yearly Cost (₹)</label><input className="input" type="number" value={form.estimated_yearly_cost} onChange={(e) => setForm({ ...form, estimated_yearly_cost: e.target.value })} /></div>
              <div><label className="label">Recommended Machines</label><input className="input" placeholder="Tractor, harvester..." value={form.recommended_machines} onChange={(e) => setForm({ ...form, recommended_machines: e.target.value })} /></div>
            </div>
            <div><label className="label">Best Practices</label><textarea className="input min-h-[80px]" value={form.best_practices} onChange={(e) => setForm({ ...form, best_practices: e.target.value })} /></div>
            <div><label className="label">Intercrop Design</label><textarea className="input" value={form.intercrop_design} onChange={(e) => setForm({ ...form, intercrop_design: e.target.value })} /></div>
            <div><label className="label">Research Notes</label><textarea className="input" value={form.research_notes} onChange={(e) => setForm({ ...form, research_notes: e.target.value })} /></div>
            <div className="flex gap-3">
              <button type="submit" className="btn-primary">Submit Design</button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        {designs.map((cd) => (
          <div key={cd.id} className="card">
            <div className="flex justify-between items-start mb-3">
              <p className="font-semibold text-[#f0ede4]">Farm: {cd.farm_id?.slice(0, 8)}</p>
              <StatusBadge status={cd.approval_status} />
            </div>
            <div className="space-y-1 text-sm text-[#8fac9a]">
              {cd.timing && <p>Timing: {cd.timing}</p>}
              {cd.estimated_yearly_cost && <p className="text-accent">₹{Number(cd.estimated_yearly_cost).toLocaleString()}/year</p>}
            </div>
          </div>
        ))}
      </div>
    </PortalPage>
  );
}
