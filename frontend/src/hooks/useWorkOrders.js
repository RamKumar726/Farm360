import { useState, useEffect, useCallback } from "react";
import { workOrdersAPI } from "../config/api";
import useAppStore from "../store/useAppStore";

export function useWorkOrders(params = {}) {
  const { setWorkOrders } = useAppStore();
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await workOrdersAPI.list(params);
      if (res.success) {
        setData(res.data);
        setWorkOrders(res.data.items);
      }
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => { fetch(); }, [fetch]);

  return { data, loading, error, refetch: fetch };
}
