"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ProjectForm } from "@/components/forms/ProjectForm";
import { projectsApi, type Project } from "@/lib/api/projects";

export default function EditProjectPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    projectsApi.get(id).then((data) => {
      setProject(data);
      setLoading(false);
    });
  }, [id]);

  const handleSave = async (data: Partial<Project>) => {
    setSaving(true);
    try {
      await projectsApi.update(id, data);
      router.push("/projects");
    } catch {
      console.error("Failed to save project");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Editar proyecto</h1>
      <ProjectForm initial={project ?? undefined} onSave={handleSave} saving={saving} />
    </div>
  );
}
