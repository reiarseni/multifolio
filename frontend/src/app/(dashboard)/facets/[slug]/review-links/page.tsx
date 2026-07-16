"use client";

import { useParams } from "next/navigation";
import { ReviewLinkSettings } from "@/components/review/ReviewLinkSettings";

export default function ReviewLinksPage() {
  const { slug: facetId } = useParams<{ slug: string }>();

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Links de Revisión</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Gestiona links protegidos para compartir tu portfolio con reclutadores.
        </p>
      </div>
      <ReviewLinkSettings facetId={facetId} />
    </div>
  );
}
