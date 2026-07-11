import { apiClient } from "@/lib/api-client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<{ access_token: string }>("/auth/login", { email, password }),
  refresh: () =>
    apiClient.post<{ access_token: string }>("/auth/refresh"),
  logout: () =>
    apiClient.post<void>("/auth/logout"),
  getOAuthUrl: (provider: "google" | "github") =>
    `${API_BASE}/auth/${provider}/login`,
};
