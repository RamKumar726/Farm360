import { useState, useEffect } from "react";
import AppLayout from "../../components/AppLayout";
import { CUSTOMER_NAV } from "./_nav";
import { projectsAPI, landSalesAPI, apiFetch, investmentsAPI } from "../../config/api";
import { TrendingUp, MapPin, X, CheckCircle, Clock, ShieldCheck, AlertCircle } from "lucide-react";
import StatusBadge from "../../components/StatusBadge";

export default function CustomerMarketplace() {
  const [projects, setProjects] = useState([]);
  const [land, setLand] = useState([]);
  const [tab, setTab] = useState("investments");

  // Modals state
  const [selectedProject, setSelectedProject] = useState(null);
  const [proposedAmount, setProposedAmount] = useState(150000);
  const [questions, setQuestions] = useState("");
  const [ackAccepted, setAckAccepted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [verificationModal, setVerificationModal] = useState(null);

  // Service Enquiry modal
  const [selectedService, setSelectedService] = useState(null);
  const [enquirySuccessMsg, setEnquirySuccessMsg] = useState("");

  useEffect(() => {
    projectsAPI.list({ status: "open" }).then((r) => { if (r.success) setProjects(r.data.items); });
    landSalesAPI.list({ status: "listed" }).then((r) => { if (r.success) setLand(r.data.items); }).catch(() => setLand([]));
  }, []);

  const openExpressInterest = (proj) => {
    const available = proj.total_amount - (proj.funded_amount || 0);
    setSelectedProject(proj);
    setProposedAmount(Math.min(150000, available > 0 ? available : 0));
    setQuestions("");
    setAckAccepted(false);
  };

  const handleConfirmInterest = async () => {
    if (!selectedProject || !ackAccepted) return;
    setIsSubmitting(true);
    try {
    const res = await investmentsAPI.expressInterest({
        project_id: selectedProject.id,
        proposed_amount: Number(proposedAmount),
        questions,
        acknowledgement_accepted: ackAccepted,
    });
    if (res.success) {
      setSelectedProject(null);
      setVerificationModal({
        project_name: selectedProject.name,
        amount: proposedAmount,
        stage: "showed_interest",
      });
    } else {
      alert(res.message || "Failed to express interest");
    }
    } catch (err) {
      alert(err?.message || err?.detail || "Could not submit investment interest. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleServiceEnquire = async () => {
    if (!selectedService) return;
    setIsSubmitting(true);
    try {
    const res = await apiFetch("/leads", {
      method: "POST",
      body: JSON.stringify({
        type: "service_enquiry",
        source: "customer_app",
        farm_details: `Service Enquiry: ${selectedService.title} - ${selectedService.desc}`,
      }),
    });
    if (res.success) {
      setSelectedService(null);
      setEnquirySuccessMsg(`Request for '${selectedService.title}' has been sent to our team! We will call and get back to you soon.`);
    } else {
      alert(res.message || "Failed to send enquiry");
    }
    } catch (err) {
      alert(err?.message || err?.detail || "Could not send your enquiry. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

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

        {/* Success Alert Banner */}
        {enquirySuccessMsg && (
          <div className="card border-accent/40 bg-accent/10 p-4 flex justify-between items-center text-accent">
            <div className="flex items-center gap-3">
              <CheckCircle size={20} />
              <p className="font-medium text-sm">{enquirySuccessMsg}</p>
            </div>
            <button onClick={() => setEnquirySuccessMsg("")} className="hover:text-white"><X size={18} /></button>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2">
          {[["investments", "🌾 Investment Projects"], ["land", "🏡 Land for Sale"], ["services", "🛠️ Farm Services"]].map(([key, label]) => (
            <button key={key} onClick={() => setTab(key)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${tab === key ? "bg-accent text-primary-900 font-bold" : "bg-white/5 text-[#8fac9a] hover:bg-white/10"}`}>
              {label}
            </button>
          ))}
        </div>

        {tab === "investments" && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((p) => {
              const available = p.total_amount - (p.funded_amount || 0);
              return (
                <div key={p.id} className="card hover:border-accent/40 hover:shadow-glow transition-all duration-300 flex flex-col justify-between">
                  <div>
                    {p.cover_image_url && <img src={p.cover_image_url} alt={p.name} className="w-full h-40 object-cover rounded-xl mb-4" />}
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-display font-bold text-[#f0ede4]">{p.name}</h3>
                      <StatusBadge status={p.status} />
                    </div>
                    <p className="text-sm text-[#8fac9a] mb-3 line-clamp-2">{p.description}</p>
                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-[#8fac9a]">Target Project Budget</span>
                        <span className="text-[#f0ede4] font-semibold">₹{Number(p.total_amount).toLocaleString()}</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-accent rounded-full" style={{ width: `${p.funding_percentage || 0}%` }} />
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-[#8fac9a]">{p.funding_percentage || 0}% funded</span>
                        <span className="text-accent font-semibold">₹{Number(p.funded_amount || 0).toLocaleString()} raised</span>
                      </div>
                    </div>
                  </div>
                  <button onClick={() => openExpressInterest(p)} className="btn-primary w-full mt-2 flex items-center justify-center gap-2 font-bold">
                    🤝 Show Interest For Investing
                  </button>
                </div>
              );
            })}
            {projects.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No open investment projects at this time</p>}
          </div>
        )}

        {tab === "land" && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {land.map((l) => (
              <div key={l.id} className="card hover:border-accent/40 hover:shadow-glow transition-all flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-semibold text-[#f0ede4] capitalize">{l.land_type?.replace("_", " ")}</h3>
                    <StatusBadge status={l.status} />
                  </div>
                  <p className="text-[#8fac9a] text-sm">{l.location || "Location TBD"}</p>
                  {l.area && <p className="text-sm text-[#8fac9a] mt-1">Area: {l.area} acres</p>}
                  {l.facing && <p className="text-sm text-[#8fac9a]">Facing: {l.facing}</p>}
                  {l.listed_price && <p className="text-2xl font-bold text-accent mt-3">₹{Number(l.listed_price).toLocaleString()}</p>}
                  <p className="text-xs text-[#8fac9a] mt-2 line-clamp-2">{l.description}</p>
                </div>
                <button onClick={async () => {
                  const r = await landSalesAPI.expressInterest(l.id);
                  if (r.success) alert("Interest registered for land listing! Our team will contact you.");
                }} className="btn-primary w-full mt-4 font-bold">
                  🏡 Express Interest
                </button>
              </div>
            ))}
            {land.length === 0 && <p className="col-span-3 text-center text-[#8fac9a] py-10">No land listings available</p>}
          </div>
        )}

        {tab === "services" && (
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { id: "farm_mgmt", icon: "🌱", title: "Farm Management", desc: "We manage your farm end-to-end — from soil preparation to harvest." },
              { id: "soil_test", icon: "🧪", title: "Soil & Water Testing", desc: "Comprehensive soil and water analysis with prescription reports." },
              { id: "irrigation", icon: "🤖", title: "Smart Irrigation", desc: "Drip and sprinkler system installation and monitoring." },
              { id: "advisory", icon: "📊", title: "Crop Advisory", desc: "Expert agri officer guidance on crop selection and timing." },
              { id: "rental", icon: "🚜", title: "Equipment Rental", desc: "Tractors, harvesters, and specialized machinery on demand." },
              { id: "monitoring", icon: "📱", title: "Digital Monitoring", desc: "Real-time crop health updates via WhatsApp and dashboard." },
            ].map((s) => (
              <div key={s.id} className="card text-center hover:shadow-glow transition-all flex flex-col justify-between">
                <div>
                  <p className="text-5xl mb-3">{s.icon}</p>
                  <h3 className="font-semibold text-[#f0ede4] text-lg mb-2">{s.title}</h3>
                  <p className="text-sm text-[#8fac9a] mb-4">{s.desc}</p>
                </div>
                <button onClick={() => setSelectedService(s)} className="btn-secondary w-full text-sm font-semibold">
                  Enquire Service
                </button>
              </div>
            ))}
          </div>
        )}

        {/* EXPRESS INTEREST MODAL */}
        {selectedProject && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#121c17] border border-accent/30 rounded-3xl p-6 max-w-lg w-full space-y-5 animate-scale-up text-left">
              <div className="flex justify-between items-center border-b border-white/10 pb-3">
                <div>
                  <span className="text-xs font-mono text-accent uppercase tracking-wider">{selectedProject.id?.slice(0, 8)}</span>
                  <h3 className="text-xl font-bold text-[#f0ede4]">{selectedProject.name}</h3>
                </div>
                <button onClick={() => setSelectedProject(null)} className="text-[#8fac9a] hover:text-white"><X size={20} /></button>
              </div>

              <div className="space-y-3">
                <div className="bg-white/5 p-3 rounded-xl flex justify-between text-sm">
                  <span className="text-[#8fac9a]">Total Project Budget:</span>
                  <span className="text-[#f0ede4] font-bold">₹{Number(selectedProject.total_amount).toLocaleString()}</span>
                </div>
                <div className="bg-white/5 p-3 rounded-xl flex justify-between text-sm">
                  <span className="text-[#8fac9a]">Available Allocation:</span>
                  <span className="text-accent font-bold">₹{Number(selectedProject.total_amount - (selectedProject.funded_amount || 0)).toLocaleString()}</span>
                </div>

                <div>
                  <label className="block text-xs text-[#8fac9a] uppercase font-semibold mb-1">Proposed Capital Participation (₹)</label>
                  <input
                    type="number"
                    min={150000}
                    max={selectedProject.total_amount - (selectedProject.funded_amount || 0)}
                    value={proposedAmount}
                    onChange={(e) => setProposedAmount(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-accent font-bold text-lg focus:border-accent outline-none"
                  />
                  <p className="text-xs text-[#8fac9a] mt-1">Minimum suggested: ₹1,50,000</p>
                </div>

                <div>
                  <label className="block text-xs text-[#8fac9a] uppercase font-semibold mb-1">Questions / Specific Clarifications</label>
                  <textarea
                    rows={3}
                    placeholder="e.g. Clarification on drip fertigation schedule or crop yield estimates..."
                    value={questions}
                    onChange={(e) => setQuestions(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm text-[#f0ede4] focus:border-accent outline-none resize-none"
                  />
                </div>

                <div className="flex items-start gap-3 bg-white/5 p-3 rounded-xl text-xs text-[#8fac9a]">
                  <input
                    type="checkbox"
                    id="ack"
                    checked={ackAccepted}
                    onChange={(e) => setAckAccepted(e.target.checked)}
                    className="mt-0.5 accent-accent"
                  />
                  <label htmlFor="ack" className="cursor-pointer select-none">
                    <strong className="text-[#f0ede4]">Mandatory Acknowledgement:</strong> I understand that this express interest is non-binding and does NOT constitute a legal investment contract or guaranteed financial yield. All participations are subject to formal agreement review and company governance.
                  </label>
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button onClick={() => setSelectedProject(null)} className="btn-secondary flex-1 py-3">Cancel</button>
                <button
                  disabled={!ackAccepted || isSubmitting}
                  onClick={handleConfirmInterest}
                  className="btn-primary flex-1 py-3 disabled:opacity-50 disabled:cursor-not-allowed font-bold"
                >
                  {isSubmitting ? "Submitting..." : "Confirm Interest"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* VERIFICATION PIPELINE MODAL */}
        {verificationModal && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#121c17] border border-accent/30 rounded-3xl p-6 max-w-xl w-full space-y-6 text-left">
              <div className="flex justify-between items-center border-b border-white/10 pb-3">
                <div>
                  <h3 className="text-xl font-bold text-[#f0ede4]">Express Interest Submitted!</h3>
                  <p className="text-xs text-[#8fac9a]">{verificationModal.project_name} — ₹{Number(verificationModal.amount).toLocaleString()}</p>
                </div>
                <button onClick={() => setVerificationModal(null)} className="text-[#8fac9a] hover:text-white"><X size={20} /></button>
              </div>

              <div className="bg-accent/10 border border-accent/20 p-4 rounded-2xl flex items-center gap-3">
                <Clock className="text-accent animate-pulse" size={24} />
                <div>
                  <p className="font-semibold text-accent text-sm">Status: Waiting for Verification</p>
                  <p className="text-xs text-[#8fac9a]">Our Branch Admin and Employee team will call you to verify your interest.</p>
                </div>
              </div>

              {/* Verification Pipeline Steps */}
              <div className="space-y-3 pl-2">
                <h4 className="text-xs font-mono uppercase text-[#8fac9a]">Behind the Scenes Verification Pipeline</h4>
                {[
                  { step: "Showed Interest", desc: "Submitted from Customer App", done: true },
                  { step: "Employee Info to Customer", desc: "Employee contacts you & explains project details", current: true },
                  { step: "Your Approval & Site Visit", desc: "Verify site & approve project scope", done: false },
                  { step: "Agreemented", desc: "Draft legal participation agreement", done: false },
                  { step: "Branch & Zone Admin Approval", desc: "Branch admin verifies interest lead", done: false },
                  { step: "Founder Approval", desc: "Founder final signoff", done: false },
                  { step: "Payment Gateway", desc: "Secure payment gateway link", done: false },
                ].map((s, idx) => (
                  <div key={s.step} className="flex items-start gap-3 text-sm">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${s.done ? "bg-accent text-primary-900" : s.current ? "border-2 border-accent text-accent animate-bounce" : "bg-white/10 text-[#8fac9a]"}`}>
                      {s.done ? "✓" : idx + 1}
                    </div>
                    <div>
                      <p className={`font-medium ${s.done || s.current ? "text-[#f0ede4]" : "text-[#8fac9a]"}`}>{s.step}</p>
                      <p className="text-xs text-[#8fac9a]">{s.desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              <button onClick={() => setVerificationModal(null)} className="btn-primary w-full py-3 font-bold">
                Got it, Thanks!
              </button>
            </div>
          </div>
        )}

        {/* FARM SERVICE ENQUIRY MODAL */}
        {selectedService && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#121c17] border border-accent/30 rounded-3xl p-6 max-w-md w-full space-y-4 text-left">
              <div className="flex justify-between items-center border-b border-white/10 pb-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{selectedService.icon}</span>
                  <div>
                    <h3 className="text-xl font-bold text-[#f0ede4]">{selectedService.title}</h3>
                    <p className="text-xs text-[#8fac9a]">FarmCare 360° Professional Service</p>
                  </div>
                </div>
                <button onClick={() => setSelectedService(null)} className="text-[#8fac9a] hover:text-white"><X size={20} /></button>
              </div>

              <p className="text-sm text-[#8fac9a]">{selectedService.desc}</p>

              <div className="bg-white/5 p-4 rounded-xl text-xs space-y-2 text-[#8fac9a]">
                <p className="font-semibold text-[#f0ede4]">How Farm Services Work:</p>
                <ol className="list-decimal list-inside space-y-1">
                  <li>You click <strong>Enquire Service</strong> to notify our employee team.</li>
                  <li>Employee assigns an Agriculture Officer to prepare a custom estimation & quotation.</li>
                  <li>You review the quotation in your <strong>Work Details</strong> tab and pay online.</li>
                  <li>Field team executes the work and uploads Proof of Work photos for your approval.</li>
                </ol>
              </div>

              <div className="flex gap-3 pt-2">
                <button onClick={() => setSelectedService(null)} className="btn-secondary flex-1 py-3">Cancel</button>
                <button onClick={handleServiceEnquire} disabled={isSubmitting} className="btn-primary flex-1 py-3 font-bold">
                  {isSubmitting ? "Sending..." : "Enquire Now"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
