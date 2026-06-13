import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";
import type { FacetThemeConfig } from "@/lib/api/themes";

export interface Facet {
  id: string;
  user_id: string;
  name: string;
  slug: string;
  title: string | null;
  bio: string | null;
  meta_title: string | null;
  meta_description: string | null;
  pdf_template: string;
  is_published: boolean;
  created_at: string;
  updated_at: string;
  experience_ids: string[];
  education_ids: string[];
  skill_ids: string[];
  project_ids: string[];
  certification_ids: string[];
  theme_config: FacetThemeConfig | null;
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return { ...opts, headers: { ...getAuthHeaders(), ...(opts.headers as Record<string, string> ?? {}) } };
}

export const facetsApi = {
  list: () => apiClient.get<Facet[]>("/api/facets", withAuth()),

  get: (id: string) => apiClient.get<Facet>(`/api/facets/${id}`, withAuth()),

  create: (data: Partial<Facet>) =>
    apiClient.post<Facet>("/api/facets", data, withAuth()),

  update: (id: string, data: Partial<Facet>) =>
    apiClient.put<Facet>(`/api/facets/${id}`, data, withAuth()),

  delete: (id: string) =>
    apiClient.delete(`/api/facets/${id}`, withAuth()),
};
