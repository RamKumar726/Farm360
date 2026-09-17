import { Camera, MapPin, Clock, FileText } from "lucide-react";
import StatusBadge from "./StatusBadge";

const typeLabels = {
  new_lead_visit: "🔍 New Lead Visit",
  auto_visit: "🤖 Auto Visit",
  assign_visit: "📋 Assigned Visit",
  sale_visit: "🏷️ Sale Visit",
  random_visit: "🎲 Random Visit",
};

export default function VisitCard({ visit, onClick }) {
  const photoCount = visit.proof_photos?.length || 0;

  return (
    <div
      className="card hover:border-accent/30 cursor-pointer animate-fade-in"
      onClick={() => onClick?.(visit)}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-semibold text-[#f0ede4]">{typeLabels[visit.type] || visit.type}</p>
          <p className="text-xs text-[#8fac9a] font-mono mt-0.5">#{visit.id?.slice(0, 8)}</p>
        </div>
        <StatusBadge status={visit.status} />
      </div>

      <div className="space-y-1.5 text-sm text-[#8fac9a]">
        {visit.gps_lat && visit.gps_lng && (
          <div className="flex items-center gap-2">
            <MapPin size={13} className="text-accent" />
            <span className="font-mono text-xs">{visit.gps_lat?.toFixed(4)}, {visit.gps_lng?.toFixed(4)}</span>
          </div>
        )}
        {visit.visited_at && (
          <div className="flex items-center gap-2">
            <Clock size={13} />
            <span>{new Date(visit.visited_at).toLocaleString()}</span>
          </div>
        )}
        {visit.notes && (
          <div className="flex items-start gap-2">
            <FileText size={13} className="mt-0.5" />
            <span className="line-clamp-2">{visit.notes}</span>
          </div>
        )}
      </div>

      {/* Proof indicators */}
      <div className="mt-3 pt-3 border-t border-white/5 flex items-center gap-3">
        {photoCount > 0 && (
          <span className="flex items-center gap-1 text-xs text-green-400">
            <Camera size={12} /> {photoCount} photos
          </span>
        )}
        {visit.proof_video_url && (
          <span className="text-xs text-blue-400">🎥 Video</span>
        )}
        {!photoCount && !visit.proof_video_url && (
          <span className="text-xs text-[#8fac9a]">No proof submitted yet</span>
        )}
      </div>
    </div>
  );
}
