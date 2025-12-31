import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

// API base URL - use relative URL to leverage Vite proxy in development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useApi<T>(
  endpoint: string,
  dependencies: any[] = [],
  autoRefreshInterval?: number,
  requireAuth: boolean = false // New parameter - defaults to false for public endpoints
): ApiState<T> {
  const { token, logout } = useAuth();
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: true,
    error: null,
    refetch: () => {},
  });

  const fetchData = useCallback(async () => {
    // Only check authentication if required
    if (requireAuth && !token) {
      console.warn(`[useApi] Auth required but no token for: ${endpoint}`);
      setState(prev => ({ ...prev, loading: false, error: 'Not authenticated' }));
      return;
    }

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const url = `${API_BASE_URL}${endpoint}`;
      console.log(`[useApi] Fetching: ${url}`);
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      // Only add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, { headers });
      console.log(`[useApi] Response status: ${response.status} for ${endpoint}`);
      
      if (response.status === 401 && requireAuth) {
        console.error(`[useApi] 401 Unauthorized for: ${endpoint}`);
        logout();
        throw new Error('Session expired. Please login again.');
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[useApi] Error ${response.status} for ${endpoint}:`, errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`[useApi] Success for ${endpoint}:`, data);
      setState(prev => ({ ...prev, data, loading: false, error: null }));
    } catch (error) {
      console.error(`[useApi] Exception for ${endpoint}:`, error);
      setState(prev => ({
        ...prev,
        data: null,
        loading: false,
        error: error instanceof Error ? error.message : 'An error occurred',
      }));
    }
  }, [endpoint, token, logout, requireAuth]);

  useEffect(() => {
    fetchData();
    
    // Auto-refresh if interval is provided
    if (autoRefreshInterval && autoRefreshInterval > 0) {
      const intervalId = setInterval(fetchData, autoRefreshInterval);
      return () => clearInterval(intervalId);
    }
  }, [fetchData, autoRefreshInterval, ...dependencies]);

  // Add refetch to state
  useEffect(() => {
    setState(prev => ({ ...prev, refetch: fetchData }));
  }, [fetchData]);

  return state;
}

export async function apiCall<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// WebSocket hook for real-time updates
export function useWebSocket(endpoint: string, onMessage: (data: any) => void) {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const wsUrl = `ws://localhost:8000${endpoint}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [endpoint, onMessage]);

  return { connected };
}
