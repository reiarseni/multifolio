"use client";

import { useEffect, useState } from "react";
import {
  reviewLinksApi,
  type ReviewLink,
  type ReviewLinkCreatePayload,
} from "@/lib/api/review-links";

interface ReviewLinkSettingsProps {
  facetId: string;
}

export function ReviewLinkSettings({ facetId }: ReviewLinkSettingsProps) {
  const [links, setLinks] = useState<ReviewLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<ReviewLinkCreatePayload>({
    label: "",
    password: "",
    expires_in_hours: undefined,
  });

  useEffect(() => {
    reviewLinksApi.listLinks(facetId).then((data) => {
      setLinks(data);
      setLoading(false);
    });
  }, [facetId]);

  const handleCreate = async () => {
    setCreating(true);
    const payload: ReviewLinkCreatePayload = {
      label: form.label || undefined,
      password: form.password || undefined,
      expires_in_hours: form.expires_in_hours || undefined,
    };
    const newLink = await reviewLinksApi.createLink(facetId, payload);
    setLinks([newLink, ...links]);
    setForm({ label: "", password: "", expires_in_hours: undefined });
    setShowForm(false);
    setCreating(false);
  };

  const handleDelete = async (linkId: string) => {
    await reviewLinksApi.deleteLink(linkId);
    setLinks(links.filter((l) => l.id !== linkId));
  };

  const copyLink = (token: string) => {
    const url = `${window.location.origin}/review/${token}`;
    navigator.clipboard.writeText(url);
  };

  if (loading) {
    return <div className="text-muted-foreground">Cargando links...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Links Activos</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="border rounded-md px-3 py-1 text-sm hover:bg-muted"
        >
          {showForm ? "Cancelar" : "+ Nuevo Link"}
        </button>
      </div>

      {showForm && (
        <div className="border rounded-lg p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground">
              Etiqueta (opcional)
            </label>
            <input
              type="text"
              value={form.label || ""}
              onChange={(e) => setForm({ ...form, label: e.target.value })}
              placeholder="Ej: Reclutador de Google"
              className="mt-1 block w-full border rounded-md px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground">
              Contraseña (opcional, mín. 6 caracteres)
            </label>
            <input
              type="password"
              value={form.password || ""}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Dejar vacío sin protección"
              className="mt-1 block w-full border rounded-md px-3 py-2 text-sm"
              minLength={6}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground">
              Expiración (horas, opcional)
            </label>
            <input
              type="number"
              value={form.expires_in_hours || ""}
              onChange={(e) =>
                setForm({
                  ...form,
                  expires_in_hours: e.target.value
                    ? parseInt(e.target.value)
                    : undefined,
                })
              }
              placeholder="Ej: 72 (3 días)"
              min={1}
              max={720}
              className="mt-1 block w-full border rounded-md px-3 py-2 text-sm"
            />
          </div>

          <button
            onClick={handleCreate}
            disabled={creating}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 text-sm"
          >
            {creating ? "Creando..." : "Crear Link"}
          </button>
        </div>
      )}

      {links.length === 0 ? (
        <p className="text-muted-foreground text-sm">
          No hay links creados. Crea uno para compartir tu portfolio.
        </p>
      ) : (
        <div className="space-y-3">
          {links.map((link) => (
            <div
              key={link.id}
              className="border rounded-lg p-4 flex items-center justify-between"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">
                    {link.label || "Sin etiqueta"}
                  </span>
                  {link.requires_password && (
                    <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">
                      Contraseña
                    </span>
                  )}
                  {link.expires_at && (
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                      Expira{" "}
                      {new Date(link.expires_at).toLocaleDateString("es-AR")}
                    </span>
                  )}
                  {link.is_used && (
                    <span className="text-xs bg-gray-100 text-gray-800 px-2 py-0.5 rounded">
                      Usado
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground font-mono">
                  /review/{link.token.slice(0, 12)}...
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => copyLink(link.token)}
                  className="text-xs border rounded px-2 py-1 hover:bg-muted"
                >
                  Copiar
                </button>
                <button
                  onClick={() => handleDelete(link.id)}
                  className="text-xs text-destructive hover:text-destructive/80"
                >
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
