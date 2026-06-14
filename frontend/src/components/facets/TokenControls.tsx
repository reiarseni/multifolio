"use client";

interface TokenGroup {
  color: Record<string, string>;
  typography: Record<string, string>;
  spacing: Record<string, string>;
  shape: Record<string, string>;
  density: string;
}

interface Props {
  activeTab: string;
  tokens: TokenGroup;
  onUpdate: (group: string, key: string, value: string | number) => void;
}

const COLOR_KEYS = [
  { key: "primary", label: "Primario" },
  { key: "background", label: "Fondo" },
  { key: "surface", label: "Superficie" },
  { key: "text_heading", label: "Encabezado" },
  { key: "text_body", label: "Cuerpo" },
  { key: "text_muted", label: "Atenuado" },
  { key: "border", label: "Borde" },
  { key: "accent", label: "Acento" },
];

function ColorControls({ tokens, onUpdate }: Omit<Props, "activeTab">) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {COLOR_KEYS.map(({ key, label }) => (
        <div key={key} className="space-y-1">
          <label className="text-xs font-medium text-gray-700">{label}</label>
          <div className="flex items-center gap-2">
            <input type="color" value={tokens.color[key] || "#000000"} onChange={(e) => onUpdate("color", key, e.target.value)} className="w-10 h-8 rounded border border-gray-300 cursor-pointer" />
            <input type="text" value={tokens.color[key] || ""} onChange={(e) => onUpdate("color", key, e.target.value)} placeholder="#000000" className="flex-1 px-2 py-1 text-xs border border-gray-300 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

function TypographyControls({ tokens, onUpdate }: Omit<Props, "activeTab">) {
  return (
    <div className="space-y-4">
      {[
        { key: "font_heading", label: "Fuente heading", placeholder: "Georgia, serif" },
        { key: "font_body", label: "Fuente body", placeholder: "system-ui, sans-serif" },
        { key: "size_base", label: "Tamaño base", placeholder: "1rem" },
      ].map(({ key, label, placeholder }) => (
        <div key={key} className="space-y-2">
          <label className="text-xs font-medium text-gray-700">{label}</label>
          <input type="text" value={tokens.typography[key] || ""} onChange={(e) => onUpdate("typography", key, e.target.value)} placeholder={placeholder} className="w-full px-2 py-1 text-xs border border-gray-300 rounded" />
        </div>
      ))}
      <div className="grid grid-cols-2 gap-2">
        {[{ key: "size_xs", label: "xs", placeholder: "0.75rem" }, { key: "size_lg", label: "lg", placeholder: "1.125rem" }].map(({ key, label, placeholder }) => (
          <div key={key} className="space-y-1">
            <label className="text-xs font-medium text-gray-700">Tamaño {label}</label>
            <input type="text" value={tokens.typography[key] || ""} onChange={(e) => onUpdate("typography", key, e.target.value)} placeholder={placeholder} className="w-full px-2 py-1 text-xs border border-gray-300 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

function SpacingControls({ tokens, onUpdate }: Omit<Props, "activeTab">) {
  return (
    <div className="space-y-4">
      {[
        { key: "section_gap", label: "Entre secciones", placeholder: "2rem" },
        { key: "item_gap", label: "Entre ítems", placeholder: "1rem" },
        { key: "padding_block", label: "Padding bloques", placeholder: "1.5rem" },
      ].map(({ key, label, placeholder }) => (
        <div key={key} className="space-y-2">
          <label className="text-xs font-medium text-gray-700">{label}</label>
          <input type="text" value={tokens.spacing[key] || ""} onChange={(e) => onUpdate("spacing", key, e.target.value)} placeholder={placeholder} className="w-full px-2 py-1 text-xs border border-gray-300 rounded" />
        </div>
      ))}
    </div>
  );
}

function ShapeControls({ tokens, onUpdate }: Omit<Props, "activeTab">) {
  return (
    <div className="space-y-4">
      {[
        { key: "radius_sm", label: "Radio sm", placeholder: "0.25rem" },
        { key: "radius_md", label: "Radio md", placeholder: "0.5rem" },
        { key: "radius_lg", label: "Radio lg", placeholder: "1rem" },
      ].map(({ key, label, placeholder }) => (
        <div key={key} className="space-y-2">
          <label className="text-xs font-medium text-gray-700">{label}</label>
          <input type="text" value={tokens.shape[key] || ""} onChange={(e) => onUpdate("shape", key, e.target.value)} placeholder={placeholder} className="w-full px-2 py-1 text-xs border border-gray-300 rounded" />
        </div>
      ))}
      <div className="space-y-2">
        <label className="text-xs font-medium text-gray-700">Sombra</label>
        <select value={tokens.shape.shadow_none || "none"} onChange={(e) => onUpdate("shape", "shadow_none", e.target.value)} className="w-full px-2 py-1 text-xs border border-gray-300 rounded">
          <option value="none">Ninguna</option>
          <option value="sm">Pequeña</option>
          <option value="md">Mediana</option>
        </select>
      </div>
    </div>
  );
}

function DensityControls({ tokens, onUpdate }: Omit<Props, "activeTab">) {
  return (
    <div className="space-y-2">
      <label className="text-xs font-medium text-gray-700">Densidad</label>
      <div className="grid grid-cols-3 gap-2">
        {(["compact", "balanced", "spacious"] as const).map((d) => (
          <button key={d} onClick={() => onUpdate("density", d, d)} className={`px-3 py-2 text-xs rounded border transition-colors ${tokens.density === d ? "border-primary bg-primary/10 font-medium" : "border-gray-300 hover:bg-gray-50"}`}>
            {d === "compact" ? "Compacto" : d === "balanced" ? "Balanceado" : "Espacioso"}
          </button>
        ))}
      </div>
    </div>
  );
}

export function TokenControls({ activeTab, tokens, onUpdate }: Props) {
  const props = { tokens, onUpdate };
  switch (activeTab) {
    case "color": return <ColorControls {...props} />;
    case "typography": return <TypographyControls {...props} />;
    case "spacing": return <SpacingControls {...props} />;
    case "shape": return <ShapeControls {...props} />;
    case "density": return <DensityControls {...props} />;
    default: return null;
  }
}
