"use client";

import { useEffect, useState } from "react";
import { themesApi, type Theme, type FacetThemeConfigUpdate } from "@/lib/api/themes";
import type { FacetThemeConfig } from "@/lib/api/themes";

interface Props {
  facetId: string;
  initial: FacetThemeConfig | null;
  onSaved?: () => void;
}

const WEB_LAYOUTS = [
  { value: "single-column", label: "Una columna" },
  { value: "sidebar", label: "Con barra lateral" },
  { value: "modular", label: "Modular" },
];

const PDF_LAYOUTS = [
  { value: "classic", label: "Clásico" },
  { value: "two-column", label: "Dos columnas" },
  { value: "compact", label: "Compacto" },
];

const PHOTO_SHAPES = [
  { value: "circle", label: "Circular" },
  { value: "rounded", label: "Redondeado" },
  { value: "square", label: "Cuadrado" },
];

export function AppearancePanel({ facetId, initial, onSaved }: Props) {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [form, setForm] = useState<FacetThemeConfigUpdate>({
    theme_id: initial?.theme_id ?? "",
    web_layout: initial?.web_layout ?? "single-column",
    pdf_layout: initial?.pdf_layout ?? "classic",
    show_photo_web: initial?.show_photo_web ?? true,
    show_photo_pdf: initial?.show_photo_pdf ?? true,
    photo_shape: initial?.photo_shape ?? "circle",
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    themesApi.list().then(setThemes);
  }, []);

  const handleSave = async () => {
    setSaving(true);
    await themesApi.updateFacetTheme(facetId, form);
    setSaved(true);
    setSaving(false);
    onSaved?.();
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Apariencia</h2>

      <div className="space-y-2">
        <label className="text-sm font-medium">Tema</label>
        <div className="grid grid-cols-3 gap-2">
          {themes.map((t) => (
            <button
              key={t.id}
              onClick={() => setForm((f) => ({ ...f, theme_id: t.id }))}
              className={`border rounded-lg p-3 text-left text-sm transition-colors ${
                form.theme_id === t.id
                  ? "border-primary bg-primary/5 font-medium"
                  : "hover:bg-muted"
              }`}
            >
              {t.name}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Layout web</label>
        <div className="flex gap-2">
          {WEB_LAYOUTS.map((l) => (
            <button
              key={l.value}
              onClick={() => setForm((f) => ({ ...f, web_layout: l.value }))}
              className={`border rounded-md px-3 py-1.5 text-sm transition-colors ${
                form.web_layout === l.value
                  ? "border-primary bg-primary/5 font-medium"
                  : "hover:bg-muted"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Layout PDF</label>
        <div className="flex gap-2">
          {PDF_LAYOUTS.map((l) => (
            <button
              key={l.value}
              onClick={() => setForm((f) => ({ ...f, pdf_layout: l.value }))}
              className={`border rounded-md px-3 py-1.5 text-sm transition-colors ${
                form.pdf_layout === l.value
                  ? "border-primary bg-primary/5 font-medium"
                  : "hover:bg-muted"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Forma de la foto</label>
        <div className="flex gap-2">
          {PHOTO_SHAPES.map((s) => (
            <button
              key={s.value}
              onClick={() => setForm((f) => ({ ...f, photo_shape: s.value }))}
              className={`border rounded-md px-3 py-1.5 text-sm transition-colors ${
                form.photo_shape === s.value
                  ? "border-primary bg-primary/5 font-medium"
                  : "hover:bg-muted"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Visibilidad de la foto</label>
        <div className="flex flex-col gap-2">
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={form.show_photo_web ?? true}
              onChange={(e) => setForm((f) => ({ ...f, show_photo_web: e.target.checked }))}
              className="rounded"
            />
            Mostrar foto en la web pública
          </label>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={form.show_photo_pdf ?? true}
              onChange={(e) => setForm((f) => ({ ...f, show_photo_pdf: e.target.checked }))}
              className="rounded"
            />
            Mostrar foto en el PDF
          </label>
        </div>
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
      >
        {saving ? "Guardando..." : saved ? "Guardado" : "Guardar apariencia"}
      </button>
    </div>
  );
}
