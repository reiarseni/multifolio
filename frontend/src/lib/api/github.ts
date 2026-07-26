import { apiClient } from "@/lib/api-client";
import { withAuth } from "@/lib/api/auth-helpers";

export interface GitHubRepo {
  id: string;
  user_id: string;
  repo_url: string;
  name: string;
  full_name: string;
  description: string | null;
  stars: number;
  forks: number;
  language: string | null;
  languages: Record<string, number> | null;
  last_commit: string | null;
  is_archived: boolean;
  last_synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export const githubApi = {
  listRepos: () =>
    apiClient.get<GitHubRepo[]>("/api/github/repos", withAuth()),

  linkRepo: (repoUrl: string) =>
    apiClient.post<GitHubRepo>("/api/github/repos", { repo_url: repoUrl }, withAuth()),

  syncRepos: () =>
    apiClient.post<GitHubRepo[]>("/api/github/repos/sync", {}, withAuth()),

  unlinkRepo: (repoId: string) =>
    apiClient.delete(`/api/github/repos/${repoId}`, withAuth()),
};
