import { useState, useRef, useEffect } from "react";
import { Bell, Check, X } from "lucide-react";
import useAppStore from "../store/useAppStore";
import { useNotifications } from "../hooks/useNotifications";

export default function NotificationBell() {
  const { notifications, unreadCount } = useAppStore();
  const { markRead } = useNotifications();
  const [open, setOpen] = useState(false);
  const ref = useRef();

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2.5 rounded-xl hover:bg-white/10 transition-colors duration-200"
      >
        <Bell size={20} className="text-[#8fac9a]" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] bg-accent text-primary-900 text-[10px] font-bold rounded-full flex items-center justify-center px-1 animate-pulse-slow">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-12 w-80 bg-surface border border-white/10 rounded-2xl shadow-card z-50 overflow-hidden animate-slide-up">
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/8">
            <h3 className="font-semibold text-[#f0ede4]">Notifications</h3>
            {unreadCount > 0 && (
              <span className="text-xs text-accent">{unreadCount} unread</span>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="text-center py-8 text-[#8fac9a]">
                <Bell size={32} className="mx-auto mb-2 opacity-40" />
                <p className="text-sm">No notifications</p>
              </div>
            ) : (
              notifications.slice(0, 20).map((n) => (
                <div
                  key={n.id}
                  className={`px-4 py-3 border-b border-white/5 flex gap-3 transition-colors ${!n.is_read ? "bg-accent/5" : ""}`}
                >
                  <div className="flex-1">
                    <p className="text-sm text-[#f0ede4] leading-relaxed">{n.message}</p>
                    <p className="text-xs text-[#8fac9a] mt-0.5">{new Date(n.created_at).toLocaleString()}</p>
                  </div>
                  {!n.is_read && (
                    <button
                      onClick={() => markRead(n.id)}
                      className="text-accent hover:text-green-400 transition-colors shrink-0"
                    >
                      <Check size={14} />
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
