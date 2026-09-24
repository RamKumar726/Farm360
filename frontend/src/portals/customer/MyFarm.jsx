import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { farmsAPI, projectsAPI, leadsAPI } from "../../config/api";
import { MapPin, Leaf, Activity } from "lucide-react";

export default function CustomerMyFarm() {
  const [farms, setFarms] = useState([]);
  const [selected, setSelected] = useState(null);
  const [cropHealth, setCropHealth] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [requesting, setRequesting] = useState(false);
  const [requestMessage, setRequestMessage] = useState("");
  const [farmRequest, setFarmRequest] = useState({ location: "", area: "", crop_name: "" });

  useEffect(() => {
    farmsAPI.list().then((r) => { if (r.success) { setFarms(r.data.items); if (r.data.items[0]) selectFarm(r.data.items[0]); } }).catch(() => {});
    projectsAPI.list().then((r) => { if (r.success) setProjects(r.data.items || []); }).catch(() => {});
  }, []);

  const requestFarmManagement = async () => {
    setRequesting(true);
    setRequestMessage("");
    try {
      const project = projects.find((item) => item.id === selectedProjectId);
      const result = await leadsAPI.create({
        type: "farm_management",
        source: "customer_app",
        is_opportunity: true,
        existing_project_id: selectedProjectId || null,
        crop_name: farmRequest.crop_name || project?.crop_name || selected?.current_crop || null,
        farm_location: farmRequest.location || selected?.location || null,
        farm_area: farmRequest.area ? Number(farmRequest.area) : selected?.area || null,
        farm_details: `Customer requested subscription farm management${project ? ` for project ${project.name}` : "; existing project not selected"}. Location: ${farmRequest.location || selected?.location || "to be confirmed"}; area: ${farmRequest.area || selected?.area || "to be confirmed"} acres; crop: ${farmRequest.crop_name || project?.crop_name || selected?.current_crop || "to be confirmed"}.`,
      });
      if (!result?.success) throw new Error(result?.message || "Request could not be created");
      setRequestMessage("Your farm management request was sent. Our team will contact you to prepare the service plan and quotation.");
    } catch (error) {
      setRequestMessage(error?.message || error?.detail || "Could not submit your request. Please try again.");
    } finally {
      setRequesting(false);
    }
  };

  const selectFarm = async (farm) => {
    setSelected(farm);
    const ch = await farmsAPI.cropHealth(farm.id);
    if (ch.success) setCropHealth(ch.data);
  };

  return (
    <PortalPage title="My Farm" subtitle="Live farm health, crop status, and work history" navItems={CUSTOMER_NAV}>
      <section className="card mb-6 space-y-3">
        <div>
          <h2 className="section-title">Manage My Farm</h2>
          <p className="text-sm text-[#8fac9a]">Request ongoing farm management. Your request will enter the team’s lead and quotation workflow.</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <select className="input flex-1" value={selectedProjectId} onChange={(e) => setSelectedProjectId(e.target.value)}>
            <option value="">Choose an existing project (optional)</option>
            {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
          </select>
          <button className="btn-primary" onClick={requestFarmManagement} disabled={requesting}>
            {requesting ? "Sending…" : "Request Farm Management"}
          </button>
        </div>
        <div className="grid sm:grid-cols-3 gap-3">
          <input className="input" placeholder="Farm location" value={farmRequest.location} onChange={(e) => setFarmRequest({ ...farmRequest, location: e.target.value })} />
          <input className="input" type="number" min="0.01" step="any" placeholder="Area in acres" value={farmRequest.area} onChange={(e) => setFarmRequest({ ...farmRequest, area: e.target.value })} />
          <input className="input" placeholder="Current or planned crop" value={farmRequest.crop_name} onChange={(e) => setFarmRequest({ ...farmRequest, crop_name: e.target.value })} />
        </div>
        {requestMessage && <p className="text-sm text-accent" role="status">{requestMessage}</p>}
      </section>
      <div className="grid md:grid-cols-3 gap-6">
        {/* Farm selector */}
        <div className="space-y-3">
          <h2 className="section-title">Your Farms</h2>
          {farms.map((f) => (
            <div key={f.id} onClick={() => selectFarm(f)}
              className={`card cursor-pointer transition-all ${selected?.id === f.id ? "border-accent" : ""}`}>
              <div className="flex items-center gap-3">
                <Leaf className="text-green-400" size={20} />
                <div>
                  <p className="font-semibold text-[#f0ede4]">{f.location || `Farm #${f.id?.slice(0, 8)}`}</p>
                  <p className="text-xs text-[#8fac9a]">{f.area} acres</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Farm details */}
        {selected && (
          <div className="md:col-span-2 space-y-4">
            <div className="card">
              <h2 className="section-title">Farm Details</h2>
              <div className="grid grid-cols-2 gap-4">
                {[
                  ["Location", selected.location], ["Area", `${selected.area} acres`],
                  ["Soil Type", selected.soil_type], ["Irrigation", selected.irrigation_type],
                  ["Current Crop", selected.current_crop || "None"], ["Zone", selected.zone_id?.slice(0, 8)],
                ].map(([label, value]) => (
                  <div key={label}>
                    <p className="text-xs text-[#8fac9a]">{label}</p>
                    <p className="text-sm font-medium text-[#f0ede4]">{value || "—"}</p>
                  </div>
                ))}
              </div>
              {selected.gps_lat && (
                <div className="mt-4 flex items-center gap-2 text-sm text-[#8fac9a]">
                  <MapPin size={14} className="text-accent" />
                  <span className="font-mono">{selected.gps_lat}, {selected.gps_lng}</span>
                </div>
              )}
            </div>
            {cropHealth && (
              <div className="card">
                <h2 className="section-title flex items-center gap-2"><Activity size={18} className="text-green-400" /> Crop Health</h2>
                <p className="text-[#8fac9a] text-sm">{JSON.stringify(cropHealth, null, 2)}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </PortalPage>
  );
}
