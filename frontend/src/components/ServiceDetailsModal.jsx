import React, { useState } from "react";
import { X, Leaf, Droplets, ClipboardCheck, ArrowRight, CheckCircle2 } from "lucide-react";
import useAppStore from "../store/useAppStore";
import { apiFetch } from "../config/api";

export default function ServiceDetailsModal({ isOpen, onClose, service }) {
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({ name: "", phone: "", location: "", notes: "" });
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const { user } = useAppStore();

  if (!isOpen) return null;

  const defaultService = {
    title: "Terrace garden setup",
    subtitle: "A productive green retreat, designed for your home.",
    image:
      "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=1000&q=80",
    features: [
      {
        icon: Leaf,
        title: "Designed for your terrace",
        desc: "Layout, growing beds and planting.",
      },
      {
        icon: Droplets,
        title: "Planned for practical care",
        desc: "Watering and upkeep guidance.",
      },
      {
        icon: ClipboardCheck,
        title: "Assessed before installation",
        desc: "Space, drainage and structural suitability reviewed.",
      },
    ],
    steps: [
      { num: "1", title: "Share your space" },
      { num: "2", title: "Site assessment" },
      { num: "3", title: "Tailored proposal" },
    ],
  };

  const data = service ? {
    ...defaultService,
    ...service,
    subtitle: service.subtitle || service.desc || defaultService.subtitle,
    features: Array.isArray(service.features) ? service.features : defaultService.features,
    steps: Array.isArray(service.steps) ? service.steps : defaultService.steps,
  } : defaultService;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSubmitError("");
    try {
      const details = {
          name: formData.name || user?.full_name || "Prospective Client",
          phone: formData.phone || user?.phone || "0000000000",
          location: formData.location,
          service: data.title,
          notes: formData.notes || `Enquiry for ${data.title}`,
        };
      if (user?.role === "customer") {
        await apiFetch("/leads", { method: "POST", body: JSON.stringify({
          type: "service_enquiry", source: "customer_app", is_opportunity: true,
          contact_name: details.name, contact_phone: details.phone,
          farm_location: formData.location,
          farm_details: `Service enquiry: ${data.title}. ${details.notes}`,
        }) });
      } else {
        await apiFetch("/leads/public", { method: "POST", body: JSON.stringify(details) });
      }
      setSubmitted(true);
    } catch (err) {
      setSubmitError(err?.detail || err?.message || "We could not send your enquiry. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-lg bg-[#fbf9f4] border border-[#e8e2d5] rounded-3xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header bar with close button */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#e8e2d5] bg-[#f5f2ea]">
          <div className="flex items-center gap-2">
            <Leaf className="w-5 h-5 text-[#143628]" />
            <span className="font-serif-brand font-bold text-sm tracking-wider text-[#143628] uppercase">
              PRASAD FARM CARE 360°
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-[#6b7770] hover:text-[#143628] hover:bg-[#e8e2d5] rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="overflow-y-auto p-6 space-y-6">
          {/* Main Photo */}
          <div className="relative h-48 sm:h-56 rounded-2xl overflow-hidden shadow-inner border border-[#e8e2d5]">
            <img
              src={data.image}
              alt={data.title}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Title & Subtitle */}
          <div>
            <h3 className="font-serif-brand text-2xl sm:text-3xl text-[#143628] font-bold">
              {data.title}
            </h3>
            <p className="text-sm text-[#4a5850] mt-1">{data.subtitle}</p>
          </div>

          {/* Features list */}
          <div className="space-y-4 pt-2">
            {data.features.map((feat, idx) => {
              const IconComp = feat.icon || Leaf;
              return (
                <div key={idx} className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-[#e2ebe4] flex items-center justify-center shrink-0 border border-[#c3d6c8]">
                    <IconComp className="w-5 h-5 text-[#143628]" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-[#143628] text-base">
                      {feat.title}
                    </h4>
                    <p className="text-xs sm:text-sm text-[#6b7770]">
                      {feat.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Stepper Flow */}
          <div className="pt-4 border-t border-[#e8e2d5]">
            <h4 className="font-serif-brand font-bold text-lg text-[#143628] mb-3">
              How it begins
            </h4>
            <div className="flex items-center justify-between bg-[#f5f2ea] p-3 rounded-xl border border-[#e8e2d5] text-xs sm:text-sm">
              {data.steps.map((step, idx) => (
                <React.Fragment key={idx}>
                  <div className="flex items-center gap-1.5 font-medium text-[#143628]">
                    <span className="w-5 h-5 rounded-full bg-[#143628] text-[#fbf9f4] font-bold text-xs flex items-center justify-center">
                      {step.num}
                    </span>
                    <span>{step.title}</span>
                  </div>
                  {idx < data.steps.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-[#c4a462] shrink-0" />
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Form or Submitted State */}
          {submitted ? (
            <div className="bg-[#e2ebe4] border border-[#c3d6c8] p-4 rounded-2xl text-center space-y-2">
              <CheckCircle2 className="w-8 h-8 text-[#143628] mx-auto" />
              <h4 className="font-serif-brand font-bold text-lg text-[#143628]">
                Enquiry Sent!
              </h4>
              <p className="text-xs text-[#4a5850]">
                Our agricultural expert will reach out to discuss your space and schedule a site assessment.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-3 pt-2">
              {submitError && <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-700" role="alert">{submitError}</p>}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="Your Name"
                  required
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className="w-full bg-[#f5f2ea] border border-[#e8e2d5] rounded-xl px-3 py-2 text-sm text-[#143628] focus:outline-none focus:border-[#143628]"
                />
                <input
                  type="tel"
                  placeholder="Phone Number"
                  required
                  value={formData.phone}
                  onChange={(e) =>
                    setFormData({ ...formData, phone: e.target.value })
                  }
                  className="w-full bg-[#f5f2ea] border border-[#e8e2d5] rounded-xl px-3 py-2 text-sm text-[#143628] focus:outline-none focus:border-[#143628]"
                />
              </div>
              <input type="text" placeholder="Farm / service location (optional)" value={formData.location} onChange={(e) => setFormData({ ...formData, location: e.target.value })} className="w-full bg-[#f5f2ea] border border-[#e8e2d5] rounded-xl px-3 py-2 text-sm text-[#143628] focus:outline-none focus:border-[#143628]" />
              <textarea placeholder="Tell us what work you need (optional)" value={formData.notes} onChange={(e) => setFormData({ ...formData, notes: e.target.value })} rows={3} className="w-full bg-[#f5f2ea] border border-[#e8e2d5] rounded-xl px-3 py-2 text-sm text-[#143628] focus:outline-none focus:border-[#143628]" />
              <button
                type="submit"
                disabled={loading}
                className="w-full btn-forest py-3 text-base shadow-md font-medium"
              >
                {loading ? "Submitting..." : "Enquire about this service →"}
              </button>
            </form>
          )}

          <p className="text-center text-xs text-[#6b7770]">
            Setup scope and ongoing care quoted separately.
          </p>
        </div>
      </div>
    </div>
  );
}
