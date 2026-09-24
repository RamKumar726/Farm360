import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import WorkOrderCard from "../../components/WorkOrderCard";
import { workOrdersAPI, apiFetch, issuesAPI, projectsAPI } from "../../config/api";
import { CheckCircle2, CreditCard, Clock, Camera } from "lucide-react";
import StatusBadge from "../../components/StatusBadge";

export default function CustomerWorkDetails() {
  const navigate = useNavigate();
  const [workOrders, setWorkOrders] = useState([]);
  const [serviceLeads, setServiceLeads] = useState([]);
  const [issues, setIssues] = useState([]);
  const [projects, setProjects] = useState([]);
  const [issueDraft, setIssueDraft] = useState({ project_id: "", title: "", description: "", severity: "medium" });
  const [savingIssue, setSavingIssue] = useState(false);

  const loadData = () => {
    workOrdersAPI.list().then((r) => { if (r.success) setWorkOrders(r.data.items); });
    apiFetch("/leads").then((r) => { if (r.success) setServiceLeads(r.data.items); });
    issuesAPI.list().then((r) => { if (r.success) setIssues(r.data.items || []); });
    projectsAPI.list().then((r) => { if (r.success) setProjects(r.data.items || []); });
  };

  useEffect(() => { loadData(); }, []);

  const handlePayQuotation = () => navigate("/customer/payments");

  const handleAcceptWork = async (woId) => {
    const res = await apiFetch(`/work-orders/${woId}/accept-work`, { method: "POST" });
    if (res.success) {
      alert("Thank you! You have accepted work completion. Ticket closed.");
      loadData();
    }
  };

  const submitIssue = async (event) => {
    event.preventDefault();
    setSavingIssue(true);
    try {
      await issuesAPI.create({ ...issueDraft, project_id: issueDraft.project_id || null });
      setIssueDraft({ project_id: "", title: "", description: "", severity: "medium" });
      const result = await issuesAPI.list();
      if (result.success) setIssues(result.data.items || []);
    } catch (error) {
      alert(error?.response?.data?.detail || error?.detail || "Could not submit issue");
    } finally { setSavingIssue(false); }
  };

  return (
    <PortalPage title="Work Details & Service Requests" subtitle="Track estimations, quotations, work progress & proof of work" navItems={CUSTOMER_NAV}>
      <div className="space-y-8">
        {/* Service Requests & Quotations Section */}
        {serviceLeads.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-[#f0ede4]">📋 Active Service Enquiries</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {serviceLeads.map((lead) => {
                let quote = null;
                try { if (lead.ao_quotation_doc) quote = JSON.parse(lead.ao_quotation_doc); } catch (e) {}

                return (
                  <div key={lead.id} className="card border-white/10 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-xs font-mono text-accent">#{lead.id.slice(0, 8)}</span>
                        <h3 className="font-semibold text-[#143628] capitalize">{lead.type.replace("_", " ")}</h3>
                      </div>
                      <StatusBadge status={lead.status} />
                    </div>

                    <p className="text-sm text-[#4a5850]">{lead.farm_details}</p>

                    {lead.status === "decision_makers" && (
                      <div className="bg-[#efe7d2] p-3 rounded-xl flex items-center gap-2 text-xs text-[#6f5316]">
                        <Clock size={16} className="animate-pulse" />
                        <span>Work is assigned to Agriculture Office, wait for estimation & quotation...</span>
                      </div>
                    )}

                    {lead.sent_to_client && quote && (
                      <div className="bg-[#efe7d2] border border-accent/40 p-4 rounded-xl space-y-2 text-sm text-[#1f2824]">
                        <div className="flex justify-between font-bold text-[#143628]">
                          <span>Quotation Estimate:</span>
                          <span className="text-accent text-lg">₹{Number(lead.final_amount || lead.price_to_complete || quote.price_to_complete || 0).toLocaleString()}</span>
                        </div>
                        {quote.solution_summary && <p className="text-xs text-[#4a5850]">{quote.solution_summary}</p>}

                        {lead.status === "payment" && !lead.payment_confirmed_at && (
                          <button onClick={() => handlePayQuotation(lead.id)} className="btn-primary w-full mt-2 flex items-center justify-center gap-2 font-bold">
                            <CreditCard size={18} /> Pay Now & Confirm Work
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Work Orders & Proof of Work Section */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-[#f0ede4]">🚜 Field Work Orders & Execution</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workOrders.map((w) => (
              <div key={w.id} className="card space-y-3 flex flex-col justify-between">
                <div>
                  <WorkOrderCard workOrder={w} />

                  {/* Proof of Work display */}
                  {w.proof_urls && (
                    <div className="bg-white/5 p-3 rounded-xl space-y-2 mt-3 text-xs">
                      <div className="flex items-center gap-2 text-accent font-semibold">
                        <Camera size={16} /> Proof of Work Submitted:
                      </div>
                      <p className="text-[#8fac9a] break-all">{w.proof_urls}</p>

                      {w.is_verified_by_employee && !w.is_accepted_by_customer && (
                        <button onClick={() => handleAcceptWork(w.id)} className="btn-primary w-full mt-3 flex items-center justify-center gap-2 font-bold text-xs">
                          <CheckCircle2 size={16} /> Accept to Close Work
                        </button>
                      )}

                      {w.is_accepted_by_customer && (
                        <div className="bg-accent/20 p-2 rounded-lg text-accent font-bold text-center">
                          ✓ Work accepted · awaiting employee closure
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {workOrders.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No active work orders</p>}
          </div>
        </div>

        <section className="card space-y-4">
          <div><h2 className="section-title">Project issues</h2><p className="text-sm text-[#8fac9a]">Report a problem against one of your projects and follow its resolution status.</p></div>
          <form className="grid md:grid-cols-2 gap-3" onSubmit={submitIssue}>
            <select className="input" value={issueDraft.project_id} onChange={(e) => setIssueDraft({ ...issueDraft, project_id: e.target.value })} required>
              <option value="">Select your project</option>{projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
            <select className="input" value={issueDraft.severity} onChange={(e) => setIssueDraft({ ...issueDraft, severity: e.target.value })}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select>
            <input className="input" placeholder="Issue title" value={issueDraft.title} onChange={(e) => setIssueDraft({ ...issueDraft, title: e.target.value })} required />
            <textarea className="input" placeholder="Describe the issue" value={issueDraft.description} onChange={(e) => setIssueDraft({ ...issueDraft, description: e.target.value })} />
            <button className="btn-primary md:col-span-2" disabled={savingIssue || projects.length === 0}>{savingIssue ? "Sending…" : "Raise issue"}</button>
          </form>
          <div className="space-y-2">{issues.map((issue) => <article key={issue.id} className="rounded-lg border border-white/10 p-3 flex justify-between gap-3 text-sm"><span>{issue.title}</span><span className="text-[#8fac9a] capitalize">{issue.severity} · {issue.status.replaceAll("_", " ")}</span></article>)}{issues.length === 0 && <p className="text-sm text-[#8fac9a]">No project issues have been raised.</p>}</div>
        </section>
      </div>
    </PortalPage>
  );
}
