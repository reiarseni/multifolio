"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { publicApi, type PublicFacetResponse } from "@/lib/api/public";
import { CVHeader } from "@/components/cv/CVHeader";
import { CVExperience } from "@/components/cv/CVExperience";
import { CVEducation } from "@/components/cv/CVEducation";
import { CVSkills } from "@/components/cv/CVSkills";
import { CVProjects } from "@/components/cv/CVProjects";

export default function PublicFacetPage() {
  const { slug } = useParams<{ slug: string }>();
  const [data, setData] = useState<PublicFacetResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    publicApi.getFacet(slug).then(setData).catch(() => setError(true)).finally(() => setLoading(false));
  }, [slug]);

  useEffect(() => {
    if (!data) return;
    document.title = data.meta_title || `${data.full_name} - ${data.title || data.slug}`;
    const meta = document.querySelector("meta[name=description]") || document.createElement("meta");
    meta.setAttribute("name", "description");
    meta.setAttribute("content", data.meta_description || data.bio || "");
    if (!meta.parentNode) document.head.appendChild(meta);
  }, [data]);

  if (loading) {
    return <div className="max-w-3xl mx-auto p-6 text-muted-foreground">Loading...</div>;
  }

  if (error || !data) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <h1 className="text-2xl font-bold">Faceta no encontrada</h1>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <CVHeader data={data} />
      <CVExperience items={data.experiences} />
      <CVEducation items={data.educations} />
      <CVSkills items={data.skills} />
      <CVProjects items={data.projects} />
    </div>
  );
}
