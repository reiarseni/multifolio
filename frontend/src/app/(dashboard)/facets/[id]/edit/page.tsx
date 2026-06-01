"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { FacetForm } from "@/components/forms/FacetForm";
import { FacetItemSelector } from "@/components/forms/FacetItemSelector";
import { facetsApi, type Facet } from "@/lib/api/facets";

export default function EditFacetPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [facet, setFacet] = useState<Facet | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selected, setSelected] = useState({
    experience_ids: [] as string[],
    education_ids: [] as string[],
    skill_ids: [] as string[],
    project_ids: [] as string[],
  });

  useEffect(() => {
    facetsApi.get(id).then((data) => {
      setFacet(data);
      setSelected({
        experience_ids: data.experience_ids ?? [],
        education_ids: data.education_ids ?? [],
        skill_ids: data.skill_ids ?? [],
        project_ids: data.project_ids ?? [],
      });
      setLoading(false);
    });
  }, [id]);

  const handleSave = async (data: Partial<Facet>) => {
    setSaving(true);
    await facetsApi.update(id, { ...data, ...selected });
    router.push("/facets");
  };

  const handleSelectionChange = (field: string, ids: string[]) => {
    setSelected((prev) => ({ ...prev, [field]: ids }));
  };

  if (loading) {
    return <div className="text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="max-w-3xl space-y-8">
      <h1 className="text-2xl font-bold">Editar faceta</h1>
      <FacetForm initial={facet ?? undefined} onSave={handleSave} saving={saving} />
      <FacetItemSelector
        selectedExperienceIds={selected.experience_ids}
        selectedEducationIds={selected.education_ids}
        selectedSkillIds={selected.skill_ids}
        selectedProjectIds={selected.project_ids}
        onChange={handleSelectionChange}
      />
    </div>
  );
}
