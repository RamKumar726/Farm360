import { create } from "zustand";

const useAppStore = create((set, get) => ({
  // Auth state
  user: null,
  isAuthenticated: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),
  clearUser: () => set({ user: null, isAuthenticated: false }),

  // Notifications
  notifications: [],
  unreadCount: 0,
  setNotifications: (notifications) =>
    set({
      notifications,
      unreadCount: notifications.filter((n) => !n.is_read).length,
    }),

  markNotificationRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, is_read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  // Global loading
  isLoading: false,
  setLoading: (val) => set({ isLoading: val }),

  // Sidebar state
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

  // Lead pipeline (cached)
  leads: [],
  setLeads: (leads) => set({ leads }),

  // Work orders (cached)
  workOrders: [],
  setWorkOrders: (workOrders) => set({ workOrders }),
}));

export default useAppStore;
