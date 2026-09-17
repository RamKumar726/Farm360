import { useState, useEffect } from "react";
import { Plus, Search, Edit2, Trash2, Layers, UserCheck } from "lucide-react";
import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { zonesAPI, branchesAPI, usersAPI } from "../../config/api";
import toast from "react-hot-toast";

export default function FounderZones() {
  const [zones, setZones] = useState([]);
  const [branches, setBranches] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editZone, setEditZone] = useState(null);
  const [form, setForm] = useState({ name: "", branch_id: "", responsible_employee_id: "" });

  const loadData = async () => {
    try {
      const [resZ, resB, resU] = await Promise.all([
        zonesAPI.list({ page_size: 100 }),
        branchesAPI.list({ page_size: 100 }),
        usersAPI.list({ page_size: 100 }),
      ]);
      if (resZ.success) setZones(resZ.data.items);
      if (resB.success) setBranches(resB.data.items);
      if (resU.success) setUsers(resU.data.items);
    } catch {
      toast.error("Failed to load zones data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateOrUpdate = async (e) => {
    e.preventDefault();
    try {
      if (editZone) {
        const res = await zonesAPI.update(editZone.id, form);
        if (res.success) {
          setZones((prev) => prev.map((z) => (z.id === editZone.id ? res.data : z)));
          toast.success("Zone updated successfully");
          setEditZone(null);
          setShowForm(false);
        }
      } else {
        const res = await zonesAPI.create(form);
        if (res.success) {
          setZones((prev) => [...prev, res.data]);
          toast.success("Zone created successfully");
          setShowForm(false);
        }
      }
      setForm({ name: "", branch_id: "", responsible_employee_id: "" });
    } catch (err) {
      toast.error(err?.detail || "Action failed");
    }
  };

  const startEdit = (z) => {
    setEditZone(z);
    setForm({
      name: z.name,
      branch_id: z.branch_id || "",
      responsible_employee_id: z.responsible_employee_id || "",
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this zone?")) return;
    try {
      const res = await zonesAPI.delete(id);
      if (res.success) {
        setZones((prev) => prev.filter((z) => z.id !== id));
        toast.success("Zone deleted");
      }
    } catch {
      toast.error("Failed to delete zone");
    }
  };

  const filtered = zones.filter(
    (z) =>
      z.name.toLowerCase().includes(search.toLowerCase()) ||
      (z.branch_id && z.branch_id.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-header">Zone Governance</h1>
            <p className="text-[#8fac9a] text-xs mt-1">Configure operational zones, branch mappings, and responsible managers.</p>
          </div>
          <button
            className="btn-primary flex items-center gap-2"
            onClick={() => {
              setEditZone(null);
              setForm({ name: "", branch_id: "", responsible_employee_id: "" });
              setShowForm(!showForm);
            }}
          >
            <Plus size={16} /> {showForm ? "Close Form" : "Add Zone"}
          </button>
        </div>

        {showForm && (
          <div className="card animate-slide-up border border-accent/40 shadow-glow">
            <h2 className="section-title text-lg mb-4">{editZone ? "Edit Zone" : "Create New Zone"}</h2>
            <form onSubmit={handleCreateOrUpdate} className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="label">Zone Name</label>
                <input
                  className="input"
                  placeholder="e.g. East Godavari Zone A"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="label">Parent Branch</label>
                <select
                  className="input"
                  value={form.branch_id}
                  onChange={(e) => setForm({ ...form, branch_id: e.target.value })}
                  required
                >
                  <option value="">Select Branch...</option>
                  {branches.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Responsible Employee / Admin</label>
                <select
                  className="input"
                  value={form.responsible_employee_id}
                  onChange={(e) => setForm({ ...form, responsible_employee_id: e.target.value })}
                >
                  <option value="">Select Responsible Staff...</option>
                  {users.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name} ({u.role})
                    </option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-3 flex gap-3 mt-2">
                <button type="submit" className="btn-primary">
                  {editZone ? "Save Changes" : "Create Zone"}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => {
                    setShowForm(false);
                    setEditZone(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="relative">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8fac9a]" />
          <input
            className="input pl-10"
            placeholder="Search zones..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="text-center text-[#8fac9a] py-8">Loading zones...</div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((z) => {
              const branch = branches.find((b) => b.id === z.branch_id);
              const respUser = users.find((u) => u.id === z.responsible_employee_id);
              return (
                <div key={z.id} className="card relative group flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2 text-accent font-semibold">
                        <Layers size={18} />
                        <span>{z.name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => startEdit(z)}
                          className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-accent transition-colors"
                          title="Edit Zone"
                        >
                          <Edit2 size={14} />
                        </button>
                        <button
                          onClick={() => handleDelete(z.id)}
                          className="p-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                          title="Delete Zone"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                    <p className="text-xs text-[#8fac9a]">
                      Branch: <span className="text-[#f0ede4] font-medium">{branch ? branch.name : z.branch_id}</span>
                    </p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs">
                    <span className="text-[#8fac9a]">Responsible Staff:</span>
                    {respUser ? (
                      <span className="inline-flex items-center gap-1 font-medium text-emerald-400">
                        <UserCheck size={12} />
                        {respUser.name}
                      </span>
                    ) : (
                      <span className="text-[#8fac9a]">Unassigned</span>
                    )}
                  </div>
                </div>
              );
            })}
            {filtered.length === 0 && (
              <div className="col-span-full text-center text-[#8fac9a] py-8 card">
                No zones found
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
