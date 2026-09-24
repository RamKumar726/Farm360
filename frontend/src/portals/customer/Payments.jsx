import { useEffect, useState } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { leadsAPI, paymentsAPI } from "../../config/api";
import { CreditCard, CheckCircle } from "lucide-react";
import toast from "react-hot-toast";
import { openRazorpayCheckout } from "../../utils/razorpay";

const money = (amount) => `₹${Number(amount || 0).toLocaleString("en-IN")}`;

export default function CustomerPayments() {
  const [leads, setLeads] = useState([]);
  const [payments, setPayments] = useState([]);
  const [busyId, setBusyId] = useState(null);

  const refresh = async () => {
    const [leadResult, paymentResult] = await Promise.all([leadsAPI.list(), paymentsAPI.list()]);
    if (leadResult.success) setLeads(leadResult.data.items || []);
    if (paymentResult.success) setPayments(paymentResult.data || []);
  };
  useEffect(() => { refresh().catch(() => toast.error("Could not load payment details")); }, []);

  const payLead = async (lead) => {
    setBusyId(lead.id);
    try {
      const order = (await paymentsAPI.leadOrder(lead.id)).data;
      const result = await openRazorpayCheckout(order, "Farm360 service payment");
      await paymentsAPI.confirm({
        gateway_order_id: result.razorpay_order_id,
        gateway_payment_id: result.razorpay_payment_id,
        gateway_signature: result.razorpay_signature,
      });
      await refresh();
      toast.success("Payment verified successfully");
    } catch (error) {
      toast.error(error?.response?.data?.detail || error?.detail || error.message || "Payment could not be completed");
    } finally { setBusyId(null); }
  };

  const paymentByLead = Object.fromEntries(payments.filter((payment) => payment.lead_id).map((payment) => [payment.lead_id, payment]));
  const paymentLeads = leads.filter((lead) => lead.status === "payment" || paymentByLead[lead.id]);

  return (
    <PortalPage title="Payments" subtitle="Pay approved service quotations and review verified transactions" navItems={CUSTOMER_NAV}>
      <div className="grid md:grid-cols-2 gap-4">
        {paymentLeads.map((lead) => {
          const payment = paymentByLead[lead.id];
          const amount = lead.final_amount ?? lead.price_to_complete;
          const isPaid = lead.payment_confirmed_at || payment?.status === "paid";
          return <article key={lead.id} className="card">
            <div className="flex justify-between items-start gap-3"><div><h2 className="font-semibold text-[#f0ede4]">{lead.services_needed || lead.type.replaceAll("_", " ")}</h2><p className="text-xs text-[#8fac9a] mt-1">Request #{lead.id.slice(0, 8)}</p></div>{isPaid ? <CheckCircle className="text-green-400" size={18} /> : <span className="badge-warning">Payment due</span>}</div>
            <p className="text-2xl font-bold mt-5">{money(amount)}</p>
            {isPaid ? <p className="text-sm text-green-400 mt-3">Payment verified. FarmCare will continue your request.</p> : <button disabled={busyId === lead.id || !amount} className="btn-primary mt-4 flex items-center gap-2" onClick={() => payLead(lead)}><CreditCard size={17} />{busyId === lead.id ? "Opening payment…" : "Pay Now"}</button>}
          </article>;
        })}
        {paymentLeads.length === 0 && <div className="card md:col-span-2 text-center py-10"><CreditCard size={36} className="mx-auto mb-2 opacity-30" /><p className="text-[#8fac9a]">No service payments are due.</p></div>}
      </div>

      <section className="card mt-6">
        <h2 className="section-title">Payment history</h2>
        <div className="divide-y divide-white/10">
          {payments.map((payment) => <div key={payment.id} className="py-3 flex justify-between items-center gap-4 text-sm"><div><p className="text-[#f0ede4] capitalize">{payment.purpose.replaceAll("_", " ")}</p><p className="text-xs text-[#8fac9a]">{payment.paid_at ? new Date(payment.paid_at).toLocaleString() : `Order created ${new Date(payment.created_at).toLocaleDateString()}`}</p></div><div className="text-right"><p className="font-semibold">{money(payment.amount)}</p><p className={payment.status === "paid" ? "text-green-400" : "text-[#8fac9a]"}>{payment.status}</p></div></div>)}
          {payments.length === 0 && <p className="py-4 text-sm text-[#8fac9a]">No transactions yet.</p>}
        </div>
      </section>
    </PortalPage>
  );
}
