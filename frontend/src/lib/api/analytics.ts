import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface ReferrerCount {
  referrer: string;
  count: number;
}

export interface AnalyticsMetrics {
  total_views: number;
  unique_views: number;
  avg_time_on_page: number | null;
  top_referrers: ReferrerCount[];
}

export interface TrendPoint {
  date: string;
  value: number;
}

export interface TrendResponse {
  metric: string;
  period: string;
  data: TrendPoint[];
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return { ...opts, headers: { ...getAuthHeaders(), ...(opts.headers as Record<string, string> ?? {}) } };
}

export const analyticsApi = {
  getMetrics: (facetId: string, days = 30) =>
    apiClient.get<AnalyticsMetrics>(`/api/facets/${facetId}/analytics?days=${days}`, withAuth()),

  getTrends: (facetId: string, days = 30) =>
    apiClient.get<TrendResponse>(`/api/facets/${facetId}/analytics/trends?days=${days}`, withAuth()),

  exportCsv: (facetId: string, days = 30) => {
    const token = getToken();
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const url = `${baseUrl}/api/facets/${facetId}/analytics/export?days=${days}`;
    return fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
  },
};
