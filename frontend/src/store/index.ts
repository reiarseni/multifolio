import { create } from "zustand";
import { devtools } from "zustand/middleware";

interface AppState {
  initialized: boolean;
  setInitialized: (value: boolean) => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    (set) => ({
      initialized: false,
      setInitialized: (value) => set({ initialized: value }),
    }),
    { name: "multifolio", enabled: process.env.NODE_ENV === "development" }
  )
);
