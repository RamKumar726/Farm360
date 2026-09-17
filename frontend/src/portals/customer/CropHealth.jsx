import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { prescriptionsAPI } from "../../config/api";
import StatusBadge from "../../components/StatusBadge";
import toast from "react-hot-toast";
import { Activity } from "lucide-react";

export default function CustomerCropHealth() {
  const [prescriptions, setPrescriptions] = useState([]);
  useEffect(() => { prescriptionsAPI.list().then((r) => { if (r.success) setPrescriptions(r.data.items); }); }, []);

  const acceptPrescription = async (id) => {
    try {
      await prescriptionsAPI.updateStatus(id, "accepted");
      setPrescriptions((p) => p.map((rx) => rx.id === id ? { ...rx, status: "accepted" } : rx));
      toast.success("Prescription accepted! Work order will be created.");
    } catch { toast.error("Failed"); }
  };

  const rejectPrescription = async (id) => {
    try {
      await prescriptionsAPI.updateStatus(id, "rejected");
      setPrescriptions((p) => p.map((rx) => rx.id === id ? { ...rx, status: "rejected" } : rx));
      toast.success("Prescription rejected");
    } catch { toast.error("Failed"); }
  };

  return (
    <PortalPage title="Crop Health & Prescriptions" subtitle="Review agri officer recommendations for your farm" navItems={CUSTOMER_NAV}>
      <div className="space-y-4">
        {prescriptions.map((rx) => (
          <div key={rx.id} className="card">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <Activity size={18} className="text-green-400" />
                <span className="font-semibold text-[#f0ede4] capitalize">{rx.type} Prescription</span>
              </div>
              <StatusBadge status={rx.status} />
            </div>
            <p className="text-sm text-[#8fac9a] mb-3">{rx.content}</p>
            {rx.items?.length > 0 && (
              <div className="flex gap-2 flex-wrap mb-3">
                {rx.items.map((item) => <span key={item} className="badge-muted">{item}</span>)}
              </div>
            )}
            {rx.estimated_cost && <p className="text-accent font-bold">Estimated Cost: ₹{Number(rx.estimated_cost).toLocaleString()}</p>}
            {rx.status === "pending" && (
              <div className="flex gap-3 mt-4">
                <button onClick={() => acceptPrescription(rx.id)} className="btn-primary text-sm">✓ Accept & Proceed</button>
                <button onClick={() => rejectPrescription(rx.id)} className="btn-secondary text-sm text-red-400 border-red-500/30 hover:bg-red-500/10">✗ Reject</button>
              </div>
            )}
          </div>
        ))}
        {prescriptions.length === 0 && (
          <div className="card text-center py-10">
            <Activity size={40} className="mx-auto mb-2 text-green-400 opacity-30" />
            <p className="text-[#8fac9a]">No prescriptions yet — your agri officer will add recommendations after a farm visit.</p>
          </div>
        )}
      </div>
    </PortalPage>
  );
}
