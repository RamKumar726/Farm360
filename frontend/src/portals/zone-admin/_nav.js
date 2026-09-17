import { LayoutDashboard, Target, Users, Wrench, DollarSign, Handshake, Map, AlertOctagon } from "lucide-react";

export const ZONE_ADMIN_NAV = [
  { path: "/zone-admin/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/zone-admin/leads", icon: Target, label: "Leads" },
  { path: "/zone-admin/employees", icon: Users, label: "Employees" },
  { path: "/zone-admin/work", icon: Wrench, label: "Work Management" },
  { path: "/zone-admin/revenue", icon: DollarSign, label: "Revenue" },
  { path: "/zone-admin/brokers", icon: Handshake, label: "Brokers" },
  { path: "/zone-admin/visits", icon: Map, label: "Visits" },
  { path: "/zone-admin/escalations", icon: AlertOctagon, label: "Escalations" },
];
