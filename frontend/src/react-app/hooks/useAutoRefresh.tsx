import { useState, useEffect, useCallback } from 'react';
import { useApi } from './useApi';

export function useAutoRefresh<T>(
  endpoint: string,
  intervalMs: number = 120000,
  enabled: boolean = true
) {
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const { data, loading, error, refetch } = useApi<T>(endpoint, [], enabled ? intervalMs : undefined);

  useEffect(() => {
    if (data && !loading) {
      setLastUpdated(new Date());
    }
  }, [data, loading]);

  const manualRefresh = useCallback(() => {
    refetch();
    setLastUpdated(new Date());
  }, [refetch]);

  return { data, loading, error, refetch: manualRefresh, lastUpdated };
}
