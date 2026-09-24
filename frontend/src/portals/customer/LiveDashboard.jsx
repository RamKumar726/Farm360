import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import PortalPage from "../../components/PortalPage";
import { CUSTOMER_NAV } from "./_nav";
import ProjectDetailsView from "./ProjectDetailsView";
import { agreementsAPI, farmsAPI, investmentsAPI, projectsAPI, workOrdersAPI } from "../../config/api";

const badge = (status) => status?.replaceAll("_", " ") || "unknown";

export default function LiveDashboard() {
  const [data, setData] = useState({ farms: [], projects: [], work: [], agreements: [], investments: [] });
  const [selectedProject, setSelectedProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = async () => {
    setLoading(true);
    setError("");
    try {
      const [farms, projects, work, agreements, investments] = await Promise.all([
        farmsAPI.list(), projectsAPI.list(), workOrdersAPI.list(), agreementsAPI.list(), investmentsAPI.list(),
      ]);
      setData({
        farms: farms.data?.items || [], projects: projects.data?.items || [],
        work: work.data?.items || [], agreements: agreements.data?.items || [],
        investments: investments.data?.items || [],
      });
    } catch (e) {
      setError(e?.response?.data?.detail || e?.detail || "Could not load your live Farm360 data.");
    } finally { setLoading(false); }
  };
  useEffect(() => { refresh(); }, []);

  if (selectedProject) return <ProjectDetailsView project={selectedProject} onBack={() => setSelectedProject(null)} />;
  return <PortalPage title="My Dashboard" subtitle="Your farms, projects, work and investment records" navItems={CUSTOMER_NAV}>
    <div className="space-y-6">
      {error && <div role="alert" className="card border-red-500/30 text-red-300">{error} <button className="underline ml-2" onClick={refresh}>Retry</button></div>}
      {loading ? <div className="card text-center text-[#8fac9a]">Loading your records…</div> : <>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {[["Farms", data.farms.length], ["Projects", data.projects.length], ["Open work", data.work.filter((w) => !["completed", "failed"].includes(w.status)).length], ["Investments", data.investments.length]].map(([title, value]) => <article key={title} className="card"><p className="text-xs text-[#8fac9a]">{title}</p><p className="text-2xl font-bold text-accent">{value}</p></article>)}
        </div>

        <section className="space-y-3">
          <div className="flex justify-between items-center"><h2 className="section-title">My farms</h2><Link className="text-sm text-accent underline" to="/customer/my-farm">Manage my farm</Link></div>
          <div className="grid md:grid-cols-2 gap-3">
            {data.farms.map((farm) => <article key={farm.id} className="card"><h3 className="font-semibold">{farm.location || "Farm location to be confirmed"}</h3><p className="text-sm text-[#8fac9a]">{farm.area ? `${farm.area} acres` : "Area not recorded"} · {farm.soil_type || "Soil details not recorded"}</p></article>)}
            {!data.farms.length && <p className="card text-sm text-[#8fac9a]">No farm records yet. Use Manage My Farm to request the service.</p>}
          </div>
        </section>

        <section className="space-y-3">
          <div className="flex justify-between items-center"><h2 className="section-title">My agreements</h2><Link to="/customer/agreements" className="text-sm text-accent underline">All agreements</Link></div>
          <div className="grid md:grid-cols-2 gap-3">{data.agreements.slice(0, 4).map((agreement) => <article key={agreement.id} className="card flex flex-wrap justify-between gap-2"><span className="capitalize">{badge(agreement.type)} agreement · {badge(agreement.status)}</span>{agreement.document_url && <a className="text-accent underline" href={agreement.document_url} target="_blank" rel="noreferrer">View document</a>}</article>)}{!data.agreements.length && <p className="card text-sm text-[#8fac9a]">No agreements are available.</p>}</div>
        </section>

        <section className="space-y-3">
          <h2 className="section-title">My projects</h2>
          <div className="grid md:grid-cols-2 gap-3">
            {data.projects.map((project) => <article key={project.id} className="card space-y-2">
              <div className="flex justify-between gap-2"><h3 className="font-semibold">{project.name}</h3><span className="text-xs text-accent capitalize">{badge(project.status)}</span></div>
              <p className="text-xs text-[#8fac9a] capitalize">{badge(project.type)}{project.crop_name ? ` · ${project.crop_name}` : ""}</p>
              {project.subscription_end && <p className="text-xs text-[#8fac9a]">Subscription through {project.subscription_end}</p>}
              <button className="btn-secondary text-sm" onClick={() => setSelectedProject(project)}>View project</button>
            </article>)}
            {!data.projects.length && <p className="card text-sm text-[#8fac9a]">No projects have been created for your account yet.</p>}
          </div>
        </section>

        <section className="space-y-3">
          <div className="flex justify-between items-center"><h2 className="section-title">Recent field work</h2><Link to="/customer/work-details" className="text-sm text-accent underline">All work</Link></div>
          <div className="space-y-2">{data.work.slice(0, 6).map((work) => <article key={work.id} className="card flex flex-wrap justify-between gap-2 text-sm"><span className="capitalize">{badge(work.type)}{work.start_date ? ` · ${work.start_date}` : ""}</span><span className="text-accent capitalize">{badge(work.status)}</span></article>)}{!data.work.length && <p className="card text-sm text-[#8fac9a]">No work orders have been assigned yet.</p>}</div>
        </section>
      </>}
    </div>
  </PortalPage>;
}
