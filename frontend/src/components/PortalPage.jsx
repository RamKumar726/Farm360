/**
 * Generic portal page template for pages that share the same list + card pattern.
 * Used across Zone Admin, Employee, Agri Officer, Farm Employee portals.
 */
import AppLayout from "./AppLayout";

export default function PortalPage({ title, subtitle, navItems, children }) {
  return (
    <AppLayout navItems={navItems}>
      <div className="space-y-6 animate-slide-up">
        {(title || subtitle) && (
          <div>
            {title && <h1 className="page-header">{title}</h1>}
            {subtitle && <p className="text-[#8fac9a] mt-1">{subtitle}</p>}
          </div>
        )}
        {children}
      </div>
    </AppLayout>
  );
}
