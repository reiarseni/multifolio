"use client";

import { useParams } from "next/navigation";
import { StoryEditor } from "@/components/story/StoryEditor";

export default function StoryEditorPage() {
  const { slug: facetId } = useParams<{ slug: string }>();

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Editor de Historia</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Crea una historia profesional con secciones enriquecidas y multimedia.
        </p>
      </div>
      <StoryEditor facetId={facetId} />
    </div>
  );
}
