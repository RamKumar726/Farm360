import { LayoutDashboard, Target, ClipboardList, MapPin, TrendingUp, Users, FileCheck } from "lucide-react";

export const EMPLOYEE_NAV = [
  { path: "/employee/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/employee/leads", icon: Target, label: "Lead Pipeline" },
  { path: "/employee/work-queue", icon: ClipboardList, label: "Work Queue" },
  { path: "/employee/land-leads", icon: MapPin, label: "Land Sales · Coming Soon" },
  { path: "/employee/investment-leads", icon: TrendingUp, label: "Investments · Coming Soon" },
  { path: "/employee/partners", icon: Users, label: "Partner Assignment" },
  { path: "/employee/follow-up", icon: FileCheck, label: "Follow-Up" },
];
