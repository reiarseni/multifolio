import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface GapItem {
  category: string;
  description: string;
  severity: string;
  suggestion: string;
}

export interface ReorderSuggestion {
  rationale: string;
  proposed_order: string[];
}

export interface JobFitResponse {
  id: string;
  job_title: string | null;
  job_company: string | null;
  overall_score: number;
  skills_score: number;
  experience_score: number;
  stack_score: number;
  tone_score: number;
  gaps: GapItem[];
  suggestions: string[];
  reorder_suggestion: ReorderSuggestion | null;
  created_at: string;
}

export interface JobFitHistoryItem {
  id: string;
  job_title: string | null;
  job_company: string | null;
  overall_score: number;
  skills_score: number;
  experience_score: number;
  stack_score: number;
  tone_score: number;
  created_at: string;
}

export interface JobFitHistoryResponse {
  analyses: JobFitHistoryItem[];
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return { ...opts, headers: { ...getAuthHeaders(), ...(opts.headers as Record<string, string> ?? {}) } };
}

export const jobFitApi = {
  analyze: (facetId: string, jobPosting: string) =>
    apiClient.post<JobFitResponse>(
      `/api/facets/${facetId}/job-fit`,
      { job_posting: jobPosting },
      withAuth(),
    ),

  getHistory: (facetId: string) =>
    apiClient.get<JobFitHistoryResponse>(
      `/api/facets/${facetId}/job-fit/history`,
      withAuth(),
    ),

  delete: (analysisId: string) =>
    apiClient.delete<{ message: string }>(
      `/api/job-fit/${analysisId}`,
      withAuth(),
    ),
};
