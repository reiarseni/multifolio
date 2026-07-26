import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface ReviewLink {
  id: string;
  facet_id: string;
  token: string;
  label: string | null;
  requires_password: boolean;
  expires_at: string | null;
  single_use: boolean;
  is_used: boolean;
  created_at: string;
  updated_at: string;
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    ...opts,
    headers: {
      ...getAuthHeaders(),
      ...((opts.headers as Record<string, string>) ?? {}),
    },
  };
}

export interface ReviewLinkCreatePayload {
  label?: string;
  password?: string;
  expires_in_hours?: number;
}

export const reviewLinksApi = {
  listLinks: (facetId: string) =>
    apiClient.get<ReviewLink[]>(
      `/api/facets/${facetId}/review-links`,
      withAuth()
    ),

  createLink: (facetId: string, data: ReviewLinkCreatePayload) =>
    apiClient.post<ReviewLink>(
      `/api/facets/${facetId}/review-links`,
      data,
      withAuth()
    ),

  deleteLink: (linkId: string) =>
    apiClient.delete(`/api/review-links/${linkId}`, withAuth()),

  validateLink: (token: string, password: string) =>
    apiClient.post<{ valid: boolean; facet_id: string }>(
      `/api/review/${token}/validate`,
      { password }
    ),

  accessLink: (token: string) =>
    apiClient.get<{ facet_id: string; token: string; label: string | null }>(
      `/api/review/${token}/access`
    ),
};
