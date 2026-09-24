import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import StatusBadge from "../../components/StatusBadge";
import { workOrdersAPI, issuesAPI, apiFetch } from "../../config/api";
import { AlertOctagon, CheckCircle, XCircle, AlertTriangle, Calendar } from "lucide-react";
import toast from "react-hot-toast";

export default function ZoneAdminEscalations() {
  const [scheduleChanges, setScheduleChanges] = useState([]);
  const [issues, setIssues] = useState([]);
  const [resolveModal, setResolveModal] = useState(null); // issue to resolve
  const [resolutionText, setResolutionText] = useState("");

  const loadData = () => {
    // Load work orders that have pending schedule change requests
    workOrdersAPI.list().then((r) => {
      if (r.success) {
        setScheduleChanges(r.data.items.filter((w) => w.is_schedule_change_requested));
      }
    });
    issuesAPI.list().then((r) => {
      if (r.success) setIssues(r.data.items);
    });
  };

  useEffect(() => { loadData(); }, []);

  const handleApproveSchedule = async (woId, approved) => {
    const res = await apiFetch(`/work-orders/${woId}/approve-schedule-change?approved=${approved}`, { method: "POST" });
    if (res.success) {
      toast.success(approved ? "Schedule change approved!" : "Schedule change rejected");
      loadData();
    }
  };

  const handleResolveIssue = async () => {
    if (!resolveModal || !resolutionText) return;
    const res = await issuesAPI.resolve(resolveModal.id, resolutionText);
    if (res.success) {
      toast.success("Issue marked as resolved!");
      setResolveModal(null);
      setResolutionText("");
      loadData();
    }
  };

  const handleEscalateIssue = async (issue) => {
    const res = await issuesAPI.escalate(issue.id);
    if (res.success) {
      toast.success("Issue escalated to Founder!");
      loadData();
    }
  };

  const severityColor = (s) => {
    if (s === "critical") return "text-red-400 bg-red-500/10 border-red-500/30";
    if (s === "high") return "text-orange-400 bg-orange-500/10 border-orange-500/30";
    if (s === "medium") return "text-amber-400 bg-amber-500/10 border-amber-500/30";
    return "text-[#8fac9a] bg-white/5 border-white/10";
  };

  return (
    <PortalPage title="Escalations & Issues" subtitle="Approve schedule changes and resolve farm issues" navItems={ZONE_ADMIN_NAV}>
      <div className="space-y-8">
        {/* KPI summary */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: "Schedule Changes Pending", val: scheduleChanges.length, col: "text-amber-400" },
            { label: "Open Issues", val: issues.filter(i => i.status === "open").length, col: "text-red-400" },
            { label: "Escalated", val: issues.filter(i => i.status === "escalated").length, col: "text-orange-400" },
          ].map(kpi => (
            <div key={kpi.label} className="card text-center py-3">
              <p className={`text-2xl font-bold ${kpi.col}`}>{kpi.val}</p>
              <p className="text-xs text-[#8fac9a] mt-1">{kpi.label}</p>
            </div>
          ))}
        </div>

        {/* Pending Schedule Change Requests */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-[#f0ede4] flex items-center gap-2">
            <Calendar size={20} className="text-amber-400" /> Pending Schedule Change Requests
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {scheduleChanges.map((wo) => (
              <div key={wo.id} className="card border-amber-500/30 bg-amber-500/5 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-mono text-amber-400">WO #{wo.id.slice(0, 8)}</span>
                    <h3 className="font-semibold text-[#f0ede4] capitalize">{wo.type?.replace(/_/g, " ")}</h3>
                  </div>
                  <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-1 rounded-full">Pending Approval</span>
                </div>

                <div className="bg-white/5 rounded-xl p-3 text-sm space-y-1">
                  <p className="text-[#8fac9a]">Reason: <span className="text-[#f0ede4]">{wo.schedule_change_reason}</span></p>
                  <p className="text-[#8fac9a]">Current Date: <span className="text-[#f0ede4]">{wo.start_date}</span></p>
                  <p className="text-[#8fac9a]">Proposed Date: <span className="text-amber-400 font-semibold">{wo.proposed_date}</span></p>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => handleApproveSchedule(wo.id, false)}
                    className="btn-secondary flex-1 py-2 text-red-400 flex items-center justify-center gap-1 text-sm"
                  >
                    <XCircle size={14} /> Reject
                  </button>
                  <button
                    onClick={() => handleApproveSchedule(wo.id, true)}
                    className="btn-primary flex-1 py-2 font-bold flex items-center justify-center gap-1 text-sm"
                  >
                    <CheckCircle size={14} /> Approve Change
                  </button>
                </div>
              </div>
            ))}
            {scheduleChanges.length === 0 && (
              <p className="col-span-2 text-center text-[#8fac9a] py-6 card">No schedule changes pending</p>
            )}
          </div>
        </div>

        {/* Farm Issues & Incidents */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-[#f0ede4] flex items-center gap-2">
            <AlertOctagon size={20} className="text-red-400" /> Farm Issues & Incidents
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {issues.map((issue) => (
              <div key={issue.id} className={`card border ${severityColor(issue.severity)} space-y-3`}>
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-mono text-[#8fac9a]">#{issue.id.slice(0, 8)}</span>
                    <h3 className="font-semibold text-[#f0ede4]">{issue.title}</h3>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <StatusBadge status={issue.status} />
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-semibold capitalize ${severityColor(issue.severity)}`}>
                      {issue.severity}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-[#8fac9a]">{issue.description || "No description"}</p>

                {issue.resolution_notes && (
                  <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-3 text-xs text-emerald-400">
                    <strong>Resolution:</strong> {issue.resolution_notes}
                  </div>
                )}

                {issue.status === "open" && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEscalateIssue(issue)}
                      className="btn-secondary flex-1 py-2 text-orange-400 text-xs flex items-center justify-center gap-1"
                    >
                      <AlertTriangle size={13} /> Escalate to Founder
                    </button>
                    <button
                      onClick={() => { setResolveModal(issue); setResolutionText(""); }}
                      className="btn-primary flex-1 py-2 text-xs flex items-center justify-center gap-1 font-bold"
                    >
                      <CheckCircle size={13} /> Mark Resolved
                    </button>
                  </div>
                )}
              </div>
            ))}
            {issues.length === 0 && (
              <p className="col-span-2 text-center text-[#8fac9a] py-6 card">No issues reported yet</p>
            )}
          </div>
        </div>
      </div>

      {/* RESOLVE ISSUE MODAL */}
      {resolveModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121c17] border border-accent/30 rounded-3xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-xl font-bold text-[#f0ede4]">Resolve Issue</h3>
            <p className="text-sm text-[#8fac9a]">{resolveModal.title}</p>
            <textarea
              className="input w-full min-h-[100px]"
              placeholder="Describe how this issue was resolved..."
              value={resolutionText}
              onChange={e => setResolutionText(e.target.value)}
            />
            <div className="flex gap-3">
              <button onClick={() => setResolveModal(null)} className="btn-secondary flex-1 py-3">Cancel</button>
              <button onClick={handleResolveIssue} className="btn-primary flex-1 py-3 font-bold">Mark Resolved</button>
            </div>
          </div>
        </div>
      )}
    </PortalPage>
  );
}
