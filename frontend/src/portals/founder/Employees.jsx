import { useState, useEffect } from "react";
import { Plus, Search, Edit2, Trash2, UserCheck, Shield } from "lucide-react";
import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { usersAPI, branchesAPI, zonesAPI } from "../../config/api";
import toast from "react-hot-toast";

export default function FounderEmployees() {
  const [users, setUsers] = useState([]);
  const [branches, setBranches] = useState([]);
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState("");
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editUser, setEditUser] = useState(null);

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    phone: "",
    role: "employee",
    branch_id: "",
    zone_id: "",
    is_available: true,
  });

  const loadData = async () => {
    try {
      const [resU, resB, resZ] = await Promise.all([
        usersAPI.list({ page_size: 100 }),
        branchesAPI.list({ page_size: 100 }),
        zonesAPI.list({ page_size: 100 }),
      ]);
      if (resU.success) setUsers(resU.data.items);
      if (resB.success) setBranches(resB.data.items);
      if (resZ.success) setZones(resZ.data.items);
    } catch {
      toast.error("Failed to load user management data");
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
      if (editUser) {
        const updatePayload = {
          name: form.name,
          phone: form.phone,
          role: form.role,
          branch_id: form.branch_id || null,
          zone_id: form.zone_id || null,
          is_available: form.is_available,
        };
        const res = await usersAPI.update(editUser.id, updatePayload);
        if (res.success) {
          setUsers((prev) => prev.map((u) => (u.id === editUser.id ? res.data : u)));
          toast.success("User updated successfully");
          setEditUser(null);
          setShowForm(false);
        }
      } else {
        const res = await usersAPI.create(form);
        if (res.success) {
          setUsers((prev) => [res.data, ...prev]);
          toast.success("User created successfully");
          setShowForm(false);
        }
      }
      setForm({
        name: "",
        email: "",
        password: "",
        phone: "",
        role: "employee",
        branch_id: "",
        zone_id: "",
        is_available: true,
      });
    } catch (err) {
      toast.error(err?.detail || "Action failed");
    }
  };

  const startEdit = (u) => {
    setEditUser(u);
    setForm({
      name: u.name,
      email: u.email,
      password: "",
      phone: u.phone || "",
      role: u.role,
      branch_id: u.branch_id || "",
      zone_id: u.zone_id || "",
      is_available: u.is_available ?? true,
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      const res = await usersAPI.delete(id);
      if (res.success) {
        setUsers((prev) => prev.filter((u) => u.id !== id));
        toast.success("User deleted");
      }
    } catch {
      toast.error("Failed to delete user");
    }
  };

  const roles = [
    { key: "", label: "All Roles" },
    { key: "founder", label: "Founder" },
    { key: "zone_admin", label: "Zone Admin" },
    { key: "employee", label: "Office Employee" },
    { key: "agri_officer", label: "Agri Officer" },
    { key: "farm_employee", label: "Farm Worker" },
    { key: "work_partner", label: "Outsourcing Provider" },
    { key: "customer", label: "Customer" },
  ];

  const filtered = users.filter((u) => {
    const matchesRole = !roleFilter || u.role === roleFilter;
    const matchesSearch =
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      (u.phone && u.phone.includes(search));
    return matchesRole && matchesSearch;
  });

  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-header">User & Employee Governance</h1>
            <p className="text-[#8fac9a] text-xs mt-1">Full enterprise control: Assign roles, manage branches, and configure zones.</p>
          </div>
          <button
            className="btn-primary flex items-center gap-2"
            onClick={() => {
              setEditUser(null);
              setForm({
                name: "",
                email: "",
                password: "",
                phone: "",
                role: "employee",
                branch_id: "",
                zone_id: "",
                is_available: true,
              });
              setShowForm(!showForm);
            }}
          >
            <Plus size={16} /> {showForm ? "Close Form" : "Create User"}
          </button>
        </div>

        {showForm && (
          <div className="card animate-slide-up border border-accent/40 shadow-glow">
            <h2 className="section-title text-lg mb-4">{editUser ? `Edit User (${editUser.email})` : "Create New User"}</h2>
            <form onSubmit={handleCreateOrUpdate} className="grid md:grid-cols-3 gap-4">
              <div>
                <label className="label">Full Name</label>
                <input
                  className="input"
                  placeholder="e.g. Rajesh Kumar"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </div>
              {!editUser && (
                <>
                  <div>
                    <label className="label">Email Address</label>
                    <input
                      className="input"
                      type="email"
                      placeholder="user@prasadfarm.com"
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="label">Password</label>
                    <input
                      className="input"
                      type="password"
                      placeholder="••••••••"
                      value={form.password}
                      onChange={(e) => setForm({ ...form, password: e.target.value })}
                      required
                    />
                  </div>
                </>
              )}
              <div>
                <label className="label">Phone Number</label>
                <input
                  className="input"
                  placeholder="+91 98765 43210"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Role Permission</label>
                <select
                  className="input"
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                  required
                >
                  <option value="founder">Founder (CEO)</option>
                  <option value="zone_admin">Zone Admin (Branch Mgr)</option>
                  <option value="employee">Office Employee (CRM)</option>
                  <option value="agri_officer">Agri Officer (Agronomist)</option>
                  <option value="farm_employee">Farm Worker (Field Agent)</option>
                  <option value="work_partner">Outsourcing Provider</option>
                  <option value="customer">Customer (Farm Owner)</option>
                </select>
              </div>
              <div>
                <label className="label">Assigned Branch</label>
                <select
                  className="input"
                  value={form.branch_id}
                  onChange={(e) => setForm({ ...form, branch_id: e.target.value })}
                >
                  <option value="">No Branch Assigned</option>
                  {branches.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Assigned Zone</label>
                <select
                  className="input"
                  value={form.zone_id}
                  onChange={(e) => setForm({ ...form, zone_id: e.target.value })}
                >
                  <option value="">No Zone Assigned</option>
                  {zones.map((z) => (
                    <option key={z.id} value={z.id}>
                      {z.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-3 flex gap-3 mt-2">
                <button type="submit" className="btn-primary">
                  {editUser ? "Save User Changes" : "Create User"}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => {
                    setShowForm(false);
                    setEditUser(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="flex flex-col md:flex-row gap-4 justify-between items-center">
          <div className="flex gap-2 flex-wrap">
            {roles.map((r) => (
              <button
                key={r.key}
                onClick={() => setRoleFilter(r.key)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  roleFilter === r.key
                    ? "bg-accent text-primary-900 shadow-glow"
                    : "bg-white/5 text-[#8fac9a] hover:bg-white/10"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>

          <div className="relative w-full md:w-64">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8fac9a]" />
            <input
              className="input pl-9 text-xs"
              placeholder="Search user name or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="text-center text-[#8fac9a] py-8">Loading users...</div>
        ) : (
          <div className="card overflow-hidden p-0">
            <table className="w-full">
              <thead className="border-b border-white/8 bg-white/3">
                <tr>
                  <th className="table-header">User Name</th>
                  <th className="table-header">Role</th>
                  <th className="table-header">Email & Phone</th>
                  <th className="table-header">Branch / Zone</th>
                  <th className="table-header">Status</th>
                  <th className="table-header text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((u) => {
                  const branch = branches.find((b) => b.id === u.branch_id);
                  const zone = zones.find((z) => z.id === u.zone_id);
                  return (
                    <tr key={u.id} className="table-row">
                      <td className="table-cell font-semibold text-[#f0ede4]">
                        <div className="flex items-center gap-2">
                          <UserCheck size={16} className="text-accent" />
                          <span>{u.name}</span>
                        </div>
                      </td>
                      <td className="table-cell">
                        <span className="badge-accent uppercase text-[10px] tracking-wider font-bold">
                          {u.role.replace("_", " ")}
                        </span>
                      </td>
                      <td className="table-cell text-[#8fac9a] text-xs">
                        <p className="text-[#f0ede4]">{u.email}</p>
                        <p>{u.phone || "No phone"}</p>
                      </td>
                      <td className="table-cell text-[#8fac9a] text-xs">
                        <p className="text-[#f0ede4] font-medium">{branch ? branch.name : "Global / None"}</p>
                        {zone && <p className="text-accent">{zone.name}</p>}
                      </td>
                      <td className="table-cell">
                        {u.is_available ? (
                          <span className="badge-success">Active</span>
                        ) : (
                          <span className="badge-error">Offline</span>
                        )}
                      </td>
                      <td className="table-cell text-right space-x-2">
                        <button
                          onClick={() => startEdit(u)}
                          className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-accent transition-colors"
                          title="Edit User"
                        >
                          <Edit2 size={15} />
                        </button>
                        <button
                          onClick={() => handleDelete(u.id)}
                          className="p-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                          title="Delete User"
                        >
                          <Trash2 size={15} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={6} className="table-cell text-center text-[#8fac9a]">
                      No users found
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
