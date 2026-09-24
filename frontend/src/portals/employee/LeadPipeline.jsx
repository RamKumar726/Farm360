import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { EMPLOYEE_NAV } from "./_nav";
import { apiFetch, usersAPI, projectsAPI, leadsAPI } from "../../config/api";
import { Plus, ArrowRight, UserCheck, Send, CheckCircle2, ShieldCheck, X, ClipboardList, KeyRound } from "lucide-react";
import toast from "react-hot-toast";
import StatusBadge from "../../components/StatusBadge";
import InvestmentPipeline from "../../components/InvestmentPipeline";

const SERVICE_STAGES = [
  "prospecting", "qualification", "need_analysis", "value_proposition",
  "decision_makers", "proposal_price", "negotiation", "register_user",
  "login_guide", "payment", "closed_won"
];

const LEASE_STAGES = [
  "prospecting", "qualification", "need_analysis", "land_verification",
  "feasibility", "commercial_model", "proposal", "negotiation",
  "agreement", "approval", "closed_won"
];
const LAND_SALE_STAGES = [
  "prospecting", "qualification", "land_verification", "feasibility",
  "proposal", "negotiation", "agreement", "approval", "closed_won"
];

export default function EmployeeLeadPipeline() {
  const [leads, setLeads] = useState([]);
  const [agriOfficers, setAgriOfficers] = useState([]);
  const [existingProjects, setExistingProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ type: "one_time_service", source: "employee", farm_details: "" });

  // Stage management modal
  const [selectedLead, setSelectedLead] = useState(null);
  const [stagePayload, setStagePayload] = useState({});
  const [registration, setRegistration] = useState({ name: "", email: "", phone: "" });
  const [temporaryPassword, setTemporaryPassword] = useState("");
  const [credentialsLead, setCredentialsLead] = useState(null);
  const [stagesLead, setStagesLead] = useState(null);
  const [closedLostLead, setClosedLostLead] = useState(null);
  const [lostReason, setLostReason] = useState("");

  const loadData = () => {
    apiFetch("/leads").then((r) => { if (r.success) setLeads(r.data.items); setLoading(false); }).catch(() => setLoading(false));
    usersAPI.list().then((r) => { if (r.success) setAgriOfficers(r.data.items.filter(u => u.role === "agri_officer")); });
    projectsAPI.list().then((r) => { if (r.success) setExistingProjects(r.data.items || []); });
  };

  useEffect(() => { loadData(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await apiFetch("/leads", { method: "POST", body: JSON.stringify(form) });
      if (res.success) { setLeads((p) => [res.data, ...p]); setShowForm(false); toast.success("Lead added to prospecting!"); }
    } catch (err) { toast.error("Failed to create lead"); }
  };

  const getNextStage = (lead) => {
    let pipeline = lead.type === "farm_lease" ? LEASE_STAGES : lead.type === "sell_land" ? LAND_SALE_STAGES : SERVICE_STAGES;
    if (lead.is_opportunity && pipeline === SERVICE_STAGES) pipeline = pipeline.filter((s) => !["register_user", "login_guide"].includes(s));
    const idx = pipeline.indexOf(lead.status);
    if (idx >= 0 && idx < pipeline.length - 1) return pipeline[idx + 1];
    return null;
  };

  const advanceStage = async (lead) => {
    const nextStage = getNextStage(lead);
    if (!nextStage) return;
    try {
      const res = await apiFetch(`/leads/${lead.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: nextStage, ...stagePayload }),
      });
      if (res.success) {
        toast.success(`Advanced to ${nextStage.replace("_", " ")}`);
        setSelectedLead(null);
        setStagePayload({});
        loadData();
      }
    } catch (e) { toast.error("Failed to advance stage"); }
  };

  const handleReviewQuote = async (leadId, action) => {
    try {
      const res = await apiFetch(`/leads/${leadId}/review-quote?action=${action}`, { method: "POST" });
      if (res.success) {
        toast.success(action === "send" ? "Quotation published to customer portal" : "Quotation reviewed");
        loadData();
      }
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not update quotation"); }
  };

  const registerCustomer = async () => {
    try {
      const registrationPayload = {
        name: registration.name || selectedLead.contact_name || "",
        email: registration.email || selectedLead.contact_email || "",
        phone: registration.phone || selectedLead.contact_phone || "",
      };
      const result = await leadsAPI.registerCustomer(selectedLead.id, registrationPayload);
      setSelectedLead(result.data.lead);
      setTemporaryPassword(result.data.temporary_password || "");
      if (result.data.temporary_password) setCredentialsLead(result.data.lead);
      toast.success(result.message || "Customer linked");
      loadData();
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not register customer"); }
  };

  const resetCustomerPassword = async () => {
    try {
      const result = await apiFetch(`/leads/${selectedLead.id}/reset-customer-password`, { method: "POST" });
      setTemporaryPassword(result.data.temporary_password);
      setCredentialsLead({ ...selectedLead, contact_email: result.data.email || selectedLead.contact_email });
      toast.success("New temporary password issued. Share it securely with the customer.");
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not reset customer password"); }
  };

  const copyTemporaryPassword = async () => {
    try {
      await navigator.clipboard.writeText(temporaryPassword);
      toast.success("Temporary password copied");
    } catch { toast.error("Could not copy password; select and copy it manually"); }
  };

  const copyCustomerCredentials = async () => {
    const email = credentialsLead?.contact_email || registration.email || selectedLead?.contact_email || "";
    const details = `Farm360 customer portal: ${window.location.origin}/login\nEmail: ${email}\nTemporary password: ${temporaryPassword}\nPlease change your password after signing in.`;
    try {
      await navigator.clipboard.writeText(details);
      toast.success("Portal link and credentials copied");
    } catch { toast.error("Could not copy credentials; select and copy them manually"); }
  };

  const getStages = (lead) => {
    let pipeline = lead.type === "farm_lease" ? LEASE_STAGES : lead.type === "sell_land" ? LAND_SALE_STAGES : SERVICE_STAGES;
    if (lead.is_opportunity && pipeline === SERVICE_STAGES) pipeline = pipeline.filter((s) => !["register_user", "login_guide"].includes(s));
    return pipeline;
  };

  const confirmClosedLost = async () => {
    if (!closedLostLead) return;
    try {
      const res = await apiFetch(`/leads/${closedLostLead.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: "closed_lost", lost_reason: lostReason }),
      });
      if (res.success) {
        toast.success("Lead marked Closed Lost");
        setClosedLostLead(null);
        setLostReason("");
        loadData();
      }
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not close lead"); }
  };

  return (
    <PortalPage title="Lead & Opportunity Pipeline" subtitle="11-Stage Service & Lease Lead Lifecycle Management" navItems={EMPLOYEE_NAV}>
      <InvestmentPipeline />
      <div className="space-y-6">
        <button className="btn-primary flex items-center gap-2 font-bold" onClick={() => setShowForm(!showForm)}><Plus size={16} /> New Lead / Opportunity</button>

        {showForm && (
          <div className="card animate-slide-up">
            <h2 className="section-title">Create New Lead Request</h2>
            <form onSubmit={handleCreate} className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="label">Lead / Service Type</label>
                <select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                  <option value="one_time_service">One-Time Service (Borewell/Fencing/Cleaning)</option>
                  <option value="farm_management">Farm Management (Managed Farm)</option>
                  <option value="farm_lease">Farm Lease (In-House / Lease Arrangement)</option>
                  <option value="sell_land">Sell My Land</option>
                  <option value="investment_interest">Investment Interest</option>
                </select>
              </div>
              <div>
                <label className="label">Source</label>
                <select className="input" value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })}>
                  <option value="employee">Employee Referral</option>
                  <option value="website">Website</option>
                  <option value="call_message">Call / Message</option>
                  <option value="referral">Customer Referral</option>
                  <option value="digital_marketing">Digital Marketing</option>
                </select>
              </div>
              <div className="md:col-span-2"><label className="label">Customer & Farm Details</label><textarea className="input min-h-[80px]" placeholder="Customer name, phone, land location, requirements..." value={form.farm_details} onChange={(e) => setForm({ ...form, farm_details: e.target.value })} required /></div>
              <div className="flex items-end gap-3">
                <button type="submit" className="btn-primary font-bold">Create Lead</button>
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        )}

        {loading ? <p className="text-center text-[#8fac9a] py-8">Loading pipeline...</p> : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {leads.map((lead) => {
              const nextStage = getNextStage(lead);
              const isLease = lead.type === "farm_lease";
              let stages = isLease ? LEASE_STAGES : lead.type === "sell_land" ? LAND_SALE_STAGES : SERVICE_STAGES;
              if (lead.is_opportunity && !isLease && lead.type !== "sell_land") stages = stages.filter((s) => !["register_user", "login_guide"].includes(s));
              const currentIdx = stages.indexOf(lead.status);

              return (
                <div key={lead.id} className="card hover:border-accent/40 transition-all flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-xs font-mono text-accent">#{lead.id.slice(0, 8)}</span>
                        <h3 className="font-bold text-[#143628] capitalize">{lead.type.replace("_", " ")}</h3>
                      </div>
                      <StatusBadge status={lead.status} />
                    </div>

                    <p className="text-sm text-[#4a5850] line-clamp-2">{lead.farm_details}</p>
                    {lead.land_verification_data && <div className="rounded-lg bg-[#fbf9f4] p-3 text-xs text-[#4a5850]"><p className="font-semibold text-[#143628]">Land verification</p><p className="whitespace-pre-wrap line-clamp-4">{lead.land_verification_data}</p></div>}
                    {lead.ao_feasibility_data && <div className="rounded-lg bg-[#fbf9f4] p-3 text-xs text-[#4a5850]"><p className="font-semibold text-[#143628]">AO feasibility</p><p className="whitespace-pre-wrap line-clamp-4">{lead.ao_feasibility_data}</p></div>}

                    {/* Stage Progress Bar */}
                    <div role="button" tabIndex={0} onClick={() => setStagesLead(lead)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setStagesLead(lead); } }} className="space-y-1 w-full text-left rounded-lg p-1 cursor-pointer hover:bg-black/5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent" title="View all pipeline stages">
                      <div className="flex justify-between text-xs text-[#4a5850]">
                        <span>Stage {currentIdx >= 0 ? currentIdx + 1 : 1} of {stages.length}</span>
                        <span className="capitalize font-semibold text-accent">{lead.status.replace("_", " ")}</span>
                      </div>
                      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-accent transition-all duration-500" style={{ width: `${((currentIdx + 1) / stages.length) * 100}%` }} />
                      </div>
                      <span className="text-[11px] text-accent inline-flex items-center gap-1"><ClipboardList size={12} /> View all stages</span>
                    </div>

                    {/* AO Assignment & Quotation Status */}
                    {lead.assigned_ao_id && (
                      <div className="bg-[#fbf9f4] p-2.5 rounded-xl text-xs flex items-center justify-between text-[#4a5850]">
                        <span>Assigned Agriculture Officer:</span>
                        <span className="font-semibold text-[#143628]">Assigned</span>
                      </div>
                    )}

                    {lead.ao_quotation_doc && (
                      <div className="bg-[#efe7d2] border border-accent/40 p-3 rounded-xl text-xs space-y-2 text-[#4a5850]">
                        <p className="font-bold text-accent">✓ AO Solution & Quotation Submitted</p>
                        <p className="text-[#1f2824]">Services: {lead.services_needed || "Custom Service Package"}</p>
                        <p className="text-[#1f2824]">Price: ₹{Number(lead.price_to_complete || 0).toLocaleString()}</p>

                        {!lead.sent_to_client && (
                          <div className="flex gap-2 mt-2">
                            <button onClick={() => handleReviewQuote(lead.id, "review")} className="btn-secondary flex-1 py-1.5 text-xs">Review</button>
                            <button onClick={() => handleReviewQuote(lead.id, "send")} className="btn-primary flex-1 py-1.5 text-xs font-bold flex items-center justify-center gap-1">
                              <Send size={12} /> Publish to Customer Portal
                            </button>
                          </div>
                        )}
                        <p className="text-[11px]">Customer can view this in Work Details after their account is linked. Share the portal link separately.</p>
                        {lead.sent_to_client && <p className="text-emerald-700 font-semibold">✓ Published to customer portal</p>}
                      </div>
                    )}
                  </div>

                  <div className="space-y-2 mt-4">
                    {nextStage && (
                      <button onClick={() => { setSelectedLead(lead); setStagePayload({}); setRegistration({ name: lead.contact_name || "", email: lead.contact_email || "", phone: lead.contact_phone || "" }); setTemporaryPassword(""); }} className="btn-primary w-full text-xs font-bold flex items-center justify-center gap-2">
                        Advance Stage → ({nextStage.replace("_", " ")})
                      </button>
                    )}
                    {lead.status !== "closed_won" && lead.status !== "closed_lost" && (
                      <button
                        onClick={() => { setClosedLostLead(lead); setLostReason(""); }}
                        className="w-full text-xs text-red-400 hover:text-red-300 py-1 font-semibold text-center border border-red-500/20 hover:bg-red-500/10 rounded-lg transition-all"
                      >
                        Mark as Closed Lost
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
            {leads.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No active leads in pipeline</p>}
          </div>
        )}
      </div>

      {stagesLead && (() => {
        const pipeline = getStages(stagesLead);
        const currentIndex = pipeline.indexOf(stagesLead.status);
        return (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-[55] flex items-center justify-center p-4" onMouseDown={(e) => { if (e.target === e.currentTarget) setStagesLead(null); }}>
            <div role="dialog" aria-modal="true" aria-labelledby="lead-stage-title" className="bg-[#121c17] border border-accent/30 rounded-2xl p-6 max-w-lg w-full max-h-[85vh] overflow-y-auto text-left">
              <div className="flex justify-between items-start border-b border-white/10 pb-4 mb-4">
                <div><h3 id="lead-stage-title" className="text-lg font-bold text-[#f0ede4]">Complete stages</h3><p className="text-xs text-[#8fac9a] mt-1">Lead #{stagesLead.id?.slice(0, 8)} · {stagesLead.type?.replace(/_/g, " ")}</p></div>
                <button aria-label="Close stages" onClick={() => setStagesLead(null)} className="text-[#8fac9a] hover:text-white"><X size={20} /></button>
              </div>
              <ol className="space-y-3">
                {pipeline.map((stage, index) => {
                  const isCurrent = stage === stagesLead.status;
                  const isComplete = currentIndex >= 0 && index < currentIndex;
                  return <li key={stage} className={`flex gap-3 items-center rounded-lg border p-3 ${isCurrent ? "border-accent bg-accent/10" : isComplete ? "border-emerald-500/30 bg-emerald-500/5" : "border-white/10 bg-white/[0.02]"}`}>
                    <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${isCurrent ? "bg-accent text-[#143628]" : isComplete ? "bg-emerald-700 text-white" : "bg-white/10 text-[#8fac9a]"}`}>{isComplete ? "✓" : index + 1}</span>
                    <span className={`capitalize flex-1 ${isCurrent ? "text-accent font-semibold" : isComplete ? "text-emerald-300" : "text-[#a8b8af]"}`}>{stage.replace(/_/g, " ")}</span>
                    {isCurrent && <span className="text-[10px] uppercase tracking-wide text-accent">Current</span>}
                    {isComplete && <span className="text-[10px] uppercase tracking-wide text-emerald-300">Complete</span>}
                  </li>;
                })}
                {stagesLead.status === "closed_lost" && <li className="rounded-lg border border-red-500/30 bg-red-500/5 p-3 text-sm text-red-300">Closed Lost{stagesLead.lost_reason ? ` · ${stagesLead.lost_reason}` : ""}</li>}
              </ol>
              <button className="btn-secondary w-full mt-5" onClick={() => setStagesLead(null)}>Close</button>
            </div>
          </div>
        );
      })()}

      {credentialsLead && temporaryPassword && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[70] flex items-center justify-center p-4" onMouseDown={(e) => { if (e.target === e.currentTarget) setCredentialsLead(null); }}>
          <div role="dialog" aria-modal="true" aria-labelledby="customer-credentials-title" className="bg-[#121c17] border border-accent/40 rounded-2xl p-6 max-w-md w-full space-y-4 text-left shadow-2xl">
            <div className="flex items-start gap-3"><div className="rounded-xl bg-accent/15 p-3 text-accent"><KeyRound size={22} /></div><div><h3 id="customer-credentials-title" className="text-lg font-bold text-[#f0ede4]">Customer account ready</h3><p className="text-xs text-[#8fac9a] mt-1">Copy these details now and share them securely. This temporary password is shown only once.</p></div></div>
            <div className="space-y-3 rounded-xl bg-white/5 p-4 text-sm">
              <div><p className="text-xs text-[#8fac9a]">Customer portal</p><a className="text-accent underline break-all" href={`${window.location.origin}/login`} target="_blank" rel="noreferrer">{window.location.origin}/login</a></div>
              <div><p className="text-xs text-[#8fac9a]">Email / login</p><p className="text-[#f0ede4] break-all">{credentialsLead.contact_email || registration.email || selectedLead?.contact_email || "Not provided"}</p></div>
              <div><p className="text-xs text-[#8fac9a]">Temporary password</p><p className="font-mono text-amber-200 select-all break-all">{temporaryPassword}</p></div>
            </div>
            <p className="text-xs text-[#8fac9a]">Ask the customer to sign in and change this password. Farm360 does not email or text credentials automatically.</p>
            <div className="flex gap-3"><button className="btn-secondary flex-1" onClick={copyCustomerCredentials}>Copy login details</button><button className="btn-primary flex-1" onClick={() => setCredentialsLead(null)}>Done</button></div>
          </div>
        </div>
      )}

      {closedLostLead && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-[60] flex items-center justify-center p-4" onMouseDown={(e) => { if (e.target === e.currentTarget) setClosedLostLead(null); }}>
          <div role="dialog" aria-modal="true" aria-labelledby="closed-lost-title" className="bg-[#121c17] border border-red-500/30 rounded-2xl p-6 max-w-md w-full space-y-4">
            <div className="flex justify-between items-start"><div><h3 id="closed-lost-title" className="text-lg font-bold text-[#f0ede4]">Mark lead as Closed Lost?</h3><p className="text-xs text-[#8fac9a] mt-1">Lead #{closedLostLead.id?.slice(0, 8)} will leave the active pipeline.</p></div><button aria-label="Close" onClick={() => setClosedLostLead(null)} className="text-[#8fac9a]"><X size={20} /></button></div>
            <label className="label" htmlFor="lost-reason">Reason (optional)</label><textarea id="lost-reason" className="input min-h-24" value={lostReason} onChange={(e) => setLostReason(e.target.value)} placeholder="Why was this lead lost?" />
            <div className="flex gap-3"><button className="btn-secondary flex-1" onClick={() => setClosedLostLead(null)}>Cancel</button><button className="flex-1 rounded-xl bg-red-700 px-4 py-3 font-semibold text-white hover:bg-red-600" onClick={confirmClosedLost}>Confirm Closed Lost</button></div>
          </div>
        </div>
      )}

      {/* ADVANCE STAGE MODAL WITH PAYLOAD FORMS */}
      {selectedLead && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121c17] border border-accent/30 rounded-3xl p-6 max-w-lg w-full space-y-4 text-left">
            <div className="flex justify-between items-center border-b border-white/10 pb-3">
              <div>
                <h3 className="text-xl font-bold text-[#f0ede4]">Advance Stage for Lead #{selectedLead.id?.slice(0, 8)}</h3>
                <p className="text-xs text-[#8fac9a]">Target Stage: <strong className="text-accent uppercase">{getNextStage(selectedLead)?.replace("_", " ")}</strong></p>
              </div>
              <button onClick={() => setSelectedLead(null)} className="text-[#8fac9a] hover:text-white"><X size={20} /></button>
            </div>

            {/* Stage-specific inputs */}
            {getNextStage(selectedLead) === "qualification" && (
              <div className="space-y-3 text-sm">
                <div><label className="label">Customer Need & Requirements</label><textarea className="input" rows={2} placeholder="What is the need, how we can help..." onChange={(e) => setStagePayload({ ...stagePayload, qualification_data: e.target.value })} /></div>
                <div>
                  <label className="label">Project Level</label>
                  <select className="input" onChange={(e) => setStagePayload({ ...stagePayload, project_level: e.target.value })}>
                    <option value="small">Small Project</option>
                    <option value="medium">Medium Project</option>
                    <option value="big">Big Project</option>
                  </select>
                </div>
                <div><label className="label">Crop (for farm plans)</label><input className="input" value={stagePayload.crop_name || ""} placeholder="e.g. Rice" onChange={(e) => setStagePayload({ ...stagePayload, crop_name: e.target.value })} /></div>
              </div>
            )}

            {getNextStage(selectedLead) === "need_analysis" && (
              <div className="space-y-3 text-sm">
                <div><label className="label">Challenges & Goals</label><textarea className="input" rows={2} placeholder="Specific challenges and goals..." onChange={(e) => setStagePayload({ ...stagePayload, need_analysis_data: e.target.value })} /></div>
                {(selectedLead.type === "farm_lease" || selectedLead.type === "sell_land") && (
                  <div>
                    <label className="label">Lease Arrangement Type</label>
                    <select className="input" onChange={(e) => setStagePayload({ ...stagePayload, lease_arrangement_type: e.target.value })}>
                      <option value="">-- Select lease arrangement --</option>
                    <option value="in_house_lease">FarmCare 360° takes the land directly (In-House Lease)</option>
                      <option value="lease_arrangement">FarmCare 360° finds another lease taker (Lease Arrangement)</option>
                    </select>
                  </div>
                )}
              </div>
            )}

            {getNextStage(selectedLead) === "land_verification" && (
              <div className="space-y-3 text-sm">
                <label className="label">Land, site and document verification</label>
                <textarea className="input min-h-40" required placeholder="Record usable acreage, land condition, soil, water and borewell, irrigation, electricity, road access, fencing/security, existing crops, surroundings, suitability, document checks, and site visit date." value={stagePayload.land_verification_data || ""} onChange={(e) => setStagePayload({ ...stagePayload, land_verification_data: e.target.value })} />
                <label className="label">Assign Agriculture Officer for feasibility</label>
                <select className="input" value={stagePayload.assigned_ao_id || selectedLead.assigned_ao_id || ""} onChange={(e) => setStagePayload({ ...stagePayload, assigned_ao_id: e.target.value })} required>
                  <option value="">Select Agriculture Officer</option>{agriOfficers.map((ao) => <option key={ao.id} value={ao.id}>{ao.name} · {ao.email}</option>)}
                </select>
              </div>
            )}

            {getNextStage(selectedLead) === "feasibility" && (
              <div className="space-y-3 text-sm">
                <p className="rounded-lg border border-accent/20 bg-accent/5 p-3 text-[#8fac9a]">The assigned Agriculture Officer must submit the land suitability, crop, water, operations, cost, revenue, risk, and farm plan assessment before the lease model can be selected.</p>
              </div>
            )}

            {getNextStage(selectedLead) === "value_proposition" && (
              <div className="space-y-3 text-sm">
                <div>
                  <label className="label">Value Proposition Statement</label>
                  <textarea
                    className="input"
                    rows={3}
                    placeholder="Clear conclusion statement explaining why customer should take our service..."
                    onChange={(e) => setStagePayload({ ...stagePayload, value_prop_data: e.target.value })}
                  />
                </div>
              </div>
            )}

            {getNextStage(selectedLead) === "decision_makers" && (
              <div className="space-y-3 text-sm">
                <label className="label">Assign Agriculture Officer</label>
                <select className="input" onChange={(e) => setStagePayload({ ...stagePayload, assigned_ao_id: e.target.value })}>
                  <option value="">-- Select Agriculture Officer --</option>
                  {agriOfficers.map(ao => (
                    <option key={ao.id} value={ao.id}>{ao.name} ({ao.email})</option>
                  ))}
                </select>
                <p className="text-xs text-[#8fac9a]">The assigned Agriculture Officer will receive a task to conduct site visit / document review and prepare a comprehensive solution and quotation.</p>
              </div>
            )}

            {getNextStage(selectedLead) === "negotiation" && (
              <div className="space-y-3 text-sm">
                <div><label className="label">Price to Complete (Original Quote)</label><input className="input" type="number" value={selectedLead.price_to_complete || 0} disabled /></div>
                <div><label className="label">Negotiated Discount (₹)</label><input className="input" type="number" onChange={(e) => {
                  const disc = Number(e.target.value) || 0;
                  const final = (selectedLead.price_to_complete || 0) - disc;
                  setStagePayload({ ...stagePayload, discount_amount: disc, final_amount: final });
                }} /></div>
                <div><label className="label">Final Agreed Price (₹)</label><input className="input font-bold text-accent" type="number" value={stagePayload.final_amount ?? selectedLead.price_to_complete ?? 0} readOnly /></div>
              </div>
            )}

            {getNextStage(selectedLead) === "proposal" && selectedLead.type === "farm_lease" && (
              <div className="space-y-3 text-sm">
                <label className="label">Lease proposal and initial terms</label>
                <textarea className="input min-h-24" required placeholder="Summarize the proposed lease, responsibilities and commercial terms." value={stagePayload.proposal_data || ""} onChange={(e) => setStagePayload({ ...stagePayload, proposal_data: e.target.value })} />
                <input className="input" type="number" min="0" step="0.01" required placeholder="Proposed total amount ₹" value={stagePayload.price_to_complete ?? selectedLead.price_to_complete ?? ""} onChange={(e) => setStagePayload({ ...stagePayload, price_to_complete: Number(e.target.value), final_amount: Number(e.target.value) })} />
              </div>
            )}

            {getNextStage(selectedLead) === "agreement" && selectedLead.type === "farm_lease" && (
              <div className="space-y-3 text-sm">
                <label className="label">Executed lease agreement document URL</label>
                <input className="input" type="url" required placeholder="https://…" value={stagePayload.agreement_url || ""} onChange={(e) => setStagePayload({ ...stagePayload, agreement_url: e.target.value })} />
              </div>
            )}

            {getNextStage(selectedLead) === "register_user" && (
              <div className="space-y-3 text-sm">
                <p className="text-xs text-emerald-400 font-semibold">✓ Registering Customer Account</p>
                <p className="text-xs text-[#8fac9a]">Customer account will be registered using phone and email details provided in the lead.</p>
              </div>
            )}

            {getNextStage(selectedLead) === "login_guide" && (
              <div className="space-y-3 text-sm">
                <p className="text-xs text-accent font-semibold">📲 Customer App Login Guidance</p>
                <p className="text-xs text-[#8fac9a]">Credentials are not sent automatically. Share the portal link and temporary password securely with the customer.</p>
                <p className="rounded-lg bg-white/5 p-3 text-xs text-[#f0ede4]">Customer portal: <a className="underline text-accent" href={`${window.location.origin}/login`} target="_blank" rel="noreferrer">{window.location.origin}/login</a></p>
              </div>
            )}

            {getNextStage(selectedLead) === "payment" && (
              <div className="space-y-3 text-sm">
                <p className="text-xs text-emerald-400 font-semibold">💳 Payment Details Verification</p>
                <p className="text-xs text-[#8fac9a]">In-app payment will be made visible to customer based on final negotiated price: ₹{Number(selectedLead.final_amount || selectedLead.price_to_complete || 0).toLocaleString()}</p>
              </div>
            )}

            {getNextStage(selectedLead) === "closed_won" && (
              <div className="space-y-3 text-sm">
                <p className="text-xs text-emerald-400 font-bold">🎉 Complete Lead & Create Linked Project</p>
                <p className="text-xs text-[#8fac9a]">Lead will be marked Closed Won, and an active project will automatically be created containing all client details, service type, and payment record.</p>
              </div>
            )}

            {selectedLead.status === "register_user" && !selectedLead.customer_id && (
              <div className="space-y-3 text-sm">
                <p className="text-xs text-[#8fac9a]">Create the customer portal account before guiding them through login.</p>
                <input className="input" placeholder="Customer name" value={registration.name} onChange={(e) => setRegistration({ ...registration, name: e.target.value })} required />
                <input className="input" type="email" placeholder="Customer email" value={registration.email} onChange={(e) => setRegistration({ ...registration, email: e.target.value })} required />
                <input className="input" placeholder="Phone number" value={registration.phone} onChange={(e) => setRegistration({ ...registration, phone: e.target.value })} />
                <button className="btn-secondary w-full" type="button" onClick={registerCustomer}>Create / Link Customer Account</button>
                {temporaryPassword && <div className="rounded-lg bg-amber-500/10 p-3 text-amber-100 space-y-2"><p>Temporary password (shown once; share securely): <strong className="select-all">{temporaryPassword}</strong></p><button type="button" className="btn-secondary text-xs" onClick={copyTemporaryPassword}>Copy password</button></div>}
              </div>
            )}

            {selectedLead.status === "login_guide" && selectedLead.customer_id && (
              <div className="space-y-2 rounded-xl border border-accent/30 bg-white/5 p-3 text-sm">
                <p className="text-[#f0ede4] font-semibold">Customer account is linked</p>
                <p className="text-xs text-[#8fac9a]">If the original temporary password was missed, issue a new one. The old password will stop working.</p>
                <button type="button" className="btn-secondary w-full" onClick={resetCustomerPassword}>Issue New Temporary Password</button>
                {temporaryPassword && <div className="space-y-2 rounded-lg bg-amber-500/10 p-3 text-amber-100"><p>Share securely with {selectedLead.contact_email || "the customer"}: <strong className="select-all">{temporaryPassword}</strong></p><button type="button" className="btn-secondary text-xs" onClick={copyTemporaryPassword}>Copy password</button></div>}
              </div>
            )}

            {selectedLead.type === "farm_lease" && !selectedLead.is_opportunity && !selectedLead.customer_id && ["agreement", "approval"].includes(selectedLead.status) && (
              <div className="space-y-3 text-sm rounded-xl border border-amber-500/30 bg-amber-500/5 p-4">
                <p className="text-[#f0ede4] font-semibold">Register the new landowner before final approval</p>
                <p className="text-xs text-[#8fac9a]">The landowner account links the executed agreement and lease project to the customer portal.</p>
                <input className="input" placeholder="Landowner name" value={registration.name} onChange={(e) => setRegistration({ ...registration, name: e.target.value })} required />
                <input className="input" type="email" placeholder="Landowner email" value={registration.email || selectedLead.contact_email || ""} onChange={(e) => setRegistration({ ...registration, email: e.target.value })} required />
                <input className="input" placeholder="Phone number" value={registration.phone || selectedLead.contact_phone || ""} onChange={(e) => setRegistration({ ...registration, phone: e.target.value })} />
                <button className="btn-secondary w-full" type="button" disabled={!registration.name || !(registration.email || selectedLead.contact_email)} onClick={registerCustomer}>Create / Link Landowner Account</button>
                {temporaryPassword && <div className="rounded-lg bg-amber-500/10 p-3 text-amber-100 space-y-2"><p>Temporary password (shown once; share securely): <strong className="select-all">{temporaryPassword}</strong></p><button type="button" className="btn-secondary text-xs" onClick={copyTemporaryPassword}>Copy password</button></div>}
              </div>
            )}

            {getNextStage(selectedLead) === "closed_won" && ["farm_manage", "farm_management"].includes(selectedLead.type) && (
              <div className="space-y-2 text-sm">
                <label className="label">Use an existing customer project or create a new one</label>
                <select className="input" value={stagePayload.existing_project_id || ""} onChange={(e) => setStagePayload({ ...stagePayload, existing_project_id: e.target.value || null })}>
                  <option value="">Create a new managing-farm project</option>
                  {existingProjects.filter((p) => p.customer_id === selectedLead.customer_id && ["completed", "settled"].includes(p.status)).map((p) => <option key={p.id} value={p.id}>{p.name} · {p.status}</option>)}
                </select>
              </div>
            )}

            {getNextStage(selectedLead) === "commercial_model" && (
              <div className="space-y-3 text-sm">
                <div>
                  <label className="label">Commercial Model Selection</label>
                    <select className="input" value={stagePayload.commercial_model_type || ""} onChange={(e) => setStagePayload({ ...stagePayload, commercial_model_type: e.target.value })}>
                    <option value="">-- Select commercial model --</option>
                    <option value="fixed_lease">Fixed Lease</option>
                    <option value="fixed_plus_percentage">Fixed Lease + Agreed Percentage</option>
                    <option value="percentage_share">Percentage / Revenue Share Only</option>
                  </select>
                </div>
                <div>
                  <label className="label">Percentage Settlement Base</label>
                  <select className="input" value={stagePayload.settlement_base || ""} onChange={(e) => setStagePayload({ ...stagePayload, settlement_base: e.target.value })}>
                    <option value="">-- Select settlement base --</option>
                    <option value="defined_profit">Defined Profit (after expenses)</option>
                    <option value="revenue">Gross Revenue</option>
                    <option value="net_realization">Net Realization</option>
                    <option value="defined_profit">Defined Profit</option>
                  </select>
                </div>
                <div><label className="label">Annual fixed lease total for the project (₹)</label><input type="number" min="0" className="input" onChange={(e) => setStagePayload({ ...stagePayload, fixed_lease_amount: Number(e.target.value) })} /></div>
                <div><label className="label">Landowner percentage</label><input type="number" min="0" max="100" className="input" onChange={(e) => setStagePayload({ ...stagePayload, revenue_share_percentage: Number(e.target.value) })} /></div>
                <div><label className="label">Lease term (months)</label><input type="number" min="1" className="input" onChange={(e) => setStagePayload({ ...stagePayload, lease_duration_months: Number(e.target.value) })} /></div>
                <div><label className="label">Payment frequency</label><select className="input" value={stagePayload.payment_frequency || ""} onChange={(e) => setStagePayload({ ...stagePayload, payment_frequency: e.target.value })}><option value="">-- Select frequency --</option><option value="annual">Annual</option><option value="quarterly">Quarterly</option><option value="monthly">Monthly</option></select></div>
                <div><label className="label">Landowner responsibilities</label><textarea className="input" onChange={(e) => setStagePayload({ ...stagePayload, landowner_responsibilities: e.target.value })} /></div>
                <div><label className="label">FarmCare responsibilities</label><textarea className="input" onChange={(e) => setStagePayload({ ...stagePayload, company_responsibilities: e.target.value })} /></div>
                <div><label className="label">Termination conditions</label><textarea className="input" onChange={(e) => setStagePayload({ ...stagePayload, termination_conditions: e.target.value })} /></div>
              </div>
            )}

            <div className="flex gap-3 pt-2">
              <button onClick={() => setSelectedLead(null)} className="btn-secondary flex-1 py-3">Cancel</button>
              <button onClick={() => advanceStage(selectedLead)} className="btn-primary flex-1 py-3 font-bold">Confirm & Advance</button>
            </div>
          </div>
        </div>
      )}
    </PortalPage>
  );
}
