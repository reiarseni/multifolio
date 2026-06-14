"use client";

import { useState, useEffect } from "react";
import { themesApi, type Theme } from "@/lib/api/themes";

interface Props {
  facetId: string;
  onApplied?: () => void;
}

export function CommunityLibrary({ facetId, onApplied }: Props) {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState<string | null>(null);
  const [preview, setPreview] = useState<Theme | null>(null);

  useEffect(() => {
    themesApi.listCommunity().then((data) => {
      setThemes(data);
      setLoading(false);
    });
  }, []);

  const handleApply = async (theme: Theme) => {
    setApplying(theme.id);
    try {
      await themesApi.updateFacetTheme(facetId, {
        theme_overrides: theme.tokens as Record<string, unknown>,
      });
      onApplied?.();
    } catch (error) {
      console.error("Error applying theme:", error);
    } finally {
      setApplying(null);
    }
  };

  if (loading) {
    return <div className="text-sm text-muted-foreground">Cargando biblioteca...</div>;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium">Biblioteca de Comunidad</h3>

      {themes.length === 0 ? (
        <p className="text-xs text-muted-foreground">
          No hay temas publicados todavia.
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {themes.map((theme) => (
            <div
              key={theme.id}
              className="border rounded-lg p-3 space-y-2 hover:bg-muted/50 transition-colors"
            >
              <div className="flex justify-between items-start">
                <span className="text-sm font-medium">{theme.name}</span>
                <div className="flex gap-1">
                  <button
                    onClick={() => setPreview(preview?.id === theme.id ? null : theme)}
                    className="text-xs px-2 py-0.5 border rounded hover:bg-muted transition-colors"
                  >
                    {preview?.id === theme.id ? "Cerrar" : "Preview"}
                  </button>
                  <button
                    onClick={() => handleApply(theme)}
                    disabled={applying === theme.id}
                    className="text-xs px-2 py-0.5 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors disabled:opacity-50"
                  >
                    {applying === theme.id ? "Aplicando..." : "Aplicar"}
                  </button>
                </div>
              </div>

              {preview?.id === theme.id && (
                <div
                  className="border rounded p-3 space-y-2 text-xs"
                  style={{
                    backgroundColor: (theme.tokens as Record<string, Record<string, string>>)?.color?.background || "#ffffff",
                    color: (theme.tokens as Record<string, Record<string, string>>)?.color?.text_heading || "#1a1a1a",
                  }}
                >
                  <h4 style={{ fontFamily: (theme.tokens as Record<string, Record<string, string>>)?.typography?.font_heading || "inherit" }}>
                    Ejemplo de encabezado
                  </h4>
                  <p style={{ fontFamily: (theme.tokens as Record<string, Record<string, string>>)?.typography?.font_body || "inherit" }}>
                    Texto de ejemplo con este tema aplicado.
                  </p>
                  <button
                    style={{
                      backgroundColor: (theme.tokens as Record<string, Record<string, string>>)?.color?.accent || "#0066cc",
                      color: "white",
                      padding: "0.25rem 0.75rem",
                      borderRadius: "0.25rem",
                      border: "none",
                    }}
                  >
                    Boton de ejemplo
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
