import { useState, useEffect } from "react";
import { notificationsAPI } from "../config/api";
import useAppStore from "../store/useAppStore";

export function useNotifications() {
  const { setNotifications, markNotificationRead, unreadCount } = useAppStore();
  const [loading, setLoading] = useState(false);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await notificationsAPI.list({ page_size: 50 });
      if (res.success) setNotifications(res.data.items);
    } finally {
      setLoading(false);
    }
  };

  const markRead = async (id) => {
    await notificationsAPI.markRead(id);
    markNotificationRead(id);
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  return { loading, unreadCount, fetchNotifications, markRead };
}
