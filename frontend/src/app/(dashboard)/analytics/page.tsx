"use client";

import { useEffect, useState } from "react";
import { facetsApi, type Facet } from "@/lib/api/facets";
import { AnalyticsDashboard } from "@/components/analytics/AnalyticsDashboard";

export default function AnalyticsPage() {
  const [facets, setFacets] = useState<Facet[]>([]);
  const [selectedFacet, setSelectedFacet] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    facetsApi.list().then((f) => {
      setFacets(f);
      if (f.length > 0) setSelectedFacet(f[0].id);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="text-muted-foreground">Cargando...</div>;
  }

  if (facets.length === 0) {
    return (
      <div className="max-w-3xl space-y-4">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          No tienes facetas publicadas. Crea una faceta para ver analytics.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Métricas de visualización y engagement por faceta.
        </p>
      </div>

      <div className="flex gap-2">
        {facets.map((f) => (
          <button
            key={f.id}
            onClick={() => setSelectedFacet(f.id)}
            className={`px-3 py-1 rounded-md text-sm ${
              selectedFacet === f.id
                ? "bg-primary text-primary-foreground"
                : "border hover:bg-muted"
            }`}
          >
            {f.name}
          </button>
        ))}
      </div>

      {selectedFacet && <AnalyticsDashboard facetId={selectedFacet} />}
    </div>
  );
}
