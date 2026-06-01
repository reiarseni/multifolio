"use client";

import { type Project } from "@/lib/api/projects";
import { useState } from "react";

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

      <div>
        <label className="text-sm text-muted-foreground">URL de imagen de portada</label>
        <input
          className="w-full border rounded-md px-3 py-2 text-sm"
          value={form.cover_image_url}
          onChange={(e) => set("cover_image_url", e.target.value)}
        />
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
