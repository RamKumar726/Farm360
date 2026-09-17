import PortalPage from "../../components/PortalPage";
import { FARM_EMP_NAV } from "./_nav";

export default function FarmEmpIncidentReport() {
  return (
    <PortalPage title="Incident Report" subtitle="Report theft, damage, or crop failures immediately" navItems={FARM_EMP_NAV}>
      <div className="card max-w-xl border-red-500/20">
        <h2 className="section-title text-red-400">🚨 Report Incident</h2>
        <div className="space-y-4">
          <div><label className="label">Farm ID</label><input className="input" placeholder="Farm UUID" /></div>
          <div>
            <label className="label">Incident Type</label>
            <select className="input">
              <option>Theft</option>
              <option>Crop Damage (Natural)</option>
              <option>Crop Failure</option>
              <option>Equipment Damage</option>
              <option>Trespassing</option>
              <option>Other</option>
            </select>
          </div>
          <div><label className="label">Description</label><textarea className="input min-h-[100px]" placeholder="Describe the incident in detail..." /></div>
          <div><label className="label">Estimated Loss (₹)</label><input className="input" type="number" placeholder="0" /></div>
          <button className="btn-primary w-full bg-red-500 hover:bg-red-600">🚨 Submit Report</button>
        </div>
      </div>
    </PortalPage>
  );
}
