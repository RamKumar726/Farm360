import { MapPin, Calendar, User, ArrowRight } from "lucide-react";
import StatusBadge from "./StatusBadge";

const sourceLabels = {
  website:           "🌐 Website",
  digital_marketing: "📱 Digital Marketing",
  call_message:      "📞 Call / Message",
  referral:          "🤝 Referral",
  employee:          "👤 Employee",
  customer_app:      "📲 Customer App",
};

const typeLabels = {
  site_management:    "Site Management",
  farm_lease:         "Farm Lease",
  farm_manage:        "Farm Manage",
  farm_management:    "Farm Management",
  one_time_service:   "One-Time Service",
  investment_interest:"Investment Interest",
  service_enquiry:    "Service Enquiry",
  sell_land:          "Sell Land",
};

// Service pipeline (11-stage)
const SERVICE_STAGES = [
  "prospecting", "qualification", "need_analysis", "value_proposition",
  "decision_makers", "proposal_price", "negotiation",
  "register_user", "login_guide", "payment", "closed_won",
];

// Lease pipeline (11-stage)
const LEASE_STAGES = [
  "prospecting", "qualification", "need_analysis", "land_verification",
  "feasibility", "commercial_model", "proposal", "negotiation",
  "agreement", "approval", "closed_won",
];

export default function LeadCard({ lead, onClick }) {
  const isLease = lead.type === "farm_lease" || lead.type === "sell_land";
  const stages = isLease ? LEASE_STAGES : SERVICE_STAGES;
  const currentIdx = stages.indexOf(lead.status);
  const progress = currentIdx >= 0 ? ((currentIdx + 1) / stages.length) * 100 : 0;
  const isLost = lead.status === "closed_lost";

  return (
    <div
      className="card hover:border-accent/30 cursor-pointer animate-fade-in flex flex-col gap-3"
      onClick={() => onClick?.(lead)}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <p className="font-semibold text-[#f0ede4] leading-tight">
            {typeLabels[lead.type] || lead.type?.replace(/_/g, " ")}
          </p>
          <p className="text-xs text-[#8fac9a] mt-0.5">{sourceLabels[lead.source] || lead.source}</p>
        </div>
        <StatusBadge status={lead.status} />
      </div>

      {/* Farm Details snippet */}
      {lead.farm_details && (
        <p className="text-sm text-[#8fac9a] line-clamp-2">{lead.farm_details}</p>
      )}

      {/* Stage progress bar */}
      <div className="space-y-1">
        <div className="flex justify-between text-[10px] text-[#8fac9a]">
          <span>Stage {currentIdx >= 0 ? currentIdx + 1 : "—"} of {stages.length}</span>
          <span className={`font-semibold capitalize ${isLost ? "text-red-400" : "text-accent"}`}>
            {lead.status?.replace(/_/g, " ")}
          </span>
        </div>
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${isLost ? "bg-red-500/60" : "bg-accent"}`}
            style={{ width: `${isLost ? 100 : progress}%` }}
          />
        </div>
      </div>

      {/* Footer meta */}
      <div className="flex items-center gap-4 text-xs text-[#8fac9a]">
        {lead.site_visit_date && (
          <span className="flex items-center gap-1">
            <Calendar size={11} /> {lead.site_visit_date}
          </span>
        )}
        {lead.price_to_complete && (
          <span className="flex items-center gap-1 text-accent font-semibold">
            ₹{Number(lead.price_to_complete).toLocaleString()}
          </span>
        )}
        <span className="flex items-center gap-1 ml-auto font-mono">
          #{lead.id?.slice(0, 8)}
        </span>
      </div>
    </div>
  );
}
