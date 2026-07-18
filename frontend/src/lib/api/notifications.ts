import { apiClient } from "@/lib/api-client";
import { getToken } from "@/lib/auth/token";

export interface NotificationOut {
  id: string;
  user_id: string;
  facet_id: string | null;
  type: string;
  title: string;
  message: string;
  referrer_domain: string | null;
  is_read: boolean;
  extra_data: Record<string, unknown> | null;
  created_at: string;
}

export interface NotificationList {
  items: NotificationOut[];
  total: number;
  unread_count: number;
}

function getAuthHeaders(): Record<string, string> {
  const token = typeof window !== "undefined" ? getToken() : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function withAuth(opts: Record<string, unknown> = {}): Record<string, unknown> {
  return { ...opts, headers: { ...getAuthHeaders(), ...(opts.headers as Record<string, string> ?? {}) } };
}

export const notificationsApi = {
  list: (params?: { limit?: number; offset?: number; unread_only?: boolean }) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set("limit", String(params.limit));
    if (params?.offset) searchParams.set("offset", String(params.offset));
    if (params?.unread_only) searchParams.set("unread_only", "true");
    const qs = searchParams.toString();
    return apiClient.get<NotificationList>(`/api/notifications${qs ? `?${qs}` : ""}`, withAuth());
  },

  markAsRead: (id: string) =>
    apiClient.patch<NotificationOut>(`/api/notifications/${id}/read`, {}, withAuth()),

  markAllAsRead: () =>
    apiClient.patch<{ marked_read: number }>("/api/notifications/read-all", {}, withAuth()),
};
