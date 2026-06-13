"use client";

import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

interface Props {
  value: string[];
  onChange: (order: string[]) => void;
  disabled?: boolean;
}

const SECTION_LABELS: Record<string, string> = {
  experiencias: "Experiencias",
  habilidades: "Habilidades",
  estudios: "Estudios",
  proyectos: "Proyectos",
  certificaciones: "Certificaciones",
};

function SortableItem({ id, disabled }: { id: string; disabled?: boolean }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id, disabled });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="flex items-center gap-2 p-2 border rounded bg-background cursor-grab active:cursor-grabbing select-none"
    >
      <span className="text-muted-foreground">⠿</span>
      <span className="text-sm">{SECTION_LABELS[id] || id}</span>
    </div>
  );
}

export function SectionOrderer({ value, onChange, disabled }: Props) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = value.indexOf(active.id as string);
    const newIndex = value.indexOf(over.id as string);
    onChange(arrayMove(value, oldIndex, newIndex));
  };

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">Orden de secciones</label>
      <p className="text-xs text-muted-foreground">
        Arrastra para reordenar las secciones de tu portfolio.
      </p>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={value} strategy={verticalListSortingStrategy}>
          <div className="space-y-1">
            {value.map((id) => (
              <SortableItem key={id} id={id} disabled={disabled} />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
}
