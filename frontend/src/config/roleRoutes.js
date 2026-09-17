/**
 * Maps each user role to their default landing route and allowed portal prefix.
 */
export const ROLE_ROUTES = {
  founder: {
    defaultPath: "/founder/dashboard",
    prefix: "/founder",
    label: "Founder",
  },
  zone_admin: {
    defaultPath: "/zone-admin/dashboard",
    prefix: "/zone-admin",
    label: "Zone Admin",
  },
  employee: {
    defaultPath: "/employee/dashboard",
    prefix: "/employee",
    label: "Employee",
  },
  agri_officer: {
    defaultPath: "/agri-officer/dashboard",
    prefix: "/agri-officer",
    label: "Agriculture Officer",
  },
  farm_employee: {
    defaultPath: "/farm-employee/dashboard",
    prefix: "/farm-employee",
    label: "Farm Employee",
  },
  customer: {
    defaultPath: "/customer/marketplace",
    prefix: "/customer",
    label: "Customer",
  },
  real_estate: {
    defaultPath: "/customer/land-sale",
    prefix: "/customer",
    label: "Real Estate",
  },
  broker: {
    defaultPath: "/customer/marketplace",
    prefix: "/customer",
    label: "Broker",
  },
};

export function getDefaultRoute(role) {
  return ROLE_ROUTES[role]?.defaultPath || "/login";
}

export function canAccessPath(role, path) {
  const route = ROLE_ROUTES[role];
  if (!route) return false;
  // Founder can access everything
  if (role === "founder") return true;
  return path.startsWith(route.prefix);
}
