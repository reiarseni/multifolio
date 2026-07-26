"use client";

import { ThemeProvider } from "@/components/ui/ThemeProvider";

export function ClientProviders({ children }: { children: React.ReactNode }) {
  return <ThemeProvider>{children}</ThemeProvider>;
}
