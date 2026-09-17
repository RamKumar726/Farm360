import PortalPage from "../../components/PortalPage";
import { AGRI_NAV } from "./_nav";

export default function AgriQuotes() {
  return (
    <PortalPage title="Cost Quotes" subtitle="Generate and submit quotes for customer approval" navItems={AGRI_NAV}>
      <div className="card">
        <h2 className="section-title">Submit a Quote</h2>
        <p className="text-[#8fac9a] text-sm mb-4">Quotes are generated from prescriptions. Customer reviews and approves — approved quotes trigger work order creation.</p>
        <div className="grid md:grid-cols-2 gap-4">
          <div><label className="label">Prescription ID</label><input className="input" placeholder="UUID" /></div>
          <div><label className="label">Quoted Amount (₹)</label><input className="input" type="number" placeholder="50000" /></div>
          <div className="md:col-span-2"><label className="label">Breakdown</label><textarea className="input min-h-[80px]" placeholder="Labor: ₹20,000, Materials: ₹30,000..." /></div>
        </div>
        <button className="btn-primary mt-4">Send Quote to Customer</button>
      </div>
    </PortalPage>
  );
}
