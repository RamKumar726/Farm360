import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { farmsAPI } from "../../config/api";
import { MapPin, Leaf, Activity } from "lucide-react";

export default function CustomerMyFarm() {
  const [farms, setFarms] = useState([]);
  const [selected, setSelected] = useState(null);
  const [cropHealth, setCropHealth] = useState(null);

  useEffect(() => { farmsAPI.list().then((r) => { if (r.success) { setFarms(r.data.items); if (r.data.items[0]) selectFarm(r.data.items[0]); } }); }, []);

  const selectFarm = async (farm) => {
    setSelected(farm);
    const ch = await farmsAPI.cropHealth(farm.id);
    if (ch.success) setCropHealth(ch.data);
  };

  return (
    <PortalPage title="My Farm" subtitle="Live farm health, crop status, and work history" navItems={CUSTOMER_NAV}>
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
