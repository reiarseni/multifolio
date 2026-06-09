import { create } from "zustand";
import { devtools } from "zustand/middleware";

interface AuthState {
  accessToken: string | null;
  setAccessToken: (token: string | null) => void;
  clearAccessToken: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    (set) => ({
      accessToken: null,
      setAccessToken: (token) => set({ accessToken: token }),
      clearAccessToken: () => set({ accessToken: null }),
    }),
    { name: "multifolio-auth", enabled: process.env.NODE_ENV === "development" }
  )
);

export function getAccessToken(): string | null {
  return useAuthStore.getState().accessToken;
}
