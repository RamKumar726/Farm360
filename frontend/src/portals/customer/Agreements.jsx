import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { agreementsAPI } from "../../config/api";
import StatusBadge from "../../components/StatusBadge";
import { FileText } from "lucide-react";

export default function CustomerAgreements() {
  const [agreements, setAgreements] = useState([]);
  useEffect(() => { agreementsAPI.list().then((r) => { if (r.success) setAgreements(r.data.items); }); }, []);
  return (
    <PortalPage title="My Agreements" subtitle="All signed agreements and terms" navItems={CUSTOMER_NAV}>
      <div className="space-y-4">
        {agreements.map((a) => (
          <div key={a.id} className="card flex items-start gap-4">
            <FileText className="text-accent shrink-0 mt-1" size={24} />
            <div className="flex-1">
              <div className="flex justify-between items-start"><p className="font-semibold text-[#f0ede4] capitalize">{a.type?.replace("_", " ")}</p><StatusBadge status={a.status} /></div>
              <div className="grid grid-cols-2 gap-2 mt-2 text-sm text-[#8fac9a]">
                {a.start_date && <span>Start: {a.start_date}</span>}
                {a.end_date && <span>End: {a.end_date}</span>}
                {a.amount && <span className="text-accent font-semibold">₹{Number(a.amount).toLocaleString()}</span>}
              </div>
            </div>
            {a.document_url && <a href={a.document_url} target="_blank" rel="noreferrer" className="btn-secondary text-sm">View PDF</a>}
          </div>
        ))}
        {agreements.length === 0 && <div className="card text-center text-[#8fac9a] py-10"><FileText size={40} className="mx-auto mb-2 opacity-30" /><p>No agreements yet</p></div>}
      </div>
    </PortalPage>
  );
}
