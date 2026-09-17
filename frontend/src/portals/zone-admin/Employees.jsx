import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import { usersAPI } from "../../config/api";

export default function ZoneAdminEmployees() {
  const [users, setUsers] = useState([]);
  useEffect(() => { usersAPI.list().then((r) => { if (r.success) setUsers(r.data.items); }); }, []);
  return (
    <PortalPage title="Branch Employees" navItems={ZONE_ADMIN_NAV}>
      <div className="card overflow-hidden p-0">
        <table className="w-full">
          <thead className="border-b border-white/8 bg-white/3"><tr><th className="table-header">Name</th><th className="table-header">Role</th><th className="table-header">Zone</th><th className="table-header">Available</th></tr></thead>
          <tbody>{users.map((u) => (<tr key={u.id} className="table-row"><td className="table-cell font-medium">{u.name}</td><td className="table-cell"><span className="badge-accent">{u.role}</span></td><td className="table-cell text-[#8fac9a] text-xs">{u.zone_id?.slice(0, 8) || "—"}</td><td className="table-cell">{u.is_available ? <span className="badge-success">Yes</span> : <span className="badge-error">No</span>}</td></tr>))}</tbody>
        </table>
      </div>
    </PortalPage>
  );
}
