import { useState, useEffect } from "react";
import AppLayout from "../../components/AppLayout";
import { CUSTOMER_NAV } from "./_nav";
import { projectsAPI, landSalesAPI } from "../../config/api";
import { TrendingUp, MapPin, Leaf, Star } from "lucide-react";
import StatusBadge from "../../components/StatusBadge";

export default function CustomerMarketplace() {
  const [projects, setProjects] = useState([]);
  const [land, setLand] = useState([]);
  const [tab, setTab] = useState("investments");

  useEffect(() => {
    projectsAPI.list({ status: "open" }).then((r) => { if (r.success) setProjects(r.data.items); });
    landSalesAPI.list({ status: "listed" }).then((r) => { if (r.success) setLand(r.data.items); });
  }, []);

  return (
    <AppLayout navItems={CUSTOMER_NAV}>
      <div className="space-y-8 animate-slide-up">
        {/* Hero */}
        <div className="relative overflow-hidden rounded-3xl bg-gold-gradient p-8 text-primary-900">
          <div className="absolute right-0 top-0 opacity-20 text-9xl select-none">🌿</div>
          <h1 className="font-display text-3xl font-extrabold mb-2">Prasad Farm Marketplace</h1>
          <p className="text-primary-700 text-lg">Invest in sustainable farming. Buy premium farmland. Build wealth.</p>
          <div className="flex gap-4 mt-4">
            <div className="flex items-center gap-2"><TrendingUp size={16} /> <span className="font-semibold">Investment Opportunities</span></div>
            <div className="flex items-center gap-2"><MapPin size={16} /> <span className="font-semibold">Land Listings</span></div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          {[["investments", "🌾 Investment Projects"], ["land", "🏡 Land for Sale"], ["services", "🛠️ Farm Services"]].map(([key, label]) => (
            <button key={key} onClick={() => setTab(key)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${tab === key ? "bg-accent text-primary-900" : "bg-white/5 text-[#8fac9a] hover:bg-white/10"}`}>
              {label}
            </button>
          ))}
        </div>

        {tab === "investments" && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((p) => (
              <div key={p.id} className="card hover:border-accent/40 hover:shadow-glow transition-all duration-300">
                {p.cover_image_url && <img src={p.cover_image_url} alt={p.name} className="w-full h-40 object-cover rounded-xl mb-4" />}
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-display font-bold text-[#f0ede4]">{p.name}</h3>
                  <StatusBadge status={p.status} />
                </div>
                <p className="text-sm text-[#8fac9a] mb-3">{p.description}</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-[#8fac9a]">Target</span>
                    <span className="text-[#f0ede4] font-semibold">₹{Number(p.total_amount).toLocaleString()}</span>
                  </div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div className="h-full bg-accent rounded-full" style={{ width: `${p.funding_percentage || 0}%` }} />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-[#8fac9a]">{p.funding_percentage}% funded</span>
                    <span className="text-accent">₹{Number(p.funded_amount).toLocaleString()} raised</span>
                  </div>
                </div>
                <button className="btn-primary w-full mt-4">💰 Invest Now</button>
              </div>
            ))}
            {projects.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No open investment projects</p>}
          </div>
        )}

        {tab === "land" && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {land.map((l) => (
              <div key={l.id} className="card hover:border-accent/40 hover:shadow-glow transition-all">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-[#f0ede4] capitalize">{l.land_type?.replace("_", " ")}</h3>
                  <StatusBadge status={l.status} />
                </div>
                <p className="text-[#8fac9a] text-sm">{l.location || "Location TBD"}</p>
                {l.area && <p className="text-sm text-[#8fac9a] mt-1">Area: {l.area} acres</p>}
                {l.facing && <p className="text-sm text-[#8fac9a]">Facing: {l.facing}</p>}
                {l.listed_price && <p className="text-2xl font-bold text-accent mt-3">₹{Number(l.listed_price).toLocaleString()}</p>}
                <p className="text-xs text-[#8fac9a]">{l.description}</p>
                <button className="btn-primary w-full mt-4">🏡 Express Interest</button>
              </div>
            ))}
            {land.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No land listings available</p>}
          </div>
        )}

        {tab === "services" && (
          <div className="grid md:grid-cols-3 gap-4">
            {[
              { icon: "🌱", title: "Farm Management", desc: "We manage your farm end-to-end — from soil preparation to harvest." },
              { icon: "🧪", title: "Soil Testing", desc: "Comprehensive soil and water analysis with prescription reports." },
              { icon: "🤖", title: "Smart Irrigation", desc: "Drip and sprinkler system installation and monitoring." },
              { icon: "📊", title: "Crop Advisory", desc: "Expert agri officer guidance on crop selection and timing." },
              { icon: "🚜", title: "Equipment Rental", desc: "Tractors, harvesters, and specialized machinery on demand." },
              { icon: "📱", title: "Digital Monitoring", desc: "Real-time crop health updates via WhatsApp and dashboard." },
            ].map((s) => (
              <div key={s.title} className="card text-center hover:shadow-glow transition-all">
                <p className="text-4xl mb-3">{s.icon}</p>
                <h3 className="font-semibold text-[#f0ede4] mb-2">{s.title}</h3>
                <p className="text-sm text-[#8fac9a]">{s.desc}</p>
                <button className="btn-secondary w-full mt-4 text-sm">Enquire</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
