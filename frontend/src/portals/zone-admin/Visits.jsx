import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import { visitsAPI } from "../../config/api";
import VisitCard from "../../components/VisitCard";

export default function ZoneAdminVisits() {
  const [visits, setVisits] = useState([]);
  useEffect(() => { visitsAPI.list().then((r) => { if (r.success) setVisits(r.data.items); }); }, []);
  return (
    <PortalPage title="Visits" subtitle="All farm and site visits in your branch" navItems={ZONE_ADMIN_NAV}>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visits.map((v) => <VisitCard key={v.id} visit={v} />)}
        {visits.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No visits found</p>}
      </div>
    </PortalPage>
  );
}
