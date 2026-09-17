import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import { AlertOctagon } from "lucide-react";

export default function ZoneAdminEscalations() {
  return (
    <PortalPage title="Escalations" navItems={ZONE_ADMIN_NAV}>
      <div className="card border-red-500/20">
        <div className="flex items-center gap-3 mb-4">
          <AlertOctagon className="text-red-400" size={24} />
          <h2 className="section-title mb-0">Escalate to Founder</h2>
        </div>
        <p className="text-[#8fac9a] text-sm mb-4">Use this to escalate critical issues, fraud alerts, or unresolved incidents to the Founder/Business Owner.</p>
        <textarea className="input min-h-[100px]" placeholder="Describe the issue to escalate..." />
        <button className="btn-primary mt-3">🚨 Escalate to Founder</button>
      </div>
    </PortalPage>
  );
}
