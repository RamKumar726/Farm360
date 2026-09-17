import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { CreditCard, CheckCircle } from "lucide-react";

export default function CustomerPayments() {
  const handlePay = async () => {
    const keyId = import.meta.env.VITE_RAZORPAY_KEY_ID;
    if (!keyId) { alert("Razorpay not configured. Set VITE_RAZORPAY_KEY_ID in .env"); return; }
    // Load Razorpay script
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    document.body.appendChild(script);
    script.onload = () => {
      const options = {
        key: keyId,
        amount: 100000, // ₹1000 in paise
        currency: "INR",
        name: "Prasad Farm Care 360°",
        description: "Farm Service Payment",
        image: "",
        handler: (response) => { alert(`Payment successful! Payment ID: ${response.razorpay_payment_id}`); },
        prefill: { name: "Customer Name", email: "customer@email.com" },
        theme: { color: "#c9a84c" },
      };
      const rzp = new window.Razorpay(options);
      rzp.open();
    };
  };

  return (
    <PortalPage title="Payments" subtitle="View invoices and make payments" navItems={CUSTOMER_NAV}>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="section-title">Payment Summary</h2>
          <div className="space-y-3">
            {[
              { label: "Farm Management Fee", amount: "₹50,000", due: "Oct 2026", status: "Due" },
              { label: "Soil Testing Service", amount: "₹5,000", due: "Paid", status: "Paid" },
              { label: "Investment Commission", amount: "₹2,500", due: "Paid", status: "Paid" },
            ].map((p) => (
              <div key={p.label} className="flex items-center justify-between py-2 border-b border-white/5">
                <div>
                  <p className="text-sm font-medium text-[#f0ede4]">{p.label}</p>
                  <p className="text-xs text-[#8fac9a]">{p.due}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-semibold text-[#f0ede4]">{p.amount}</span>
                  {p.status === "Paid" ? <CheckCircle size={16} className="text-green-400" /> : <span className="badge-warning">Due</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <h2 className="section-title">Make a Payment</h2>
          <p className="text-[#8fac9a] text-sm mb-6">Securely pay for farm services via Razorpay. Supports UPI, cards, and net banking.</p>
          <div className="space-y-3">
            <div><label className="label">Amount (₹)</label><input className="input" type="number" placeholder="50000" /></div>
            <div><label className="label">Reference / Invoice</label><input className="input" placeholder="INV-2026-001" /></div>
          </div>
          <button onClick={handlePay} className="btn-primary w-full mt-4 flex items-center justify-center gap-2">
            <CreditCard size={18} /> Pay via Razorpay
          </button>
          <p className="text-xs text-center text-[#8fac9a] mt-3">256-bit SSL secured · UPI, Cards, Net Banking</p>
        </div>
      </div>
    </PortalPage>
  );
}
