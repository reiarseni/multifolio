import { apiClient } from "@/lib/api-client";
import { withAuth } from "@/lib/api/auth-helpers";

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
