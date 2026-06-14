import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface Theme {
  id: string;
  name: string;
  tokens: Record<string, unknown>;
  is_public: boolean;
  owner_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface FacetThemeConfig {
  theme_id: string;
  theme: Theme;
  theme_overrides: Record<string, unknown> | null;
  web_layout: string;
  pdf_layout: string;
  show_photo_web: boolean;
  show_photo_pdf: boolean;
  photo_shape: string;
  section_order: string[] | null;
}

export interface FacetThemeConfigUpdate {
  theme_id?: string;
  theme_overrides?: Record<string, unknown> | null;
  web_layout?: string;
  pdf_layout?: string;
  show_photo_web?: boolean;
  show_photo_pdf?: boolean;
  photo_shape?: string;
  section_order?: string[];
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return {
    ...opts,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...((opts.headers as Record<string, string>) ?? {}),
    },
  };
}

export interface CustomThemeCreate {
  name: string;
  tokens: Record<string, unknown>;
  is_public: boolean;
}

export const themesApi = {
  list: () => apiClient.get<Theme[]>("/api/themes", withAuth()),

  listCommunity: () => apiClient.get<Theme[]>("/api/themes/community", withAuth()),

  createCustomTheme: (data: CustomThemeCreate) =>
    apiClient.post<Theme>("/api/themes", data, withAuth()),

  publishTheme: (id: string) =>
    apiClient.post<Theme>(`/api/themes/${id}/publish`, {}, withAuth()),

  unpublishTheme: (id: string) =>
    apiClient.post<Theme>(`/api/themes/${id}/unpublish`, {}, withAuth()),

  deleteCustomTheme: (id: string) =>
    apiClient.delete<Theme>(`/api/themes/${id}`, withAuth()),

  updateFacetTheme: (facetId: string, data: FacetThemeConfigUpdate) =>
    apiClient.put<FacetThemeConfig>(`/api/facets/${facetId}/theme`, data, withAuth()),
};
