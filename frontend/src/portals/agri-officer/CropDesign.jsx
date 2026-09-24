import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { AGRI_NAV } from "./_nav";
import { cropDesignsAPI, projectsAPI, apiFetch } from "../../config/api";
import StatusBadge from "../../components/StatusBadge";
import { Plus, Check, Zap, Sprout } from "lucide-react";
import toast from "react-hot-toast";

export default function AgriCropDesign() {
  const [designs, setDesigns] = useState([]);
  const [prototypes, setPrototypes] = useState([]);
  const [projects, setProjects] = useState([]);
  const [tab, setTab] = useState("prototypes");

  // New Prototype Form
  const [showProtoForm, setShowProtoForm] = useState(false);
  const [protoForm, setProtoForm] = useState({
    crop_name: "", total_duration_days: 120, project_type: "managed",
    water_schedule_days: 15, fertilizer_schedule_days: 25,
    ao_visit_schedule_days: 15, harvest_day: 120, description: "",
  });

  // Apply Prototype Modal
  const [selectedProto, setSelectedProto] = useState(null);
  const [targetProjectId, setTargetProjectId] = useState("");

  const loadData = () => {
    cropDesignsAPI.list().then((r) => { if (r.success) setDesigns(r.data.items); });
    apiFetch("/projects/prototypes").then((r) => { if (r.success) setPrototypes(r.data); });
    projectsAPI.list().then((r) => { if (r.success) setProjects(r.data.items); });
  };

  useEffect(() => { loadData(); }, []);

  const handleCreatePrototype = async (e) => {
    e.preventDefault();
    const res = await apiFetch("/projects/prototypes", {
      method: "POST",
      body: JSON.stringify(protoForm),
    });
    if (res.success) {
      toast.success("Crop Prototype created!");
      setShowProtoForm(false);
      loadData();
    } else {
      toast.error(res.message || "Failed to create prototype");
    }
  };

  const handleApplyPrototype = async () => {
    if (!selectedProto || !targetProjectId) return;
    const res = await apiFetch(`/projects/${targetProjectId}/apply-prototype?prototype_id=${selectedProto.id}`, {
      method: "POST",
    });
    if (res.success) {
      toast.success(res.message || "Prototype applied and task timeline generated!");
      setSelectedProto(null);
    } else {
      toast.error(res.message || "Failed to apply prototype");
    }
  };

  return (
    <PortalPage title="Crop Design & Prototypes" subtitle="Build reusable crop prototypes and auto-generate task schedules for projects" navItems={AGRI_NAV}>
      <div className="space-y-6">
        <div className="flex gap-2 border-b border-white/10 pb-3">
          <button onClick={() => setTab("prototypes")} className={`px-4 py-2 rounded-xl text-sm font-semibold ${tab === "prototypes" ? "bg-accent text-primary-900" : "bg-white/5 text-[#8fac9a]"}`}>
            🌾 Crop Prototypes ({prototypes.length})
          </button>
          <button onClick={() => setTab("designs")} className={`px-4 py-2 rounded-xl text-sm font-semibold ${tab === "designs" ? "bg-accent text-primary-900" : "bg-white/5 text-[#8fac9a]"}`}>
            📋 Custom Crop Designs ({designs.length})
          </button>
        </div>

        {tab === "prototypes" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <p className="text-sm text-[#8fac9a]">Prototypes automate task creation for Managed & Lease projects.</p>
              <button className="btn-primary flex items-center gap-2 font-bold text-sm" onClick={() => setShowProtoForm(!showProtoForm)}>
                <Plus size={16} /> Build Crop Prototype
              </button>
            </div>

            {showProtoForm && (
              <div className="card border-accent/40 animate-slide-up">
                <form onSubmit={handleCreatePrototype} className="space-y-4">
                  <h3 className="text-lg font-bold text-[#f0ede4]">Build Reusable Crop Prototype</h3>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                    <div><label className="label">Crop Name</label><input className="input" placeholder="e.g. Rice / Banana" value={protoForm.crop_name} onChange={(e) => setProtoForm({ ...protoForm, crop_name: e.target.value })} required /></div>
                    <div><label className="label">Total Crop Duration (Days)</label><input className="input" type="number" value={protoForm.total_duration_days} onChange={(e) => setProtoForm({ ...protoForm, total_duration_days: Number(e.target.value) })} required /></div>
                    <div>
                      <label className="label">Project Type</label>
                      <select className="input" value={protoForm.project_type} onChange={(e) => setProtoForm({ ...protoForm, project_type: e.target.value })}>
                        <option value="managed">Managed Farm</option>
                        <option value="lease">Lease Farm</option>
                        <option value="one_time">One-Time Service</option>
                      </select>
                    </div>
                    <div><label className="label">Water Schedule (Interval Days)</label><input className="input" type="number" value={protoForm.water_schedule_days} onChange={(e) => setProtoForm({ ...protoForm, water_schedule_days: Number(e.target.value) })} /></div>
                    <div><label className="label">Fertilizer Schedule (Day #)</label><input className="input" type="number" value={protoForm.fertilizer_schedule_days} onChange={(e) => setProtoForm({ ...protoForm, fertilizer_schedule_days: Number(e.target.value) })} /></div>
                    <div><label className="label">AO Visit Schedule (Interval Days)</label><input className="input" type="number" value={protoForm.ao_visit_schedule_days} onChange={(e) => setProtoForm({ ...protoForm, ao_visit_schedule_days: Number(e.target.value) })} /></div>
                    <div><label className="label">Harvest Day (Day #)</label><input className="input" type="number" value={protoForm.harvest_day} onChange={(e) => setProtoForm({ ...protoForm, harvest_day: Number(e.target.value) })} /></div>
                  </div>
                  <div><label className="label">Description & Practices</label><textarea className="input" rows={2} value={protoForm.description} onChange={(e) => setProtoForm({ ...protoForm, description: e.target.value })} /></div>
                  <div className="flex gap-3">
                    <button type="submit" className="btn-primary font-bold">Save Prototype</button>
                    <button type="button" className="btn-secondary" onClick={() => setShowProtoForm(false)}>Cancel</button>
                  </div>
                </form>
              </div>
            )}

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {prototypes.map((proto) => (
                <div key={proto.id} className="card hover:border-accent/40 transition-all flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex justify-between items-start">
                      <h3 className="font-bold text-[#f0ede4] text-lg flex items-center gap-2"><Sprout className="text-accent" size={18} /> {proto.crop_name}</h3>
                      <span className="text-xs bg-white/10 px-2.5 py-1 rounded-full text-accent font-semibold uppercase">{proto.project_type}</span>
                    </div>
                    <p className="text-xs text-[#8fac9a]">Duration: {proto.total_duration_days} Days</p>

                    <div className="bg-white/5 p-3 rounded-xl text-xs space-y-1 text-[#8fac9a]">
                      <p>💧 Water Schedule: Every {proto.water_schedule_days} Days</p>
                      <p>🧪 Fertilizer: Day {proto.fertilizer_schedule_days}</p>
                      <p>👨‍🌾 AO Visits: Every {proto.ao_visit_schedule_days} Days</p>
                      <p>🌾 Harvest: Day {proto.harvest_day}</p>
                    </div>
                  </div>

                  <button onClick={() => { setSelectedProto(proto); setTargetProjectId(""); }} className="btn-primary w-full mt-4 text-xs font-bold flex items-center justify-center gap-2">
                    <Zap size={14} /> Apply Prototype to Project
                  </button>
                </div>
              ))}
              {prototypes.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No crop prototypes defined yet</p>}
            </div>
          </div>
        )}

        {tab === "designs" && (
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
        )}
      </div>

      {/* APPLY PROTOTYPE MODAL */}
      {selectedProto && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121c17] border border-accent/30 rounded-3xl p-6 max-w-md w-full space-y-4 text-left">
            <h3 className="text-xl font-bold text-[#f0ede4]">Apply Prototype ({selectedProto.crop_name})</h3>
            <p className="text-xs text-[#8fac9a]">Select a project to automatically generate water, fertilizer, AO inspection & harvest task schedules.</p>

            <div>
              <label className="block text-xs text-[#8fac9a] uppercase font-semibold mb-1">Target Project</label>
              <select className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-[#f0ede4] outline-none" value={targetProjectId} onChange={(e) => setTargetProjectId(e.target.value)}>
                <option value="">-- Select Project --</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.name} (#{p.id?.slice(0, 8)})</option>
                ))}
              </select>
            </div>

            <div className="flex gap-3 pt-2">
              <button onClick={() => setSelectedProto(null)} className="btn-secondary flex-1 py-3">Cancel</button>
              <button onClick={handleApplyPrototype} disabled={!targetProjectId} className="btn-primary flex-1 py-3 font-bold disabled:opacity-50">Apply Now</button>
            </div>
          </div>
        </div>
      )}
    </PortalPage>
  );
}
