import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface SEOVariant {
  title: string;
  description: string;
  rationale: string;
}

export interface SEOSuggestResponse {
  variants: SEOVariant[];
}

export interface SEOConfigResponse {
  meta_title: string | null;
  meta_description: string | null;
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return { ...opts, headers: { ...getAuthHeaders(), ...(opts.headers as Record<string, string> ?? {}) } };
}

export const seoApi = {
  getConfig: (facetId: string) =>
    apiClient.get<SEOConfigResponse>(`/api/facets/${facetId}/seo`, withAuth()),

  suggest: (facetId: string) =>
    apiClient.post<SEOSuggestResponse>(
      `/api/facets/${facetId}/seo/suggest`,
      {},
      withAuth(),
    ),

  update: (facetId: string, meta_title: string | null, meta_description: string | null) =>
    apiClient.put<{ message: string }>(
      `/api/facets/${facetId}/seo`,
      { meta_title, meta_description },
      withAuth(),
    ),
};
