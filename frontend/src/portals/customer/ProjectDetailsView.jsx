import { useEffect, useState } from "react";
import { agreementsAPI, harvestsAPI, issuesAPI, projectFinanceAPI, workOrdersAPI } from "../../config/api";

const label = (value) => value?.replaceAll("_", " ") || "—";
const money = (value) => `₹${Number(value || 0).toLocaleString("en-IN")}`;

function proofItems(raw) {
  if (!raw) return [];
  try { const value = JSON.parse(raw); return Array.isArray(value) ? value : [value]; }
  catch { return raw.split(",").map((item) => item.trim()).filter(Boolean); }
}

export default function ProjectDetailsView({ project, onBack }) {
  const [tab, setTab] = useState("overview");
  const [data, setData] = useState({ work: [], issues: [], expenses: [], settlements: [], harvests: [], agreements: [], contracts: [] });
  const [draft, setDraft] = useState({ title: "", description: "", severity: "medium" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const refresh = async () => {
    if (!project?.id) return;
    setError("");
    try {
      const [work, issues, expenses, settlements, harvests, agreements, contracts] = await Promise.all([
        workOrdersAPI.list(), issuesAPI.list(), projectFinanceAPI.expenses(project.id),
        projectFinanceAPI.settlements(project.id), harvestsAPI.list({ project_id: project.id }), agreementsAPI.list(),
        projectFinanceAPI.outsourcingContracts(project.id),
      ]);
      setData({
        work: (work.data?.items || []).filter((row) => row.project_id === project.id),
        issues: (issues.data?.items || []).filter((row) => row.project_id === project.id),
        expenses: expenses.data || [], settlements: settlements.data || [],
        harvests: (harvests.data?.items || []),
        agreements: (agreements.data?.items || []).filter((row) => row.project_id === project.id),
        contracts: contracts.data || [],
      });
    } catch (e) { setError(e?.response?.data?.detail || e?.detail || "Could not load project records."); }
  };
  useEffect(() => { refresh(); }, [project?.id]);

  const submitIssue = async (event) => {
    event.preventDefault();
    setSaving(true);
    try {
      await issuesAPI.create({ ...draft, project_id: project.id });
      setDraft({ title: "", description: "", severity: "medium" });
      await refresh();
    } catch (e) { setError(e?.response?.data?.detail || e?.detail || "Could not submit issue."); }
    finally { setSaving(false); }
  };

  if (!project) return null;
  const tabs = ["overview", "work & proof", "finance", "issues", "agreements"];
  return <main className="min-h-screen bg-[#fbf9f4] text-[#1f2824]">
    <header className="sticky top-0 z-20 bg-[#143628] text-white px-4 py-3">
      <button className="text-sm underline" onClick={onBack}>← My dashboard</button>
    </header>
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-5">
      <section className="bg-[#143628] text-white rounded-2xl p-5">
        <p className="text-xs uppercase tracking-wide text-[#c4a462]">{label(project.type)} · {label(project.status)}</p>
        <h1 className="text-2xl font-bold mt-1">{project.name}</h1>
        {project.crop_name && <p className="text-sm mt-2">Crop: {project.crop_name}</p>}
        <p className="text-sm text-[#d0dfc5] mt-2">{project.description || "No project notes recorded."}</p>
        {project.subscription_end && <p className="text-xs mt-2">Farm management through {project.subscription_end}</p>}
      </section>

      <nav className="flex flex-wrap gap-2" aria-label="Project sections">
        {tabs.map((name) => <button key={name} onClick={() => setTab(name)} className={`px-3 py-2 rounded-lg text-sm capitalize ${tab === name ? "bg-[#143628] text-white" : "bg-[#e2ebe4] text-[#143628]"}`}>{name}</button>)}
      </nav>
      {error && <div role="alert" className="rounded-xl border border-red-300 bg-red-50 p-3 text-sm text-red-800">{error} <button className="underline ml-2" onClick={refresh}>Retry</button></div>}

      {tab === "overview" && <section className="grid sm:grid-cols-2 gap-3">
        {[["Project amount", money(project.total_amount)], ["Investment funded", money(project.funded_amount)], ["Project revenue", money(project.total_revenue)], ["Project expenses", money(project.total_expenses)], ["Landowner settlement", money(project.landowner_settlement)], ["Net project result", money(project.net_profit)]].map(([name, value]) => <article className="rounded-xl bg-white border border-[#e8e2d5] p-4" key={name}><p className="text-xs text-[#6b7770]">{name}</p><p className="text-lg font-bold text-[#143628]">{value}</p></article>)}
        {data.harvests.map((harvest) => <article key={harvest.id} className="rounded-xl bg-white border border-[#e8e2d5] p-4"><p className="font-semibold">{harvest.crop_name || "Harvest"} · {harvest.harvest_date || "Date not recorded"}</p><p className="text-sm text-[#6b7770]">{harvest.yield_quantity || 0} {harvest.yield_unit || "kg"} · Sale {money(harvest.gross_revenue)} · {harvest.is_revenue_received ? "payment received" : "payment pending"}</p></article>)}
      </section>}

      {tab === "work & proof" && <section className="space-y-3">
        {data.work.map((work) => <article key={work.id} className="rounded-xl bg-white border border-[#e8e2d5] p-4 space-y-2"><div className="flex justify-between gap-3"><h2 className="font-semibold capitalize">{label(work.type)}</h2><span className="text-sm text-[#2c5e47] capitalize">{label(work.status)}</span></div><p className="text-sm text-[#6b7770]">{work.notes || "No instructions recorded."}</p><p className="text-xs text-[#6b7770]">Scheduled: {work.start_date || "Not scheduled"}</p>{proofItems(work.proof_urls).map((url) => <a key={url} className="text-sm text-[#143628] underline block" href={url} target="_blank" rel="noreferrer">View proof</a>)}</article>)}
        {!data.work.length && <p className="rounded-xl bg-white p-4 text-sm text-[#6b7770]">No work orders are linked to this project.</p>}
      </section>}

      {tab === "finance" && <section className="space-y-4">
        <div className="grid sm:grid-cols-2 gap-3">{[["Received harvest revenue", data.harvests.filter((row) => row.is_revenue_received).reduce((sum, row) => sum + Number(row.gross_revenue || 0), 0)], ["Approved expenses", data.expenses.filter((row) => ["approved", "paid"].includes(row.status)).reduce((sum, row) => sum + Number(row.amount || 0), 0)]].map(([title, value]) => <article key={title} className="rounded-xl bg-white border border-[#e8e2d5] p-4"><p className="text-xs text-[#6b7770]">{title}</p><p className="text-lg font-bold">{money(value)}</p></article>)}</div>
        <h2 className="font-semibold">Expenses</h2>{data.expenses.map((row) => <article key={row.id} className="rounded-xl bg-white border border-[#e8e2d5] p-3 text-sm flex justify-between gap-3"><span>{row.category}{row.vendor ? ` · ${row.vendor}` : ""}</span><span>{money(row.amount)} · {label(row.status)}</span></article>)}{!data.expenses.length && <p className="text-sm text-[#6b7770]">No expenses recorded.</p>}
        <h2 className="font-semibold">Landowner settlements</h2>{data.settlements.map((row) => <article key={row.id} className="rounded-xl bg-white border border-[#e8e2d5] p-3 text-sm flex justify-between gap-3"><span>{row.period_key}</span><span>{money(row.amount)} · {label(row.status)}</span></article>)}{!data.settlements.length && <p className="text-sm text-[#6b7770]">No settlements recorded.</p>}
      </section>}

      {tab === "issues" && <section className="space-y-4">
        <form onSubmit={submitIssue} className="rounded-xl bg-white border border-[#e8e2d5] p-4 space-y-3"><h2 className="font-semibold">Raise a project issue</h2><input className="input" required placeholder="Issue title" value={draft.title} onChange={(e) => setDraft({ ...draft, title: e.target.value })} /><textarea className="input" placeholder="Describe the issue" value={draft.description} onChange={(e) => setDraft({ ...draft, description: e.target.value })} /><select className="input" value={draft.severity} onChange={(e) => setDraft({ ...draft, severity: e.target.value })}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select><button disabled={saving} className="btn-primary">{saving ? "Sending…" : "Submit issue"}</button></form>
        {data.issues.map((issue) => <article key={issue.id} className="rounded-xl bg-white border border-[#e8e2d5] p-4 flex justify-between gap-3"><span>{issue.title}</span><span className="text-sm capitalize">{label(issue.severity)} · {label(issue.status)}</span></article>)}
        {!data.issues.length && <p className="text-sm text-[#6b7770]">No issues have been reported for this project.</p>}
      </section>}

      {tab === "agreements" && <section className="space-y-3">{data.agreements.map((agreement) => <article key={agreement.id} className="rounded-xl bg-white border border-[#e8e2d5] p-4"><h2 className="font-semibold capitalize">{label(agreement.type)} · {label(agreement.status)}</h2><p className="text-sm text-[#6b7770]">{agreement.start_date || "—"} to {agreement.end_date || "—"} · {money(agreement.amount)}</p>{agreement.payment_terms && <pre className="text-xs whitespace-pre-wrap mt-2">{agreement.payment_terms}</pre>}{agreement.document_url && <a href={agreement.document_url} target="_blank" rel="noreferrer" className="text-sm text-[#143628] underline">Open agreement document</a>}</article>)}{!data.agreements.length && <p className="text-sm text-[#6b7770]">No agreements are linked to this project.</p>}<h2 className="font-semibold pt-3">Outsourcing contracts</h2>{data.contracts.map((row) => <article key={row.id} className="rounded-xl bg-white border border-[#e8e2d5] p-4"><h3 className="font-semibold">Provider contract · {money(row.amount)} · {label(row.status)}</h3><p className="text-sm text-[#6b7770]">{row.scope}</p>{row.terms && <p className="text-xs mt-2">{row.terms}</p>}<a href={row.document_url} target="_blank" rel="noreferrer" className="text-sm text-[#143628] underline">Open signed contract</a></article>)}{!data.contracts.length && <p className="text-sm text-[#6b7770]">No outsourcing contracts are linked to this project.</p>}</section>}
    </div>
  </main>;
}
