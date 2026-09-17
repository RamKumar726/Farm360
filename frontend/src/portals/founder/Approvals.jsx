import AppLayout from "../../components/AppLayout";
import { FOUNDER_NAV } from "./_nav";
import { CheckSquare, Clock } from "lucide-react";

export default function FounderApprovals() {
  return (
    <AppLayout navItems={FOUNDER_NAV}>
      <div className="space-y-6">
        <h1 className="page-header">Approvals Queue</h1>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { title: "Pending Crop Designs", count: 0, color: "text-yellow-400", icon: Clock },
            { title: "Lease Prescriptions", count: 0, color: "text-accent", icon: CheckSquare },
            { title: "Investment Settlements", count: 0, color: "text-green-400", icon: CheckSquare },
          ].map((item) => (
            <div key={item.title} className="card text-center">
              <item.icon size={32} className={`mx-auto mb-2 ${item.color}`} />
              <p className="font-semibold text-[#f0ede4]">{item.title}</p>
              <p className={`text-3xl font-bold mt-1 ${item.color}`}>{item.count}</p>
              <p className="text-xs text-[#8fac9a] mt-1">pending approval</p>
            </div>
          ))}
        </div>
        <div className="card">
          <p className="text-[#8fac9a] text-sm">
            Lease-type prescriptions from Agriculture Officers are routed here for Founder approval before work begins.
            Managed customer work orders requiring payment confirmation also appear here.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}
