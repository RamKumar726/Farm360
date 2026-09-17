import { useEffect, useState } from "react";
import PortalPage from "../../components/PortalPage";
import { EMPLOYEE_NAV } from "./_nav";
import StatCard from "../../components/StatCard";
import { Target, ClipboardList, Handshake, TrendingUp } from "lucide-react";
import { leadsAPI, workOrdersAPI } from "../../config/api";

export default function EmployeeDashboard() {
  const [leadCount, setLeadCount] = useState(0);
  const [workCount, setWorkCount] = useState(0);

  useEffect(() => {
    leadsAPI.list().then((r) => { if (r.success) setLeadCount(r.data.total); });
    workOrdersAPI.list().then((r) => { if (r.success) setWorkCount(r.data.total); });
  }, []);

  return (
    <PortalPage title="My Dashboard" subtitle="Your daily work queue and pipeline" navItems={EMPLOYEE_NAV}>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="My Leads" value={leadCount} icon={Target} />
        <StatCard title="Work Orders" value={workCount} icon={ClipboardList} />
        <StatCard title="Land Leads" value="—" icon={Handshake} />
        <StatCard title="Investments" value="—" icon={TrendingUp} />
      </div>
      <div className="card">
        <h2 className="section-title">Today's Priority Tasks</h2>
        <div className="space-y-2">
          {["Follow up with site visit leads", "Assign outsourcing partners for pending work orders", "Check land sale broadcast responses", "Update investment lead statuses"].map((t) => (
            <div key={t} className="flex items-center gap-3 p-3 bg-white/5 rounded-xl">
              <span className="w-2 h-2 rounded-full bg-accent" />
              <span className="text-sm text-[#8fac9a]">{t}</span>
            </div>
          ))}
        </div>
      </div>
    </PortalPage>
  );
}
