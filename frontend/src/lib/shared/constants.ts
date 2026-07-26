export const PHOTO_SHAPE_CLASS: Record<string, string> = {
  circle: "rounded-full",
  rounded: "rounded-xl",
  square: "rounded-none",
};

export const WEB_LAYOUTS = [
  { value: "single-column", label: "Una columna" },
  { value: "sidebar", label: "Con barra lateral" },
  { value: "modular", label: "Modular" },
];

export const PDF_LAYOUTS = [
  { value: "classic", label: "Clásico" },
  { value: "two-column", label: "Dos columnas" },
  { value: "compact", label: "Compacto" },
];

export const STORY_SECTION_LABELS: Record<string, string> = {
  context: "Contexto / Problema",
  process: "Proceso",
  solution: "Solución",
  impact: "Impacto y resultados",
};
