"use client";

import { profileApi, type BaseProfile } from "@/lib/api/profile";
import { projectsApi, type Project } from "@/lib/api/projects";
import { useEffect, useState } from "react";

interface Props {
  selectedExperienceIds: string[];
  selectedEducationIds: string[];
  selectedSkillIds: string[];
  selectedProjectIds: string[];
  selectedCertificationIds: string[];
  onChange: (field: string, ids: string[]) => void;
}

type Section = {
  key: string;
  label: string;
  items: { id: string; label: string; badge?: string }[];
  field: string;
};

export function FacetItemSelector({
  selectedExperienceIds,
  selectedEducationIds,
  selectedSkillIds,
  selectedProjectIds,
  selectedCertificationIds,
  onChange,
}: Props) {
  const [profile, setProfile] = useState<BaseProfile | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([profileApi.get(), projectsApi.list()]).then(([p, projs]) => {
      setProfile(p);
      setProjects(projs);
      setLoading(false);
    });
  }, []);

  const selectedMap: Record<string, string[]> = {
    experience_ids: selectedExperienceIds,
    education_ids: selectedEducationIds,
    skill_ids: selectedSkillIds,
    project_ids: selectedProjectIds,
    certification_ids: selectedCertificationIds,
  };

  const sections: Section[] = [
    {
      key: "experiences",
      label: "Experiencia laboral",
      field: "experience_ids",
      items: (profile?.experiences ?? []).map((e) => ({
        id: e.id,
        label: `${e.position} en ${e.company}`,
      })),
    },
    {
      key: "educations",
      label: "Educación",
      field: "education_ids",
      items: (profile?.educations ?? []).map((e) => ({
        id: e.id,
        label: `${e.degree} - ${e.institution}`,
      })),
    },
    {
      key: "skills",
      label: "Habilidades",
      field: "skill_ids",
      items: (profile?.skills ?? []).map((s) => ({
        id: s.id,
        label: s.name,
        badge: s.is_transversal ? "transversal" : undefined,
      })),
    },
    {
      key: "projects",
      label: "Proyectos",
      field: "project_ids",
      items: projects.map((p) => ({
        id: p.id,
        label: p.title,
      })),
    },
    {
      key: "certifications",
      label: "Certificaciones",
      field: "certification_ids",
      items: (profile?.certifications ?? []).map((c) => ({
        id: c.id,
        label: `${c.name} — ${c.issuer}`,
      })),
    },
  ];

  const toggle = (field: string, id: string) => {
    const current = selectedMap[field] ?? [];
    const next = current.includes(id)
      ? current.filter((x) => x !== id)
      : [...current, id];
    onChange(field, next);
  };

  if (loading) {
    return <p className="text-sm text-muted-foreground">Cargando perfil...</p>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Selección de items</h2>
      <p className="text-sm text-muted-foreground">
        Marca los elementos que quieres incluir en esta faceta.
      </p>

      {sections.map((section) => (
        <div key={section.key} className="space-y-2">
          <h3 className="text-sm font-medium">{section.label}</h3>
          {section.items.length === 0 ? (
            <p className="text-xs text-muted-foreground">No hay elementos.</p>
          ) : (
            <div className="space-y-1 max-h-48 overflow-y-auto border rounded-md p-2">
              {section.items.map((item) => (
                <label
                  key={item.id}
                  className="flex items-center gap-2 px-2 py-1 rounded hover:bg-muted cursor-pointer text-sm"
                >
                  <input
                    type="checkbox"
                    checked={(selectedMap[section.field] ?? []).includes(item.id)}
                    onChange={() => toggle(section.field, item.id)}
                    className="rounded"
                  />
                  <span>{item.label}</span>
                  {item.badge === "transversal" && (
                    <span className="ml-auto text-xs bg-blue-100 text-blue-700 rounded px-1.5 py-0.5">
                      Transversal
                    </span>
                  )}
                </label>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
