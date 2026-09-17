import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { AlertTriangle, Shield } from "lucide-react";

export default function FounderRiskFraud() {
  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-6">
        <h1 className="page-header">Risk & Fraud Visibility</h1>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="card border-red-500/20">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="text-red-400" size={24} />
              <h2 className="section-title mb-0">Failed Visits</h2>
            </div>
            <p className="text-[#8fac9a] text-sm">Farm employees with repeated failed visits are flagged here for review. Connect to /visits/failed endpoint to see live data.</p>
          </div>
          <div className="card border-yellow-500/20">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="text-yellow-400" size={24} />
              <h2 className="section-title mb-0">Rejected Quotes</h2>
            </div>
            <p className="text-[#8fac9a] text-sm">Prescriptions and quotes rejected by customers are tracked here. Review patterns for pricing issues.</p>
          </div>
        </div>
        <div className="card">
          <h2 className="section-title">Audit Log</h2>
          <p className="text-[#8fac9a] text-sm">Random visits, audit trail, and critical alerts appear here. Founder can trigger random visits from the system.</p>
          <div className="mt-4 p-4 bg-white/3 rounded-xl text-center text-[#8fac9a] text-sm">
            🔒 All actions are logged with user ID, timestamp, and GPS coordinates.
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
