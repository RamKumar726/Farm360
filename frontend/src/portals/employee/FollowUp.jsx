import PortalPage from "../../components/PortalPage";
import { EMPLOYEE_NAV } from "./_nav";

export default function EmployeeFollowUp() {
  return (
    <PortalPage title="Follow-Up Tracker" subtitle="Track all pending follow-ups and reminders" navItems={EMPLOYEE_NAV}>
      <div className="card">
        <p className="text-[#8fac9a] text-sm">Auto-generated follow-up tasks appear here based on:
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Leads scheduled for site visits</li>
            <li>Customers who've expressed land purchase interest</li>
            <li>Investment leads needing pitch follow-up</li>
            <li>Work orders pending partner acceptance</li>
          </ul>
        </p>
      </div>
    </PortalPage>
  );
}
