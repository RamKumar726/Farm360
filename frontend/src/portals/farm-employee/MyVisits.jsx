import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { FARM_EMP_NAV } from "./_nav";
import VisitCard from "../../components/VisitCard";
import { visitsAPI } from "../../config/api";

export default function FarmEmpMyVisits() {
  const [visits, setVisits] = useState([]);
  useEffect(() => { visitsAPI.list().then((r) => { if (r.success) setVisits(r.data.items); }); }, []);
  return (
    <PortalPage title="My Visits" subtitle="All visits assigned to you" navItems={FARM_EMP_NAV}>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visits.map((v) => <VisitCard key={v.id} visit={v} />)}
        {visits.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No visits assigned</p>}
      </div>
    </PortalPage>
  );
}
