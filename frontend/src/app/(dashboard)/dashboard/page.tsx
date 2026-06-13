"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { profileApi, type BaseProfile } from "@/lib/api/profile";
import { projectsApi, type Project } from "@/lib/api/projects";
import { facetsApi, type Facet } from "@/lib/api/facets";
import { OverviewCards } from "@/components/dashboard/OverviewCards";
import { FacetCard } from "@/components/dashboard/FacetCard";

export default function DashboardHome() {
  const [profile, setProfile] = useState<BaseProfile | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [facets, setFacets] = useState<Facet[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      profileApi.get().catch(() => null),
      projectsApi.list().catch(() => [] as Project[]),
      facetsApi.list().catch(() => [] as Facet[]),
    ]).then(([p, projs, facs]) => {
      setProfile(p);
      setProjects(projs);
      setFacets(facs);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div className="text-muted-foreground">Loading...</div>;
  }

  const profileCount = profile ? 1 : 0;

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Bienvenido{profile?.full_name ? `, ${profile.full_name}` : ""}. Gestiona tu contenido desde aquí.
        </p>
      </div>

      <OverviewCards
        profileCount={profileCount}
        projectCount={projects.length}
        facetCount={facets.length}
      />

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Tus facetas</h2>
          <Link
            href="/facets/new"
            className="text-sm text-primary hover:underline"
          >
            Crear faceta
          </Link>
        </div>
        {facets.length === 0 ? (
          <p className="text-sm text-muted-foreground">No tienes facetas aún. ¡Crea tu primera faceta!</p>
        ) : (
          <div className="space-y-3">
            {facets.map((facet) => (
              <FacetCard key={facet.id} facet={facet} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
