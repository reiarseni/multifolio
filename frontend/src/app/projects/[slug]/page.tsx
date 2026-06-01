"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import type { Project } from "@/lib/api/projects";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function PublicProjectPage() {
  const { slug } = useParams<{ slug: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${BASE_URL}/api/projects/public/${slug}`)
      .then((res) => {
        if (!res.ok) throw new Error("Not found");
        return res.json();
      })
      .then((data) => {
        setProject(data);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [slug]);

  if (loading) {
    return <div className="max-w-3xl mx-auto p-6 text-muted-foreground">Loading...</div>;
  }

  if (error || !project) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <h1 className="text-2xl font-bold">Proyecto no encontrado</h1>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">{project.title}</h1>
        {project.description && (
          <p className="text-muted-foreground mt-2">{project.description}</p>
        )}
      </div>

      <div className="flex gap-4">
        {project.github_url && (
          <a
            href={project.github_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline"
          >
            Ver código fuente
          </a>
        )}
        {project.live_url && (
          <a
            href={project.live_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline"
          >
            Ver sitio en vivo
          </a>
        )}
      </div>

      {project.cover_image_url && (
        <img
          src={project.cover_image_url}
          alt={project.title}
          className="w-full rounded-lg object-cover max-h-96"
        />
      )}

      {project.markdown_content && (
        <div className="prose prose-sm max-w-none">
          {project.markdown_content.split("\n").map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
      )}

      {project.images.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Galería</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {project.images.map((img) => (
              <div key={img.id}>
                <img
                  src={img.image_url}
                  alt={img.caption ?? ""}
                  className="w-full rounded-md object-cover aspect-video"
                />
                {img.caption && (
                  <p className="text-xs text-muted-foreground mt-1">{img.caption}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {project.attachments.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Archivos adjuntos</h2>
          <ul className="space-y-2">
            {project.attachments.map((att) => (
              <li key={att.id}>
                <a
                  href={att.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline"
                >
                  {att.filename}
                </a>
                <span className="text-xs text-muted-foreground ml-2">
                  ({att.mime_type})
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
