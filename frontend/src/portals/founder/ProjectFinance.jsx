import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { harvestsAPI, investmentsAPI, projectsAPI, projectFinanceAPI, workOrdersAPI, workPartnersAPI } from "../../config/api";
import useAppStore from "../../store/useAppStore";

const money = (n) => `₹${Number(n || 0).toLocaleString("en-IN")}`;

export default function ProjectFinance() {
  const { user } = useAppStore();
  const isApprover = ["founder", "zone_admin"].includes(user?.role);
  const [projects, setProjects] = useState([]);
  const [workOrders, setWorkOrders] = useState([]);
  const [projectId, setProjectId] = useState("");
  const [expenses, setExpenses] = useState([]);
  const [harvests, setHarvests] = useState([]);
  const [settlements, setSettlements] = useState([]);
  const [investments, setInvestments] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [partners, setPartners] = useState([]);
  const [busy, setBusy] = useState(false);
  const [expense, setExpense] = useState({ category: "", vendor: "", amount: "", proof_url: "" });
  const [harvest, setHarvest] = useState({ crop_name: "", yield_quantity: "", yield_unit: "kg", market_price_per_unit: "", buyer_name: "", sale_reference: "" });
  const [period, setPeriod] = useState(new Date().toISOString().slice(0, 7));
  const [settlementHarvestId, setSettlementHarvestId] = useState("");
  const [payment, setPayment] = useState({});
  const [contract, setContract] = useState({ work_order_id: "", partner_id: "", scope: "", terms: "", amount: "", document_url: "" });

  useEffect(() => {
    projectsAPI.list().then((r) => {
      if (r.success) {
        const rows = r.data.items || [];
        setProjects(rows);
        if (rows[0]) setProjectId(rows[0].id);
      }
    }).catch(() => toast.error("Could not load projects"));
    workOrdersAPI.list().then((r) => { if (r.success) setWorkOrders(r.data.items || []); }).catch(() => {});
    investmentsAPI.list().then((r) => { if (r.success) setInvestments(r.data.items || []); }).catch(() => {});
    workPartnersAPI.list({ page_size: 100 }).then((r) => { if (r.success) setPartners(r.data.items || []); }).catch(() => {});
  }, []);

  const refresh = async () => {
    if (!projectId) return;
    const [e, s, h, i, c] = await Promise.all([
      projectFinanceAPI.expenses(projectId),
      projectFinanceAPI.settlements(projectId),
      harvestsAPI.list({ project_id: projectId }),
      investmentsAPI.list(),
      projectFinanceAPI.outsourcingContracts(projectId),
    ]);
    if (e.success) setExpenses(e.data || []);
    if (s.success) setSettlements(s.data || []);
    if (h.success) setHarvests(h.data.items || []);
    if (i.success) setInvestments((i.data.items || []).filter((row) => row.project_id === projectId));
    if (c.success) setContracts(c.data || []);
  };
  useEffect(() => { refresh().catch(() => toast.error("Could not load project finance records")); }, [projectId]);

  const run = async (action, successMessage) => {
    setBusy(true);
    try { await action(); await refresh(); toast.success(successMessage); }
    catch (error) { toast.error(error?.response?.data?.detail || error?.detail || error.message || "Could not save record"); }
    finally { setBusy(false); }
  };

  const submitExpense = (event) => {
    event.preventDefault();
    run(() => projectFinanceAPI.createExpense({ ...expense, project_id: projectId, amount: Number(expense.amount) }), "Expense submitted for review");
    setExpense({ category: "", vendor: "", amount: "", proof_url: "" });
  };

  const submitHarvest = (event) => {
    event.preventDefault();
    run(() => harvestsAPI.create({
      ...harvest, project_id: projectId,
      work_order_id: harvest.work_order_id || null,
      yield_quantity: Number(harvest.yield_quantity),
      market_price_per_unit: Number(harvest.market_price_per_unit),
    }), "Harvest and revenue saved");
    setHarvest({ crop_name: "", yield_quantity: "", yield_unit: "kg", market_price_per_unit: "", buyer_name: "", sale_reference: "" });
  };

  const submitContract = (event) => {
    event.preventDefault();
    run(async () => {
      await projectFinanceAPI.createOutsourcingContract(projectId, { ...contract, amount: Number(contract.amount) });
      setContract({ work_order_id: "", partner_id: "", scope: "", terms: "", amount: "", document_url: "" });
    }, "Signed outsourcing contract recorded");
  };

  return <section className="card space-y-5">
    <div>
      <h2 className="section-title">Project operations and finance</h2>
      <p className="text-sm text-[#8fac9a]">Harvest revenue, expenses, and landowner settlements are stored against the selected project.</p>
    </div>
    <select className="input" value={projectId} onChange={(e) => setProjectId(e.target.value)}>
      <option value="">Select project</option>
      {projects.map((p) => <option key={p.id} value={p.id}>{p.name} · {p.type}</option>)}
    </select>
    {!projectId ? <p className="text-sm text-[#8fac9a]">No projects are available.</p> : <>
      <div className="grid lg:grid-cols-2 gap-5">
        <form className="space-y-3 rounded-xl border border-white/10 p-4" onSubmit={submitHarvest}>
          <h3 className="font-semibold">Record harvest revenue</h3>
          <input className="input" placeholder="Crop name" value={harvest.crop_name} onChange={(e) => setHarvest({ ...harvest, crop_name: e.target.value })} required />
          <select className="input" value={harvest.work_order_id || ""} onChange={(e) => setHarvest({ ...harvest, work_order_id: e.target.value })} required={projects.find((p) => p.id === projectId)?.type === "lease"}>
            <option value="">{projects.find((p) => p.id === projectId)?.type === "lease" ? "Select the harvest work order" : "Link to work order (optional)"}</option>{workOrders.filter((w) => w.project_id === projectId).map((w) => <option key={w.id} value={w.id}>{w.type} · {w.start_date || "unscheduled"}</option>)}
          </select>
          <div className="grid grid-cols-3 gap-2">
            <input className="input" type="number" min="0.01" step="any" placeholder="Quantity" value={harvest.yield_quantity} onChange={(e) => setHarvest({ ...harvest, yield_quantity: e.target.value })} required />
            <input className="input" placeholder="Unit" value={harvest.yield_unit} onChange={(e) => setHarvest({ ...harvest, yield_unit: e.target.value })} required />
            <input className="input" type="number" min="0.01" step="any" placeholder="Price / unit" value={harvest.market_price_per_unit} onChange={(e) => setHarvest({ ...harvest, market_price_per_unit: e.target.value })} required />
          </div>
          <input className="input" placeholder="Buyer name (optional)" value={harvest.buyer_name} onChange={(e) => setHarvest({ ...harvest, buyer_name: e.target.value })} />
          <input className="input" placeholder="Sale receipt / invoice reference" value={harvest.sale_reference} onChange={(e) => setHarvest({ ...harvest, sale_reference: e.target.value })} />
          <button disabled={busy} className="btn-primary" type="submit">Save harvest</button>
        </form>
        <form className="space-y-3 rounded-xl border border-white/10 p-4" onSubmit={submitExpense}>
          <h3 className="font-semibold">Submit project expense</h3>
          <input className="input" placeholder="Expense category" value={expense.category} onChange={(e) => setExpense({ ...expense, category: e.target.value })} required />
          <select className="input" value={expense.work_order_id || ""} onChange={(e) => setExpense({ ...expense, work_order_id: e.target.value })} required={projects.find((p) => p.id === projectId)?.type === "lease"}>
            <option value="">{projects.find((p) => p.id === projectId)?.type === "lease" ? "Select the related work order" : "Link to work order (optional)"}</option>{workOrders.filter((w) => w.project_id === projectId).map((w) => <option key={w.id} value={w.id}>{w.type} · {w.start_date || "unscheduled"}</option>)}
          </select>
          <input className="input" placeholder="Vendor (optional)" value={expense.vendor} onChange={(e) => setExpense({ ...expense, vendor: e.target.value })} />
          <input className="input" type="number" min="0.01" step="any" placeholder="Amount ₹" value={expense.amount} onChange={(e) => setExpense({ ...expense, amount: e.target.value })} required />
          <input className="input" type="url" placeholder="Invoice or proof URL" value={expense.proof_url} onChange={(e) => setExpense({ ...expense, proof_url: e.target.value })} required />
          <button disabled={busy} className="btn-primary" type="submit">Submit expense</button>
        </form>
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold">Harvest records</h3>
        {harvests.map((row) => <article key={row.id} className="rounded-xl border border-white/10 p-3 flex flex-wrap items-center justify-between gap-3 text-sm">
          <span>{row.crop_name || "Harvest"} · {row.yield_quantity || 0} {row.yield_unit || "kg"} · {row.harvest_date || "Date not set"}{row.buyer_name ? ` · Buyer ${row.buyer_name}` : ""}{row.sale_reference ? ` · Sale ${row.sale_reference}` : ""}</span>
          <span>Revenue {money(row.gross_revenue)} · {row.is_revenue_received ? `Received · ${row.revenue_payment_reference}` : "Awaiting payment"}</span>
          {!row.is_revenue_received && ["founder", "zone_admin", "employee"].includes(user?.role) && <div className="flex gap-2"><input className="input max-w-48" placeholder="Payment reference" value={payment[`revenue-${row.id}`]?.ref || ""} onChange={(e) => setPayment({ ...payment, [`revenue-${row.id}`]: { ref: e.target.value } })} /><button disabled={busy || !payment[`revenue-${row.id}`]?.ref} className="btn-primary" onClick={() => run(() => harvestsAPI.recordPayment(row.id, { payment_reference: payment[`revenue-${row.id}`].ref }), "Harvest sale payment recorded")}>Record receipt</button></div>}
        </article>)}
        {harvests.length === 0 && <p className="text-sm text-[#8fac9a]">No harvests recorded.</p>}
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold">Expenses</h3>
        {expenses.map((row) => <article key={row.id} className="rounded-xl border border-white/10 p-3 flex flex-wrap items-center justify-between gap-3 text-sm">
          <span>{row.category}{row.vendor ? ` · ${row.vendor}` : ""} · {money(row.amount)} · {row.status}</span>
          <div className="flex gap-2">
            {isApprover && row.status === "submitted" && <><button disabled={busy} className="btn-secondary" onClick={() => run(() => projectFinanceAPI.reviewExpense(row.id, true), "Expense approved")}>Approve</button><button disabled={busy} className="btn-secondary" onClick={() => run(() => projectFinanceAPI.reviewExpense(row.id, false), "Expense rejected")}>Reject</button></>}
            {isApprover && row.status === "approved" && <><input className="input max-w-48" placeholder="Transaction reference" value={payment[row.id]?.ref || ""} onChange={(e) => setPayment({ ...payment, [row.id]: { ...payment[row.id], ref: e.target.value } })} /><button disabled={busy || !payment[row.id]?.ref || !payment[row.id]?.proof} className="btn-primary" onClick={() => run(() => projectFinanceAPI.markExpensePaid(row.id, { transaction_reference: payment[row.id].ref, proof_url: payment[row.id].proof }), "Expense payment recorded")}>Mark paid</button></>}
          </div>
          {row.status === "approved" && <input className="input max-w-56" type="url" placeholder="Payment proof URL" value={payment[row.id]?.proof || ""} onChange={(e) => setPayment({ ...payment, [row.id]: { ...payment[row.id], proof: e.target.value } })} />}
        </article>)}
        {expenses.length === 0 && <p className="text-sm text-[#8fac9a]">No expenses recorded.</p>}
      </div>

      <div className="space-y-3 border-t border-white/10 pt-4">
        <h3 className="font-semibold">Outsourcing contracts</h3>
        {contracts.map((row) => <article key={row.id} className="rounded-xl border border-white/10 p-3 text-sm space-y-1">
          <p>{partners.find((p) => p.id === row.partner_id)?.name || `Provider ${row.partner_id.slice(0, 8)}`} · {money(row.amount)} · {row.status}</p>
          <p className="text-[#8fac9a]">{row.scope}</p>
          <a className="text-accent underline" href={row.document_url} target="_blank" rel="noreferrer">View signed contract</a>
        </article>)}
        {contracts.length === 0 && <p className="text-sm text-[#8fac9a]">No outsourcing contracts recorded for this project.</p>}
        {["founder", "zone_admin", "employee"].includes(user?.role) && <form onSubmit={submitContract} className="grid md:grid-cols-2 gap-3 rounded-xl border border-white/10 p-4">
          <h4 className="md:col-span-2 font-semibold">Record a signed provider contract</h4>
          <select className="input" required value={contract.partner_id} onChange={(e) => setContract({ ...contract, partner_id: e.target.value, work_order_id: "" })}><option value="">Select active provider</option>{partners.filter((p) => p.status === "active").map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}</select>
          <select className="input" required value={contract.work_order_id} onChange={(e) => setContract({ ...contract, work_order_id: e.target.value })}><option value="">Select assigned work order</option>{workOrders.filter((w) => w.project_id === projectId && w.outsourcing_partner_id === contract.partner_id).map((w) => <option key={w.id} value={w.id}>{w.type} · {w.start_date || "unscheduled"}</option>)}</select>
          <input className="input" placeholder="Contract amount ₹" type="number" min="0" step="0.01" required value={contract.amount} onChange={(e) => setContract({ ...contract, amount: e.target.value })} />
          <input className="input" type="url" placeholder="Signed contract document URL" required value={contract.document_url} onChange={(e) => setContract({ ...contract, document_url: e.target.value })} />
          <input className="input md:col-span-2" placeholder="Scope of work" required value={contract.scope} onChange={(e) => setContract({ ...contract, scope: e.target.value })} />
          <textarea className="input md:col-span-2" placeholder="Payment and delivery terms (optional)" value={contract.terms} onChange={(e) => setContract({ ...contract, terms: e.target.value })} />
          <button disabled={busy || !contract.partner_id || !contract.work_order_id} className="btn-primary md:col-span-2" type="submit">Save contract record</button>
        </form>}
      </div>

      {projects.find((p) => p.id === projectId)?.type === "lease" && <div className="space-y-3 border-t border-white/10 pt-4">
        <h3 className="font-semibold">Landowner settlements</h3>
        <div className="flex flex-wrap gap-2"><input className="input max-w-56" type="month" value={period} onChange={(e) => { setPeriod(e.target.value); setSettlementHarvestId(""); }} />
          {projects.find((p) => p.id === projectId)?.commercial_model_type !== "fixed_lease" && <select className="input min-w-56" value={settlementHarvestId} onChange={(e) => setSettlementHarvestId(e.target.value)}><option value="">Select paid harvest for revenue share</option>{harvests.filter((h) => h.is_revenue_received && (!h.harvest_date || h.harvest_date.startsWith(period))).map((h) => <option key={h.id} value={h.id}>{h.crop_name || "Harvest"} · {h.harvest_date || "date not set"}</option>)}</select>}
          <button disabled={busy || (projects.find((p) => p.id === projectId)?.commercial_model_type !== "fixed_lease" && !settlementHarvestId)} className="btn-primary" onClick={() => run(() => projectFinanceAPI.createSettlement(projectId, { period_key: period, harvest_id: settlementHarvestId || null }), "Settlement calculated and submitted for approval")}>Calculate settlement</button></div>
        {settlements.map((row) => <article key={row.id} className="rounded-xl border border-white/10 p-3 flex flex-wrap items-center justify-between gap-3 text-sm">
          <span>{row.period_key} · {money(row.amount)} · {row.status}</span>
          <div className="flex gap-2">
            {isApprover && row.status === "pending_approval" && <><button disabled={busy} className="btn-secondary" onClick={() => run(() => projectFinanceAPI.approveSettlement(row.id, true), "Settlement approved")}>Approve</button><button disabled={busy} className="btn-secondary" onClick={() => run(() => projectFinanceAPI.approveSettlement(row.id, false), "Settlement rejected")}>Reject</button></>}
            {isApprover && row.status === "approved" && <><input className="input max-w-48" placeholder="Transaction reference" value={payment[row.id]?.ref || ""} onChange={(e) => setPayment({ ...payment, [row.id]: { ...payment[row.id], ref: e.target.value } })} /><input className="input max-w-48" type="url" placeholder="Payment proof URL" value={payment[row.id]?.proof || ""} onChange={(e) => setPayment({ ...payment, [row.id]: { ...payment[row.id], proof: e.target.value } })} /><button disabled={busy || !payment[row.id]?.ref || !payment[row.id]?.proof} className="btn-primary" onClick={() => run(() => projectFinanceAPI.markSettlementPaid(row.id, { transaction_reference: payment[row.id].ref, proof_url: payment[row.id].proof }), "Settlement payment recorded")}>Mark paid</button></>}
          </div>
        </article>)}
      </div>}
      {investments.length > 0 && <div className="space-y-3 border-t border-white/10 pt-4">
        <h3 className="font-semibold">Investor returns and payouts</h3>
        {investments.map((row) => <article key={row.id} className="rounded-xl border border-white/10 p-3 space-y-2 text-sm">
          <div className="flex flex-wrap justify-between gap-2"><span>Investment {row.id.slice(0, 8)} · {row.revenue_share_percentage ?? 0}% share</span><span>Calculated return {money(row.actual_return ?? row.expected_return)} · {row.status}</span></div>
          {isApprover && ["completed", "settled"].includes(projects.find((p) => p.id === projectId)?.status) && row.status === "active" && <div className="flex flex-wrap gap-2">
            <input className="input max-w-56" placeholder="Transfer reference" value={payment[`invest-${row.id}`]?.ref || ""} onChange={(e) => setPayment({ ...payment, [`invest-${row.id}`]: { ...payment[`invest-${row.id}`], ref: e.target.value } })} />
            <input className="input max-w-56" type="url" placeholder="Payout proof URL" value={payment[`invest-${row.id}`]?.proof || ""} onChange={(e) => setPayment({ ...payment, [`invest-${row.id}`]: { ...payment[`invest-${row.id}`], proof: e.target.value } })} />
            <button disabled={busy || !payment[`invest-${row.id}`]?.ref || !payment[`invest-${row.id}`]?.proof} className="btn-primary" onClick={() => run(() => investmentsAPI.recordPayout(row.id, { transaction_reference: payment[`invest-${row.id}`].ref, proof_url: payment[`invest-${row.id}`].proof }), "Investor payout recorded")}>Record payout</button>
          </div>}
          {row.payout_reference && <p className="text-[#8fac9a]">Paid · {row.payout_reference} · <a className="text-accent underline" href={row.payout_proof_url} target="_blank" rel="noreferrer">View proof</a></p>}
        </article>)}
      </div>}
    </>}
  </section>;
}
