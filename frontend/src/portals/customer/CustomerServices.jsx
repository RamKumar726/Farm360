import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { MessageSquare, Phone } from "lucide-react";

export default function CustomerServices() {
  return (
    <PortalPage title="Customer Services" subtitle="Get help and raise service requests" navItems={CUSTOMER_NAV}>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="section-title">Raise a Request</h2>
          <div className="space-y-4">
            <div>
              <label className="label">Service Type</label>
              <select className="input">
                <option>Farm Visit Request</option>
                <option>Prescription Update</option>
                <option>Work Order Issue</option>
                <option>Payment Dispute</option>
                <option>Agreement Query</option>
                <option>Other</option>
              </select>
            </div>
            <div><label className="label">Description</label><textarea className="input min-h-[100px]" placeholder="Describe your request..." /></div>
            <button className="btn-primary w-full">Submit Request</button>
          </div>
        </div>
        <div className="space-y-4">
          <div className="card">
            <h2 className="section-title">Contact Support</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3"><Phone size={18} className="text-accent" /><div><p className="text-sm font-medium text-[#f0ede4]">Customer Care</p><p className="text-[#8fac9a] text-sm">+91 98765 43210</p></div></div>
              <div className="flex items-center gap-3"><MessageSquare size={18} className="text-green-400" /><div><p className="text-sm font-medium text-[#f0ede4]">WhatsApp</p><p className="text-[#8fac9a] text-sm">Chat with us on WhatsApp</p></div></div>
            </div>
          </div>
          <div className="card">
            <h2 className="section-title">FAQ</h2>
            <div className="space-y-2 text-sm text-[#8fac9a]">
              {["How do I view my crop health?", "When will the work order be completed?", "How are investment returns calculated?", "Can I list my land for sale?"].map((q) => (
                <p key={q} className="cursor-pointer hover:text-[#f0ede4] transition-colors">→ {q}</p>
              ))}
            </div>
          </div>
        </div>
      </div>
    </PortalPage>
  );
}
