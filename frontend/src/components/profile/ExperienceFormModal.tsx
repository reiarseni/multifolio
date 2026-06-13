"use client";

import { Dialog } from "@base-ui/react/dialog";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { profileApi, type WorkExperience } from "@/lib/api/profile";

const schema = z.object({
  company: z.string().min(1, "Requerido"),
  position: z.string().min(1, "Requerido"),
  description: z.string().optional(),
  start_date: z.string().min(1, "Requerido"),
  end_date: z.string().optional(),
  is_current: z.boolean(),
});

type FormData = z.infer<typeof schema>;

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initial?: WorkExperience;
  onSaved: () => void;
}

export function ExperienceFormModal({ open, onOpenChange, initial, onSaved }: Props) {
  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      company: initial?.company ?? "",
      position: initial?.position ?? "",
      description: initial?.description ?? "",
      start_date: initial?.start_date ?? "",
      end_date: initial?.end_date ?? "",
      is_current: initial?.is_current ?? false,
    },
  });

  const isCurrent = watch("is_current");

  const onSubmit = async (data: FormData) => {
    const payload = {
      ...data,
      end_date: data.is_current ? undefined : data.end_date || undefined,
    };
    if (initial?.id) {
      await profileApi.updateExperience(initial.id, payload);
    } else {
      await profileApi.createExperience(payload);
    }
    onSaved();
    onOpenChange(false);
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 bg-black/40 z-40" />
        <Dialog.Popup className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-lg bg-background border rounded-lg shadow-lg p-6">
          <Dialog.Title className="text-lg font-semibold mb-4">
            {initial ? "Editar experiencia" : "Añadir experiencia"}
          </Dialog.Title>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm text-muted-foreground">Empresa *</label>
                <input className="w-full border rounded-md px-3 py-2 text-sm" {...register("company")} />
                {errors.company && <p className="text-xs text-destructive">{errors.company.message}</p>}
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Cargo *</label>
                <input className="w-full border rounded-md px-3 py-2 text-sm" {...register("position")} />
                {errors.position && <p className="text-xs text-destructive">{errors.position.message}</p>}
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Fecha inicio *</label>
                <input type="date" className="w-full border rounded-md px-3 py-2 text-sm" {...register("start_date")} />
                {errors.start_date && <p className="text-xs text-destructive">{errors.start_date.message}</p>}
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Fecha fin</label>
                <input type="date" disabled={isCurrent} className="w-full border rounded-md px-3 py-2 text-sm disabled:opacity-50" {...register("end_date")} />
              </div>
              <div className="col-span-2 flex items-center gap-2">
                <input type="checkbox" id="exp_current" {...register("is_current")} />
                <label htmlFor="exp_current" className="text-sm">Trabajo actual</label>
              </div>
              <div className="col-span-2">
                <label className="text-sm text-muted-foreground">Descripción</label>
                <textarea className="w-full border rounded-md px-3 py-2 text-sm min-h-[80px]" {...register("description")} />
              </div>
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
