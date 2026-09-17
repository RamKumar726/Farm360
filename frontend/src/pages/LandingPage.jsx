import { Link, useNavigate } from "react-router-dom";
import {
  Leaf,
  Shield,
  TrendingUp,
  MapPin,
  Users,
  Award,
  Activity,
  ChevronRight,
  ArrowRight,
  CheckCircle2,
  BarChart3,
  Layers,
  Sparkles,
  PhoneCall,
  Mail,
  Lock,
  UserCheck,
  Stethoscope,
  Tractor,
  Building2,
} from "lucide-react";
import useAppStore from "../store/useAppStore";
import { getDefaultRoute } from "../config/roleRoutes";

export default function LandingPage() {
  const { user, isAuthenticated } = useAppStore();
  const navigate = useNavigate();

  const handlePortalClick = (rolePath) => {
    if (isAuthenticated && user) {
      navigate(getDefaultRoute(user.role));
    } else {
      navigate(`/login?role=${rolePath}`);
    }
  };

  const portalRoles = [
    {
      title: "Founder & Admin",
      roleKey: "founder",
      icon: Building2,
      color: "from-amber-500/20 to-yellow-600/10 border-amber-500/30 text-amber-400",
      desc: "Full business oversight, branch monitoring, revenue metrics, approvals & fraud prevention.",
    },
    {
      title: "Zone Manager",
      roleKey: "zone_admin",
      icon: MapPin,
      color: "from-emerald-500/20 to-teal-600/10 border-emerald-500/30 text-emerald-400",
      desc: "Zone-level work allocation, lead conversions, field employee supervision & escalations.",
    },
    {
      title: "Field Employee",
      roleKey: "employee",
      icon: UserCheck,
      color: "from-blue-500/20 to-cyan-600/10 border-blue-500/30 text-blue-400",
      desc: "Lead pipeline management, partner onboarding, site visits & customer follow-ups.",
    },
    {
      title: "Agronomy Officer",
      roleKey: "agri_officer",
      icon: Stethoscope,
      color: "from-green-500/20 to-emerald-600/10 border-green-500/30 text-green-400",
      desc: "Scientific crop design, soil health prescriptions, diagnostic visits & harvest quotes.",
    },
    {
      title: "Farm Worker",
      roleKey: "farm_employee",
      icon: Tractor,
      color: "from-orange-500/20 to-amber-600/10 border-orange-500/30 text-orange-400",
      desc: "Work order execution, GPS-tagged proof submission, crop monitoring & incident logs.",
    },
    {
      title: "Customer / Investor",
      roleKey: "customer",
      icon: Users,
      color: "from-purple-500/20 to-indigo-600/10 border-purple-500/30 text-purple-400",
      desc: "MyFarm telemetry, marketplace land sales, crop health reports & investment shares.",
    },
  ];

  const features = [
    {
      icon: Activity,
      title: "360° Real-Time Telemetry",
      description:
        "Satellite monitoring, soil moisture tracking, and micro-climate analytics for optimal yield.",
    },
    {
      icon: Stethoscope,
      title: "Agronomist Prescriptions",
      description:
        "Direct digital prescriptions and treatment plans from certified Agricultural Officers.",
    },
    {
      icon: Layers,
      title: "End-to-End Work Management",
      description:
        "GPS-verified field execution, proof of work uploads, and automated partner payouts.",
    },
    {
      icon: TrendingUp,
      title: "High-Yield Farmland Investments",
      description:
        "Transparent fractional land investments with quarterly revenue distributions.",
    },
    {
      icon: MapPin,
      title: "Verified Land Marketplace",
      description:
        "Buy, sell, or lease agricultural land with verified survey documents and broker support.",
    },
    {
      icon: Shield,
      title: "Enterprise Governance",
      description:
        "Multi-tier role access, audit logs, risk fraud detection, and automated escalation flows.",
    },
  ];

  return (
    <div className="min-h-screen bg-background text-[#f0ede4] font-sans selection:bg-accent/30 selection:text-white">
      {/* Navigation Bar */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-[#0f1f19]/80 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 bg-accent/20 border border-accent/40 rounded-xl flex items-center justify-center shadow-glow">
              <Leaf size={24} className="text-accent" />
            </div>
            <div>
              <span className="font-display font-bold text-xl tracking-tight text-[#f0ede4]">
                Prasad Farm
              </span>
              <span className="text-gradient-gold font-semibold text-sm block -mt-1">
                Care 360°
              </span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-[#8fac9a]">
            <a href="#features" className="hover:text-accent transition-colors">
              Features
            </a>
            <a href="#portals" className="hover:text-accent transition-colors">
              Role Portals
            </a>
            <a href="#solutions" className="hover:text-accent transition-colors">
              Solutions
            </a>
            <a href="#contact" className="hover:text-accent transition-colors">
              Contact
            </a>
          </div>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <button
                onClick={() => navigate(getDefaultRoute(user?.role))}
                className="btn-primary flex items-center gap-2"
              >
                <span>Open Dashboard</span>
                <ChevronRight size={18} />
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm font-semibold text-[#f0ede4] hover:text-accent px-4 py-2 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="btn-primary text-sm flex items-center gap-1.5"
                >
                  <span>Get Started</span>
                  <ArrowRight size={16} />
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="relative pt-16 pb-24 md:pt-24 md:pb-32 overflow-hidden bg-hero-gradient">
        {/* Background Glowing Orbs */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-accent/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-1/3 right-10 w-96 h-96 bg-primary-500/20 rounded-full blur-[100px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-md">
            <Sparkles size={16} className="text-accent animate-pulse" />
            <span className="text-xs font-semibold uppercase tracking-wider text-accent">
              Next-Gen Agribusiness Management Platform
            </span>
          </div>

          <h1 className="font-display text-4xl sm:text-6xl lg:text-7xl font-extrabold text-[#f0ede4] tracking-tight leading-[1.15] max-w-5xl mx-auto">
            360° Smart Agricultural <br />
            <span className="text-gradient-gold">Asset & Farm Ecosystem</span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-[#8fac9a] max-w-3xl mx-auto font-normal leading-relaxed">
            Unifying land owners, agronomy officers, zone managers, field workers, and investors
            into a single data-driven farm management cloud.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/login"
              className="btn-primary text-base px-8 py-4 rounded-xl flex items-center gap-3 shadow-glow"
            >
              <Lock size={18} />
              <span>Launch Operations Portal</span>
            </Link>
            <a
              href="#portals"
              className="btn-secondary text-base px-8 py-4 rounded-xl flex items-center gap-2"
            >
              <span>Explore Roles</span>
              <ChevronRight size={18} />
            </a>
          </div>

          {/* Quick Metrics Bar */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="glass-panel p-5 text-center">
              <p className="font-display text-3xl font-bold text-accent">12,500+</p>
              <p className="text-xs text-[#8fac9a] mt-1 font-medium uppercase tracking-wider">
                Acres Managed
              </p>
            </div>
            <div className="glass-panel p-5 text-center">
              <p className="font-display text-3xl font-bold text-accent">99.4%</p>
              <p className="text-xs text-[#8fac9a] mt-1 font-medium uppercase tracking-wider">
                Crop Health Accuracy
              </p>
            </div>
            <div className="glass-panel p-5 text-center">
              <p className="font-display text-3xl font-bold text-accent">6 Portals</p>
              <p className="text-xs text-[#8fac9a] mt-1 font-medium uppercase tracking-wider">
                Multi-Role Governance
              </p>
            </div>
            <div className="glass-panel p-5 text-center">
              <p className="font-display text-3xl font-bold text-accent">₹45 Cr+</p>
              <p className="text-xs text-[#8fac9a] mt-1 font-medium uppercase tracking-wider">
                Project Capital Handled
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Role Portals Section */}
      <section id="portals" className="py-20 bg-surface/30 border-t border-b border-white/5 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="section-title text-3xl sm:text-4xl text-center mb-3">
              Role-Tailored Workflows
            </h2>
            <p className="text-[#8fac9a] text-base">
              Customized interfaces designed specifically for every stakeholder in the agricultural chain.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {portalRoles.map((portal) => {
              const IconComponent = portal.icon;
              return (
                <div
                  key={portal.roleKey}
                  onClick={() => handlePortalClick(portal.roleKey)}
                  className="glass-panel p-6 rounded-2xl border border-white/10 hover:border-accent/40 transition-all duration-300 hover:-translate-y-1 cursor-pointer group flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className={`p-3 rounded-xl border ${portal.color}`}>
                        <IconComponent size={24} />
                      </div>
                      <span className="text-xs font-semibold text-[#8fac9a] uppercase tracking-wider group-hover:text-accent transition-colors flex items-center gap-1">
                        Sign In <ChevronRight size={14} />
                      </span>
                    </div>

                    <h3 className="font-display text-xl font-bold text-[#f0ede4] mb-2 group-hover:text-accent transition-colors">
                      {portal.title}
                    </h3>
                    <p className="text-sm text-[#8fac9a] leading-relaxed">
                      {portal.desc}
                    </p>
                  </div>

                  <div className="mt-6 pt-4 border-t border-white/5 flex items-center text-xs text-[#8fac9a] font-medium group-hover:text-[#f0ede4]">
                    <span>Access {portal.title} Portal</span>
                    <ArrowRight size={14} className="ml-auto transform group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-semibold text-accent uppercase tracking-widest block mb-2">
              Capabilities & Tools
            </span>
            <h2 className="section-title text-3xl sm:text-4xl text-center mb-4">
              Everything Needed for Modern Farm Operations
            </h2>
            <p className="text-[#8fac9a] text-base">
              From agronomic diagnosis to field proof verification and investment tracking.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feat, idx) => {
              const FeatIcon = feat.icon;
              return (
                <div key={idx} className="glass-panel p-8 rounded-2xl relative overflow-hidden group">
                  <div className="w-12 h-12 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center text-accent mb-6 group-hover:scale-110 transition-transform">
                    <FeatIcon size={24} />
                  </div>
                  <h3 className="font-display text-xl font-bold text-[#f0ede4] mb-3">
                    {feat.title}
                  </h3>
                  <p className="text-sm text-[#8fac9a] leading-relaxed">
                    {feat.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Solutions Banner */}
      <section id="solutions" className="py-16 bg-hero-gradient relative border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="glass-panel p-10 md:p-16 rounded-3xl border border-accent/30 max-w-4xl mx-auto relative overflow-hidden">
            <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-accent/10 rounded-full blur-3xl" />
            <h2 className="font-display text-3xl md:text-4xl font-bold text-[#f0ede4] mb-4">
              Ready to Digitally Transform Your Farm Assets?
            </h2>
            <p className="text-[#8fac9a] text-base md:text-lg mb-8 max-w-2xl mx-auto">
              Connect your farmland, monitor health metrics in real time, and gain access to expert agronomy officers and verified buyers.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/register" className="btn-primary text-base px-8 py-3.5 rounded-xl">
                Create Free Account
              </Link>
              <Link to="/login" className="btn-secondary text-base px-8 py-3.5 rounded-xl">
                Sign In to Portal
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="contact" className="bg-[#0a1511] border-t border-white/10 py-12 text-sm text-[#8fac9a]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Leaf size={20} className="text-accent" />
                <span className="font-display font-bold text-lg text-[#f0ede4]">Prasad Farm</span>
              </div>
              <p className="text-xs text-[#8fac9a] leading-relaxed">
                Prasad Farm Care 360° is an end-to-end digital agriculture operating system providing real-time telemetry, agronomic prescriptions, and farmland asset management.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-[#f0ede4] mb-3">Quick Navigation</h4>
              <ul className="space-y-2 text-xs">
                <li><a href="#features" className="hover:text-accent">Platform Features</a></li>
                <li><a href="#portals" className="hover:text-accent">Role Portals</a></li>
                <li><Link to="/login" className="hover:text-accent">Login Portal</Link></li>
                <li><Link to="/register" className="hover:text-accent">Register User</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-[#f0ede4] mb-3">Supported Portals</h4>
              <ul className="space-y-2 text-xs">
                <li><Link to="/login?role=founder" className="hover:text-accent">Founder & Admin Portal</Link></li>
                <li><Link to="/login?role=zone_admin" className="hover:text-accent">Zone Admin Portal</Link></li>
                <li><Link to="/login?role=agri_officer" className="hover:text-accent">Agri Officer Portal</Link></li>
                <li><Link to="/login?role=customer" className="hover:text-accent">Customer & Investor Portal</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-[#f0ede4] mb-3">Support & Contact</h4>
              <div className="space-y-2 text-xs">
                <p className="flex items-center gap-2">
                  <PhoneCall size={14} className="text-accent" />
                  <span>+91 (800) 360-FARM</span>
                </p>
                <p className="flex items-center gap-2">
                  <Mail size={14} className="text-accent" />
                  <span>support@prasadfarm.com</span>
                </p>
                <p className="flex items-center gap-2">
                  <MapPin size={14} className="text-accent" />
                  <span>Hyderabad, Telangana, India</span>
                </p>
              </div>
            </div>
          </div>

          <div className="pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-xs text-[#8fac9a]">
            <p>© {new Date().getFullYear()} Prasad Farm Care 360°. All rights reserved.</p>
            <p className="mt-2 sm:mt-0">Enterprise Agribusiness Suite</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
