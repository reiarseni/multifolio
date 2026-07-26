import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface StorySection {
  id: string;
  facet_id: string;
  section_type: string;
  title: string;
  content: string | null;
  media_urls: string[] | null;
  order: number;
  is_visible: boolean;
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

export const storiesApi = {
  getStory: (facetId: string) =>
    apiClient.get<StorySection[]>(`/api/facets/${facetId}/story`, withAuth()),

  createSection: (facetId: string, data: Partial<StorySection>) =>
    apiClient.post<StorySection>(`/api/facets/${facetId}/story/sections`, data, withAuth()),

  updateSection: (sectionId: string, data: Partial<StorySection>) =>
    apiClient.patch<StorySection>(`/api/story/sections/${sectionId}`, data, withAuth()),

  reorderSections: (facetId: string, sectionIds: string[]) =>
    apiClient.put<StorySection[]>(`/api/facets/${facetId}/story/reorder`, { section_ids: sectionIds }, withAuth()),

  deleteSection: (sectionId: string) =>
    apiClient.delete(`/api/story/sections/${sectionId}`, withAuth()),

  uploadMedia: async (sectionId: string, file: File) => {
    const token = typeof window !== "undefined" ? getToken() : null;
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${baseUrl}/api/story/sections/${sectionId}/media`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) throw new Error("Upload failed");
    return res.json() as Promise<{ url: string }>;
  },
};
