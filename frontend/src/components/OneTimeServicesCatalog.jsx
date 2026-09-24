import React, { useEffect, useMemo, useState } from "react";
import { Leaf } from "lucide-react";
import ServiceDetailsModal from "./ServiceDetailsModal";
import { apiFetch } from "../config/api";

export default function OneTimeServicesCatalog({ onSelectService }) {
  const [services, setServices] = useState([]);
  const [activeCategory, setActiveCategory] = useState("All services");
  const [selectedService, setSelectedService] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    apiFetch("/services")
      .then((result) => {
        if (!active) return;
        if (result?.success && Array.isArray(result.data)) setServices(result.data);
        else setError("Services are temporarily unavailable. Please try again shortly.");
      })
      .catch(() => active && setError("Services are temporarily unavailable. Please try again shortly."));
    return () => { active = false; };
  }, []);

  const categories = useMemo(() => ["All services", ...new Set(services.map((item) => item.category))], [services]);
  const filtered = activeCategory === "All services" ? services : services.filter((item) => item.category === activeCategory);
  const featured = services.filter((item) => item.is_featured).slice(0, 3);
  const openService = (service) => {
    onSelectService?.(service);
    setSelectedService(service);
  };

  return (
    <div className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12">
      <div className="text-center max-w-3xl mx-auto space-y-3">
        <span className="text-xs font-semibold tracking-widest text-[#6b7770] uppercase">ONE-TIME SERVICES</span>
        <h2 className="font-serif-brand text-3xl sm:text-5xl text-[#143628] font-bold">One thoughtful beginning.<br />Lasting possibilities.</h2>
        <p className="text-sm sm:text-base text-[#4a5850]">Expert setup and improvements, tailored to your space.</p>
        <div className="flex flex-wrap items-center justify-center gap-2 pt-4">
          {categories.map((category) => <button key={category} onClick={() => setActiveCategory(category)} className={`px-4 py-2 rounded-full text-xs sm:text-sm font-medium border transition-all ${activeCategory === category ? "bg-[#143628] text-[#fbf9f4] border-[#143628]" : "bg-[#fbf9f4] text-[#4a5850] border-[#e8e2d5] hover:border-[#143628]"}`}>{category}</button>)}
        </div>
      </div>

      {error ? <p role="alert" className="text-center text-sm text-red-700">{error}</p> : services.length === 0 ? <p className="text-center text-sm text-[#6b7770]">Loading services…</p> : <>
        {featured.length > 0 && <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {featured.map((service) => <button key={service.id} onClick={() => openService(service)} className="text-left bg-[#f5f2ea] border border-[#e8e2d5] rounded-3xl p-5 space-y-3 hover:border-[#143628] transition-all group">
            <div className="h-48 rounded-2xl overflow-hidden"><img src={service.image} alt={service.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" /></div>
            <h3 className="font-serif-brand font-bold text-xl text-[#143628]">{service.title}</h3>
            <p className="text-xs text-[#6b7770]">{service.subtitle || service.desc}</p>
            <span className="text-xs font-semibold text-[#143628] block">Explore this service ↗</span>
          </button>)}
        </div>}
        <div className="space-y-6 pt-6 border-t border-[#e8e2d5]">
          <div className="flex items-center justify-between"><h2 className="font-serif-brand text-2xl font-bold text-[#143628]">Explore all one-time services</h2><span className="text-xs font-semibold text-[#6b7770] uppercase tracking-widest">SMALL STEPS, STRONGER SPACES.</span></div>
          {filtered.length === 0 ? <p className="text-sm text-[#6b7770]">No services are available in this category.</p> : <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">{filtered.map((service) => <button key={service.id} onClick={() => openService(service)} className="text-left bg-[#f5f2ea] border border-[#e8e2d5] rounded-2xl p-4 space-y-3 hover:border-[#143628] transition-all group"><div className="h-40 rounded-xl overflow-hidden"><img src={service.image} alt={service.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" /></div><h3 className="font-serif-brand font-bold text-base text-[#143628]">{service.title}</h3><p className="text-xs text-[#6b7770] line-clamp-2">{service.desc}</p></button>)}</div>}
        </div>
        <div className="bg-[#143628] text-[#fbf9f4] rounded-3xl p-6 sm:p-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3"><div className="w-10 h-10 rounded-full bg-[#1b4d39] text-[#c4a462] flex items-center justify-center border border-[#2a6b4e]"><Leaf size={20} /></div><div><span className="text-[10px] font-bold text-[#c4a462] uppercase tracking-widest block">A GREENER TOMORROW BEGINS HERE</span><h3 className="font-serif-brand text-xl sm:text-2xl font-bold">Tell us what your space needs</h3></div></div>
          <button onClick={() => openService({ title: "Request a Tailored Service Plan", subtitle: "Our agronomist will consult on your space requirements.", image: featured[0]?.image || services[0]?.image, features: [], steps: [] })} className="btn-gold py-3 px-6 text-sm font-bold text-[#143628] shrink-0">Request a tailored plan →</button>
        </div>
      </>}
      <ServiceDetailsModal isOpen={Boolean(selectedService)} onClose={() => setSelectedService(null)} service={selectedService} />
    </div>
  );
}
