import PortalPage from "../../components/PortalPage";
import { AGRI_NAV } from "./_nav";
import { farmsAPI } from "../../config/api";
import { useState, useEffect } from "react";

export default function AgriAssignments() {
  const [farms, setFarms] = useState([]);
  useEffect(() => { farmsAPI.list().then((r) => { if (r.success) setFarms(r.data.items); }); }, []);
  return (
    <PortalPage title="Farm Assignments" subtitle="Farms assigned for inspection and care" navItems={AGRI_NAV}>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {farms.map((f) => (
          <div key={f.id} className="card">
            <p className="font-semibold text-[#f0ede4]">Farm #{f.id?.slice(0, 8)}</p>
            <p className="text-sm text-[#8fac9a]">{f.location || "Location not set"}</p>
            {f.area && <p className="text-sm text-accent">{f.area} acres</p>}
            <p className="text-xs text-[#8fac9a] mt-2">Crop: {f.current_crop || "Not planted"}</p>
          </div>
        ))}
        {farms.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No farms assigned</p>}
      </div>
    </PortalPage>
  );
}
