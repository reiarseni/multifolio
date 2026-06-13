import { apiClient } from "@/lib/api-client";

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<{ access_token: string }>("/auth/login", { email, password }),
  refresh: () =>
    apiClient.post<{ access_token: string }>("/auth/refresh"),
  logout: () =>
    apiClient.post<void>("/auth/logout"),
};
