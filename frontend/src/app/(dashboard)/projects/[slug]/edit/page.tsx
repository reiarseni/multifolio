"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { ProjectForm } from "@/components/forms/ProjectForm";
import { projectsApi, type Project, type ProjectImage, type ProjectAttachment } from "@/lib/api/projects";
import { uploadFile } from "@/lib/api/upload";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function EditProjectPage() {
  const { slug: id } = useParams<{ slug: string }>();
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [imageUploading, setImageUploading] = useState(false);
  const [attachmentUploading, setAttachmentUploading] = useState(false);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const attachmentInputRef = useRef<HTMLInputElement>(null);

  const reload = () =>
    projectsApi.get(id).then((data) => {
      setProject(data);
    });

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
    } finally {
      setSaving(false);
    }
  };

  const handleAddImage = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageUploading(true);
    try {
      const url = await uploadFile(file);
      await projectsApi.addImage(id, { image_url: url, sort_order: project?.images.length ?? 0 });
      await reload();
    } finally {
      setImageUploading(false);
      if (imageInputRef.current) imageInputRef.current.value = "";
    }
  };

  const handleDeleteImage = async (img: ProjectImage) => {
    await projectsApi.deleteImage(id, img.id);
    await reload();
  };

  const handleAddAttachment = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAttachmentUploading(true);
    try {
      const url = await uploadFile(file);
      await projectsApi.addAttachment(id, {
        file_url: url,
        filename: file.name,
        mime_type: file.type,
        file_size: file.size,
      });
      await reload();
    } finally {
      setAttachmentUploading(false);
      if (attachmentInputRef.current) attachmentInputRef.current.value = "";
    }
  };

  const handleDeleteAttachment = async (att: ProjectAttachment) => {
    await projectsApi.deleteAttachment(id, att.id);
    await reload();
  };

  if (loading) {
    return <div className="text-muted-foreground">Cargando...</div>;
  }

  const resolveUrl = (url: string) =>
    url.startsWith("/media") ? `${BASE_URL}${url}` : url;

  return (
    <div className="max-w-3xl space-y-8">
      <h1 className="text-2xl font-bold">Editar proyecto</h1>
      <ProjectForm initial={project ?? undefined} onSave={handleSave} saving={saving} />

      <hr className="border-border" />

      {/* Galería */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Galería de imágenes</h2>
          <button
            onClick={() => imageInputRef.current?.click()}
            disabled={imageUploading}
            className="text-sm border rounded-md px-3 py-1.5 hover:bg-muted disabled:opacity-50"
          >
            {imageUploading ? "Subiendo..." : "+ Añadir imagen"}
          </button>
          <input ref={imageInputRef} type="file" accept="image/*" className="hidden" onChange={handleAddImage} />
        </div>
        {(project?.images ?? []).length === 0 ? (
          <p className="text-sm text-muted-foreground">No hay imágenes en la galería.</p>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            {(project?.images ?? []).map((img) => (
              <div key={img.id} className="relative group">
                <img
                  src={resolveUrl(img.image_url)}
                  alt={img.caption ?? ""}
                  className="h-24 w-full object-cover rounded-md border"
                />
                <button
                  onClick={() => handleDeleteImage(img)}
                  className="absolute top-1 right-1 bg-destructive text-white text-xs rounded px-1.5 py-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  Eliminar
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      <hr className="border-border" />

      {/* Adjuntos */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Adjuntos</h2>
          <button
            onClick={() => attachmentInputRef.current?.click()}
            disabled={attachmentUploading}
            className="text-sm border rounded-md px-3 py-1.5 hover:bg-muted disabled:opacity-50"
          >
            {attachmentUploading ? "Subiendo..." : "+ Añadir adjunto"}
          </button>
          <input ref={attachmentInputRef} type="file" className="hidden" onChange={handleAddAttachment} />
        </div>
        {(project?.attachments ?? []).length === 0 ? (
          <p className="text-sm text-muted-foreground">No hay adjuntos.</p>
        ) : (
          <div className="space-y-2">
            {(project?.attachments ?? []).map((att) => (
              <div key={att.id} className="flex items-center justify-between border rounded-md px-3 py-2">
                <div>
                  <a
                    href={resolveUrl(att.file_url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium hover:underline"
                  >
                    {att.filename}
                  </a>
                  <p className="text-xs text-muted-foreground">
                    {att.mime_type} · {(att.file_size / 1024).toFixed(1)} KB
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteAttachment(att)}
                  className="text-destructive text-sm hover:underline"
                >
                  Eliminar
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
