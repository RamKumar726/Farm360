import { Clock3 } from "lucide-react";
import PortalPage from "./PortalPage";

export default function ComingSoonPage({ title, navItems }) {
  return (
    <PortalPage title={title} subtitle="This module is intentionally unavailable until its commercial and legal workflow is approved." navItems={navItems}>
      <section className="card max-w-2xl mx-auto text-center py-14 px-6">
        <Clock3 size={42} className="mx-auto text-[#c9a84c] mb-4" aria-hidden="true" />
        <h2 className="section-title">Coming Soon</h2>
        <p className="text-[#8fac9a] mt-3">
          No applications, payments, listings or approvals can be submitted from this module yet.
        </p>
      </section>
    </PortalPage>
  );
}
