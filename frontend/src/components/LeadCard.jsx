import { MapPin, Calendar, User } from "lucide-react";
import StatusBadge from "./StatusBadge";

const sourceLabels = {
  website: "🌐 Website",
  digital_marketing: "📱 Digital Marketing",
  call_message: "📞 Call/Message",
  referral: "🤝 Referral",
  employee: "👤 Employee",
};

const typeLabels = {
  site_management: "Site Management",
  farm_lease: "Farm Lease",
  farm_manage: "Farm Manage",
  farm_management: "Farm Management",
};

export default function LeadCard({ lead, onClick }) {
  return (
    <div
      className="card hover:border-accent/30 cursor-pointer animate-fade-in"
      onClick={() => onClick?.(lead)}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-semibold text-[#f0ede4]">{typeLabels[lead.type] || lead.type}</p>
          <p className="text-xs text-[#8fac9a] mt-0.5">{sourceLabels[lead.source] || lead.source}</p>
        </div>
        <StatusBadge status={lead.status} />
      </div>

      {lead.farm_details && (
        <p className="text-sm text-[#8fac9a] mb-3 line-clamp-2">{lead.farm_details}</p>
      )}

      <div className="flex items-center gap-4 text-xs text-[#8fac9a]">
        {lead.site_visit_date && (
          <span className="flex items-center gap-1">
            <Calendar size={12} /> {lead.site_visit_date}
          </span>
        )}
        <span className="flex items-center gap-1">
          <User size={12} /> {lead.id?.slice(0, 8)}
        </span>
      </div>

      {/* State machine progress */}
      <div className="mt-4">
        <div className="flex items-center gap-1">
          {["new", "site_visit", "advance_paid", "won", "completed"].map((step, i) => {
            const steps = ["new", "site_visit", "advance_paid", "won", "completed"];
            const currentIdx = steps.indexOf(lead.status);
            const isCurrent = lead.status === step;
            const isPast = currentIdx > i;
            const isLost = lead.status === "lost";
            return (
              <div key={step} className="flex items-center flex-1">
                <div
                  className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${
                    isLost ? "bg-red-500/40" :
                    isPast ? "bg-accent" :
                    isCurrent ? "bg-accent/60" :
                    "bg-white/10"
                  }`}
                />
              </div>
            );
          })}
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-[10px] text-[#8fac9a]">New</span>
          <span className="text-[10px] text-[#8fac9a]">Complete</span>
        </div>
      </div>
    </div>
  );
}
