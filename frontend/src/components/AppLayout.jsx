import { NavLink } from "react-router-dom";
import { LogOut, Menu, X, Leaf } from "lucide-react";
import useAppStore from "../store/useAppStore";
import { useAuth } from "../hooks/useAuth";
import NotificationBell from "./NotificationBell";

export default function AppLayout({ children, navItems }) {
  const { sidebarOpen, toggleSidebar } = useAppStore();
  const { user, logout } = useAuth();

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <aside
        className={`flex flex-col bg-surface border-r border-white/8 transition-all duration-300 ease-in-out z-40
          ${sidebarOpen ? "w-64" : "w-0 md:w-16"} overflow-hidden shrink-0`}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-white/8 shrink-0">
          <div className="p-2 rounded-xl bg-accent/20 shrink-0">
            <Leaf size={20} className="text-accent" />
          </div>
          {sidebarOpen && (
            <div className="overflow-hidden">
              <p className="font-display font-bold text-[#f0ede4] text-sm leading-tight">Prasad Farm</p>
              <p className="text-gradient-gold text-xs font-semibold">Care 360°</p>
            </div>
          )}
        </div>

        {/* Nav items */}
        <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <item.icon size={18} className="shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User info + logout */}
        <div className="px-3 pb-4 border-t border-white/8 pt-4">
          {sidebarOpen && user && (
            <div className="px-2 mb-3">
              <p className="text-sm font-medium text-[#f0ede4] truncate">{user.name}</p>
              <p className="text-xs text-accent capitalize">{user.role?.replace("_", " ")}</p>
            </div>
          )}
          <button onClick={logout} className="sidebar-link w-full text-red-400 hover:text-red-300 hover:bg-red-500/10">
            <LogOut size={18} className="shrink-0" />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-white/8 bg-background/80 backdrop-blur-sm shrink-0">
          <button onClick={toggleSidebar} className="btn-ghost p-2">
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
          <div className="flex items-center gap-3">
            <NotificationBell />
            <div className="h-8 w-8 rounded-full bg-accent/20 border border-accent/30 flex items-center justify-center">
              <span className="text-accent text-sm font-bold">{user?.name?.[0]?.toUpperCase()}</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6 animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
}
