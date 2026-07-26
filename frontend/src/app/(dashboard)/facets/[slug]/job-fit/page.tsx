"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { facetsApi, type Facet } from "@/lib/api/facets";
import { JobFitDashboard } from "@/components/job-fit/JobFitDashboard";

export default function JobFitPage() {
  const { slug: id } = useParams<{ slug: string }>();
  const [facet, setFacet] = useState<Facet | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    facetsApi
      .get(id)
      .then((data) => {
        setFacet(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-muted-foreground">Loading...</div>;
  if (!facet) return <div className="text-destructive">Faceta no encontrada</div>;

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link
            href={`/facets/${facet.id}`}
            className="text-sm text-muted-foreground hover:text-foreground mb-1 block"
          >
            ← Volver a {facet.name}
          </Link>
          <h1 className="text-2xl font-bold">Job Market Fit</h1>
          <p className="text-sm text-muted-foreground">
            Analiza qué tan competitivo es tu perfil para un empleo específico
          </p>
        </div>
      </div>

      <JobFitDashboard facetId={facet.id} />
    </div>
  );
}
