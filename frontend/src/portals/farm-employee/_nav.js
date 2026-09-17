import { LayoutDashboard, Map, Camera, Eye, Package, AlertTriangle } from "lucide-react";

export const FARM_EMP_NAV = [
  { path: "/farm-employee/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/farm-employee/visits", icon: Map, label: "My Visits" },
  { path: "/farm-employee/submit-proof", icon: Camera, label: "Submit Proof" },
  { path: "/farm-employee/monitor", icon: Eye, label: "Work Monitor" },
  { path: "/farm-employee/harvest", icon: Package, label: "Harvest" },
  { path: "/farm-employee/incident", icon: AlertTriangle, label: "Report Incident" },
];
