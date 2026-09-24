import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import PortalPage from "../../components/PortalPage";
import ProofUploader from "../../components/ProofUploader";
import StatusBadge from "../../components/StatusBadge";
import { WORK_PARTNER_NAV } from "./_nav";
import { apiFetch, workOrdersAPI, workPartnersAPI } from "../../config/api";

export default function WorkPartnerDashboard() {
  const [partner, setPartner] = useState(null);
  const [workOrders, setWorkOrders] = useState([]);
  const [dates, setDates] = useState({});
  const [activeProofId, setActiveProofId] = useState(null);
  const [proofUrls, setProofUrls] = useState([]);
  const [notes, setNotes] = useState("");

  const refresh = async () => {
    const [partnerResult, workResult] = await Promise.all([workPartnersAPI.list(), workOrdersAPI.list()]);
    const linkedPartner = partnerResult?.data?.items?.[0] || null;
    setPartner(linkedPartner);
    setWorkOrders(workResult?.data?.items || []);
  };
  useEffect(() => { refresh().catch(() => toast.error("Could not load provider work")); }, []);

  const decide = async (workOrder, accept) => {
    const date = dates[workOrder.id] || workOrder.start_date || "";
    if (accept && !date) return toast.error("Confirm the work date before accepting");
    try {
      const body = { work_order_id: workOrder.id, confirmed_start_date: accept ? date : null };
      if (accept) await workPartnersAPI.accept(partner.id, body);
      else await workPartnersAPI.reject(partner.id, body);
      toast.success(accept ? "Assignment and date confirmed" : "Assignment declined; the team was notified");
      await refresh();
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not update assignment"); }
  };

  const start = async (workOrder) => {
    try {
      await workOrdersAPI.updateStatus(workOrder.id, { status: "in_progress" });
      await refresh();
      toast.success("Work marked in progress");
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not start work"); }
  };

  const submitProof = async () => {
    if (!activeProofId || !proofUrls.length) return;
    try {
      await apiFetch(`/work-orders/${activeProofId}/submit-proof`, { method: "POST", body: JSON.stringify({ proof_urls: proofUrls, notes }) });
      setActiveProofId(null); setProofUrls([]); setNotes("");
      await refresh();
      toast.success("Proof submitted to FarmCare for verification");
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not submit proof"); }
  };

  return <PortalPage title="Assigned Provider Work" subtitle="Confirm assignments and dates, track work, and submit proof for verification" navItems={WORK_PARTNER_NAV}>
    {!partner && <p className="card text-sm text-amber-300">This login is not linked to an active outsourcing partner account. Ask FarmCare staff to link your account.</p>}
    <div className="grid md:grid-cols-2 gap-4">
      {workOrders.map((work) => <article key={work.id} className="card space-y-3">
        <div className="flex justify-between gap-2"><h2 className="font-semibold capitalize">{work.type?.replaceAll("_", " ")}</h2><StatusBadge status={work.status} /></div>
        <p className="text-xs text-[#8fac9a]">{work.notes || "No work details supplied"}</p>
        <p className="text-sm">Scheduled: {work.start_date || "Date not set"}</p>
        {work.status === "assigned" && <div className="space-y-2"><label className="label">Confirm work date</label><input type="date" min={new Date().toISOString().slice(0, 10)} className="input" value={dates[work.id] ?? work.start_date ?? ""} onChange={(event) => setDates({ ...dates, [work.id]: event.target.value })} /><div className="flex gap-2"><button className="btn-primary flex-1" onClick={() => decide(work, true)}>Accept assignment</button><button className="btn-secondary flex-1" onClick={() => decide(work, false)}>Decline</button></div></div>}
        {work.status === "partner_accepted" && <button className="btn-primary w-full" onClick={() => start(work)}>Start work</button>}
        {work.status === "in_progress" && <button className="btn-primary w-full" onClick={() => setActiveProofId(work.id)}>Submit proof of work</button>}
        {work.status === "proof_submitted" && <p className="text-sm text-emerald-300">Proof submitted; waiting for FarmCare verification.</p>}
      </article>)}
      {partner && workOrders.length === 0 && <p className="card text-sm text-[#8fac9a]">No work orders are currently assigned to your account.</p>}
    </div>
    {activeProofId && <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"><div className="card w-full max-w-xl space-y-4"><h2 className="section-title">Submit work proof</h2><ProofUploader onUpload={setProofUrls} /><textarea className="input min-h-24" placeholder="Work completed and notes" value={notes} onChange={(event) => setNotes(event.target.value)} /><div className="flex gap-3"><button className="btn-secondary" onClick={() => setActiveProofId(null)}>Cancel</button><button className="btn-primary" disabled={!proofUrls.length} onClick={submitProof}>Submit proof</button></div></div></div>}
  </PortalPage>;
}
