import { useState, useEffect, useCallback } from "react";
import { visitsAPI } from "../config/api";

export function useVisits(params = {}) {
  const [data, setData] = useState({ total: 0, items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await visitsAPI.list(params);
      if (res.success) setData(res.data);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => { fetch(); }, [fetch]);

  const submitProof = async (visitId, proofData) => {
    const res = await visitsAPI.submitProof(visitId, proofData);
    if (res.success) await fetch();
    return res;
  };

  return { data, loading, error, refetch: fetch, submitProof };
}
