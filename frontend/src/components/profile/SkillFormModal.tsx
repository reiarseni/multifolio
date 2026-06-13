"use client";

import { Dialog } from "@base-ui/react/dialog";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { profileApi, type Skill } from "@/lib/api/profile";

const schema = z.object({
  name: z.string().min(1, "Requerido"),
  category: z.string().optional(),
  level: z.string().optional(),
  is_transversal: z.boolean(),
});

type FormData = z.infer<typeof schema>;

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initial?: Skill;
  onSaved: () => void;
}

export function SkillFormModal({ open, onOpenChange, initial, onSaved }: Props) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: initial?.name ?? "",
      category: initial?.category ?? "",
      level: initial?.level ?? "",
      is_transversal: initial?.is_transversal ?? false,
    },
  });

  const onSubmit = async (data: FormData) => {
    if (initial?.id) {
      await profileApi.updateSkill(initial.id, data);
    } else {
      await profileApi.createSkill(data);
    }
    onSaved();
    onOpenChange(false);
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 bg-black/40 z-40" />
        <Dialog.Popup className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md bg-background border rounded-lg shadow-lg p-6">
          <Dialog.Title className="text-lg font-semibold mb-4">
            {initial ? "Editar habilidad" : "Añadir habilidad"}
          </Dialog.Title>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
            <div>
              <label className="text-sm text-muted-foreground">Nombre *</label>
              <input className="w-full border rounded-md px-3 py-2 text-sm" {...register("name")} />
              {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Categoría</label>
              <input className="w-full border rounded-md px-3 py-2 text-sm" {...register("category")} />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Nivel</label>
              <select className="w-full border rounded-md px-3 py-2 text-sm" {...register("level")}>
                <option value="">Sin especificar</option>
                <option value="básico">Básico</option>
                <option value="intermedio">Intermedio</option>
                <option value="avanzado">Avanzado</option>
                <option value="experto">Experto</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="skill_transversal" {...register("is_transversal")} />
              <label htmlFor="skill_transversal" className="text-sm">
                Transversal (se pre-selecciona en todas las facetas)
              </label>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Dialog.Close className="px-4 py-2 text-sm border rounded-md hover:bg-muted">Cancelar</Dialog.Close>
              <button type="submit" disabled={isSubmitting} className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md disabled:opacity-50">
                {isSubmitting ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </form>
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
