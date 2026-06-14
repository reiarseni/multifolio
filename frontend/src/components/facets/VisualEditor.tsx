"use client";

import { useState } from "react";
import { themesApi } from "@/lib/api/themes";
import type { FacetThemeConfig } from "@/lib/api/themes";
import { TokenControls } from "./TokenControls";

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

interface TokenGroup {
  color: Record<string, string>;
  typography: Record<string, string>;
  spacing: Record<string, string>;
  shape: Record<string, string>;
  density: string;
}

const EMPTY_TOKENS: TokenGroup = { color: {}, typography: {}, spacing: {}, shape: {}, density: "balanced" };

export function VisualEditor({ facetId, initial, onSaved }: Props) {
  const [form, setForm] = useState({
    theme_id: initial?.theme_id ?? "",
    web_layout: initial?.web_layout ?? "single-column",
    pdf_layout: initial?.pdf_layout ?? "classic",
    show_photo_web: initial?.show_photo_web ?? true,
    show_photo_pdf: initial?.show_photo_pdf ?? true,
    photo_shape: initial?.photo_shape ?? "circle",
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [activeTab, setActiveTab] = useState("color");
  const [previewTokens, setPreviewTokens] = useState<TokenGroup>(EMPTY_TOKENS);

  const handleSave = async () => {
    setSaving(true);
    try {
      await themesApi.updateFacetTheme(facetId, {
        theme_id: form.theme_id || undefined,
        theme_overrides: previewTokens as unknown as Record<string, unknown>,
        web_layout: form.web_layout,
        pdf_layout: form.pdf_layout,
        show_photo_web: form.show_photo_web,
        show_photo_pdf: form.show_photo_pdf,
        photo_shape: form.photo_shape,
      });
      setSaved(true);
      onSaved?.();
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error("Error saving appearance:", error);
    } finally {
      setSaving(false);
    }
  };

  const updateToken = (group: string, key: string, value: string | number) => {
    setPreviewTokens((prev) => ({
      ...prev,
      [group]: { ...prev[group as keyof TokenGroup] as Record<string, string>, [key]: String(value) },
    }));
  };

  const saveAsCustomTheme = async () => {
    try {
      const response = await themesApi.createCustomTheme({
        name: `Tema personalizado ${new Date().toLocaleDateString()}`,
        tokens: previewTokens as unknown as Record<string, unknown>,
        is_public: false,
      });
      setForm((f) => ({ ...f, theme_id: response.id }));
    } catch (error) {
      console.error("Error saving custom theme:", error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Editor Visual de Tokens</h2>
        <div className="flex gap-2">
          <button onClick={() => setPreviewTokens(EMPTY_TOKENS)} className="px-3 py-1.5 text-xs border border-gray-300 rounded hover:bg-gray-50 transition-colors">
            Resetear a tema base
          </button>
          <button onClick={saveAsCustomTheme} className="px-3 py-1.5 text-xs bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors">
            Guardar como tema personalizado
          </button>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-2">
        {["color", "typography", "spacing", "shape", "density"].map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`px-3 py-2 text-sm rounded border transition-colors ${activeTab === tab ? "border-primary bg-primary/10 font-medium" : "border-gray-300 hover:bg-gray-50"}`}>
            {tab === "color" ? "Color" : tab === "typography" ? "Tipografía" : tab === "spacing" ? "Espaciado" : tab === "shape" ? "Forma" : "Densidad"}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <TokenControls activeTab={activeTab} tokens={previewTokens} onUpdate={updateToken} />
        </div>
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Preview</h3>
          <div className="border rounded-lg p-4 space-y-3">
            <div style={{ backgroundColor: previewTokens.color?.background || "#ffffff", color: previewTokens.color?.text_heading || "#1a1a1a", padding: "1rem", borderRadius: previewTokens.shape?.radius_md || "0.5rem", border: `1px solid ${previewTokens.color?.border || "#e0e0e0"}` }}>
              <h4 style={{ fontFamily: previewTokens.typography?.font_heading || "inherit" }}>Encabezado de ejemplo</h4>
              <p style={{ fontFamily: previewTokens.typography?.font_body || "inherit" }}>Texto de ejemplo con tema personalizado.</p>
              <button style={{ backgroundColor: previewTokens.color?.accent || "#4a90e2", color: "white", padding: "0.5rem 1rem", borderRadius: "0.25rem", border: "none", cursor: "pointer" }}>Botón de ejemplo</button>
            </div>
            <div className="text-xs space-y-1">
              <div><strong>Densidad:</strong> {previewTokens.density}</div>
              <div><strong>Tamaño base:</strong> {previewTokens.typography?.size_base || "N/A"}</div>
              <div><strong>Acento:</strong> {previewTokens.color?.accent || "N/A"}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t pt-6">
        <h3 className="text-sm font-medium mb-4">Configuración de Layout</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium">Layout web</label>
            <div className="flex gap-2">
              {WEB_LAYOUTS.map((l) => (
                <button key={l.value} onClick={() => setForm((f) => ({ ...f, web_layout: l.value }))} className={`px-3 py-1.5 text-xs rounded border transition-colors ${form.web_layout === l.value ? "border-primary bg-primary/10 font-medium" : "border-gray-300 hover:bg-gray-50"}`}>
                  {l.label}
                </button>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium">Layout PDF</label>
            <div className="flex gap-2">
              {PDF_LAYOUTS.map((l) => (
                <button key={l.value} onClick={() => setForm((f) => ({ ...f, pdf_layout: l.value }))} className={`px-3 py-1.5 text-xs rounded border transition-colors ${form.pdf_layout === l.value ? "border-primary bg-primary/10 font-medium" : "border-gray-300 hover:bg-gray-50"}`}>
                  {l.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <button onClick={handleSave} disabled={saving} className="w-full bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50">
        {saving ? "Guardando..." : saved ? "Guardado" : "Guardar apariencia"}
      </button>
    </div>
  );
}
