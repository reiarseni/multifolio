"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { projectsApi, type Project } from "@/lib/api/projects";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsApi.list().then((data) => {
      setProjects(data);
      setLoading(false);
    });
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm("¿Eliminar este proyecto?")) return;
    await projectsApi.delete(id);
    setProjects((prev) => prev.filter((p) => p.id !== id));
  };

  if (loading) {
    return <div className="text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Proyectos</h1>
        <div className="flex gap-2">
          <Link
            href="/projects/github-import"
            className="border px-4 py-2 rounded-md text-sm hover:bg-muted"
          >
            Importar desde GitHub
          </Link>
          <Link
            href="/projects/new"
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm"
          >
            Nuevo proyecto
          </Link>
        </div>
      </div>

      {projects.length === 0 ? (
        <p className="text-muted-foreground">No hay proyectos aún.</p>
      ) : (
        <div className="space-y-3">
          {projects.map((project) => (
            <div key={project.id} className="border rounded-md p-4 flex justify-between items-start gap-4">
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{project.title}</p>
                {project.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">{project.description}</p>
                )}
                <p className="text-xs text-muted-foreground mt-1">
                  {project.images.length} imagen(es) · {project.attachments.length} adjunto(s)
                </p>
              </div>
              <div className="flex gap-2 shrink-0">
                <Link
                  href={`/projects/${project.id}/edit`}
                  className="text-sm text-muted-foreground hover:underline"
                >
                  Editar
                </Link>
                <button
                  onClick={() => handleDelete(project.id)}
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
