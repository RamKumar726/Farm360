import { useEffect, useState } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { invoicesAPI, leadsAPI, paymentsAPI, quotesAPI } from "../../config/api";
import { CreditCard, CheckCircle } from "lucide-react";
import toast from "react-hot-toast";
import { openRazorpayCheckout } from "../../utils/razorpay";

const money = (amount) => `₹${Number(amount || 0).toLocaleString("en-IN")}`;

export default function CustomerPayments() {
  const [leads, setLeads] = useState([]);
  const [payments, setPayments] = useState([]);
  const [quotes, setQuotes] = useState({});
  const [invoices, setInvoices] = useState([]);
  const [busyId, setBusyId] = useState(null);

  const refresh = async () => {
    const [leadResult, paymentResult, invoiceResult] = await Promise.all([leadsAPI.list(), paymentsAPI.list(), invoicesAPI.list()]);
    const rows = leadResult.success ? (leadResult.data.items || []) : [];
    setLeads(rows);
    if (paymentResult.success) setPayments(paymentResult.data || []);
    if (invoiceResult.success) setInvoices(invoiceResult.data?.items || []);
    const quoteResults = await Promise.all(rows.map(async (lead) => {
      try { return [lead.id, (await quotesAPI.forLead(lead.id)).data || []]; }
      catch { return [lead.id, []]; }
    }));
    setQuotes(Object.fromEntries(quoteResults));
  };

  const acceptQuote = async (quote) => {
    setBusyId(quote.id);
    try {
      await quotesAPI.accept(quote.id);
      await refresh();
      toast.success("Quotation accepted. You can now make the payment.");
    } catch (error) {
      toast.error(error?.detail || error.message || "Quotation could not be accepted");
    } finally { setBusyId(null); }
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
  const paymentLeads = leads.filter((lead) => lead.status === "payment" || paymentByLead[lead.id] || (quotes[lead.id] || []).some((quote) => quote.status === "sent"));

  return (
    <PortalPage title="Payments" subtitle="Pay approved service quotations and review verified transactions" navItems={CUSTOMER_NAV}>
      <div className="grid md:grid-cols-2 gap-4">
        {paymentLeads.map((lead) => {
          const payment = paymentByLead[lead.id];
          const amount = lead.final_amount ?? lead.price_to_complete;
          const isPaid = lead.payment_confirmed_at || payment?.status === "paid";
          const quote = (quotes[lead.id] || [])[0];
          return <article key={lead.id} className="card">
            <div className="flex justify-between items-start gap-3"><div><h2 className="font-semibold text-[#f0ede4]">{lead.services_needed || lead.type.replaceAll("_", " ")}</h2><p className="text-xs text-[#8fac9a] mt-1">Request #{lead.id.slice(0, 8)}</p></div>{isPaid ? <CheckCircle className="text-green-400" size={18} /> : <span className="badge-warning">Payment due</span>}</div>
            {quote && <div className="mt-4 rounded-xl border border-white/10 p-3 text-sm space-y-2">
              <div className="flex justify-between"><span>Quotation v{quote.version_number}</span><span className="capitalize">{quote.status}</span></div>
              {quote.items.map((item) => <div key={item.id} className="flex justify-between text-[#8fac9a]"><span>{item.description} × {item.quantity} {item.unit}</span><span>{money(item.line_total)}</span></div>)}
              <div className="flex justify-between font-semibold border-t border-white/10 pt-2"><span>Total</span><span>{money(quote.total)}</span></div>
              {quote.status === "sent" && <button disabled={busyId === quote.id} className="btn-primary w-full" onClick={() => acceptQuote(quote)}>{busyId === quote.id ? "Accepting…" : "Accept this quotation"}</button>}
            </div>}
            <p className="text-2xl font-bold mt-5">{money(quote?.total ?? amount)}</p>
            {isPaid ? <p className="text-sm text-green-400 mt-3">Payment verified. FarmCare will continue your request.</p> : quote?.status === "accepted" || lead.status === "payment" ? <button disabled={busyId === lead.id || !amount} className="btn-primary mt-4 flex items-center gap-2" onClick={() => payLead(lead)}><CreditCard size={17} />{busyId === lead.id ? "Opening payment…" : "Pay Now"}</button> : <p className="text-sm text-[#8fac9a] mt-3">Accept the latest approved quotation before payment.</p>}
          </article>;
        })}
        {paymentLeads.length === 0 && <div className="card md:col-span-2 text-center py-10"><CreditCard size={36} className="mx-auto mb-2 opacity-30" /><p className="text-[#8fac9a]">No service payments are due.</p></div>}
      </div>

      <section className="card mt-6">
        <h2 className="section-title">Invoices</h2>
        <div className="divide-y divide-white/10">
          {invoices.map((invoice) => <div key={invoice.id} className="py-3 flex justify-between items-center gap-4 text-sm"><div><p className="text-[#f0ede4]">{invoice.invoice_number}</p><p className="text-xs text-[#8fac9a] capitalize">{invoice.status.replaceAll("_", " ")}</p></div><div className="text-right"><p className="font-semibold">{money(invoice.total)}</p><p className="text-xs text-[#8fac9a]">Balance {money(invoice.balance)}</p></div></div>)}
          {invoices.length === 0 && <p className="py-4 text-sm text-[#8fac9a]">No invoices yet.</p>}
        </div>
      </section>

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
