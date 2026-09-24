import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { investmentsAPI, projectsAPI } from "../config/api";
import useAppStore from "../store/useAppStore";

const ordered = ["showed_interest", "employee_contacted", "customer_approved", "site_visit", "agreemented", "zone_approved", "founder_approved", "payment_gateway", "completed"];
const label = (s) => s.replaceAll("_", " ");

export default function InvestmentPipeline() {
  const { user } = useAppStore();
  const [items, setItems] = useState([]);
  const [projects, setProjects] = useState({});
  const [busy, setBusy] = useState(null);
  const [agreementUrls, setAgreementUrls] = useState({});
  const role = user?.role;
  const refresh = async () => {
    const [i, p] = await Promise.all([investmentsAPI.list(), projectsAPI.list()]);
    if (i.success) setItems(i.data.items || []);
    if (p.success) setProjects(Object.fromEntries((p.data.items || []).map((x) => [x.id, x])));
  };
  useEffect(() => { refresh().catch(() => toast.error("Could not load investment pipeline")); }, []);

  const nextAllowed = (stage) => {
    const next = ordered[ordered.indexOf(stage) + 1];
    if (!next || next === "completed" || next === "customer_approved") return null;
    if (next === "zone_approved" && !["zone_admin", "founder"].includes(role)) return null;
    if (next === "founder_approved" && role !== "founder") return null;
    if (next === "payment_gateway" && role !== "founder") return null;
    return next;
  };
  const advance = async (item, stage) => {
    const agreementUrl = stage === "agreemented" ? (agreementUrls[item.id] || "").trim() : undefined;
    if (stage === "agreemented" && !agreementUrl) {
      toast.error("Add the signed agreement URL before recording agreement completion");
      return;
    }
    setBusy(item.id);
    try {
      await investmentsAPI.updatePipeline(item.id, stage, agreementUrl);
      await refresh();
      toast.success(`Investment moved to ${label(stage)}`);
    } catch (error) {
      toast.error(error?.response?.data?.detail || error?.detail || error.message || "Could not update investment");
    } finally { setBusy(null); }
  };

  const active = items.filter((item) => item.verification_stage !== "completed");
  return <section className="card space-y-4">
    <div><h2 className="section-title">Investment interest verification</h2><p className="text-sm text-[#8fac9a]">Contact the customer, record site visit and agreement progress, then complete Zone and Founder approvals in order.</p></div>
    <div className="grid md:grid-cols-2 gap-3">
      {active.map((item) => {
        const next = nextAllowed(item.verification_stage);
        return <article key={item.id} className="rounded-xl border border-white/10 p-4 space-y-3">
          <div className="flex justify-between gap-2"><h3 className="font-semibold">{projects[item.project_id]?.name || `Project ${item.project_id.slice(0, 8)}`}</h3><span className="text-xs text-accent">{label(item.verification_stage)}</span></div>
          <p className="text-sm text-[#8fac9a]">Customer: {item.customer_id} · Interest: ₹{Number(item.proposed_amount || item.amount).toLocaleString("en-IN")}</p>
          {item.questions && <p className="text-xs text-[#8fac9a]">{item.questions}</p>}
          {item.agreement_url && <a className="text-xs text-accent underline" href={item.agreement_url} target="_blank" rel="noreferrer">View agreement</a>}
          {next === "agreemented" && <input className="input" type="url" placeholder="Signed agreement document URL" value={agreementUrls[item.id] || ""} onChange={(e) => setAgreementUrls({ ...agreementUrls, [item.id]: e.target.value })} />}
          {next && <button disabled={busy === item.id} className="btn-primary" onClick={() => advance(item, next)}>{busy === item.id ? "Saving…" : `Record: ${label(next)}`}</button>}
          {item.verification_stage === "customer_approved" && <p className="text-xs text-amber-300">Waiting for site visit and agreement work.</p>}
          {item.verification_stage === "payment_gateway" && <p className="text-xs text-green-300">Approved. Customer can pay from Investments.</p>}
        </article>;
      })}
      {active.length === 0 && <p className="text-sm text-[#8fac9a]">No investment interests are awaiting verification.</p>}
    </div>
  </section>;
}
