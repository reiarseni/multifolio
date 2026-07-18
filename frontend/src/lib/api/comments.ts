import { apiClient } from "@/lib/api-client";

export interface Comment {
  id: string;
  facet_id: string;
  parent_id: string | null;
  author_name: string | null;
  author_email: string | null;
  content: string;
  section_ref: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  replies: Comment[];
}

export interface CommentCreatePayload {
  content: string;
  parent_id?: string;
  section_ref?: string;
  author_name?: string;
  author_email?: string;
}

export interface ReviewLink {
  id: string;
  facet_id: string;
  token: string;
  is_active: boolean;
  created_at: string;
}

export const commentsApi = {
  listByToken: (token: string) =>
    apiClient.get<Comment[]>(`/api/review/${token}/comments`),

  createByToken: (token: string, data: CommentCreatePayload) =>
    apiClient.post<Comment>(`/api/review/${token}/comments`, data),

  listByFacet: (facetId: string) =>
    apiClient.get<Comment[]>(`/api/facets/${facetId}/comments`),

  resolve: (commentId: string) =>
    apiClient.patch<Comment>(`/api/comments/${commentId}/resolve`),

  getUnreadCount: () =>
    apiClient.get<{ count: number }>("/api/dashboard/comments/unread"),
};

export const reviewLinksApi = {
  create: (facetId: string) =>
    apiClient.post<ReviewLink>("/api/review/links", { facet_id: facetId }),

  validate: (token: string) =>
    apiClient.get<ReviewLink>(`/api/review/${token}/validate`),

  deactivate: (linkId: string) =>
    apiClient.delete(`/api/review-links/${linkId}`),

  listByFacet: (facetId: string) =>
    apiClient.get<ReviewLink[]>(`/api/facets/${facetId}/review-links`),
};
