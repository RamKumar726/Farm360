import PortalPage from "../../components/PortalPage";
import { FARM_EMP_NAV } from "./_nav";

export default function FarmEmpHarvest() {
  return (
    <PortalPage title="Harvest Reporting" subtitle="Log harvest quantities and quality" navItems={FARM_EMP_NAV}>
      <div className="card max-w-xl">
        <h2 className="section-title">Log Harvest</h2>
        <div className="space-y-4">
          <div><label className="label">Farm ID</label><input className="input" placeholder="Farm UUID" /></div>
          <div><label className="label">Crop Name</label><input className="input" placeholder="e.g., Tomato" /></div>
          <div><label className="label">Quantity (kg)</label><input className="input" type="number" placeholder="500" /></div>
          <div><label className="label">Quality (1-10)</label><input className="input" type="number" min="1" max="10" placeholder="8" /></div>
          <div><label className="label">Notes</label><textarea className="input min-h-[80px]" placeholder="Harvest observations..." /></div>
          <button className="btn-primary w-full">📦 Log Harvest</button>
        </div>
      </div>
    </PortalPage>
  );
}
