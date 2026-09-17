import { useEffect, useState } from "react";
import PortalPage from "../../components/PortalPage";
import { FARM_EMP_NAV } from "./_nav";
import StatCard from "../../components/StatCard";
import { Map, Camera, Package, Eye } from "lucide-react";
import { visitsAPI, workOrdersAPI } from "../../config/api";

export default function FarmEmpDashboard() {
  const [visitCount, setVisitCount] = useState(0);
  const [workCount, setWorkCount] = useState(0);

  useEffect(() => {
    visitsAPI.list().then((r) => { if (r.success) setVisitCount(r.data.total); });
    workOrdersAPI.list().then((r) => { if (r.success) setWorkCount(r.data.total); });
  }, []);

  return (
    <PortalPage title="My Dashboard" subtitle="Your daily farm visits and tasks" navItems={FARM_EMP_NAV}>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="My Visits" value={visitCount} icon={Map} color="green" />
        <StatCard title="Work Orders" value={workCount} icon={Eye} />
        <StatCard title="Proof Pending" value="—" icon={Camera} color="accent" />
        <StatCard title="Harvests" value="—" icon={Package} />
      </div>
      <div className="card">
        <h2 className="section-title">Today's Schedule</h2>
        <p className="text-[#8fac9a] text-sm">Auto-generated visits based on your crop cycle schedule appear here. Complete visits and submit GPS-tagged proof photos.</p>
      </div>
    </PortalPage>
  );
}
