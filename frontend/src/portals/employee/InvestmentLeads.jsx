import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { EMPLOYEE_NAV } from "./_nav";
import { investmentsAPI, projectsAPI } from "../../config/api";

export default function EmployeeInvestmentLeads() {
  const [projects, setProjects] = useState([]);
  useEffect(() => { projectsAPI.list({ status: "open" }).then((r) => { if (r.success) setProjects(r.data.items); }); }, []);
  return (
    <PortalPage title="Investment Leads" subtitle="Open projects for customer investment pitching" navItems={EMPLOYEE_NAV}>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map((p) => (
          <div key={p.id} className="card">
            <p className="font-semibold text-[#f0ede4]">{p.name}</p>
            <p className="text-xs text-accent mb-2">{p.type?.replace("_", " ")}</p>
            <p className="text-sm text-[#8fac9a]">Target: ₹{Number(p.total_amount).toLocaleString()}</p>
            <div className="mt-2 h-1.5 bg-white/10 rounded-full"><div className="h-full bg-accent rounded-full" style={{ width: `${p.funding_percentage || 0}%` }} /></div>
            <p className="text-right text-xs text-accent mt-1">{p.funding_percentage}% funded</p>
            <p className="text-xs text-[#8fac9a] mt-2">{p.description}</p>
          </div>
        ))}
      </div>
    </PortalPage>
  );
}
