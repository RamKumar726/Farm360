import { Store, LayoutDashboard, Leaf, FileText, Wrench, Activity, TrendingUp, MapPin, CreditCard, HelpCircle } from "lucide-react";

export const CUSTOMER_NAV = [
  { path: "/customer/marketplace", icon: Store, label: "Marketplace" },
  { path: "/customer/dashboard", icon: LayoutDashboard, label: "My Dashboard" },
  { path: "/customer/my-farm", icon: Leaf, label: "My Farm" },
  { path: "/customer/agreements", icon: FileText, label: "Agreements" },
  { path: "/customer/work-details", icon: Wrench, label: "Work Details" },
  { path: "/customer/crop-health", icon: Activity, label: "Crop Health" },
  { path: "/customer/investments", icon: TrendingUp, label: "Investments" },
  { path: "/customer/land-sale", icon: MapPin, label: "Land Sale" },
  { path: "/customer/payments", icon: CreditCard, label: "Payments" },
  { path: "/customer/services", icon: HelpCircle, label: "Services" },
];
