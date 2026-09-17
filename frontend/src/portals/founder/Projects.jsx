import { useState, useEffect } from "react";
import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { projectsAPI } from "../../config/api";
import { Plus, FolderKanban } from "lucide-react";
import StatusBadge from "../../components/StatusBadge";
import toast from "react-hot-toast";

export default function FounderProjects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", type: "project_investment", total_amount: "", description: "" });

  useEffect(() => {
    projectsAPI.list().then((r) => { if (r.success) setProjects(r.data.items); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await projectsAPI.create({ ...form, total_amount: parseFloat(form.total_amount) });
      if (res.success) { setProjects((p) => [res.data, ...p]); setShowForm(false); toast.success("Project posted! Customers notified."); }
    } catch { toast.error("Failed to create project"); }
  };

  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="page-header">Investment Projects</h1>
          <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}><Plus size={16} /> Post Project</button>
        </div>

        {showForm && (
          <div className="card animate-slide-up">
            <h2 className="section-title">New Investment Project</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div><label className="label">Project Name</label><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></div>
                <div>
                  <label className="label">Type</label>
                  <select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                    <option value="project_investment">Project Investment</option>
                    <option value="agricultural_investment">Agricultural Investment</option>
                    <option value="joint_project">Joint Project</option>
                  </select>
                </div>
                <div><label className="label">Total Amount (₹)</label><input className="input" type="number" value={form.total_amount} onChange={(e) => setForm({ ...form, total_amount: e.target.value })} required /></div>
              </div>
              <div><label className="label">Description</label><textarea className="input min-h-[80px]" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
              <div className="flex gap-3">
                <button type="submit" className="btn-primary">Post Project</button>
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        )}

        {loading ? <div className="text-center py-8 text-[#8fac9a]">Loading...</div> : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((p) => (
              <div key={p.id} className="card">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-[#f0ede4]">{p.name}</h3>
                  <StatusBadge status={p.status} />
                </div>
                <p className="text-xs text-accent mb-3">{p.type?.replace("_", " ")}</p>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-[#8fac9a]">Target</span><span className="font-semibold text-[#f0ede4]">₹{Number(p.total_amount).toLocaleString()}</span></div>
                  <div className="flex justify-between"><span className="text-[#8fac9a]">Funded</span><span className="text-green-400">₹{Number(p.funded_amount).toLocaleString()}</span></div>
                </div>
                <div className="mt-3">
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-accent rounded-full" style={{ width: `${p.funding_percentage || 0}%` }} />
                  </div>
                  <p className="text-right text-xs text-accent mt-1">{p.funding_percentage}% funded</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
