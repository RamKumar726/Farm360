import { useState, useEffect } from "react";
import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { projectsAPI, apiFetch } from "../../config/api";
import { CheckSquare, Clock, Check, X, ShieldAlert, TrendingUp, Key } from "lucide-react";
import toast from "react-hot-toast";
import ProjectFinance from "./ProjectFinance";
import InvestmentPipeline from "../../components/InvestmentPipeline";

export default function FounderApprovals() {
  const [pendingProjects, setPendingProjects] = useState([]);
  const [pendingLeases, setPendingLeases] = useState([]);

  const loadData = () => {
    projectsAPI.list({ approval_status: "pending_approval" }).then((r) => {
      if (r.success) setPendingProjects(r.data.items);
    });
    apiFetch("/leads").then((r) => {
      if (r.success) {
        setPendingLeases(r.data.items.filter(l => (l.type === "farm_lease" || l.type === "sell_land") && l.status === "approval" && l.approval_status === "approved_zone"));
      }
    });
  };

  useEffect(() => { loadData(); }, []);

  const handleApproveProject = async (projId, approved) => {
    const res = await apiFetch(`/projects/${projId}/approve?approved=${approved}`, { method: "PATCH" });
    if (res.success) {
      toast.success(approved ? "Project listing approved & published to Marketplace!" : "Project listing rejected");
      loadData();
    }
  };

  const handleApproveLease = async (leadId, approved) => {
    const res = await apiFetch(`/leads/${leadId}/approval?approved=${approved}`, { method: "POST" });
    if (res.success) {
      toast.success(approved ? "Lease Opportunity approved! Moved to Closed Won & Project created." : "Lease Opportunity rejected");
      loadData();
    }
  };

  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-8 animate-slide-up">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="page-header">Founder Approvals Hub</h1>
            <p className="text-sm text-[#8fac9a]">Review Branch Admin investment listings and long-term financial lease commitments</p>
          </div>
        </div>

        {/* Counter Summary */}
        <div className="grid md:grid-cols-2 gap-4">
          <div className="card text-center border-amber-500/30 bg-amber-500/5">
            <TrendingUp size={32} className="mx-auto mb-2 text-amber-400" />
            <p className="font-semibold text-[#f0ede4]">Pending Marketplace Investment Listings</p>
            <p className="text-3xl font-bold mt-1 text-amber-400">{pendingProjects.length}</p>
            <p className="text-xs text-[#8fac9a] mt-1">Requires Founder signoff to go live</p>
          </div>
          <div className="card text-center border-accent/30 bg-accent/5">
            <Key size={32} className="mx-auto mb-2 text-accent" />
            <p className="font-semibold text-[#f0ede4]">Pending Financial Lease Commitments</p>
            <p className="text-3xl font-bold mt-1 text-accent">{pendingLeases.length}</p>
            <p className="text-xs text-[#8fac9a] mt-1">Requires Founder final signoff</p>
          </div>
        </div>

        {/* Pending Investment Project Listings Queue */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-[#f0ede4]">🌾 Pending Marketplace Investment Listings</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {pendingProjects.map((proj) => (
              <div key={proj.id} className="card border-amber-500/30 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-mono text-amber-400 uppercase">#{proj.id.slice(0, 8)}</span>
                    <h3 className="font-bold text-[#f0ede4] text-lg">{proj.name}</h3>
                  </div>
                  <span className="text-xs bg-amber-500/20 text-amber-400 px-2.5 py-1 rounded-full font-semibold">Pending Founder Approval</span>
                </div>

                <p className="text-sm text-[#8fac9a]">{proj.description}</p>
                <div className="bg-white/5 p-3 rounded-xl flex justify-between text-sm">
                  <span className="text-[#8fac9a]">Target Investment Budget:</span>
                  <span className="text-accent font-bold">₹{Number(proj.total_amount).toLocaleString()}</span>
                </div>

                <div className="flex gap-3 pt-2">
                  <button onClick={() => handleApproveProject(proj.id, false)} className="btn-secondary flex-1 py-2 text-red-400 font-semibold flex items-center justify-center gap-1">
                    <X size={16} /> Reject Listing
                  </button>
                  <button onClick={() => handleApproveProject(proj.id, true)} className="btn-primary flex-1 py-2 font-bold flex items-center justify-center gap-1">
                    <Check size={16} /> Approve & Publish to Marketplace
                  </button>
                </div>
              </div>
            ))}
            {pendingProjects.length === 0 && <p className="col-span-2 text-center text-[#8fac9a] py-8 card">No investment listings pending approval</p>}
          </div>
        </div>

        {/* Pending Financial Lease Commitments Queue */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-[#f0ede4]">🔑 Pending Financial Lease Opportunities</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {pendingLeases.map((lease) => (
              <div key={lease.id} className="card border-accent/30 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-mono text-accent uppercase">#{lease.id.slice(0, 8)}</span>
                    <h3 className="font-bold text-[#f0ede4] text-lg capitalize">{lease.type?.replace("_", " ")}</h3>
                  </div>
                  <span className="text-xs bg-accent/20 text-accent px-2.5 py-1 rounded-full font-semibold">Awaiting Founder Approval</span>
                </div>

                <p className="text-sm text-[#8fac9a]">{lease.farm_details}</p>

                {lease.commercial_model_data && (
                  <div className="bg-white/5 p-3 rounded-xl text-xs text-[#8fac9a] space-y-1">
                    <p className="font-semibold text-[#f0ede4]">Commercial Terms:</p>
                    <p>{lease.commercial_model_data}</p>
                  </div>
                )}

                <div className="flex gap-3 pt-2">
                  <button onClick={() => handleApproveLease(lease.id, false)} className="btn-secondary flex-1 py-2 text-red-400 font-semibold flex items-center justify-center gap-1">
                    <X size={16} /> Reject Lease
                  </button>
                  <button onClick={() => handleApproveLease(lease.id, true)} className="btn-primary flex-1 py-2 font-bold flex items-center justify-center gap-1">
                    <Check size={16} /> Approve Lease & Create Project
                  </button>
                </div>
              </div>
            ))}
            {pendingLeases.length === 0 && <p className="col-span-2 text-center text-[#8fac9a] py-8 card">No lease commitments pending approval</p>}
          </div>
        </div>
        <ProjectFinance />
        <InvestmentPipeline />
      </div>
    </AppLayout>
  );
}
