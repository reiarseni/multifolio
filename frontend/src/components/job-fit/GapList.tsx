"use client";

import type { GapItem, ReorderSuggestion } from "@/lib/api/job-fit";

interface GapListProps {
  gaps: GapItem[];
  suggestions: string[];
  reorderSuggestion: ReorderSuggestion | null;
  onApplyReorder?: () => void;
}

const severityColors: Record<string, string> = {
  high: "bg-red-100 border-red-300 text-red-800",
  medium: "bg-yellow-100 border-yellow-300 text-yellow-800",
  low: "bg-blue-100 border-blue-300 text-blue-800",
};

const severityLabels: Record<string, string> = {
  high: "Alta",
  medium: "Media",
  low: "Baja",
};

export function GapList({ gaps, suggestions, reorderSuggestion, onApplyReorder }: GapListProps) {
  return (
    <div className="space-y-6">
      {gaps.length > 0 && (
        <div className="border rounded-lg p-4">
          <p className="text-sm font-medium mb-4">Brechas detectadas ({gaps.length})</p>
          <div className="space-y-3">
            {gaps.map((gap, i) => (
              <div key={i} className={`border rounded-md p-3 text-sm ${severityColors[gap.severity] ?? "border-gray-200"}`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium capitalize">{gap.category}</span>
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-white/50">
                    {severityLabels[gap.severity] ?? gap.severity}
                  </span>
                </div>
                <p className="mb-1">{gap.description}</p>
                <p className="text-xs opacity-75">💡 {gap.suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="border rounded-lg p-4">
          <p className="text-sm font-medium mb-3">Sugerencias de mejora</p>
          <ul className="space-y-2">
            {suggestions.map((s, i) => (
              <li key={i} className="text-sm flex gap-2">
                <span className="text-primary">•</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {reorderSuggestion && (
        <div className="border rounded-lg p-4">
          <p className="text-sm font-medium mb-2">Reordenamiento sugerido</p>
          <p className="text-sm text-muted-foreground mb-3">{reorderSuggestion.rationale}</p>
          <div className="flex flex-wrap gap-2 mb-3">
            {reorderSuggestion.proposed_order.map((section, i) => (
              <span
                key={section}
                className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded-md"
              >
                {i + 1}. {section}
              </span>
            ))}
          </div>
          {onApplyReorder && (
            <button
              onClick={onApplyReorder}
              className="text-sm bg-primary text-primary-foreground px-3 py-1.5 rounded-md hover:opacity-90"
            >
              Aplicar reordenamiento
            </button>
          )}
        </div>
      )}
    </div>
  );
}
