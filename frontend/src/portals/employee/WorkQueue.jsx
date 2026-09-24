import { useState, useEffect } from "react";
import PortalPage from "../../components/PortalPage";
import { EMPLOYEE_NAV } from "./_nav";
import StatusBadge from "../../components/StatusBadge";
import { workOrdersAPI, farmsAPI, workPartnersAPI, usersAPI, apiFetch } from "../../config/api";
import { Plus, CheckCircle, User, Wrench, AlertTriangle, Eye } from "lucide-react";
import toast from "react-hot-toast";
import ProjectFinance from "../founder/ProjectFinance";

const WO_TYPES = [
  "cleaning", "securing", "irrigation", "electric", "harvest",
  "soil_water_test", "cropping", "land_leveling", "pruning",
  "fertilizer_pestcontrol", "monitoring", "construction", "land_sale_followup"
];

export default function EmployeeWorkQueue() {
  const [workOrders, setWorkOrders] = useState([]);
  const [farms, setFarms] = useState([]);
  const [partners, setPartners] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [agriOfficers, setAgriOfficers] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [activeWO, setActiveWO] = useState(null); // for assign modal
  const [assignType, setAssignType] = useState("partner"); // "partner" | "employee"
  const [assignId, setAssignId] = useState("");
  const [verifyWO, setVerifyWO] = useState(null);

  // Create form
  const [form, setForm] = useState({ farm_id: "", type: "irrigation", agri_officer_id: "", notes: "", start_date: "", end_date: "" });

  const loadData = () => {
    workOrdersAPI.list().then((r) => { if (r.success) setWorkOrders(r.data.items); });
    farmsAPI.list().then((r) => { if (r.success) setFarms(r.data.items); });
    workPartnersAPI.list().then((r) => { if (r.success) setPartners(r.data.items); });
    usersAPI.list({ role: "farm_employee" }).then((r) => { if (r.success) setEmployees(r.data.items); });
    usersAPI.list({ role: "agri_officer" }).then((r) => { if (r.success) setAgriOfficers(r.data.items); });
  };

  useEffect(() => { loadData(); }, []);

  const handleCreate = async () => {
    if (!form.farm_id || !form.type) return toast.error("Farm and Type are required");
    if (form.type === "monitoring" && !form.agri_officer_id) return toast.error("Choose an Agriculture Officer for this inspection");
    try {
      const res = await workOrdersAPI.create(form);
      if (res.success) {
        toast.success("Work order created!");
        setShowCreate(false);
        setForm({ farm_id: "", type: "irrigation", agri_officer_id: "", notes: "", start_date: "", end_date: "" });
        loadData();
      } else toast.error("Failed to create work order");
    } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Failed to create work order"); }
  };

  const handleAssign = async () => {
    if (!assignId || !activeWO) return;
    let res;
    if (assignType === "partner") {
      res = await workOrdersAPI.assignPartner(activeWO.id, assignId);
    } else {
      res = await workOrdersAPI.assignEmployee(activeWO.id, assignId);
    }
    if (res.success) {
      toast.success(`${assignType === "partner" ? "Partner" : "Employee"} assigned!`);
      setActiveWO(null);
      setAssignId("");
      loadData();
    }
  };

  const handleVerify = async (wo) => {
    const res = await workOrdersAPI.verify(wo.id);
    if (res.success) {
      toast.success("Work order verified!");
      loadData();
    }
  };

  const statusColor = (s) => {
    if (s === "completed") return "border-emerald-500/30 bg-emerald-500/5";
    if (s === "verified") return "border-accent/30 bg-accent/5";
    if (s === "in_progress") return "border-blue-500/30 bg-blue-500/5";
    if (s === "failed") return "border-red-500/30 bg-red-500/5";
    return "border-white/10";
  };

  return (
    <PortalPage title="Work Queue" subtitle="Create, assign, and verify farm work orders" navItems={EMPLOYEE_NAV}>
      <div className="space-y-6">
        <ProjectFinance />
        {/* Header */}
        <div className="flex justify-between items-center">
              <div className="grid grid-cols-3 gap-4 flex-1 mr-6">
            {[
              { label: "Total", val: workOrders.length, col: "text-[#f0ede4]" },
                { label: "Proofs Pending Verify", val: workOrders.filter(w => w.status === "proof_submitted").length, col: "text-amber-400" },
              { label: "Verified", val: workOrders.filter(w => w.status === "verified").length, col: "text-accent" },
            ].map(kpi => (
              <div key={kpi.label} className="card text-center py-3">
                <p className={`text-2xl font-bold ${kpi.col}`}>{kpi.val}</p>
                <p className="text-xs text-[#8fac9a] mt-1">{kpi.label}</p>
              </div>
            ))}
          </div>
          <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2">
            <Plus size={18} /> New Work Order
          </button>
        </div>

        {/* Work Order Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workOrders.map((wo) => (
            <div key={wo.id} className={`card border ${statusColor(wo.status)} space-y-3`}>
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-xs font-mono text-accent">#{wo.id.slice(0, 8)}</span>
                  <h3 className="font-semibold text-[#f0ede4] capitalize">{wo.type?.replace(/_/g, " ")}</h3>
                </div>
                <StatusBadge status={wo.status} />
              </div>

              <p className="text-xs text-[#8fac9a]">{wo.notes || "No notes"}</p>

              <div className="text-xs text-[#8fac9a] space-y-1 bg-white/5 rounded-xl p-2">
                <div className="flex justify-between"><span>Farm</span><span className="text-[#f0ede4] font-mono">{wo.farm_id?.slice(0, 8)}</span></div>
                <div className="flex justify-between"><span>Start</span><span className="text-[#f0ede4]">{wo.start_date || "TBD"}</span></div>
                {wo.outsourcing_partner_id && <div className="flex justify-between"><span>Partner</span><span className="text-amber-400 font-semibold">Assigned</span></div>}
                {wo.farm_employee_id && <div className="flex justify-between"><span>Employee</span><span className="text-accent font-semibold">Assigned</span></div>}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col gap-2">
                {wo.type === "land_sale_followup" && ["assigned", "in_progress"].includes(wo.status) && <button className="btn-primary w-full text-xs" onClick={async () => { const notes = prompt("Record the land sale follow-up outcome:"); if (!notes?.trim()) return; try { await workOrdersAPI.close(wo.id, notes); toast.success("Follow-up task closed"); loadData(); } catch (error) { toast.error(error?.response?.data?.detail || error?.detail || "Could not close follow-up task"); } }}>Record outcome & close</button>}
                {(["pending", "assigned", "partner_accepted"].includes(wo.status) && !["monitoring", "land_sale_followup"].includes(wo.type) && (!wo.farm_employee_id || !wo.outsourcing_partner_id)) && (
                  <button
                    onClick={() => { setActiveWO(wo); setAssignType("partner"); setAssignId(""); }}
                    className="btn-secondary w-full text-xs flex items-center justify-center gap-1"
                  >
                    <User size={14} /> Assign Partner / Employee
                  </button>
                )}
                {wo.status === "proof_submitted" && !wo.is_verified_by_employee && (
                  <button
                    onClick={() => handleVerify(wo)}
                    className="btn-primary w-full text-xs flex items-center justify-center gap-1 font-bold"
                  >
                    <CheckCircle size={14} /> Verify Work Done
                  </button>
                )}
                {wo.status === "verified" && (
                  <div className="flex items-center gap-1 text-accent text-xs font-semibold justify-center">
                    <CheckCircle size={14} /> Verified ✓
                  </div>
                )}
              </div>
            </div>
          ))}
          {workOrders.length === 0 && (
            <p className="col-span-3 text-center text-[#8fac9a] py-10 card">No work orders yet</p>
          )}
        </div>
      </div>

      {/* CREATE WORK ORDER MODAL */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121c17] border border-accent/30 rounded-3xl p-6 max-w-lg w-full space-y-4">
            <h3 className="text-xl font-bold text-[#f0ede4] flex items-center gap-2"><Wrench size={20} /> Create Work Order</h3>

            <div className="space-y-3">
              <div>
                <label className="label">Farm</label>
                <select className="input" value={form.farm_id} onChange={e => setForm({ ...form, farm_id: e.target.value })}>
                  <option value="">-- Select Farm --</option>
                  {farms.map(f => <option key={f.id} value={f.id}>{f.location || f.id.slice(0, 8)}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Work Type</label>
                <select className="input" value={form.type} onChange={e => setForm({ ...form, type: e.target.value })}>
                  {WO_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
                </select>
              </div>
              {form.type === "monitoring" && <div><label className="label">Agriculture Officer</label><select className="input" value={form.agri_officer_id} onChange={(e) => setForm({ ...form, agri_officer_id: e.target.value })} required><option value="">-- Select Agriculture Officer --</option>{agriOfficers.map((officer) => <option key={officer.id} value={officer.id}>{officer.name}</option>)}</select></div>}
              <div className="grid grid-cols-2 gap-3">
                <div><label className="label">Start Date</label><input type="date" className="input" value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} /></div>
                <div><label className="label">End Date</label><input type="date" className="input" value={form.end_date} onChange={e => setForm({ ...form, end_date: e.target.value })} /></div>
              </div>
              <div>
                <label className="label">Notes</label>
                <textarea className="input min-h-[70px]" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Instructions for the worker..." />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button onClick={() => setShowCreate(false)} className="btn-secondary flex-1 py-3">Cancel</button>
              <button onClick={handleCreate} className="btn-primary flex-1 py-3 font-bold">Create</button>
            </div>
          </div>
        </div>
      )}

      {/* ASSIGN PARTNER / EMPLOYEE MODAL */}
      {activeWO && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#121c17] border border-amber-500/30 rounded-3xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-xl font-bold text-[#f0ede4]">Assign Work Order #{activeWO.id.slice(0, 8)}</h3>

            <div className="flex gap-3">
              <button
                onClick={() => setAssignType("partner")}
                className={`flex-1 py-2 rounded-xl text-sm font-semibold border transition-all ${assignType === "partner" ? "btn-primary" : "btn-secondary"}`}
              >Outsourcing Partner</button>
              <button
                onClick={() => setAssignType("employee")}
                className={`flex-1 py-2 rounded-xl text-sm font-semibold border transition-all ${assignType === "employee" ? "btn-primary" : "btn-secondary"}`}
              >Farm Employee</button>
            </div>

            {assignType === "partner" ? (
              <select className="input w-full" value={assignId} onChange={e => setAssignId(e.target.value)}>
                <option value="">-- Select Partner --</option>
                {partners.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            ) : (
              <select className="input w-full" value={assignId} onChange={e => setAssignId(e.target.value)}>
                <option value="">-- Select Farm Employee --</option>
                {employees.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            )}

            <div className="flex gap-3 pt-2">
              <button onClick={() => setActiveWO(null)} className="btn-secondary flex-1 py-3">Cancel</button>
              <button onClick={handleAssign} className="btn-primary flex-1 py-3 font-bold">Assign</button>
            </div>
          </div>
        </div>
      )}
    </PortalPage>
  );
}
