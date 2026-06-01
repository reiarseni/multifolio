"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { facetsApi, type Facet } from "@/lib/api/facets";

export default function FacetsPage() {
  const [facets, setFacets] = useState<Facet[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    facetsApi.list().then((data) => {
      setFacets(data);
      setLoading(false);
    });
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm("¿Eliminar esta faceta?")) return;
    await facetsApi.delete(id);
    setFacets((prev) => prev.filter((f) => f.id !== id));
  };

  if (loading) {
    return <div className="text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Facetas</h1>
        <Link
          href="/facets/new"
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm"
        >
          Nueva faceta
        </Link>
      </div>

      {facets.length === 0 ? (
        <p className="text-muted-foreground">No hay facetas aún.</p>
      ) : (
        <div className="space-y-3">
          {facets.map((facet) => (
            <div key={facet.id} className="border rounded-md p-4 flex justify-between items-start gap-4">
              <div className="flex-1 min-w-0">
                <p className="font-medium">{facet.name}</p>
                <p className="text-xs text-muted-foreground font-mono">/{facet.slug}</p>
                <span
                  className={`inline-block text-xs px-2 py-0.5 rounded-full mt-1 ${
                    facet.is_published
                      ? "bg-green-100 text-green-700"
                      : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {facet.is_published ? "Publicada" : "Borrador"}
                </span>
              </div>
              <div className="flex gap-2 shrink-0">
                <Link
                  href={`/facets/${facet.id}/edit`}
                  className="text-sm text-muted-foreground hover:underline"
                >
                  Editar
                </Link>
                <button
                  onClick={() => handleDelete(facet.id)}
                  className="text-sm text-destructive hover:underline"
                >
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
