import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { EMPLOYEE_NAV } from "./_nav";
import { landSalesAPI } from "../../config/api";
import StatusBadge from "../../components/StatusBadge";
import toast from "react-hot-toast";

export default function EmployeeLandLeads() {
  const [listings, setListings] = useState([]);
  useEffect(() => { landSalesAPI.list().then((r) => { if (r.success) setListings(r.data.items); }); }, []);
  const broadcast = async (id) => { await landSalesAPI.broadcast(id); toast.success("Broadcast sent to brokers and customers!"); };
  return (
    <PortalPage title="Land Leads" subtitle="Manage land sale listings and broadcast to network" navItems={EMPLOYEE_NAV}>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {listings.map((l) => (
          <div key={l.id} className="card">
            <div className="flex justify-between items-start mb-2"><p className="font-semibold text-[#f0ede4]">{l.land_type}</p><StatusBadge status={l.status} /></div>
            <p className="text-sm text-[#8fac9a]">{l.location || "Location not specified"}</p>
            {l.area && <p className="text-sm text-[#8fac9a]">Area: {l.area} acres</p>}
            {l.listed_price && <p className="text-accent font-semibold">₹{Number(l.listed_price).toLocaleString()}</p>}
            {l.status === "listed" && (
              <button onClick={() => broadcast(l.id)} className="btn-primary w-full mt-3 text-sm">📢 Broadcast to Brokers</button>
            )}
          </div>
        ))}
        {listings.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No land listings</p>}
      </div>
    </PortalPage>
  );
}
