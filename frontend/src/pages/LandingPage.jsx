import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Leaf,
  ArrowRight,
  ChevronRight,
  MapPin,
  Users,
  Building2,
  UserCheck,
  Stethoscope,
  Tractor,
  Sliders,
  CheckCircle2,
  Calendar,
  Sparkles,
  PhoneCall,
  Menu,
  X,
  ExternalLink,
  ChevronLeft,
  ChevronRight as ChevronRightIcon,
  Home,
} from "lucide-react";
import useAppStore from "../store/useAppStore";
import { getDefaultRoute } from "../config/roleRoutes";
import ServiceDetailsModal from "../components/ServiceDetailsModal";
import OneTimeServicesCatalog from "../components/OneTimeServicesCatalog";
import { leadsAPI } from "../config/api";

export default function LandingPage() {
  const { user, isAuthenticated } = useAppStore();
  const navigate = useNavigate();

  // Modal State
  const [selectedService, setSelectedService] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Before/After Slider position (0 to 100)
  const [sliderPos, setSliderPos] = useState(50);

  // Active Category Filters
  const [activeCareCategory, setActiveCareCategory] = useState("Small plots & sites");
  const [activeDiscoverFilter, setActiveDiscoverFilter] = useState("Small plots");

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Lead Consultation Form State (Image 08)
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [consultForm, setConsultForm] = useState({
    name: "",
    email: "",
    contact: "",
    location: "",
    spaceType: "Terrace",
    service: "",
    notes: "",
  });

  const handlePortalClick = (rolePath) => {
    if (isAuthenticated && user) {
      navigate(getDefaultRoute(user.role));
    } else {
      navigate(`/login?role=${rolePath}`);
    }
  };

  const openServiceDetails = (title, subtitle, image) => {
    setSelectedService({ title, subtitle, image });
    setIsModalOpen(true);
  };

  const handleConsultationSubmit = async (e) => {
    e.preventDefault();
    setFormLoading(true);
    try {
      const result = await leadsAPI.createPublic({
          name: consultForm.name,
          email: consultForm.email,
          phone: consultForm.contact,
          location: consultForm.location,
          space_type: consultForm.spaceType,
          service: consultForm.service,
          notes: consultForm.notes,
      });
      if (!result?.success) throw new Error(result?.message || "Could not submit your request");
      setFormSubmitted(true);
    } catch (err) {
      console.error("Lead submission failed", err);
      window.alert(err?.message || "Could not submit your request. Please try again.");
    } finally {
      setFormLoading(false);
    }
  };

  const portalRoles = [
    { title: "Founder & Admin", roleKey: "founder", icon: Building2, desc: "Business oversight, approvals & branch metrics." },
    { title: "Zone Manager", roleKey: "zone_admin", icon: MapPin, desc: "Work allocation, lead pipeline & field staff management." },
    { title: "Field Employee", roleKey: "employee", icon: UserCheck, desc: "Lead pipeline, site visits & partner onboarding." },
    { title: "Agronomy Officer", roleKey: "agri_officer", icon: Stethoscope, desc: "Scientific crop design & soil health prescriptions." },
    { title: "Farm Worker", roleKey: "farm_employee", icon: Tractor, desc: "Work order execution & proof of work uploads." },
    { title: "Customer / Investor", roleKey: "customer", icon: Users, desc: "MyFarm telemetry, marketplace & service tracking." },
  ];

  return (
    <div className="min-h-screen bg-[#fbf9f4] text-[#1f2824] font-sans selection:bg-[#c4a462]/30 selection:text-[#143628]">
      {/* ---------------------------------------------------- */}
      {/* NAVBAR */}
      {/* ---------------------------------------------------- */}
      <nav className="sticky top-0 z-40 bg-[#fbf9f4]/90 backdrop-blur-md border-b border-[#e8e2d5]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#143628] rounded-xl flex items-center justify-center text-[#fbf9f4] shadow-sm">
              <Leaf size={22} className="text-[#c4a462]" />
            </div>
            <div>
              <span className="font-serif-brand font-bold text-xl tracking-tight text-[#143628] block leading-none">
                PRASAD
              </span>
              <span className="text-[10px] font-semibold text-[#6b7770] tracking-widest block uppercase mt-0.5">
                FARM CARE 360°
              </span>
            </div>
          </Link>

          <div className="hidden lg:flex items-center gap-8 text-sm font-medium text-[#4a5850]">
            <a href="#hero" className="hover:text-[#143628] transition-colors">Home</a>
            <a href="#process" className="hover:text-[#143628] transition-colors">Our Process</a>
            <a href="#one-time" className="hover:text-[#143628] transition-colors">One-Time Services</a>
            <a href="#managed-care" className="hover:text-[#143628] transition-colors">Managed Care</a>
            <a href="#landowners" className="hover:text-[#143628] transition-colors">For Landowners</a>
            <a href="#contact" className="hover:text-[#143628] transition-colors">Get in Touch</a>
          </div>

          <div className="hidden sm:flex items-center gap-3">
            {isAuthenticated ? (
              <button
                onClick={() => navigate(getDefaultRoute(user.role))}
                className="btn-forest text-sm py-2 px-5"
              >
                Go to Portal ({user.role})
              </button>
            ) : (
              <>
                <Link to="/login" className="btn-outline-forest text-sm py-2 px-4">
                  Log in
                </Link>
                <a href="#contact" className="btn-forest text-sm py-2 px-5">
                  Plan a Consultation →
                </a>
              </>
            )}
          </div>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 text-[#143628]"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* ---------------------------------------------------- */}
      {/* SECTION 1: HERO (Images 01 & 09 Desktop View) */}
      {/* ---------------------------------------------------- */}
      <section id="hero" className="relative pt-8 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-6 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#e2ebe4] text-[#143628] text-xs font-semibold uppercase tracking-widest">
              <Leaf size={14} className="text-[#c4a462]" />
              HEALTHY LAND • HAPPIER LIVES
            </div>
            <h1 className="font-serif-brand text-4xl sm:text-5xl lg:text-6xl text-[#143628] font-bold leading-tight">
              A little land.<br />
              A world of possibility.
            </h1>
            <p className="text-base sm:text-lg text-[#4a5850] max-w-xl font-normal leading-relaxed">
              Beautiful gardens. Productive farms. Thoughtfully managed land. Turning unused spaces into thriving green retreats.
            </p>
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <a href="#one-time" className="btn-gold py-3 px-7 text-base shadow-md font-semibold">
                Explore our services →
              </a>
              <a href="#contact" className="btn-outline-forest py-3 px-6 text-base">
                Discuss your space
              </a>
            </div>
            <span className="text-xs text-[#6b7770] tracking-widest uppercase block pt-2">
              GREENER SPACES • KINDER TOMORROWS
            </span>
          </div>

          <div className="lg:col-span-6 relative">
            <div className="relative rounded-3xl overflow-hidden shadow-xl border border-[#e8e2d5] aspect-[4/3]">
              <img
                src="https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=1200&q=80"
                alt="Terrace Garden Setup"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent"></div>
              <div className="absolute bottom-4 left-4 right-4 bg-[#fbf9f4]/90 backdrop-blur-md p-4 rounded-2xl border border-[#e8e2d5] flex items-center justify-between">
                <div>
                  <span className="text-xs font-semibold text-[#6b7770] uppercase">Featured Setup</span>
                  <h4 className="font-serif-brand font-bold text-base text-[#143628]">Urban Terrace Sanctuary</h4>
                </div>
                <button
                  onClick={() =>
                    openServiceDetails(
                      "Terrace garden setup",
                      "Green living, right at home.",
                      "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=1000&q=80"
                    )
                  }
                  className="btn-gold py-1.5 px-4 text-xs font-semibold"
                >
                  View Scope
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 3 Large Category Carousel Cards (Image 09) */}
        <div className="pt-8 border-t border-[#e8e2d5] space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold tracking-widest text-[#6b7770] uppercase">OUR SERVICES</span>
              <h2 className="font-serif-brand text-2xl sm:text-3xl font-bold text-[#143628]">
                What would you like to create?
              </h2>
            </div>
            <p className="text-xs text-[#6b7770] hidden sm:block max-w-xs text-right">
              Different spaces. A shared purpose. Let's find what's right for yours.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div
              onClick={() =>
                openServiceDetails(
                  "A garden above the city",
                  "Terrace garden setup & urban planter designs.",
                  "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=800&q=80"
                )
              }
              className="bg-[#f5f2ea] border border-[#e8e2d5] rounded-3xl p-5 space-y-4 cursor-pointer hover:border-[#143628] transition-all group"
            >
              <div className="h-56 rounded-2xl overflow-hidden relative">
                <img
                  src="https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=800&q=80"
                  alt="A garden above the city"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <span className="text-[10px] font-bold text-[#6b7770] tracking-wider uppercase block">
                TERRACE GARDEN SETUP
              </span>
              <div className="flex items-center justify-between">
                <h3 className="font-serif-brand font-bold text-xl text-[#143628]">A garden above the city</h3>
                <span className="text-xs font-semibold text-[#143628]">See more ↗</span>
              </div>
            </div>

            <div
              onClick={() =>
                openServiceDetails(
                  "Possibility in every plot",
                  "Land design & agricultural development.",
                  "https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=800&q=80"
                )
              }
              className="bg-[#f5f2ea] border border-[#e8e2d5] rounded-3xl p-5 space-y-4 cursor-pointer hover:border-[#143628] transition-all group"
            >
              <div className="h-56 rounded-2xl overflow-hidden relative">
                <img
                  src="https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=800&q=80"
                  alt="Possibility in every plot"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <span className="text-[10px] font-bold text-[#6b7770] tracking-wider uppercase block">
                LAND DESIGN & DEVELOPMENT
              </span>
              <div className="flex items-center justify-between">
                <h3 className="font-serif-brand font-bold text-xl text-[#143628]">Possibility in every plot</h3>
                <span className="text-xs font-semibold text-[#143628]">See more ↗</span>
              </div>
            </div>

            <div
              onClick={() =>
                openServiceDetails(
                  "Care that continues",
                  "Managed farms & ongoing garden care.",
                  "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80"
                )
              }
              className="bg-[#f5f2ea] border border-[#e8e2d5] rounded-3xl p-5 space-y-4 cursor-pointer hover:border-[#143628] transition-all group"
            >
              <div className="h-56 rounded-2xl overflow-hidden relative">
                <img
                  src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80"
                  alt="Care that continues"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <span className="text-[10px] font-bold text-[#6b7770] tracking-wider uppercase block">
                MANAGED FARMS & GARDENS
              </span>
              <div className="flex items-center justify-between">
                <h3 className="font-serif-brand font-bold text-xl text-[#143628]">Care that continues</h3>
                <span className="text-xs font-semibold text-[#143628]">See more ↗</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------- */}
      {/* SECTION 2: 4-STEP PROCESS (Image 08) */}
      {/* ---------------------------------------------------- */}
      <section id="process" className="py-16 px-4 sm:px-6 lg:px-8 bg-[#f5f2ea] border-y border-[#e8e2d5]">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <span className="text-xs font-semibold tracking-widest text-[#6b7770] uppercase">
              OUR PROCESS
            </span>
            <h2 className="font-serif-brand text-3xl sm:text-5xl text-[#143628] font-bold">
              From your idea to a living space.
            </h2>
            <p className="text-sm sm:text-base text-[#4a5850]">
              Thoughtful guidance. Practical expertise. Beautiful outcomes.
            </p>
          </div>

          {/* 4 Steps Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-[#fbf9f4] border border-[#e8e2d5] rounded-3xl p-5 space-y-3">
              <div className="h-44 rounded-2xl overflow-hidden relative">
                <img
                  src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=600&q=80"
                  alt="Step 01"
                  className="w-full h-full object-cover"
                />
                <span className="absolute bottom-2 left-2 bg-[#143628] text-[#fbf9f4] font-serif-brand text-lg font-bold w-8 h-8 rounded-full flex items-center justify-center">
                  01
                </span>
              </div>
              <h3 className="font-serif-brand font-bold text-lg text-[#143628]">Tell us your vision</h3>
              <p className="text-xs text-[#6b7770]">
                We listen to your ideas, understand your goals and explore the possibilities together.
              </p>
            </div>

            <div className="bg-[#fbf9f4] border border-[#e8e2d5] rounded-3xl p-5 space-y-3">
              <div className="h-44 rounded-2xl overflow-hidden relative">
                <img
                  src="https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=600&q=80"
                  alt="Step 02"
                  className="w-full h-full object-cover"
                />
                <span className="absolute bottom-2 left-2 bg-[#143628] text-[#fbf9f4] font-serif-brand text-lg font-bold w-8 h-8 rounded-full flex items-center justify-center">
                  02
                </span>
              </div>
              <h3 className="font-serif-brand font-bold text-lg text-[#143628]">Assess your space</h3>
              <p className="text-xs text-[#6b7770]">
                We study your soil, space and surroundings to recommend what works best.
              </p>
            </div>

            <div className="bg-[#fbf9f4] border border-[#e8e2d5] rounded-3xl p-5 space-y-3">
              <div className="h-44 rounded-2xl overflow-hidden relative">
                <img
                  src="https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=600&q=80"
                  alt="Step 03"
                  className="w-full h-full object-cover"
                />
                <span className="absolute bottom-2 left-2 bg-[#143628] text-[#fbf9f4] font-serif-brand text-lg font-bold w-8 h-8 rounded-full flex items-center justify-center">
                  03
                </span>
              </div>
              <h3 className="font-serif-brand font-bold text-lg text-[#143628]">Review your tailored plan</h3>
              <p className="text-xs text-[#6b7770]">
                We create a plan suited to your space, needs and long term vision.
              </p>
            </div>

            <div className="bg-[#fbf9f4] border border-[#e8e2d5] rounded-3xl p-5 space-y-3">
              <div className="h-44 rounded-2xl overflow-hidden relative">
                <img
                  src="https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=600&q=80"
                  alt="Step 04"
                  className="w-full h-full object-cover"
                />
                <span className="absolute bottom-2 left-2 bg-[#143628] text-[#fbf9f4] font-serif-brand text-lg font-bold w-8 h-8 rounded-full flex items-center justify-center">
                  04
                </span>
              </div>
              <h3 className="font-serif-brand font-bold text-lg text-[#143628]">We create. We care.</h3>
              <p className="text-xs text-[#6b7770]">
                Our team brings the plan to life and stays with you for lasting growth and care.
              </p>
            </div>
          </div>

          {/* Stay Close Overlay Banner (Image 08) */}
          <div className="relative rounded-3xl overflow-hidden shadow-md border border-[#e8e2d5] h-72 sm:h-96">
            <img
              src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"
              alt="Stay close banner"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-black/30"></div>
            <div className="absolute bottom-6 right-6 max-w-sm bg-[#fbf9f4]/95 backdrop-blur-md p-6 rounded-3xl border border-[#e8e2d5] space-y-2">
              <h3 className="font-serif-brand text-2xl font-bold text-[#143628]">Stay close to every step.</h3>
              <p className="text-xs text-[#4a5850]">Agreed scope. Clear updates. Work you can see.</p>
              <span className="text-[10px] font-bold text-[#c4a462] uppercase tracking-widest block pt-2">
                SAME LAND, A BRIGHTER TOMORROW
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------- */}
      {/* SECTION 3: ONE-TIME SERVICES CATALOG (Image 10) */}
      {/* ---------------------------------------------------- */}
      <section id="one-time">
        <OneTimeServicesCatalog
          onSelectService={(serv) => openServiceDetails(serv.title, serv.desc, serv.image)}
        />
      </section>

      {/* ---------------------------------------------------- */}
      {/* SECTION 4: MANAGED CARE & BEFORE/AFTER SLIDER (Image 03) */}
      {/* ---------------------------------------------------- */}
      <section id="managed-care" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12">
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="text-xs font-semibold tracking-widest text-[#6b7770] uppercase">
            MANAGED CARE
          </span>
          <h2 className="font-serif-brand text-3xl sm:text-5xl text-[#143628] font-bold">
            Your space, cared for.<br />
            Season after season.
          </h2>
          <p className="text-sm sm:text-base text-[#4a5850]">
            Ongoing care for farms, vacant plots and terrace gardens.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-4 pt-4">
            {[
              "Farms & orchards",
              "Small plots & sites",
              "Terrace gardens",
              "Farmhouse gardens",
            ].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveCareCategory(tab)}
                className={`px-4 py-2 rounded-full text-xs sm:text-sm font-medium border transition-all ${
                  activeCareCategory === tab
                    ? "bg-[#143628] text-[#fbf9f4] border-[#143628]"
                    : "bg-[#fbf9f4] text-[#4a5850] border-[#e8e2d5] hover:border-[#143628]"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Interactive Before/After Split Image */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center bg-[#f5f2ea] border border-[#e8e2d5] p-6 sm:p-8 rounded-3xl shadow-sm">
          <div className="lg:col-span-7 space-y-3">
            <div className="relative h-80 sm:h-[400px] rounded-2xl overflow-hidden shadow-inner border border-[#e8e2d5] select-none touch-none">
              <img
                src="https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=1200&q=80"
                alt="Possibilities After Care"
                className="absolute inset-0 w-full h-full object-cover"
              />
              <span className="absolute bottom-4 right-4 bg-[#143628]/80 backdrop-blur-md text-[#fbf9f4] text-xs px-3 py-1 rounded-full font-semibold z-10">
                Possibilities after care
              </span>

              <div
                className="absolute inset-y-0 left-0 overflow-hidden"
                style={{ width: `${sliderPos}%` }}
              >
                <img
                  src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80"
                  alt="Before"
                  className="absolute inset-y-0 left-0 w-full h-full object-cover max-w-none"
                  style={{ width: "100%", height: "100%" }}
                />
                <span className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-md text-[#fbf9f4] text-xs px-3 py-1 rounded-full font-semibold">
                  Before
                </span>
              </div>

              <div
                className="absolute inset-y-0 w-1 bg-white cursor-ew-resize z-20 flex items-center justify-center shadow-lg"
                style={{ left: `${sliderPos}%` }}
              >
                <div className="w-8 h-8 rounded-full bg-[#143628] border-2 border-white text-white flex items-center justify-center text-xs shadow-md">
                  ⟨ ⟩
                </div>
              </div>

              <input
                type="range"
                min="0"
                max="100"
                value={sliderPos}
                onChange={(e) => setSliderPos(Number(e.target.value))}
                className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-30"
              />
            </div>
          </div>

          <div className="lg:col-span-5 space-y-6">
            <h3 className="font-serif-brand text-2xl sm:text-3xl text-[#143628] font-bold">
              Idle land. A fresh purpose.
            </h3>
            <p className="text-sm text-[#4a5850] leading-relaxed">
              Turn an unused plot into a kitchen garden, or keep it clean and cared for with expert agronomists.
            </p>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-[#e2ebe4] flex items-center justify-center shrink-0 border border-[#c3d6c8] mt-0.5">
                  <Leaf className="w-4 h-4 text-[#143628]" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-[#143628]">Seasonal growing</h4>
                  <p className="text-xs text-[#6b7770]">Plan and grow what suits your space and the season.</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-[#e2ebe4] flex items-center justify-center shrink-0 border border-[#c3d6c8] mt-0.5">
                  <Sparkles className="w-4 h-4 text-[#143628]" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-[#143628]">Regular upkeep</h4>
                  <p className="text-xs text-[#6b7770]">Weeding, watering, pruning and site care.</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-[#e2ebe4] flex items-center justify-center shrink-0 border border-[#c3d6c8] mt-0.5">
                  <CheckCircle2 className="w-4 h-4 text-[#143628]" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-[#143628]">Harvest support</h4>
                  <p className="text-xs text-[#6b7770]">Guidance to help you make the most of your produce.</p>
                </div>
              </div>
            </div>

            <button
              onClick={() =>
                openServiceDetails(
                  "Plot Managed Care",
                  "Practical care plans priced to your space and agreed scope.",
                  "https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=1000&q=80"
                )
              }
              className="btn-forest py-3 px-6 text-sm font-semibold"
            >
              Explore plot care ↗
            </button>
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------- */}
      {/* SECTION 5: FOR LANDOWNERS (Image 04) */}
      {/* ---------------------------------------------------- */}
      <section id="landowners" className="py-16 px-4 sm:px-6 lg:px-8 bg-[#f5f2ea] border-t border-[#e8e2d5]">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center max-w-3xl mx-auto space-y-2">
            <span className="text-xs font-semibold tracking-widest text-[#6b7770] uppercase">
              FOR LANDOWNERS — CULTIVATING BRIGHTER TOMORROWS
            </span>
            <h2 className="font-serif-brand text-3xl sm:text-5xl text-[#143628] font-bold">
              Your land. The right arrangement.
            </h2>
            <p className="text-sm sm:text-base text-[#4a5850]">
              Two ways to explore agricultural leasing with FarmCare.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-[#fbf9f4] border border-[#e8e2d5] rounded-3xl p-6 sm:p-8 flex flex-col justify-between space-y-6 shadow-sm">
              <div className="space-y-4">
                <div className="h-48 rounded-2xl overflow-hidden">
                  <img
                    src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80"
                    alt="Direct Leasing"
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="font-serif-brand text-2xl font-bold text-[#143628]">
                  Lease directly to FarmCare
                </h3>
                <p className="text-sm text-[#4a5850]">
                  We assess your land and discuss a lease operated directly by our team.
                </p>
                <div className="flex flex-wrap gap-2 pt-2">
                  <span className="chip-pill text-xs">Fixed lease</span>
                  <span className="chip-pill text-xs">Lease + revenue share</span>
                  <span className="chip-pill text-xs">Revenue share</span>
                </div>
              </div>
              <button
                onClick={() =>
                  openServiceDetails(
                    "Direct Farm Care Lease",
                    "We assess your land and manage agricultural ops.",
                    "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80"
                  )
                }
                className="btn-forest py-3 px-6 text-sm font-semibold self-start"
              >
                Explore direct leasing ↗
              </button>
            </div>

            <div className="bg-[#fbf9f4] border border-[#e8e2d5] rounded-3xl p-6 sm:p-8 flex flex-col justify-between space-y-6 shadow-sm">
              <div className="space-y-4">
                <div className="h-48 rounded-2xl overflow-hidden">
                  <img
                    src="https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=800&q=80"
                    alt="Partner Leasing"
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="font-serif-brand text-2xl font-bold text-[#143628]">
                  Find a lease partner
                </h3>
                <p className="text-sm text-[#4a5850]">
                  We help connect your land with a suitable external lease operator and coordinate the process.
                </p>
                <div className="flex flex-wrap gap-2 pt-2">
                  <span className="chip-pill text-xs">Partner matching</span>
                  <span className="chip-pill text-xs">Site assessment</span>
                  <span className="chip-pill text-xs">Agreement support</span>
                </div>
              </div>
              <button
                onClick={() =>
                  openServiceDetails(
                    "Lease Partner Matching",
                    "Connect your land with verified lease operators.",
                    "https://images.unsplash.com/photo-1592417817098-8f3d6eb12755?auto=format&fit=crop&w=800&q=80"
                  )
                }
                className="btn-forest py-3 px-6 text-sm font-semibold self-start"
              >
                Explore partner leasing ↗
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------- */}
      {/* SECTION 6: INTERACTIVE LEAD CONSULTATION FORM (Image 08) */}
      {/* ---------------------------------------------------- */}
      <section id="contact" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-5 space-y-4">
            <span className="text-xs font-semibold tracking-widest text-[#6b7770] uppercase">
              GET IN TOUCH
            </span>
            <h2 className="font-serif-brand text-3xl sm:text-5xl text-[#143628] font-bold leading-tight">
              Let's begin with your space.
            </h2>
            <p className="text-sm sm:text-base text-[#4a5850] leading-relaxed">
              A terrace, a small plot or an established farm. Tell us what you have in mind.
            </p>
            <span className="text-xs font-bold text-[#c4a462] tracking-widest uppercase block pt-4">
              GOOD SPACES GROW GREAT LIVES
            </span>
          </div>

          <div className="lg:col-span-7 bg-[#f5f2ea] border border-[#e8e2d5] rounded-3xl p-6 sm:p-8 shadow-sm">
            {formSubmitted ? (
              <div className="bg-[#e2ebe4] border border-[#c3d6c8] p-6 rounded-2xl text-center space-y-3">
                <CheckCircle2 size={40} className="text-[#143628] mx-auto" />
                <h3 className="font-serif-brand font-bold text-2xl text-[#143628]">
                  Consultation Request Sent!
                </h3>
                <p className="text-sm text-[#4a5850]">
                  Thank you! Our agricultural specialist will contact you shortly to discuss your space and schedule a site visit.
                </p>
              </div>
            ) : (
              <form onSubmit={handleConsultationSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="label text-xs">Your name</label>
                    <input
                      type="text"
                      required
                      placeholder="Enter your name"
                      value={consultForm.name}
                      onChange={(e) => setConsultForm({ ...consultForm, name: e.target.value })}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-xs">Phone</label>
                    <input
                      type="text"
                      required
                      placeholder="Enter your phone number"
                      value={consultForm.contact}
                      onChange={(e) => setConsultForm({ ...consultForm, contact: e.target.value })}
                      className="input"
                    />
                  </div>
                  <div>
                    <label className="label text-xs">Email (optional)</label>
                    <input
                      type="email"
                      placeholder="you@example.com"
                      value={consultForm.email}
                      onChange={(e) => setConsultForm({ ...consultForm, email: e.target.value })}
                      className="input"
                    />
                  </div>
                </div>

                <div>
                  <label className="label text-xs">Location</label>
                  <input
                    type="text"
                    placeholder="Enter your city or location"
                    value={consultForm.location}
                    onChange={(e) => setConsultForm({ ...consultForm, location: e.target.value })}
                    className="input"
                  />
                </div>

                <div>
                  <label className="label text-xs">Your space</label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {["Terrace", "Small plot", "Farm", "Other"].map((sp) => (
                      <button
                        type="button"
                        key={sp}
                        onClick={() => setConsultForm({ ...consultForm, spaceType: sp })}
                        className={`py-2 px-3 rounded-xl text-xs font-semibold border text-center transition-all ${
                          consultForm.spaceType === sp
                            ? "bg-[#143628] text-[#fbf9f4] border-[#143628]"
                            : "bg-[#fbf9f4] text-[#4a5850] border-[#e8e2d5] hover:border-[#143628]"
                        }`}
                      >
                        {sp === "Terrace" && "🏠 "}
                        {sp === "Small plot" && "🌱 "}
                        {sp === "Farm" && "🌾 "}
                        {sp === "Other" && "••• "}
                        {sp}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="label text-xs">What would you like help with?</label>
                  <select
                    value={consultForm.service}
                    onChange={(e) => setConsultForm({ ...consultForm, service: e.target.value })}
                    className="input"
                  >
                    <option value="">Choose a service</option>
                    <option value="Terrace garden setup">Terrace garden setup</option>
                    <option value="Vacant plot care">Vacant plot care</option>
                    <option value="Managed farm care">Managed farm care</option>
                    <option value="Agricultural leasing">Agricultural leasing</option>
                  </select>
                </div>

                <div>
                  <label className="label text-xs">Tell us a little about your plans</label>
                  <textarea
                    rows="3"
                    placeholder="Share your ideas, goals or any specific requirements..."
                    value={consultForm.notes}
                    onChange={(e) => setConsultForm({ ...consultForm, notes: e.target.value })}
                    className="input"
                  ></textarea>
                </div>

                <button
                  type="submit"
                  disabled={formLoading}
                  className="w-full btn-forest py-3.5 text-base font-semibold shadow-md"
                >
                  {formLoading ? "Submitting..." : "Request a consultation →"}
                </button>
                <p className="text-[11px] text-center text-[#6b7770]">
                  By submitting, you agree to be contacted about this enquiry.
                </p>
              </form>
            )}
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------- */}
      {/* SECTION 7: ROLE PORTALS */}
      {/* ---------------------------------------------------- */}
      <section id="portals" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8 bg-[#f5f2ea] border-t border-[#e8e2d5]">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <span className="text-xs font-semibold tracking-widest text-[#6b7770] uppercase">
            ENTERPRISE OPERATING SYSTEM
          </span>
          <h2 className="font-serif-brand text-3xl sm:text-4xl text-[#143628] font-bold">
            Role Portals Access
          </h2>
          <p className="text-sm text-[#4a5850]">
            Direct login portals for administrators, zone managers, agronomists, field teams, and customers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {portalRoles.map((portal) => {
            const IconComp = portal.icon;
            return (
              <div
                key={portal.roleKey}
                onClick={() => handlePortalClick(portal.roleKey)}
                className="bg-[#fbf9f4] border border-[#e8e2d5] rounded-2xl p-6 cursor-pointer hover:border-[#143628] hover:shadow-md transition-all group flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="w-12 h-12 rounded-xl bg-[#143628] text-[#c4a462] flex items-center justify-center">
                    <IconComp size={24} />
                  </div>
                  <h3 className="font-serif-brand font-bold text-xl text-[#143628] group-hover:text-[#1b4d39]">
                    {portal.title}
                  </h3>
                  <p className="text-xs text-[#6b7770] leading-relaxed">{portal.desc}</p>
                </div>
                <div className="pt-4 flex items-center text-xs font-semibold text-[#143628] gap-1 group-hover:translate-x-1 transition-transform">
                  Enter Portal <ChevronRight size={16} />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-[#143628] text-[#fbf9f4] pt-12 pb-8 border-t border-[#1b4d39]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-8 border-b border-[#2a6b4e]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#fbf9f4] text-[#143628] rounded-xl flex items-center justify-center font-bold">
                <Leaf size={22} className="text-[#143628]" />
              </div>
              <div>
                <span className="font-serif-brand font-bold text-xl text-[#fbf9f4] block">PRASAD</span>
                <span className="text-[10px] font-semibold text-[#c4a462] tracking-widest block uppercase">
                  FARM CARE 360°
                </span>
              </div>
            </div>

            <div className="flex flex-wrap gap-6 text-xs text-[#d0dfc5]">
              <a href="#hero" className="hover:text-[#fbf9f4]">Home</a>
              <a href="#process" className="hover:text-[#fbf9f4]">Process</a>
              <a href="#one-time" className="hover:text-[#fbf9f4]">One-Time Services</a>
              <a href="#managed-care" className="hover:text-[#fbf9f4]">Managed Care</a>
              <a href="#landowners" className="hover:text-[#fbf9f4]">For Landowners</a>
              <a href="#contact" className="hover:text-[#fbf9f4]">Contact</a>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#a3b8aa]">
            <p>© 2026 PRASAD Farm Care 360°. All rights reserved.</p>
            <p className="tracking-wide">
              ROOTED IN INDIA FOR GENERATIONS AHEAD • Nurturing land. Enriching lives.
            </p>
          </div>
        </div>
      </footer>

      {/* Service Details Popup Modal */}
      <ServiceDetailsModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        service={selectedService}
      />
    </div>
  );
}
