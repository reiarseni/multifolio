"use client";

import { useEffect, useState } from "react";
import { openToRoleApi, type OpenToRole } from "@/lib/api/open-to-role";

interface OpenToRoleFormProps {
  facetId: string;
}

const STATUS_OPTIONS = [
  { value: "actively_looking", label: "Activamente buscando" },
  { value: "open_to_opportunities", label: "Abierto a oportunidades" },
  { value: "not_available", label: "No disponible" },
];

const ROLE_OPTIONS = [
  "Frontend",
  "Backend",
  "Fullstack",
  "DevOps",
  "Data",
  "Mobile",
  "UI/UX",
  "QA",
  "Project Manager",
  "Other",
];

const MODALITY_OPTIONS = [
  { value: "remote", label: "Remoto" },
  { value: "hybrid", label: "Híbrido" },
  { value: "onsite", label: "Presencial" },
];

export function OpenToRoleForm({ facetId }: OpenToRoleFormProps) {
  const [data, setData] = useState<OpenToRole | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    openToRoleApi.get(facetId).then((d) => {
      setData(d);
      setLoading(false);
    });
  }, [facetId]);

  const handleSave = async () => {
    if (!data) return;
    setSaving(true);
    await openToRoleApi.upsert(facetId, data);
    setSaving(false);
  };

  const handleDelete = async () => {
    setSaving(true);
    await openToRoleApi.delete(facetId);
    setData(null);
    setSaving(false);
  };

  if (loading) {
    return <div className="text-muted-foreground">Cargando...</div>;
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium">Estado</label>
        <select
          value={data?.status ?? "not_available"}
          onChange={(e) => setData((prev) => ({ ...prev, status: e.target.value } as OpenToRole))}
          className="w-full border rounded-md px-3 py-2 mt-1"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="text-sm font-medium">Tipo de rol</label>
        <select
          value={data?.role_type ?? ""}
          onChange={(e) => setData((prev) => ({ ...prev, role_type: e.target.value || null } as OpenToRole))}
          className="w-full border rounded-md px-3 py-2 mt-1"
        >
          <option value="">Seleccionar...</option>
          {ROLE_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="text-sm font-medium">Modalidad</label>
        <select
          value={data?.modality ?? ""}
          onChange={(e) => setData((prev) => ({ ...prev, modality: e.target.value || null } as OpenToRole))}
          className="w-full border rounded-md px-3 py-2 mt-1"
        >
          <option value="">Seleccionar...</option>
          {MODALITY_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="text-sm font-medium">Ubicación</label>
        <input
          type="text"
          value={data?.location ?? ""}
          onChange={(e) => setData((prev) => ({ ...prev, location: e.target.value || null } as OpenToRole))}
          placeholder="ej: Madrid, España"
          className="w-full border rounded-md px-3 py-2 mt-1"
        />
      </div>

      <div>
        <label className="text-sm font-medium">Zona horaria</label>
        <input
          type="text"
          value={data?.timezone ?? ""}
          onChange={(e) => setData((prev) => ({ ...prev, timezone: e.target.value || null } as OpenToRole))}
          placeholder="ej: Europe/Madrid"
          className="w-full border rounded-md px-3 py-2 mt-1"
        />
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleSave}
          disabled={saving}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm"
        >
          {saving ? "Guardando..." : "Guardar"}
        </button>
        {data && (
          <button
            onClick={handleDelete}
            disabled={saving}
            className="border px-4 py-2 rounded-md text-sm hover:bg-muted"
          >
            Eliminar
          </button>
        )}
      </div>
    </div>
  );
}
