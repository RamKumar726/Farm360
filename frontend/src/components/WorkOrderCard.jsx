import { Calendar, User, MapPin, Wrench } from "lucide-react";
import StatusBadge from "./StatusBadge";

const typeLabels = {
  cleaning: "🧹 Cleaning",
  securing: "🔒 Securing",
  irrigation: "💧 Irrigation",
  electric: "⚡ Electric",
  harvest: "🌾 Harvest",
  soil_water_test: "🧪 Soil & Water Test",
  cropping: "🌱 Cropping",
  land_leveling: "📐 Land Leveling",
  pruning: "✂️ Pruning",
  fertilizer_pestcontrol: "🌿 Fertilizer/Pest Control",
  monitoring: "👁️ Monitoring",
  construction: "🏗️ Construction",
};

export default function WorkOrderCard({ workOrder, onClick }) {
  return (
    <div
      className="card hover:border-accent/30 cursor-pointer animate-fade-in"
      onClick={() => onClick?.(workOrder)}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-semibold text-[#f0ede4]">
            {typeLabels[workOrder.type] || workOrder.type}
          </p>
          <p className="text-xs text-[#8fac9a] font-mono mt-0.5">#{workOrder.id?.slice(0, 8)}</p>
        </div>
        <StatusBadge status={workOrder.status} />
      </div>

      <div className="space-y-1.5 text-sm text-[#8fac9a]">
        {workOrder.start_date && (
          <div className="flex items-center gap-2">
            <Calendar size={13} />
            <span>{workOrder.start_date} → {workOrder.end_date || "TBD"}</span>
          </div>
        )}
        {workOrder.farm_employee_id && (
          <div className="flex items-center gap-2">
            <User size={13} />
            <span>Employee: #{workOrder.farm_employee_id.slice(0, 8)}</span>
          </div>
        )}
      </div>

      <div className="mt-3 pt-3 border-t border-white/5 flex items-center justify-between">
        <StatusBadge status={workOrder.payment_status} />
        {workOrder.outsourcing_partner_id && (
          <span className="text-xs text-accent">🤝 Partner assigned</span>
        )}
      </div>
    </div>
  );
}
