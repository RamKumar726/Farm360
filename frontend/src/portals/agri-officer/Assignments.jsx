import PortalPage from "../../components/PortalPage";
import { AGRI_NAV } from "./_nav";
import { apiFetch, workOrdersAPI } from "../../config/api";
import { useState, useEffect } from "react";
import StatusBadge from "../../components/StatusBadge";
import { FileText, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import ProofUploader from "../../components/ProofUploader";

export default function AgriAssignments() {
  const [assignedLeads, setAssignedLeads] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);

  // Quotation Modal
  const [activeLead, setActiveLead] = useState(null);
  const [activeFeasibilityLead, setActiveFeasibilityLead] = useState(null);
  const [feasibilityReport, setFeasibilityReport] = useState("");
  const [servicesNeeded, setServicesNeeded] = useState("");
  const [priceToComplete, setPriceToComplete] = useState("");
  const [solutionSummary, setSolutionSummary] = useState("");

  // Schedule Change Modal
  const [activeWO, setActiveWO] = useState(null);
  const [changeReason, setChangeReason] = useState("");
  const [proposedDate, setProposedDate] = useState("");
  const [activeProofWO, setActiveProofWO] = useState(null);
  const [proofUrls, setProofUrls] = useState([]);
  const [proofNotes, setProofNotes] = useState("");

  const loadData = () => {
    apiFetch("/leads").then((r) => { if (r.success) setAssignedLeads(r.data.items); });
    workOrdersAPI.list().then((r) => { if (r.success) setWorkOrders(r.data.items); });
  };

  useEffect(() => { loadData(); }, []);

  const handleSubmitQuotation = async () => {
    if (!activeLead || !priceToComplete) return;
    const payload = {
      services_needed: servicesNeeded,
      price_to_complete: Number(priceToComplete),
      solution_summary: solutionSummary,
    };
    const res = await apiFetch(`/leads/${activeLead.id}/ao-quotation`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (res.success) {
      alert("Solution and quotation document submitted to employee for review!");
      setActiveLead(null);
      loadData();
    }
  };

  const handleSubmitFeasibility = async () => {
    if (!activeFeasibilityLead || !feasibilityReport.trim()) return;
    try {
      const res = await apiFetch(`/leads/${activeFeasibilityLead.id}/ao-feasibility`, {
        method: "POST", body: JSON.stringify({ report: feasibilityReport }),
      });
      if (res.success) {
        alert("Lease feasibility report submitted to the project team.");
        setActiveFeasibilityLead(null); setFeasibilityReport(""); loadData();
      }
    } catch (error) { alert(error?.response?.data?.detail || error?.detail || "Could not submit the feasibility report"); }
  };

  const handleRequestScheduleChange = async () => {
    if (!activeWO || !changeReason || !proposedDate) return;
    const res = await apiFetch(`/work-orders/${activeWO.id}/request-schedule-change?reason=${encodeURIComponent(changeReason)}&proposed_date=${proposedDate}`, {
      method: "POST",
    });
    if (res.success) {
      alert("Urgent schedule change requested! Sent to Zone Admin for approval.");
      setActiveWO(null);
      loadData();
    }
  };

  const startAOVisit = async (wo) => {
    try {
      await workOrdersAPI.updateStatus(wo.id, { status: "in_progress" });
      loadData();
    } catch (error) { alert(error?.response?.data?.detail || error?.detail || "Could not start this visit"); }
  };

  const submitAOProof = async () => {
    if (!activeProofWO || !proofUrls.length) return;
    try {
      await apiFetch(`/work-orders/${activeProofWO.id}/submit-proof`, {
        method: "POST", body: JSON.stringify({ proof_urls: proofUrls, notes: proofNotes }),
      });
      setActiveProofWO(null); setProofUrls([]); setProofNotes(""); loadData();
    } catch (error) { alert(error?.response?.data?.detail || error?.detail || "Could not submit visit proof"); }
  };

  return (
    <PortalPage title="Agri Officer Tasks & Assignments" subtitle="Review incoming lead requests, prepare feasibility reports, and manage schedule changes" navItems={AGRI_NAV}>
      <div className="space-y-8">
        {/* Incoming Lead Request Tasks */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-[#f0ede4]">📋 Assigned Lead & Service Requests</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {assignedLeads.map((lead) => (
              <div key={lead.id} className="card border-white/10 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-mono text-accent">#{lead.id.slice(0, 8)}</span>
                    <h3 className="font-semibold text-[#143628] capitalize">{lead.type.replace("_", " ")}</h3>
                  </div>
                  <StatusBadge status={lead.status} />
                </div>

                <p className="text-sm text-[#4a5850]">{lead.farm_details || "No details specified"}</p>

                {lead.qualification_data && (
                  <div className="bg-[#fbf9f4] p-3 rounded-xl text-xs space-y-1 text-[#4a5850]">
                    <p className="font-semibold text-[#143628]">Qualification Details:</p>
                    <p>{lead.qualification_data}</p>
                  </div>
                )}

                {lead.need_analysis_data && (
                  <div className="bg-[#fbf9f4] p-3 rounded-xl text-xs space-y-1 text-[#4a5850]">
                    <p className="font-semibold text-[#143628]">Need Analysis Details:</p>
                    <p>{lead.need_analysis_data}</p>
                  </div>
                )}

                {lead.land_verification_data && <div className="bg-[#fbf9f4] p-3 rounded-xl text-xs text-[#4a5850]"><p className="font-semibold text-[#143628]">Land verification</p><p className="whitespace-pre-wrap">{lead.land_verification_data}</p></div>}
                {lead.type === "farm_lease" && lead.status === "feasibility" && (
                  <button onClick={() => { setActiveFeasibilityLead(lead); setFeasibilityReport(lead.ao_feasibility_data || ""); }} className="btn-primary w-full mt-2 flex items-center justify-center gap-2 font-bold text-sm"><FileText size={16} /> Submit Lease Feasibility</button>
                )}

                {lead.status === "decision_makers" && lead.type !== "farm_lease" && <button onClick={() => {
                  setActiveLead(lead);
                  setServicesNeeded(lead.services_needed || "");
                  setPriceToComplete(lead.price_to_complete || "");
                  setSolutionSummary("");
                }} className="btn-primary w-full mt-2 flex items-center justify-center gap-2 font-bold text-sm">
                  <FileText size={16} /> Submit Solution & Quotation
                </button>}
              </div>
            ))}
            {assignedLeads.length === 0 && <p className="col-span-2 text-center text-[#8fac9a] py-10">No pending lead tasks assigned</p>}
          </div>
        </div>

        {/* Active Work Orders & Schedule Change Requests */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-[#f0ede4]">🚜 Active Work Orders</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workOrders.map((wo) => (
              <div key={wo.id} className="card space-y-3">
                <div className="flex justify-between items-start">
                  <span className="font-semibold text-[#f0ede4] capitalize">{wo.type?.replace("_", " ")}</span>
                  <StatusBadge status={wo.status} />
                </div>
                <p className="text-xs text-[#8fac9a]">{wo.notes}</p>
                <p className="text-xs text-[#8fac9a]">Scheduled Date: {wo.start_date || "TBD"}</p>
                {wo.type === "monitoring" && wo.status === "assigned" && <button onClick={() => startAOVisit(wo)} className="btn-secondary w-full">Start Agriculture Officer Visit</button>}
                {wo.type === "monitoring" && wo.status === "in_progress" && <button onClick={() => setActiveProofWO(wo)} className="btn-primary w-full">Submit Visit Proof</button>}

                {wo.is_schedule_change_requested && (
                  <div className="bg-amber-500/10 border border-amber-500/30 p-3 rounded-xl text-xs text-amber-400 space-y-1">
                    <p className="font-bold flex items-center gap-1"><AlertTriangle size={14} /> Schedule Change Pending Approval</p>
                    <p>Reason: {wo.schedule_change_reason}</p>
                    <p>Proposed: {wo.proposed_date}</p>
                  </div>
                )}

                {!wo.is_schedule_change_requested && (
                  <button onClick={() => { setActiveWO(wo); setChangeReason(""); setProposedDate(""); }} className="btn-secondary w-full text-xs font-semibold flex items-center justify-center gap-2">
                    <AlertTriangle size={14} /> Request Urgent Schedule Change
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SUBMIT SOLUTION & QUOTATION MODAL */}
      {activeLead && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121c17] border border-accent/30 rounded-3xl p-6 max-w-lg w-full space-y-4 text-left">
            <h3 className="text-xl font-bold text-[#f0ede4]">Comprehensive Solution & Quotation Document</h3>
            <p className="text-xs text-[#8fac9a]">Submit proposed services and price to complete for Lead #{activeLead.id?.slice(0, 8)}</p>

            <div className="space-y-3 text-sm">
              <div>
                <label className="block text-xs text-[#8fac9a] uppercase font-semibold mb-1">Services Needed</label>
                <input
                  type="text"
                  placeholder="e.g. Borewell drilling, Soil testing, Drip irrigation, Fencing"
                  value={servicesNeeded}
                  onChange={(e) => setServicesNeeded(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-[#f0ede4] outline-none"
                />
              </div>

              <div>
                <label className="block text-xs text-[#8fac9a] uppercase font-semibold mb-1">Price to Complete (₹)</label>
                <input
                  type="number"
                  placeholder="e.g. 150000"
                  value={priceToComplete}
                  onChange={(e) => setPriceToComplete(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-accent font-bold outline-none"
                />
              </div>

              <div>
                <label className="block text-xs text-[#8fac9a] uppercase font-semibold mb-1">Solution Summary & Feasibility Notes</label>
                <textarea
                  rows={4}
                  placeholder="Detailed feasibility summary, site observations, estimated timeline..."
                  value={solutionSummary}
                  onChange={(e) => setSolutionSummary(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-[#f0ede4] outline-none resize-none"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button onClick={() => setActiveLead(null)} className="btn-secondary flex-1 py-3">Cancel</button>
              <button onClick={handleSubmitQuotation} className="btn-primary flex-1 py-3 font-bold">Submit Document</button>
            </div>
          </div>
        </div>
      )}

      {activeFeasibilityLead && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121c17] border border-accent/30 rounded-3xl p-6 max-w-2xl w-full space-y-4">
            <h3 className="text-xl font-bold text-[#f0ede4]">Lease agriculture feasibility report</h3>
            <p className="text-xs text-[#8fac9a]">{activeFeasibilityLead.farm_details}</p>
            <p className="text-xs text-[#8fac9a]">Include suitability, possible crops and crop duration, water requirement, expected operations and expenses, possible harvest/revenue, risks, and recommended crop/farm plan.</p>
            <textarea className="input min-h-56" value={feasibilityReport} onChange={(e) => setFeasibilityReport(e.target.value)} required />
            <div className="flex gap-3"><button className="btn-secondary flex-1" onClick={() => setActiveFeasibilityLead(null)}>Cancel</button><button className="btn-primary flex-1" disabled={!feasibilityReport.trim()} onClick={handleSubmitFeasibility}>Submit Report</button></div>
          </div>
        </div>
      )}

      {activeProofWO && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
          <div className="card max-w-xl w-full space-y-4">
            <h3 className="text-xl font-bold">Agriculture Officer Visit Proof</h3>
            <ProofUploader onUpload={setProofUrls} />
            <textarea className="input min-h-24" placeholder="Visit findings and recommendations" value={proofNotes} onChange={(event) => setProofNotes(event.target.value)} />
            <div className="flex gap-3"><button className="btn-secondary flex-1" onClick={() => setActiveProofWO(null)}>Cancel</button><button className="btn-primary flex-1" disabled={!proofUrls.length} onClick={submitAOProof}>Submit proof</button></div>
          </div>
        </div>
      )}

      {/* REQUEST URGENT SCHEDULE CHANGE MODAL */}
      {activeWO && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121c17] border border-amber-500/30 rounded-3xl p-6 max-w-md w-full space-y-4 text-left">
            <h3 className="text-xl font-bold text-[#f0ede4]">Request Urgent Schedule Change</h3>
            <p className="text-xs text-[#8fac9a]">Identify problem on site and propose date change for Zone Admin approval</p>

            <div className="space-y-3 text-sm">
              <div>
                <label className="block text-xs text-[#8fac9a] uppercase font-semibold mb-1">Reason & Recommendation</label>
                <textarea
                  rows={3}
                  placeholder="e.g. Urgent fertilizer application required due to pest indication..."
                  value={changeReason}
                  onChange={(e) => setChangeReason(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-[#f0ede4] outline-none resize-none"
                />
              </div>

              <div>
                <label className="block text-xs text-[#8fac9a] uppercase font-semibold mb-1">Proposed Work Date</label>
                <input
                  type="date"
                  value={proposedDate}
                  onChange={(e) => setProposedDate(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-[#f0ede4] outline-none"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button onClick={() => setActiveWO(null)} className="btn-secondary flex-1 py-3">Cancel</button>
              <button onClick={handleRequestScheduleChange} className="btn-primary flex-1 py-3 font-bold">Send Request</button>
            </div>
          </div>
        </div>
      )}
    </PortalPage>
  );
}
