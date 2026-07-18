"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { facetsApi, type Facet } from "@/lib/api/facets";
import { seoApi, type SEOVariant } from "@/lib/api/seo";
import { MetaPreview } from "@/components/seo/MetaPreview";
import { SEOSuggestions } from "@/components/seo/SEOSuggestions";

export default function SEOPage() {
  const { slug: id } = useParams<{ slug: string }>();
  const [facet, setFacet] = useState<Facet | null>(null);
  const [loading, setLoading] = useState(true);
  const [variants, setVariants] = useState<SEOVariant[]>([]);
  const [suggesting, setSuggesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const load = useCallback(async () => {
    const [facetData, seoData] = await Promise.all([
      facetsApi.get(id).catch(() => null),
      seoApi.getConfig(id).catch(() => null),
    ]);
    if (facetData && seoData) {
      setFacet(facetData);
      setTitle(seoData.meta_title ?? "");
      setDescription(seoData.meta_description ?? "");
    }
    setLoading(false);
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const handleSuggest = async () => {
    setSuggesting(true);
    try {
      const res = await seoApi.suggest(id);
      setVariants(res.variants);
    } catch {
      // silent
    } finally {
      setSuggesting(false);
    }
  };

  const handleSelect = (variant: SEOVariant) => {
    setTitle(variant.title);
    setDescription(variant.description);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await seoApi.update(id, title || null, description || null);
    } catch {
      // silent
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="text-muted-foreground">Loading...</div>;
  if (!facet) return <div className="text-destructive">Faceta no encontrada</div>;

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link
            href={`/facets/${facet.id}`}
            className="text-sm text-muted-foreground hover:text-foreground mb-1 block"
          >
            ← Volver a {facet.name}
          </Link>
          <h1 className="text-2xl font-bold">SEO - {facet.name}</h1>
          <p className="text-sm text-muted-foreground">
            Optimiza el meta título y descripción para buscadores
          </p>
        </div>
      </div>

      <MetaPreview title={title} description={description} url={`${facet.slug}`} />

      <div className="border rounded-lg p-4 space-y-4">
        <div>
          <label htmlFor="meta-title" className="block text-sm font-medium mb-1">
            Meta Título ({title.length}/60)
          </label>
          <input
            id="meta-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full border rounded-md px-3 py-2 text-sm"
            maxLength={60}
            placeholder="Ej: Backend Developer Especializado en Python y FastAPI"
          />
        </div>
        <div>
          <label htmlFor="meta-desc" className="block text-sm font-medium mb-1">
            Meta Descripción ({description.length}/160)
          </label>
          <textarea
            id="meta-desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full border rounded-md p-3 text-sm min-h-[80px] resize-y"
            maxLength={160}
            placeholder="Ej: Backend Developer con 5+ años de experiencia en Python, FastAPI y PostgreSQL..."
          />
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            {saving ? "Guardando..." : "Guardar"}
          </button>
          <button
            onClick={handleSuggest}
            disabled={suggesting}
            className="border px-4 py-2 rounded-md text-sm font-medium hover:bg-muted disabled:opacity-50"
          >
            {suggesting ? "Generando..." : "Obtener sugerencias IA"}
          </button>
        </div>
      </div>

      {suggesting && (
        <div className="text-center py-8 text-muted-foreground text-sm">
          Analizando perfil y generando sugerencias...
        </div>
      )}

      {variants.length > 0 && !suggesting && (
        <SEOSuggestions variants={variants} onSelect={handleSelect} />
      )}
    </div>
  );
}
