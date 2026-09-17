import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import { workOrdersAPI, workPartnersAPI } from "../../config/api";
import WorkOrderCard from "../../components/WorkOrderCard";
import toast from "react-hot-toast";

export default function ZoneAdminWorkManagement() {
  const [workOrders, setWorkOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    workOrdersAPI.list().then((r) => { if (r.success) setWorkOrders(r.data.items); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const handleVerify = async (id) => {
    try {
      await workOrdersAPI.verify(id);
      toast.success("Work order verified!");
      setWorkOrders((p) => p.map((w) => w.id === id ? { ...w, status: "verified" } : w));
    } catch { toast.error("Verification failed"); }
  };

  return (
    <PortalPage title="Work Management" subtitle="Assign, track, and verify all work orders" navItems={ZONE_ADMIN_NAV}>
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
    </PortalPage>
  );
}
