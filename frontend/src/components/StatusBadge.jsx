const statusConfig = {
  // ── New 11-stage Lead Pipeline Statuses ─────────────────────────────
  prospecting:      { label: "🌱 Prospecting",       class: "badge-info" },
  qualification:    { label: "🔍 Qualification",     class: "badge-accent" },
  need_analysis:    { label: "📋 Need Analysis",     class: "badge-accent" },
  value_proposition:{ label: "💡 Value Prop",        class: "badge-warning" },
  decision_makers:  { label: "👥 Decision Makers",   class: "badge-warning" },
  proposal_price:   { label: "📄 Proposal / Price",  class: "badge-warning" },
  negotiation:      { label: "🤝 Negotiation",       class: "badge-warning" },
  register_user:    { label: "📲 Register User",     class: "badge-info" },
  login_guide:      { label: "🔐 Login Guide",       class: "badge-info" },
  payment:          { label: "💳 Payment",            class: "badge-accent" },
  closed_won:       { label: "🏆 Closed Won",        class: "badge-success" },
  closed_lost:      { label: "❌ Closed Lost",       class: "badge-error" },

  // ── Lease Pipeline Stages ────────────────────────────────────────────
  land_verification:{ label: "🗺️ Land Verification", class: "badge-info" },
  feasibility:      { label: "🔬 Feasibility",       class: "badge-accent" },
  commercial_model: { label: "💼 Commercial Model",  class: "badge-warning" },
  proposal:         { label: "📃 Proposal",          class: "badge-warning" },
  agreement:        { label: "📜 Agreement",         class: "badge-accent" },
  approval:         { label: "✅ Approval",           class: "badge-success" },

  // ── Work Order Statuses ─────────────────────────────────────────────
  pending:          { label: "Pending",              class: "badge-muted" },
  assigned:         { label: "Assigned",             class: "badge-info" },
  partner_accepted: { label: "Partner Accepted",     class: "badge-accent" },
  in_progress:      { label: "In Progress",          class: "badge-warning" },
  verified:         { label: "Verified ✓",           class: "badge-success" },
  failed:           { label: "Failed",               class: "badge-error" },

  // ── Payment Statuses ─────────────────────────────────────────────────
  paid:             { label: "Paid",                 class: "badge-success" },
  partial:          { label: "Partial",              class: "badge-warning" },
  reduced:          { label: "Reduced",              class: "badge-error" },

  // ── Generic ──────────────────────────────────────────────────────────
  active:           { label: "Active",               class: "badge-success" },
  inactive:         { label: "Inactive",             class: "badge-muted" },
  draft:            { label: "Draft",                class: "badge-muted" },
  approved:         { label: "Approved",             class: "badge-success" },
  rejected:         { label: "Rejected",             class: "badge-error" },
  settled:          { label: "Settled",              class: "badge-success" },
  listed:           { label: "Listed",               class: "badge-info" },
  sold:             { label: "Sold 🎉",              class: "badge-success" },

  // ── Legacy (backward compat) ─────────────────────────────────────────
  new:              { label: "New",                  class: "badge-info" },
  site_visit:       { label: "Site Visit",           class: "badge-accent" },
  advance_paid:     { label: "Advance Paid",         class: "badge-warning" },
  won:              { label: "Won 🏆",               class: "badge-success" },
  completed:        { label: "Completed ✓",          class: "badge-success" },
  lost:             { label: "Lost",                 class: "badge-error" },
};

export default function StatusBadge({ status }) {
  const config = statusConfig[status] || { label: status?.replace(/_/g, " ") || "—", class: "badge-muted" };
  return <span className={config.class}>{config.label}</span>;
}
