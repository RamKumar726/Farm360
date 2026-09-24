import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { FARM_EMP_NAV } from "./_nav";
import { visitsAPI, workOrdersAPI, apiFetch } from "../../config/api";
import GPSTracker from "../../components/GPSTracker";
import ProofUploader from "../../components/ProofUploader";
import toast from "react-hot-toast";

export default function FarmEmpSubmitProof() {
  const [visits, setVisits] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);
  const [mode, setMode] = useState("work_order"); // work_order or visit
  const [selected, setSelected] = useState("");
  const [gps, setGps] = useState(null);
  const [proofUrls, setProofUrls] = useState([]);
  const [notes, setNotes] = useState("");
  const [starting, setStarting] = useState(false);
  const selectedWorkOrder = workOrders.find((work) => work.id === selected);

  const refreshWorkOrders = () => workOrdersAPI.list().then((r) => {
    if (r.success) setWorkOrders(r.data.items.filter((w) => ["assigned", "in_progress"].includes(w.status)));
  });

  useEffect(() => {
    visitsAPI.list({ status: "pending" }).then((r) => { if (r.success) setVisits(r.data.items); });
    refreshWorkOrders();
  }, []);

  const startWork = async () => {
    setStarting(true);
    try {
      await workOrdersAPI.updateStatus(selected, { status: "in_progress" });
      await refreshWorkOrders();
      toast.success("Work marked in progress");
    } catch (error) {
      toast.error(error?.response?.data?.detail || error?.detail || "Could not start this work order");
    } finally { setStarting(false); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selected) return toast.error("Select an item to submit proof for");

    if (mode === "work_order") {
      const res = await apiFetch(`/work-orders/${selected}/submit-proof`, {
        method: "POST",
        body: JSON.stringify({ proof_urls: proofUrls, notes }),
      });
      if (res.success) {
        toast.success("Proof of work submitted! Sent to employee for verification.");
        setSelected(""); setProofUrls([]); setNotes("");
        refreshWorkOrders();
      } else toast.error("Failed to submit proof");
    } else {
      try {
        const res = await visitsAPI.submitProof(selected, { gps_lat: gps?.lat, gps_lng: gps?.lng, proof_photos: proofUrls, notes });
        if (res.success) toast.success("Proof submitted! Visit marked as completed.");
      } catch (err) { toast.error(err?.detail || "Submission failed"); }
    }
  };

  return (
    <PortalPage title="Submit Work & Visit Proof" subtitle="Upload GPS-tagged photos and proof for assigned tasks" navItems={FARM_EMP_NAV}>
      <div className="card max-w-2xl">
        <div className="flex gap-2 border-b border-white/10 pb-4 mb-6">
          <button type="button" onClick={() => { setMode("work_order"); setSelected(""); }} className={`px-4 py-2 rounded-xl text-sm font-semibold ${mode === "work_order" ? "bg-accent text-primary-900 font-bold" : "bg-white/5 text-[#8fac9a]"}`}>
            🚜 Field Work Orders ({workOrders.length})
          </button>
          <button type="button" onClick={() => { setMode("visit"); setSelected(""); }} className={`px-4 py-2 rounded-xl text-sm font-semibold ${mode === "visit" ? "bg-accent text-primary-900 font-bold" : "bg-white/5 text-[#8fac9a]"}`}>
            🚗 Farm Visits ({visits.length})
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="label">Select {mode === "work_order" ? "Work Order" : "Visit"}</label>
            <select className="input" value={selected} onChange={(e) => setSelected(e.target.value)} required>
              <option value="">-- Select {mode === "work_order" ? "Work Order" : "Visit"} --</option>
              {mode === "work_order" ? (
                workOrders.map((w) => <option key={w.id} value={w.id}>Work Order #{w.id?.slice(0, 8)} — {w.type?.replace("_", " ")} ({w.start_date || "No date"})</option>)
              ) : (
                visits.map((v) => <option key={v.id} value={v.id}>Visit #{v.id?.slice(0, 8)} — {v.type}</option>)
              )}
            </select>
          </div>

          {mode === "work_order" && selectedWorkOrder?.status === "assigned" && <button type="button" disabled={starting} onClick={startWork} className="btn-secondary w-full">{starting ? "Starting…" : "Start Work"}</button>}
          {mode === "work_order" && selectedWorkOrder?.status === "in_progress" && <p className="text-sm text-emerald-300">Work in progress{selectedWorkOrder.started_at ? ` since ${new Date(selectedWorkOrder.started_at).toLocaleString()}` : ""}. Submit proof when finished.</p>}

          <div>
            <label className="label">GPS Location (mandatory)</label>
            <GPSTracker onCapture={setGps} showMap={true} />
          </div>

          <div>
            <label className="label">Proof Photos / Video Links</label>
            <ProofUploader onUpload={setProofUrls} />
          </div>

          <div>
            <label className="label">Field Work Notes</label>
            <textarea className="input min-h-[80px]" placeholder="Describe work completed on site..." value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>

          <button type="submit" disabled={mode === "work_order" && selectedWorkOrder?.status !== "in_progress"} className="btn-primary w-full font-bold disabled:opacity-50">✓ Submit Proof of Work</button>
        </form>
      </div>
    </PortalPage>
  );
}
