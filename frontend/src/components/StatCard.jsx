import { TrendingUp, TrendingDown } from "lucide-react";

export default function StatCard({ title, value, subtitle, trend, trendLabel, icon: Icon, color = "accent" }) {
  const isPositive = trend > 0;
  const colorMap = {
    accent: "text-accent",
    green: "text-green-400",
    blue: "text-blue-400",
    red: "text-red-400",
  };

  return (
    <div className="card-stat group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-[#8fac9a] font-medium">{title}</p>
          <p className={`text-3xl font-display font-bold mt-1 ${colorMap[color]}`}>{value}</p>
          {subtitle && <p className="text-xs text-[#8fac9a] mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl bg-white/5 ${colorMap[color]} group-hover:scale-110 transition-transform duration-300`}>
            <Icon size={22} />
          </div>
        )}
      </div>
      {trend !== undefined && (
        <div className={`flex items-center gap-1 text-sm mt-3 ${isPositive ? "text-green-400" : "text-red-400"}`}>
          {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          <span className="font-medium">{Math.abs(trend)}%</span>
          {trendLabel && <span className="text-[#8fac9a]">{trendLabel}</span>}
        </div>
      )}
    </div>
  );
}
