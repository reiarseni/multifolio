"use client";

import type { StorySection } from "@/lib/api/stories";

interface SectionBlockProps {
  section: StorySection;
  onUpdate: (id: string, data: Partial<StorySection>) => void;
  onDelete: (id: string) => void;
  onToggleVisibility: (id: string, visible: boolean) => void;
}

const SECTION_LABELS: Record<string, string> = {
  context: "Contexto / Problema",
  process: "Proceso",
  solution: "Solución",
  impact: "Impacto y resultados",
};

export function SectionBlock({
  section,
  onUpdate,
  onDelete,
  onToggleVisibility,
}: SectionBlockProps) {
  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-muted-foreground">
            {SECTION_LABELS[section.section_type] ?? section.section_type}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onToggleVisibility(section.id, !section.is_visible)}
            className="text-xs text-muted-foreground hover:text-foreground"
          >
            {section.is_visible ? "Ocultar" : "Mostrar"}
          </button>
          <button
            onClick={() => onDelete(section.id)}
            className="text-xs text-destructive hover:text-destructive/80"
          >
            Eliminar
          </button>
        </div>
      </div>

      <input
        type="text"
        value={section.title}
        onChange={(e) => onUpdate(section.id, { title: e.target.value })}
        placeholder="Título de la sección"
        className="w-full border rounded-md px-3 py-2 text-sm font-medium"
      />

      <textarea
        value={section.content ?? ""}
        onChange={(e) => onUpdate(section.id, { content: e.target.value })}
        placeholder="Escribe tu historia en Markdown..."
        rows={6}
        className="w-full border rounded-md px-3 py-2 text-sm font-mono resize-y"
      />

      {section.media_urls && section.media_urls.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {section.media_urls.map((url, idx) => (
            <div key={idx} className="relative">
              {url.includes("youtube.com") || url.includes("vimeo.com") ? (
                <div className="w-32 h-20 bg-muted rounded flex items-center justify-center text-xs">
                  Video
                </div>
              ) : (
                <img
                  src={url}
                  alt={`Media ${idx + 1}`}
                  className="w-32 h-20 object-cover rounded"
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
