import { useEffect, useState } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import StatCard from "../../components/StatCard";
import { Leaf, FileText, Wrench, TrendingUp } from "lucide-react";
import { farmsAPI, agreementsAPI, investmentsAPI, workOrdersAPI } from "../../config/api";

export default function CustomerDashboard() {
  const [farms, setFarms] = useState([]);
  const [agrCount, setAgrCount] = useState(0);
  const [invCount, setInvCount] = useState(0);
  const [woCount, setWoCount] = useState(0);

  useEffect(() => {
    farmsAPI.list().then((r) => { if (r.success) setFarms(r.data.items); });
    agreementsAPI.list().then((r) => { if (r.success) setAgrCount(r.data.total); });
    investmentsAPI.list().then((r) => { if (r.success) setInvCount(r.data.total); });
    workOrdersAPI.list().then((r) => { if (r.success) setWoCount(r.data.total); });
  }, []);

  return (
    <PortalPage title="My Overview" subtitle="Your farms, agreements, and investments at a glance" navItems={CUSTOMER_NAV}>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="My Farms" value={farms.length} icon={Leaf} color="green" />
        <StatCard title="Agreements" value={agrCount} icon={FileText} color="accent" />
        <StatCard title="Work Orders" value={woCount} icon={Wrench} />
        <StatCard title="Investments" value={invCount} icon={TrendingUp} color="green" />
      </div>

      {farms.length > 0 && (
        <div className="card">
          <h2 className="section-title">Your Farms</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {farms.map((f) => (
              <div key={f.id} className="bg-white/5 rounded-xl p-4">
                <p className="font-semibold text-[#f0ede4]">{f.location || `Farm #${f.id?.slice(0, 8)}`}</p>
                <p className="text-sm text-[#8fac9a]">{f.area} acres · {f.current_crop || "Not planted"}</p>
                <div className="mt-2 flex gap-2">
                  <span className="badge-success">{f.soil_type || "Loam"}</span>
                  {f.irrigation_type && <span className="badge-info">{f.irrigation_type}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </PortalPage>
  );
}
