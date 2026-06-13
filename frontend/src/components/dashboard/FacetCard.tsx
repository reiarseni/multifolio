"use client";

import { useState } from "react";
import type { Facet } from "@/lib/api/facets";
import { facetsApi } from "@/lib/api/facets";
import { ShareButton } from "@/components/dashboard/ShareButton";

export function FacetCard({ facet }: { facet: Facet }) {
  const publicUrl = typeof window !== "undefined" ? `${window.location.origin}/${facet.slug}` : `/${facet.slug}`;
  const [published, setPublished] = useState(facet.is_published);

  const togglePublish = async () => {
    try {
      await facetsApi.update(facet.id, { is_published: !published });
      setPublished(!published);
    } catch {
      // silently ignore — state remains unchanged
    }
  };

  return (
    <div className="border rounded-md p-4 flex justify-between items-start gap-4">
      <div className="flex-1 min-w-0">
        <p className="font-medium">{facet.name}</p>
        <p className="text-xs text-muted-foreground font-mono">/{facet.slug}</p>
        <span
          className={`inline-block text-xs px-2 py-0.5 rounded-full mt-1 ${
            published
              ? "bg-green-100 text-green-700"
              : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {published ? "Publicada" : "Borrador"}
        </span>
      </div>
      <div className="flex gap-2 shrink-0 items-center">
        {published && (
          <>
            <a
              href={publicUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              Ver CV
            </a>
            <ShareButton url={publicUrl} label="Compartir" />
          </>
        )}
        <button
          onClick={togglePublish}
          className="text-xs text-muted-foreground hover:underline"
        >
          {published ? "Despublicar" : "Publicar"}
        </button>
      </div>
    </div>
  );
}
