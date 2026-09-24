import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import { workOrdersAPI, apiFetch } from "../../config/api";
import WorkOrderCard from "../../components/WorkOrderCard";
import toast from "react-hot-toast";
import { AlertTriangle, Check, X } from "lucide-react";

export default function ZoneAdminWorkManagement() {
  const [workOrders, setWorkOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = () => {
    workOrdersAPI.list().then((r) => { if (r.success) setWorkOrders(r.data.items); setLoading(false); }).catch(() => setLoading(false));
  };

  useEffect(() => { loadData(); }, []);

  const handleVerify = async (id) => {
    try {
      await workOrdersAPI.verify(id);
      toast.success("Work order verified!");
      loadData();
    } catch { toast.error("Verification failed"); }
  };

  const handleApproveScheduleChange = async (id, approved) => {
    const res = await apiFetch(`/work-orders/${id}/approve-schedule-change?approved=${approved}`, { method: "POST" });
    if (res.success) {
      toast.success(approved ? "Urgent schedule change approved!" : "Schedule change rejected");
      loadData();
    }
  };

  const pendingScheduleChanges = workOrders.filter(w => w.is_schedule_change_requested);

  return (
    <PortalPage title="Work Management & Approvals" subtitle="Assign, track, verify work orders and approve urgent schedule changes" navItems={ZONE_ADMIN_NAV}>
      <div className="space-y-8">
        {/* Urgent Schedule Change Requests Queue */}
        {pendingScheduleChanges.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-[#f0ede4] flex items-center gap-2 text-amber-400">
              <AlertTriangle size={20} /> Urgent Schedule Change Requests ({pendingScheduleChanges.length})
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {pendingScheduleChanges.map((wo) => (
                <div key={wo.id} className="card border-amber-500/30 space-y-3">
                  <div className="flex justify-between items-start">
                    <span className="font-bold text-[#f0ede4] capitalize">{wo.type?.replace("_", " ")}</span>
                    <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-1 rounded-full font-semibold">Schedule Approval Required</span>
                  </div>
                  <div className="bg-white/5 p-3 rounded-xl text-xs space-y-1 text-[#8fac9a]">
                    <p className="font-semibold text-[#f0ede4]">Reason & Recommendation:</p>
                    <p>{wo.schedule_change_reason}</p>
                    <p className="text-amber-400 font-bold mt-1">Proposed New Date: {wo.proposed_date}</p>
                  </div>
                  <div className="flex gap-3 pt-1">
                    <button onClick={() => handleApproveScheduleChange(wo.id, false)} className="btn-secondary flex-1 py-2 text-red-400 text-xs font-semibold flex items-center justify-center gap-1">
                      <X size={14} /> Reject
                    </button>
                    <button onClick={() => handleApproveScheduleChange(wo.id, true)} className="btn-primary flex-1 py-2 text-xs font-bold flex items-center justify-center gap-1">
                      <Check size={14} /> Approve Schedule Change
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* All Work Orders */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-[#f0ede4]">🚜 Zone Work Orders</h2>
          {loading ? <p className="text-[#8fac9a] text-center py-8">Loading...</p> : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {workOrders.map((w) => (
                <div key={w.id}>
                  <WorkOrderCard workOrder={w} />
                  {w.status === "in_progress" && (
                    <button onClick={() => handleVerify(w.id)} className="btn-secondary w-full mt-2 text-sm">✓ Verify Work</button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </PortalPage>
  );
}
