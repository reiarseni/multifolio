interface OpenToRoleBadgeProps {
  status: string;
  role_type: string | null;
  modality: string | null;
  location: string | null;
}

const STATUS_LABELS: Record<string, string> = {
  actively_looking: "Activamente buscando",
  open_to_opportunities: "Abierto a oportunidades",
  not_available: "No disponible",
};

const MODALITY_LABELS: Record<string, string> = {
  remote: "Remoto",
  hybrid: "Híbrido",
  onsite: "Presencial",
};

export function OpenToRoleBadge({ status, role_type, modality, location }: OpenToRoleBadgeProps) {
  if (status === "not_available") return null;

  return (
    <div className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm">
      <span className="font-medium">{STATUS_LABELS[status] ?? status}</span>
      {role_type && (
        <>
          <span className="text-muted-foreground">·</span>
          <span>{role_type}</span>
        </>
      )}
      {modality && (
        <>
          <span className="text-muted-foreground">·</span>
          <span>{MODALITY_LABELS[modality] ?? modality}</span>
        </>
      )}
      {location && (
        <>
          <span className="text-muted-foreground">·</span>
          <span>{location}</span>
        </>
      )}
    </div>
  );
}
