import { LayoutDashboard, GitBranch, Map, Users, Target, DollarSign, AlertTriangle, FolderKanban, BarChart3, CheckSquare } from "lucide-react";

export const FOUNDER_NAV = [
  { path: "/founder/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/founder/branches", icon: GitBranch, label: "Branches" },
  { path: "/founder/zones", icon: Map, label: "Zones" },
  { path: "/founder/employees", icon: Users, label: "Employees" },
  { path: "/founder/leads", icon: Target, label: "Leads" },
  { path: "/founder/revenue", icon: DollarSign, label: "Revenue" },
  { path: "/founder/risk", icon: AlertTriangle, label: "Risk & Fraud" },
  { path: "/founder/projects", icon: FolderKanban, label: "Projects" },
  { path: "/founder/analytics", icon: BarChart3, label: "Analytics" },
  { path: "/founder/approvals", icon: CheckSquare, label: "Approvals" },
];
