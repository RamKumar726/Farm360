import { useState, useEffect, useCallback } from "react";
import { leadsAPI } from "../config/api";
import useAppStore from "../store/useAppStore";

export function useLeads(params = {}) {
  const { setLeads } = useAppStore();
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await leadsAPI.list(params);
      if (res.success) {
        setData(res.data);
        setLeads(res.data.items);
      }
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => { fetch(); }, [fetch]);

  const updateLeadStatus = async (id, statusData) => {
    const res = await leadsAPI.updateStatus(id, statusData);
    if (res.success) await fetch();
    return res;
  };

  return { data, loading, error, refetch: fetch, updateLeadStatus };
}
