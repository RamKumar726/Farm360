import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { FARM_EMP_NAV } from "./_nav";
import { visitsAPI } from "../../config/api";
import GPSTracker from "../../components/GPSTracker";
import ProofUploader from "../../components/ProofUploader";
import toast from "react-hot-toast";

export default function FarmEmpSubmitProof() {
  const [visits, setVisits] = useState([]);
  const [selected, setSelected] = useState("");
  const [gps, setGps] = useState(null);
  const [proofUrls, setProofUrls] = useState([]);
  const [notes, setNotes] = useState("");

  useEffect(() => { visitsAPI.list({ status: "pending" }).then((r) => { if (r.success) setVisits(r.data.items); }); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selected) return toast.error("Select a visit");
    try {
      const res = await visitsAPI.submitProof(selected, { gps_lat: gps?.lat, gps_lng: gps?.lng, proof_photos: proofUrls, notes });
      if (res.success) toast.success("Proof submitted! Visit marked as completed.");
    } catch (err) { toast.error(err?.detail || "Submission failed"); }
  };

  return (
    <PortalPage title="Submit Visit Proof" subtitle="Upload GPS-tagged photos and videos for completed visits" navItems={FARM_EMP_NAV}>
      <div className="card max-w-2xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="label">Select Visit</label>
            <select className="input" value={selected} onChange={(e) => setSelected(e.target.value)} required>
              <option value="">-- Select a pending visit --</option>
              {visits.map((v) => <option key={v.id} value={v.id}>Visit #{v.id?.slice(0, 8)} — {v.type}</option>)}
            </select>
          </div>
          <div>
            <label className="label">GPS Location (mandatory)</label>
            <GPSTracker onCapture={setGps} showMap={true} />
          </div>
          <div>
            <label className="label">Proof Photos / Videos</label>
            <ProofUploader onUpload={setProofUrls} />
          </div>
          <div>
            <label className="label">Visit Notes</label>
            <textarea className="input min-h-[80px]" placeholder="Describe what you observed..." value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>
          <button type="submit" className="btn-primary w-full">✓ Submit Proof</button>
        </form>
      </div>
    </PortalPage>
  );
}
