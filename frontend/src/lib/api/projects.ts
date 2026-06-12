import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface ProjectImage {
  id: string;
  project_id: string;
  image_url: string;
  caption: string | null;
  sort_order: number;
  created_at: string;
}

export interface ProjectAttachment {
  id: string;
  project_id: string;
  file_url: string;
  filename: string;
  mime_type: string;
  file_size: number;
  created_at: string;
}

export interface Project {
  id: string;
  profile_id: string;
  title: string;
  description: string | null;
  cover_image_url: string | null;
  markdown_content: string | null;
  github_url: string | null;
  live_url: string | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
  images: ProjectImage[];
  attachments: ProjectAttachment[];
}

function getAuthHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return { ...opts, headers: { ...getAuthHeaders(), ...(opts.headers as Record<string, string> ?? {}) } };
}

export const projectsApi = {
  list: () => apiClient.get<Project[]>("/api/projects", withAuth()),

  get: (id: string) => apiClient.get<Project>(`/api/projects/${id}`, withAuth()),

  create: (data: Partial<Project>) =>
    apiClient.post<Project>("/api/projects", data, withAuth()),

  update: (id: string, data: Partial<Project>) =>
    apiClient.put<Project>(`/api/projects/${id}`, data, withAuth()),

  delete: (id: string) =>
    apiClient.delete(`/api/projects/${id}`, withAuth()),

  addImage: (id: string, data: { image_url: string; caption?: string; sort_order?: number }) =>
    apiClient.post<ProjectImage>(`/api/projects/${id}/images`, data, withAuth()),

  deleteImage: (id: string, imageId: string) =>
    apiClient.delete(`/api/projects/${id}/images/${imageId}`, withAuth()),

  addAttachment: (
    id: string,
    data: { file_url: string; filename: string; mime_type: string; file_size: number }
  ) => apiClient.post<ProjectAttachment>(`/api/projects/${id}/attachments`, data, withAuth()),

  deleteAttachment: (id: string, attachmentId: string) =>
    apiClient.delete(`/api/projects/${id}/attachments/${attachmentId}`, withAuth()),
};
