import { LayoutDashboard, ClipboardList, FileText, Leaf, Map, DollarSign } from "lucide-react";

export const AGRI_NAV = [
  { path: "/agri-officer/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { path: "/agri-officer/assignments", icon: ClipboardList, label: "Assignments" },
  { path: "/agri-officer/prescriptions", icon: FileText, label: "Prescriptions" },
  { path: "/agri-officer/crop-design", icon: Leaf, label: "Crop Design" },
  { path: "/agri-officer/farm-visits", icon: Map, label: "Farm Visits" },
  { path: "/agri-officer/quotes", icon: DollarSign, label: "Quotes" },
];
