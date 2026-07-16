import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface AISuggestion {
  original: string;
  suggested: string;
  changes_summary: string;
}

export interface AIHeadline {
  title: string;
  bio: string;
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

export const aiApi = {
  improveSection: (sectionId: string) =>
    apiClient.post<AISuggestion>(
      `/api/ai/story/sections/${sectionId}/improve`,
      {},
      withAuth()
    ),

  expandSection: (sectionId: string) =>
    apiClient.post<AISuggestion>(
      `/api/ai/story/sections/${sectionId}/expand`,
      {},
      withAuth()
    ),

  suggestHeadline: (facetId: string, targetRole: string) =>
    apiClient.post<AIHeadline>(
      `/api/ai/facets/${facetId}/suggest-headline`,
      { target_role: targetRole },
      withAuth()
    ),

  applySuggestion: (sectionId: string, suggestion: string) =>
    apiClient.post<{ id: string }>(
      "/api/ai/apply-suggestion",
      { section_id: sectionId, suggestion },
      withAuth()
    ),
};
