"use client";

import { useEffect, useState } from "react";
import { storiesApi, type StorySection } from "@/lib/api/stories";
import { SectionBlock } from "./SectionBlock";
import { MediaUploader } from "./MediaUploader";

interface StoryEditorProps {
  facetId: string;
}

const SECTION_TYPES = [
  { value: "context", label: "Contexto / Problema" },
  { value: "process", label: "Proceso" },
  { value: "solution", label: "Solución" },
  { value: "impact", label: "Impacto y resultados" },
];

export function StoryEditor({ facetId }: StoryEditorProps) {
  const [sections, setSections] = useState<StorySection[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    storiesApi.getStory(facetId).then((data) => {
      setSections(data);
      setLoading(false);
    });
  }, [facetId]);

  const handleAddSection = async (type: string) => {
    setSaving(true);
    const newSection = await storiesApi.createSection(facetId, {
      section_type: type,
      title: SECTION_LABELS[type] ?? type,
      order: sections.length,
    });
    setSections([...sections, newSection]);
    setSaving(false);
  };

  const handleUpdate = async (id: string, data: Partial<StorySection>) => {
    setSections((prev) =>
      prev.map((s) => (s.id === id ? { ...s, ...data } : s))
    );
    await storiesApi.updateSection(id, data);
  };

  const handleDelete = async (id: string) => {
    await storiesApi.deleteSection(id);
    setSections((prev) => prev.filter((s) => s.id !== id));
  };

  const handleToggleVisibility = async (id: string, visible: boolean) => {
    await storiesApi.updateSection(id, { is_visible: visible });
    setSections((prev) =>
      prev.map((s) => (s.id === id ? { ...s, is_visible: visible } : s))
    );
  };

  const handleMoveUp = async (index: number) => {
    if (index === 0) return;
    const newSections = [...sections];
    [newSections[index - 1], newSections[index]] = [newSections[index], newSections[index - 1]];
    setSections(newSections);
    await storiesApi.reorderSections(
      facetId,
      newSections.map((s) => s.id)
    );
  };

  const handleMoveDown = async (index: number) => {
    if (index === sections.length - 1) return;
    const newSections = [...sections];
    [newSections[index], newSections[index + 1]] = [newSections[index + 1], newSections[index]];
    setSections(newSections);
    await storiesApi.reorderSections(
      facetId,
      newSections.map((s) => s.id)
    );
  };

  const handleMediaUpload = async (sectionId: string, url: string) => {
    const section = sections.find((s) => s.id === sectionId);
    if (!section) return;
    const mediaUrls = [...(section.media_urls ?? []), url];
    await storiesApi.updateSection(sectionId, { media_urls: mediaUrls });
    setSections((prev) =>
      prev.map((s) =>
        s.id === sectionId ? { ...s, media_urls: mediaUrls } : s
      )
    );
  };

  if (loading) {
    return <div className="text-muted-foreground">Cargando historia...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Historia Estructurada</h2>
      </div>

      <div className="space-y-4">
        {sections.map((section, index) => (
          <div key={section.id} className="relative">
            <div className="absolute -left-8 top-4 flex flex-col gap-1">
              <button
                onClick={() => handleMoveUp(index)}
                disabled={index === 0}
                className="text-xs text-muted-foreground hover:text-foreground disabled:opacity-30"
              >
                ↑
              </button>
              <button
                onClick={() => handleMoveDown(index)}
                disabled={index === sections.length - 1}
                className="text-xs text-muted-foreground hover:text-foreground disabled:opacity-30"
              >
                ↓
              </button>
            </div>
            <SectionBlock
              section={section}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
              onToggleVisibility={handleToggleVisibility}
            />
            <div className="mt-2">
              <MediaUploader
                sectionId={section.id}
                onUpload={(url) => handleMediaUpload(section.id, url)}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        {SECTION_TYPES.map((type) => (
          <button
            key={type.value}
            onClick={() => handleAddSection(type.value)}
            disabled={saving}
            className="border rounded-md px-3 py-1 text-xs hover:bg-muted disabled:opacity-50"
          >
            + {type.label}
          </button>
        ))}
      </div>
    </div>
  );
}

const SECTION_LABELS: Record<string, string> = {
  context: "Contexto / Problema",
  process: "Proceso",
  solution: "Solución",
  impact: "Impacto y resultados",
};
