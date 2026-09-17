import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import { landSalesAPI } from "../../config/api";
import StatusBadge from "../../components/StatusBadge";
import { MapPin, Plus } from "lucide-react";
import toast from "react-hot-toast";

export default function CustomerLandSale() {
  const [listings, setListings] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ land_type: "agricultural", area: "", location: "", facing: "", listed_price: "", description: "" });

  useEffect(() => { landSalesAPI.list().then((r) => { if (r.success) setListings(r.data.items); }); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await landSalesAPI.create({ ...form, area: parseFloat(form.area), listed_price: parseFloat(form.listed_price) });
      if (res.success) { setListings((p) => [res.data, ...p]); setShowForm(false); toast.success("Land listing submitted for review!"); }
    } catch { toast.error("Failed"); }
  };

  return (
    <PortalPage title="Land Sale" subtitle="List your land for sale through our broker network" navItems={CUSTOMER_NAV}>
      <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(!showForm)}><Plus size={16} /> List Your Land</button>

      {showForm && (
        <div className="card animate-slide-up">
          <form onSubmit={handleCreate} className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="label">Land Type</label>
              <select className="input" value={form.land_type} onChange={(e) => setForm({ ...form, land_type: e.target.value })}>
                <option value="agricultural">Agricultural</option>
                <option value="residential">Residential</option>
                <option value="commercial">Commercial</option>
                <option value="farm_plot">Farm Plot</option>
              </select>
            </div>
            <div><label className="label">Area (acres)</label><input className="input" type="number" value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })} required /></div>
            <div><label className="label">Location</label><input className="input" placeholder="Village, District, State" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} required /></div>
            <div><label className="label">Facing</label><input className="input" placeholder="East, North-East..." value={form.facing} onChange={(e) => setForm({ ...form, facing: e.target.value })} /></div>
            <div><label className="label">Listed Price (₹)</label><input className="input" type="number" value={form.listed_price} onChange={(e) => setForm({ ...form, listed_price: e.target.value })} /></div>
            <div className="md:col-span-2"><label className="label">Description</label><textarea className="input min-h-[80px]" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
            <div className="flex gap-3"><button type="submit" className="btn-primary">Submit Listing</button><button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button></div>
          </form>
        </div>
      )}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {listings.map((l) => (
          <div key={l.id} className="card">
            <div className="flex justify-between mb-2"><p className="font-semibold text-[#f0ede4] capitalize">{l.land_type?.replace("_", " ")}</p><StatusBadge status={l.status} /></div>
            <div className="flex items-center gap-1 text-sm text-[#8fac9a] mb-1"><MapPin size={12} /> {l.location || "Location TBD"}</div>
            {l.area && <p className="text-sm text-[#8fac9a]">{l.area} acres · {l.facing || "—"} facing</p>}
            {l.listed_price && <p className="text-accent font-bold text-lg mt-2">₹{Number(l.listed_price).toLocaleString()}</p>}
          </div>
        ))}
      </div>
    </PortalPage>
  );
}
