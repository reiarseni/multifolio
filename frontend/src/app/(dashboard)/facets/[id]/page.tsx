"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { facetsApi, type Facet } from "@/lib/api/facets";
import { ShareButton } from "@/components/dashboard/ShareButton";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";

export default function FacetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [facet, setFacet] = useState<Facet | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    facetsApi.get(id).then((data) => {
      setFacet(data);
      setLoading(false);
    });
  }, [id]);

  if (loading) return <div className="text-muted-foreground">Loading...</div>;
  if (!facet) return <div className="text-destructive">Faceta no encontrada</div>;

  const publicUrl = `${API_URL}/${facet.slug}`;
  const pdfUrl = `${API_URL}/${facet.slug}/pdf`;

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{facet.name}</h1>
          <p className="text-sm text-muted-foreground font-mono">/{facet.slug}</p>
        </div>
        <Link
          href={`/facets/${facet.id}/edit`}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm"
        >
          Editar
        </Link>
      </div>

      <div className="border rounded-md p-4 space-y-3">
        <h2 className="font-semibold">Enlaces públicos</h2>
        {facet.is_published ? (
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <a href={publicUrl} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">
                {publicUrl}
              </a>
              <ShareButton url={publicUrl} />
            </div>
            <div className="flex items-center gap-3">
              <a href={pdfUrl} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">
                {pdfUrl}
              </a>
              <ShareButton url={pdfUrl} label="Copiar link PDF" />
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Publica esta faceta para compartirla.</p>
        )}
      </div>

      {facet.title && (
        <div>
          <p className="text-sm text-muted-foreground">Título</p>
          <p>{facet.title}</p>
        </div>
      )}
      {facet.bio && (
        <div>
          <p className="text-sm text-muted-foreground">Bio</p>
          <p className="text-sm">{facet.bio}</p>
        </div>
      )}
    </div>
  );
}
