import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface OpenToRole {
  id: string;
  facet_id: string;
  status: string;
  role_type: string | null;
  modality: string | null;
  location: string | null;
  timezone: string | null;
  created_at: string;
  updated_at: string;
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return { ...opts, headers: { ...getAuthHeaders(), ...(opts.headers as Record<string, string> ?? {}) } };
}

export const openToRoleApi = {
  get: (facetId: string) =>
    apiClient.get<OpenToRole | null>(`/api/facets/${facetId}/open-to-role`, withAuth()),

  upsert: (facetId: string, data: Partial<OpenToRole>) =>
    apiClient.put<OpenToRole>(`/api/facets/${facetId}/open-to-role`, data, withAuth()),

  delete: (facetId: string) =>
    apiClient.delete(`/api/facets/${facetId}/open-to-role`, withAuth()),
};
