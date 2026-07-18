import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface AIGeneratedProject {
  repo_id: string;
  title: string;
  description: string | null;
  markdown_content: string | null;
  github_url: string;
}

export interface ImportAnalyzeResponse {
  projects: AIGeneratedProject[];
}

export interface ImportConfirmResponse {
  message: string;
  count: number;
  project_ids: string[];
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return { ...opts, headers: { ...getAuthHeaders(), ...(opts.headers as Record<string, string> ?? {}) } };
}

export const githubImportApi = {
  analyze: (repoIds: string[], facetId: string) =>
    apiClient.post<ImportAnalyzeResponse>("/api/github/import/analyze", { repo_ids: repoIds, facet_id: facetId }, withAuth()),

  confirm: (facetId: string, projects: AIGeneratedProject[]) =>
    apiClient.post<ImportConfirmResponse>("/api/github/import/confirm", { facet_id: facetId, projects }, withAuth()),
};
