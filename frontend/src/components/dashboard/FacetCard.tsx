"use client";

import { useState } from "react";
import type { Facet } from "@/lib/api/facets";
import { ShareButton } from "@/components/dashboard/ShareButton";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";

export function FacetCard({ facet }: { facet: Facet }) {
  const publicUrl = `${API_URL}/${facet.slug}`;
  const [published, setPublished] = useState(facet.is_published);

  const togglePublish = async () => {
    const res = await fetch(`/api/facets/${facet.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_published: !published }),
    });
    if (res.ok) setPublished(!published);
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
