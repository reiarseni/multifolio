"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ProjectForm } from "@/components/forms/ProjectForm";
import { projectsApi } from "@/lib/api/projects";

export default function NewProjectPage() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);

  const handleSave = async (data: Parameters<typeof projectsApi.create>[0]) => {
    setSaving(true);
    const project = await projectsApi.create(data);
    router.push("/projects");
  };

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Nuevo proyecto</h1>
      <ProjectForm onSave={handleSave} saving={saving} />
    </div>
  );
}
