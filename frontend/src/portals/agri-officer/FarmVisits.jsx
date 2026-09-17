import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { AGRI_NAV } from "./_nav";
import { visitsAPI } from "../../config/api";
import VisitCard from "../../components/VisitCard";
import GPSTracker from "../../components/GPSTracker";
import ProofUploader from "../../components/ProofUploader";
import toast from "react-hot-toast";
import { Plus } from "lucide-react";

export default function AgriFarmVisits() {
  const [visits, setVisits] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ farm_id: "", type: "assign_visit", notes: "" });
  const [gps, setGps] = useState(null);
  const [proofUrls, setProofUrls] = useState([]);

  useEffect(() => { visitsAPI.list().then((r) => { if (r.success) setVisits(r.data.items); }); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await visitsAPI.create({ ...form, gps_lat: gps?.lat, gps_lng: gps?.lng, proof_photos: proofUrls });
      if (res.success) { setVisits((p) => [res.data, ...p]); setShowForm(false); toast.success("Visit logged!"); }
    } catch { toast.error("Failed"); }
  };

  return (
    <PortalPage title="Farm Visits" subtitle="Log and submit proof for farm visits" navItems={AGRI_NAV}>
      <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}><Plus size={16} /> Log Visit</button>
      {showForm && (
        <div className="card animate-slide-up space-y-4">
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div><label className="label">Farm ID</label><input className="input" value={form.farm_id} onChange={(e) => setForm({ ...form, farm_id: e.target.value })} required /></div>
              <div>
                <label className="label">Visit Type</label>
                <select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                  <option value="assign_visit">Assigned Visit</option>
                  <option value="random_visit">Random Visit</option>
                  <option value="sale_visit">Sale Visit</option>
                </select>
              </div>
              <div className="md:col-span-2"><label className="label">Notes</label><textarea className="input min-h-[80px]" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
            </div>
            <div>
              <label className="label">GPS Location</label>
              <GPSTracker onCapture={setGps} showMap={true} />
            </div>
            <div>
              <label className="label">Proof Photos/Videos</label>
              <ProofUploader onUpload={setProofUrls} />
            </div>
            <div className="flex gap-3">
              <button type="submit" className="btn-primary">Log Visit</button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {visits.map((v) => <VisitCard key={v.id} visit={v} />)}
      </div>
    </PortalPage>
  );
}
