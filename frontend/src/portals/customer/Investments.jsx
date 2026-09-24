import { useEffect, useMemo, useState } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { investmentsAPI, projectsAPI, paymentsAPI } from "../../config/api";
import StatusBadge from "../../components/StatusBadge";
import { TrendingUp } from "lucide-react";
import toast from "react-hot-toast";
import { openRazorpayCheckout } from "../../utils/razorpay";

const money = (amount) => `₹${Number(amount || 0).toLocaleString("en-IN")}`;

export default function CustomerInvestments() {
  const [investments, setInvestments] = useState([]);
  const [projects, setProjects] = useState([]);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({ proposed_amount: 150000, questions: "", acknowledgement_accepted: false });
  const [loading, setLoading] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const projectsById = useMemo(() => Object.fromEntries(projects.map((p) => [p.id, p])), [projects]);

  const refresh = async () => {
    const [investmentResult, projectResult] = await Promise.all([
      investmentsAPI.list(),
      projectsAPI.list({ status: "open" }),
    ]);
    if (investmentResult.success) setInvestments(investmentResult.data.items || []);
    if (projectResult.success) setProjects(projectResult.data.items || []);
  };

  useEffect(() => { refresh().catch(() => toast.error("Could not load investments")); }, []);

  const expressInterest = async (event) => {
    event.preventDefault();
    if (!selected) return;
    setLoading(true);
    try {
      const result = await investmentsAPI.expressInterest({
        project_id: selected.id,
        proposed_amount: Number(form.proposed_amount),
        questions: form.questions || null,
        acknowledgement_accepted: form.acknowledgement_accepted,
      });
      setInvestments((current) => [result.data, ...current]);
      setSelected(null);
      setForm({ proposed_amount: 150000, questions: "", acknowledgement_accepted: false });
      toast.success("Interest submitted. Our employee will contact you for verification.");
    } catch (error) {
      toast.error(error?.response?.data?.detail || error?.detail || "Could not submit interest");
    } finally { setLoading(false); }
  };

  const approveInterest = async (id) => {
    setBusyId(id);
    try { await investmentsAPI.approveInterest(id); await refresh(); toast.success("Interest approved"); }
    catch (error) { toast.error(error?.response?.data?.detail || "Could not approve interest"); }
    finally { setBusyId(null); }
  };

  const payInvestment = async (investment) => {
    setBusyId(investment.id);
    try {
      const order = (await paymentsAPI.investmentOrder(investment.id)).data;
      const result = await openRazorpayCheckout(order, "Farm investment participation");
      await paymentsAPI.confirm({
        gateway_order_id: result.razorpay_order_id,
        gateway_payment_id: result.razorpay_payment_id,
        gateway_signature: result.razorpay_signature,
      });
      await refresh();
      toast.success("Payment verified. Your investment is active.");
    } catch (error) {
      toast.error(error?.response?.data?.detail || error?.detail || error.message || "Payment could not be completed");
    } finally { setBusyId(null); }
  };

  return (
    <PortalPage title="Investments" subtitle="Show interest, complete verification and track returns" navItems={CUSTOMER_NAV}>
      <section className="card space-y-4">
        <div>
          <h2 className="section-title">Open investment opportunities</h2>
          <p className="text-sm text-[#8fac9a]">Choose a project to show interest. Payment becomes available after employee verification, site visit, agreement and required approvals.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => {
            const remaining = Math.max(0, Number(project.total_amount) - Number(project.funded_amount || 0));
            return <article key={project.id} className="rounded-xl border border-white/10 p-4">
              <h3 className="font-semibold text-[#f0ede4]">{project.name}</h3>
              <p className="text-sm text-[#8fac9a] mt-2">Target {money(project.total_amount)} · Available {money(remaining)}</p>
              <p className="text-xs text-[#8fac9a] mt-1">Minimum interest {money(project.minimum_investment || 150000)}</p>
              <button disabled={remaining < Number(project.minimum_investment || 150000)} className="btn-primary mt-4" onClick={() => { setSelected(project); setForm({ proposed_amount: Number(project.minimum_investment || 150000), questions: "", acknowledgement_accepted: false }); }}>
                Show Interest for Investing
              </button>
            </article>;
          })}
          {projects.length === 0 && <p className="text-sm text-[#8fac9a]">There are no approved investment projects open right now.</p>}
        </div>
      </section>

      {selected && <div className="fixed inset-0 z-50 bg-black/70 grid place-items-center p-4" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelected(null); }}>
        <form className="card w-full max-w-lg space-y-4" onSubmit={expressInterest}>
          <h2 className="section-title">Show Interest for Investing</h2>
          <p className="text-sm text-[#8fac9a]">{selected.name} · available amount {money(Number(selected.total_amount) - Number(selected.funded_amount || 0))}</p>
          <div><label className="label">Amount to invest (₹)</label><input className="input" type="number" min={selected.minimum_investment || 150000} max={Number(selected.total_amount) - Number(selected.funded_amount || 0)} step="1000" required value={form.proposed_amount} onChange={(event) => setForm({ ...form, proposed_amount: event.target.value })} /></div>
          <div><label className="label">Questions or notes (optional)</label><textarea className="input min-h-24" value={form.questions} onChange={(event) => setForm({ ...form, questions: event.target.value })} /></div>
          <label className="flex gap-2 text-sm text-[#8fac9a]"><input type="checkbox" checked={form.acknowledgement_accepted} onChange={(event) => setForm({ ...form, acknowledgement_accepted: event.target.checked })} required />I understand this is an expression of interest and the team must verify it before payment.</label>
          <div className="flex gap-3"><button disabled={loading} className="btn-primary" type="submit">{loading ? "Submitting…" : "Submit Interest"}</button><button className="btn-secondary" type="button" onClick={() => setSelected(null)}>Cancel</button></div>
        </form>
      </div>}

      <section className="space-y-4">
        <h2 className="section-title">My investment interests</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {investments.map((investment) => <article key={investment.id} className="card">
            <div className="flex justify-between items-start mb-3"><span className="font-semibold text-[#f0ede4]">{projectsById[investment.project_id]?.name || `Project ${investment.project_id.slice(0, 8)}`}</span><StatusBadge status={investment.status === "pending" ? investment.verification_stage : investment.status} /></div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-[#8fac9a]">Proposed amount</span><span className="font-semibold">{money(investment.proposed_amount)}</span></div>
              {investment.revenue_share_percentage != null && <div className="flex justify-between"><span className="text-[#8fac9a]">Revenue share</span><span className="text-accent font-semibold">{investment.revenue_share_percentage.toFixed(2)}%</span></div>}
              {investment.expected_return != null && <div className="flex justify-between"><span className="text-[#8fac9a]">Expected return</span><span className="text-green-400 font-semibold">{money(investment.expected_return)}</span></div>}
              {investment.actual_return != null && <div className="flex justify-between"><span className="text-[#8fac9a]">{investment.payout_reference ? "Paid return" : "Calculated return"}</span><span className="font-semibold">{money(investment.actual_return)}</span></div>}
              <p className="text-[#8fac9a]">Status: {investment.verification_stage?.replaceAll("_", " ")}</p>
              {investment.agreement_url && <a className="text-accent underline text-sm" href={investment.agreement_url} target="_blank" rel="noreferrer">Review investment agreement</a>}
              {investment.payout_reference && <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs">Payout recorded {investment.settlement_date ? `on ${investment.settlement_date}` : ""} · Reference: {investment.payout_reference}{investment.payout_proof_url && <> · <a className="text-accent underline" href={investment.payout_proof_url} target="_blank" rel="noreferrer">View transfer proof</a></>}</div>}
              {investment.verification_stage === "customer_approved" && <p className="text-xs text-[#8fac9a]">Your approval is recorded. The team is obtaining site visit, agreement and administrative approvals.</p>}
              {investment.verification_stage === "employee_contacted" && <button disabled={busyId === investment.id} className="btn-primary mt-2" onClick={() => approveInterest(investment.id)}>Approve this interest</button>}
              {investment.verification_stage === "payment_gateway" && <button disabled={busyId === investment.id} className="btn-primary mt-2" onClick={() => payInvestment(investment)}>{busyId === investment.id ? "Opening payment…" : `Pay ${money(investment.proposed_amount)}`}</button>}
            </div>
          </article>)}
          {investments.length === 0 && <div className="md:col-span-2 card text-center py-10"><TrendingUp size={36} className="mx-auto mb-2 opacity-30" /><p className="text-[#8fac9a]">You have not expressed interest in a project.</p></div>}
        </div>
      </section>
    </PortalPage>
  );
}
