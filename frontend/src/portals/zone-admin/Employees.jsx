import { useEffect, useState } from "react";
import { Edit2, Plus, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import { usersAPI, zonesAPI } from "../../config/api";
import useAppStore from "../../store/useAppStore";

const EMPTY_FORM = {
  name: "", email: "", password: "", phone: "", role: "employee", zone_id: "", is_available: true,
};

export default function ZoneAdminEmployees() {
  const currentUser = useAppStore((state) => state.user);
  const [users, setUsers] = useState([]);
  const [zones, setZones] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const loadData = async () => {
    try {
      const [userResult, zoneResult] = await Promise.all([
        usersAPI.list({ page_size: 100 }), zonesAPI.list({ page_size: 100 }),
      ]);
      if (userResult.success) setUsers(userResult.data.items);
      if (zoneResult.success) setZones(zoneResult.data.items);
    } catch (error) {
      toast.error(error?.detail || "Could not load branch staff");
    }
  };

  useEffect(() => { loadData(); }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setShowForm(true);
  };

  const openEdit = (staff) => {
    setEditing(staff);
    setForm({
      name: staff.name, email: staff.email, password: "", phone: staff.phone || "",
      role: staff.role, zone_id: staff.zone_id || "", is_available: staff.is_available,
    });
    setShowForm(true);
  };

  const save = async (event) => {
    event.preventDefault();
    try {
      const payload = {
        name: form.name, phone: form.phone || null, role: form.role,
        branch_id: currentUser.branch_id, zone_id: form.zone_id || null,
        is_available: form.is_available,
      };
      const result = editing
        ? await usersAPI.update(editing.id, payload)
        : await usersAPI.create({ ...payload, email: form.email, password: form.password });
      if (result.success) {
        toast.success(editing ? "Staff member updated" : "Staff member created");
        setShowForm(false);
        setEditing(null);
        setForm(EMPTY_FORM);
        await loadData();
      }
    } catch (error) {
      toast.error(error?.detail || "Could not save staff member");
    }
  };

  const remove = async (staff) => {
    if (!window.confirm(`Deactivate ${staff.name}?`)) return;
    try {
      const result = await usersAPI.delete(staff.id);
      if (result.success) {
        setUsers((items) => items.filter((item) => item.id !== staff.id));
        toast.success("Staff member deactivated");
      }
    } catch (error) {
      toast.error(error?.detail || "Could not deactivate staff member");
    }
  };

  return (
    <PortalPage title="Branch Employees" navItems={ZONE_ADMIN_NAV}>
      <div className="space-y-5">
        <div className="flex justify-end">
          <button className="btn-primary flex items-center gap-2" onClick={openCreate}>
            <Plus size={16} /> Add Branch Staff
          </button>
        </div>

        {showForm && (
          <form className="card grid gap-4 md:grid-cols-3" onSubmit={save}>
            <div><label className="label">Full name</label><input className="input" required minLength={2} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
            {!editing && <div><label className="label">Email</label><input className="input" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></div>}
            {!editing && <div><label className="label">Temporary password</label><input className="input" type="password" required minLength={12} maxLength={72} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></div>}
            <div><label className="label">Phone</label><input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></div>
            <div>
              <label className="label">Role</label>
              <select className="input" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                <option value="employee">Office Employee</option>
                <option value="agri_officer">Agriculture Officer</option>
                <option value="farm_employee">Farm Employee</option>
                <option value="work_partner">Work Partner</option>
              </select>
            </div>
            <div>
              <label className="label">Zone</label>
              <select className="input" value={form.zone_id} onChange={(e) => setForm({ ...form, zone_id: e.target.value })}>
                <option value="">No zone assigned</option>
                {zones.map((zone) => <option key={zone.id} value={zone.id}>{zone.name}</option>)}
              </select>
            </div>
            <label className="flex items-center gap-2 text-sm text-[#8fac9a]">
              <input type="checkbox" checked={form.is_available} onChange={(e) => setForm({ ...form, is_available: e.target.checked })} /> Available for assignment
            </label>
            <div className="md:col-span-3 flex gap-3">
              <button className="btn-primary" type="submit">{editing ? "Save changes" : "Create staff account"}</button>
              <button className="btn-secondary" type="button" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        )}

        <div className="card overflow-hidden p-0">
          <table className="w-full">
            <thead className="border-b border-white/8 bg-white/3"><tr><th className="table-header">Name</th><th className="table-header">Role</th><th className="table-header">Zone</th><th className="table-header">Available</th><th className="table-header text-right">Actions</th></tr></thead>
            <tbody>{users.map((staff) => (
              <tr key={staff.id} className="table-row">
                <td className="table-cell"><p className="font-medium">{staff.name}</p><p className="text-xs text-[#8fac9a]">{staff.email}</p></td>
                <td className="table-cell"><span className="badge-accent">{staff.role.replaceAll("_", " ")}</span></td>
                <td className="table-cell text-[#8fac9a] text-xs">{zones.find((zone) => zone.id === staff.zone_id)?.name || "—"}</td>
                <td className="table-cell">{staff.is_available ? <span className="badge-success">Yes</span> : <span className="badge-error">No</span>}</td>
                <td className="table-cell text-right space-x-2">
                  <button className="p-1.5 text-accent" title="Edit staff" onClick={() => openEdit(staff)}><Edit2 size={15} /></button>
                  {staff.id !== currentUser.id && <button className="p-1.5 text-red-400" title="Deactivate staff" onClick={() => remove(staff)}><Trash2 size={15} /></button>}
                </td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </div>
    </PortalPage>
  );
}
