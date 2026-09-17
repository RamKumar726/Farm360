import PortalPage from "../../components/PortalPage";
import { ZONE_ADMIN_NAV } from "./_nav";
import StatCard from "../../components/StatCard";
import { DollarSign } from "lucide-react";

export default function ZoneAdminRevenue() {
  return (
    <PortalPage title="Branch Revenue" navItems={ZONE_ADMIN_NAV}>
      <div className="grid grid-cols-2 gap-4">
        <StatCard title="Monthly Revenue" value="—" icon={DollarSign} color="accent" />
        <StatCard title="Pending Payments" value="—" icon={DollarSign} color="red" />
      </div>
      <div className="card"><p className="text-[#8fac9a] text-sm">Branch revenue analytics will display agreement totals, investment activity, and project revenue scoped to this branch.</p></div>
    </PortalPage>
  );
}
