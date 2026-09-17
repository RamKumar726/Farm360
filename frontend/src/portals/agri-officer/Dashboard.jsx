import { useEffect, useState } from "react";
import PortalPage from "../../components/PortalPage";
import { AGRI_NAV } from "./_nav";
import StatCard from "../../components/StatCard";
import { Leaf, FileText, Map, ClipboardList } from "lucide-react";
import { cropDesignsAPI, prescriptionsAPI, visitsAPI } from "../../config/api";

export default function AgriDashboard() {
  const [cdCount, setCdCount] = useState(0);
  const [rxCount, setRxCount] = useState(0);
  const [visitCount, setVisitCount] = useState(0);

  useEffect(() => {
    cropDesignsAPI.list().then((r) => { if (r.success) setCdCount(r.data.total); });
    prescriptionsAPI.list().then((r) => { if (r.success) setRxCount(r.data.total); });
    visitsAPI.list().then((r) => { if (r.success) setVisitCount(r.data.total); });
  }, []);

  return (
    <PortalPage title="Agri Officer Dashboard" subtitle="Manage crop designs, prescriptions, and farm visits" navItems={AGRI_NAV}>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Crop Designs" value={cdCount} icon={Leaf} color="green" />
        <StatCard title="Prescriptions" value={rxCount} icon={FileText} color="accent" />
        <StatCard title="Farm Visits" value={visitCount} icon={Map} />
        <StatCard title="Assignments" value="—" icon={ClipboardList} />
      </div>
      <div className="card">
        <h2 className="section-title">Your Role</h2>
        <p className="text-[#8fac9a] text-sm">As Agri Officer, you visit farms, assess soil and crop health, create prescriptions, design crop plans, and generate quotes for customers.</p>
      </div>
    </PortalPage>
  );
}
