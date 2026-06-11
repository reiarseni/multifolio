import { SingleColumnLayout } from "./SingleColumnLayout";
import { SidebarLayout } from "./SidebarLayout";
import { ModularLayout } from "./ModularLayout";
import type { PublicFacetResponse } from "@/lib/api/public";
import type { ComponentType } from "react";

export const layoutRegistry: Record<string, ComponentType<{ data: PublicFacetResponse }>> = {
  "single-column": SingleColumnLayout,
  sidebar: SidebarLayout,
  modular: ModularLayout,
};
