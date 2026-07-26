"use client";

import type { SEOVariant } from "@/lib/api/seo";

interface SEOSuggestionsProps {
  variants: SEOVariant[];
  onSelect: (variant: SEOVariant) => void;
}

export function SEOSuggestions({ variants, onSelect }: SEOSuggestionsProps) {
  if (variants.length === 0) {
    return (
      <div className="text-sm text-muted-foreground text-center py-8">
        No se generaron sugerencias. Intenta de nuevo.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm font-medium">Sugerencias generadas por IA</p>
      <div className="grid gap-4">
        {variants.map((variant, i) => (
          <button
            key={i}
            onClick={() => onSelect(variant)}
            className="text-left border rounded-lg p-4 hover:border-primary hover:bg-accent/50 transition-colors cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <span className="text-xs font-medium text-muted-foreground bg-secondary px-2 py-0.5 rounded-full">
                Variante {i + 1}
              </span>
            </div>
            <p className="text-sm font-medium mb-1">{variant.title}</p>
            <p className="text-xs text-muted-foreground mb-2 line-clamp-2">{variant.description}</p>
            <p className="text-xs text-primary/70 italic">{variant.rationale}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
