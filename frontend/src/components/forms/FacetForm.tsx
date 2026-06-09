"use client";

import { type Facet } from "@/lib/api/facets";
import { useState } from "react";

interface Props {
  initial?: Partial<Facet>;
  onSave: (data: Partial<Facet>) => Promise<void>;
  saving?: boolean;
}

export function FacetForm({ initial, onSave, saving }: Props) {
  const [form, setForm] = useState({
    name: initial?.name ?? "",
    slug: initial?.slug ?? "",
    title: initial?.title ?? "",
    bio: initial?.bio ?? "",
    meta_title: initial?.meta_title ?? "",
    meta_description: initial?.meta_description ?? "",
    pdf_template: initial?.pdf_template ?? "moderna",
    is_published: initial?.is_published ?? false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave(form);
  };

  const slugFromName = (name: string) =>
    name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

  const set = (field: string, value: string | boolean) =>
    setForm((prev) => {
      const next = { ...prev, [field]: value };
      if (field === "name" && !initial?.slug) {
        next.slug = slugFromName(value as string);
      }
      return next;
    });

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-2xl">
      <div>
        <label className="text-sm text-muted-foreground">Nombre interno *</label>
        <input
          required
          className="w-full border rounded-md px-3 py-2 text-sm"
          value={form.name}
          onChange={(e) => set("name", e.target.value)}
        />
      </div>

      <div>
        <label className="text-sm text-muted-foreground">Slug</label>
        <input
          required
          className="w-full border rounded-md px-3 py-2 text-sm font-mono"
          value={form.slug}
          onChange={(e) => set("slug", e.target.value)}
        />
        <p className="text-xs text-muted-foreground mt-1">
          {form.slug ? `/${form.slug}` : "Se generará automáticamente"}
        </p>
      </div>

      <div>
        <label className="text-sm text-muted-foreground">Título de presentación</label>
        <input
          className="w-full border rounded-md px-3 py-2 text-sm"
          value={form.title}
          onChange={(e) => set("title", e.target.value)}
        />
      </div>

      <div>
        <label className="text-sm text-muted-foreground">Bio</label>
        <textarea
          className="w-full border rounded-md px-3 py-2 text-sm min-h-[80px]"
          value={form.bio}
          onChange={(e) => set("bio", e.target.value)}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm text-muted-foreground">Meta title (SEO)</label>
          <input
            className="w-full border rounded-md px-3 py-2 text-sm"
            value={form.meta_title}
            onChange={(e) => set("meta_title", e.target.value)}
          />
        </div>
        <div>
          <label className="text-sm text-muted-foreground">Meta description</label>
          <input
            className="w-full border rounded-md px-3 py-2 text-sm"
            value={form.meta_description}
            onChange={(e) => set("meta_description", e.target.value)}
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-sm text-muted-foreground">Publicado</label>
        <input
          type="checkbox"
          checked={form.is_published}
          onChange={(e) => set("is_published", e.target.checked)}
          className="rounded"
        />
      </div>

      <button
        type="submit"
        disabled={saving}
        className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
      >
        {saving ? "Guardando..." : "Guardar faceta"}
      </button>
    </form>
  );
}
