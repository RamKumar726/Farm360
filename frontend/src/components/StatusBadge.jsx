const statusConfig = {
  // Lead statuses
  new: { label: "New", class: "badge-info" },
  site_visit: { label: "Site Visit", class: "badge-accent" },
  advance_paid: { label: "Advance Paid", class: "badge-warning" },
  won: { label: "Won 🏆", class: "badge-success" },
  completed: { label: "Completed ✓", class: "badge-success" },
  lost: { label: "Lost", class: "badge-error" },

  // Work order statuses
  pending: { label: "Pending", class: "badge-muted" },
  assigned: { label: "Assigned", class: "badge-info" },
  partner_accepted: { label: "Partner Accepted", class: "badge-accent" },
  in_progress: { label: "In Progress", class: "badge-warning" },
  verified: { label: "Verified ✓", class: "badge-success" },
  failed: { label: "Failed", class: "badge-error" },

  // Payment statuses
  paid: { label: "Paid", class: "badge-success" },
  partial: { label: "Partial", class: "badge-warning" },
  reduced: { label: "Reduced", class: "badge-error" },

  // Generic
  active: { label: "Active", class: "badge-success" },
  inactive: { label: "Inactive", class: "badge-muted" },
  draft: { label: "Draft", class: "badge-muted" },
  approved: { label: "Approved", class: "badge-success" },
  rejected: { label: "Rejected", class: "badge-error" },
  settled: { label: "Settled", class: "badge-success" },
  listed: { label: "Listed", class: "badge-info" },
  sold: { label: "Sold 🎉", class: "badge-success" },
};

export default function StatusBadge({ status }) {
  const config = statusConfig[status] || { label: status, class: "badge-muted" };
  return <span className={config.class}>{config.label}</span>;
}
