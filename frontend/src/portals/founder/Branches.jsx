import { useState, useEffect } from "react";
import { Plus, Search, Edit2, Trash2, Shield, MapPin } from "lucide-react";
import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { branchesAPI, usersAPI } from "../../config/api";
import toast from "react-hot-toast";

export default function FounderBranches() {
  const [branches, setBranches] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editBranch, setEditBranch] = useState(null);
  const [form, setForm] = useState({ name: "", location: "", admin_user_id: "" });

  const loadData = async () => {
    try {
      const [resB, resU] = await Promise.all([branchesAPI.list(), usersAPI.list({ page_size: 100 })]);
      if (resB.success) setBranches(resB.data.items);
      if (resU.success) setUsers(resU.data.items);
    } catch {
      toast.error("Failed to load branches data");
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
      if (editBranch) {
        const res = await branchesAPI.update(editBranch.id, form);
        if (res.success) {
          setBranches((prev) => prev.map((b) => (b.id === editBranch.id ? res.data : b)));
          toast.success("Branch updated successfully");
          setEditBranch(null);
          setShowForm(false);
        }
      } else {
        const res = await branchesAPI.create(form);
        if (res.success) {
          setBranches((prev) => [...prev, res.data]);
          toast.success("Branch created successfully");
          setShowForm(false);
        }
      }
      setForm({ name: "", location: "", admin_user_id: "" });
    } catch (err) {
      toast.error(err?.detail || "Action failed");
    }
  };

  const startEdit = (b) => {
    setEditBranch(b);
    setForm({ name: b.name, location: b.location || "", admin_user_id: b.admin_user_id || "" });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this branch?")) return;
    try {
      const res = await branchesAPI.delete(id);
      if (res.success) {
        setBranches((prev) => prev.filter((b) => b.id !== id));
        toast.success("Branch deleted");
      }
    } catch {
      toast.error("Failed to delete branch");
    }
  };

  const filtered = branches.filter(
    (b) =>
      b.name.toLowerCase().includes(search.toLowerCase()) ||
      (b.location && b.location.toLowerCase().includes(search.toLowerCase()))
  );

  const zoneAdmins = users.filter((u) => u.role === "zone_admin" || u.role === "founder");

  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-header">Branch Governance</h1>
            <p className="text-[#8fac9a] text-xs mt-1">Manage physical enterprise branches, locations, and assigned admins.</p>
          </div>
          <button
            className="btn-primary flex items-center gap-2"
            onClick={() => {
              setEditBranch(null);
              setForm({ name: "", location: "", admin_user_id: "" });
              setShowForm(!showForm);
            }}
          >
            <Plus size={16} /> {showForm ? "Close Form" : "Add Branch"}
          </button>
        </div>

        {showForm && (
          <div className="card animate-slide-up border border-accent/40 shadow-glow">
            <h2 className="section-title text-lg mb-4">{editBranch ? "Edit Branch" : "Create New Branch"}</h2>
            <form onSubmit={handleCreateOrUpdate} className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="label">Branch Name</label>
                <input
                  className="input"
                  placeholder="e.g. Rajahmundry Main Branch"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="label">Location / Address</label>
                <input
                  className="input"
                  placeholder="e.g. NH-16, East Godavari, AP"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Assign Branch Admin (Zone Admin)</label>
                <select
                  className="input"
                  value={form.admin_user_id}
                  onChange={(e) => setForm({ ...form, admin_user_id: e.target.value })}
                >
                  <option value="">Select Admin User...</option>
                  {zoneAdmins.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name} ({u.email})
                    </option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-3 flex gap-3 mt-2">
                <button type="submit" className="btn-primary">
                  {editBranch ? "Save Changes" : "Create Branch"}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => {
                    setShowForm(false);
                    setEditBranch(null);
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
            placeholder="Search branches by name or location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="text-center text-[#8fac9a] py-8">Loading branches...</div>
        ) : (
          <div className="card overflow-hidden p-0">
            <table className="w-full">
              <thead className="border-b border-white/8 bg-white/3">
                <tr>
                  <th className="table-header">Branch Name</th>
                  <th className="table-header">Location</th>
                  <th className="table-header">Assigned Admin</th>
                  <th className="table-header">Created Date</th>
                  <th className="table-header text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((b) => {
                  const adminUser = users.find((u) => u.id === b.admin_user_id);
                  return (
                    <tr key={b.id} className="table-row">
                      <td className="table-cell font-semibold text-[#f0ede4]">
                        <div className="flex items-center gap-2">
                          <MapPin size={16} className="text-accent" />
                          <span>{b.name}</span>
                        </div>
                      </td>
                      <td className="table-cell text-[#8fac9a]">{b.location || "—"}</td>
                      <td className="table-cell">
                        {adminUser ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                            <Shield size={12} />
                            {adminUser.name}
                          </span>
                        ) : (
                          <span className="text-xs text-[#8fac9a]">Unassigned</span>
                        )}
                      </td>
                      <td className="table-cell text-[#8fac9a] text-xs">
                        {new Date(b.created_at).toLocaleDateString()}
                      </td>
                      <td className="table-cell text-right space-x-2">
                        <button
                          onClick={() => startEdit(b)}
                          className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-accent transition-colors"
                          title="Edit Branch"
                        >
                          <Edit2 size={15} />
                        </button>
                        <button
                          onClick={() => handleDelete(b.id)}
                          className="p-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                          title="Delete Branch"
                        >
                          <Trash2 size={15} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={5} className="table-cell text-center text-[#8fac9a]">
                      No branches found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
