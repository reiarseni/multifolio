"use client";

import { type Project } from "@/lib/api/projects";
import { useRef, useState } from "react";
import { uploadFile } from "@/lib/api/upload";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Props {
  initial?: Partial<Project>;
  onSave: (data: Partial<Project>) => Promise<void>;
  saving?: boolean;
}

export function ProjectForm({ initial, onSave, saving }: Props) {
  const [form, setForm] = useState({
    title: initial?.title ?? "",
    description: initial?.description ?? "",
    markdown_content: initial?.markdown_content ?? "",
    github_url: initial?.github_url ?? "",
    live_url: initial?.live_url ?? "",
    cover_image_url: initial?.cover_image_url ?? "",
    sort_order: initial?.sort_order ?? 0,
  });
  const [coverUploading, setCoverUploading] = useState(false);
  const coverInputRef = useRef<HTMLInputElement>(null);

  const handleCoverChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setCoverUploading(true);
    try {
      const url = await uploadFile(file);
      setForm((prev) => ({ ...prev, cover_image_url: url }));
    } finally {
      setCoverUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave(form);
  };

  const set = (field: string, value: string | number) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-2xl">
      <div>
        <label className="text-sm text-muted-foreground">Título *</label>
        <input
          required
          className="w-full border rounded-md px-3 py-2 text-sm"
          value={form.title}
          onChange={(e) => set("title", e.target.value)}
        />
      </div>

      <div>
        <label className="text-sm text-muted-foreground">Descripción corta</label>
        <textarea
          className="w-full border rounded-md px-3 py-2 text-sm min-h-[60px]"
          value={form.description}
          onChange={(e) => set("description", e.target.value)}
        />
      </div>

      <div>
        <label className="text-sm text-muted-foreground">Contenido (Markdown)</label>
        <textarea
          className="w-full border rounded-md px-3 py-2 text-sm min-h-[200px] font-mono"
          value={form.markdown_content}
          onChange={(e) => set("markdown_content", e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm text-muted-foreground">Imagen de portada</label>
        {form.cover_image_url && (
          <img
            src={form.cover_image_url.startsWith("/media") ? `${BASE_URL}${form.cover_image_url}` : form.cover_image_url}
            alt="Portada"
            className="h-24 w-auto rounded-md border object-cover"
          />
        )}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => coverInputRef.current?.click()}
            disabled={coverUploading}
            className="text-sm border rounded-md px-3 py-1.5 hover:bg-muted disabled:opacity-50"
          >
            {coverUploading ? "Subiendo..." : form.cover_image_url ? "Cambiar imagen" : "Subir imagen"}
          </button>
          {form.cover_image_url && (
            <button
              type="button"
              onClick={() => setForm((prev) => ({ ...prev, cover_image_url: "" }))}
              className="text-sm text-destructive hover:underline"
            >
              Eliminar
            </button>
          )}
        </div>
        <input ref={coverInputRef} type="file" accept="image/*" className="hidden" onChange={handleCoverChange} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm text-muted-foreground">URL del repositorio</label>
          <input
            className="w-full border rounded-md px-3 py-2 text-sm"
            value={form.github_url}
            onChange={(e) => set("github_url", e.target.value)}
          />
        </div>
        <div>
          <label className="text-sm text-muted-foreground">URL en vivo</label>
          <input
            className="w-full border rounded-md px-3 py-2 text-sm"
            value={form.live_url}
            onChange={(e) => set("live_url", e.target.value)}
          />
        </div>
      </div>

      <div>
        <label className="text-sm text-muted-foreground">Orden</label>
        <input
          type="number"
          className="w-full border rounded-md px-3 py-2 text-sm"
          value={form.sort_order}
          onChange={(e) => set("sort_order", Number(e.target.value))}
        />
      </div>

      <button
        type="submit"
        disabled={saving}
        className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
      >
        {saving ? "Guardando..." : "Guardar proyecto"}
      </button>
    </form>
  );
}
