"use client";

import { Dialog } from "@base-ui/react/dialog";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { profileApi, type Certification } from "@/lib/api/profile";

const schema = z.object({
  name: z.string().min(1, "Requerido"),
  issuer: z.string().min(1, "Requerido"),
  issue_date: z.string().optional(),
  expiry_date: z.string().optional(),
  credential_url: z.string().url("URL inválida").optional().or(z.literal("")),
});

type FormData = z.infer<typeof schema>;

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initial?: Certification;
  onSaved: () => void;
}

export function CertificationFormModal({ open, onOpenChange, initial, onSaved }: Props) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: initial?.name ?? "",
      issuer: initial?.issuer ?? "",
      issue_date: initial?.issue_date ?? "",
      expiry_date: initial?.expiry_date ?? "",
      credential_url: initial?.credential_url ?? "",
    },
  });

  const onSubmit = async (data: FormData) => {
    const payload = {
      ...data,
      issue_date: data.issue_date || undefined,
      expiry_date: data.expiry_date || undefined,
      credential_url: data.credential_url || undefined,
    };
    if (initial?.id) {
      await profileApi.updateCertification(initial.id, payload);
    } else {
      await profileApi.createCertification(payload);
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
            {initial ? "Editar certificación" : "Añadir certificación"}
          </Dialog.Title>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
            <div>
              <label className="text-sm text-muted-foreground">Nombre *</label>
              <input className="w-full border rounded-md px-3 py-2 text-sm" {...register("name")} />
              {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Emisor *</label>
              <input className="w-full border rounded-md px-3 py-2 text-sm" {...register("issuer")} />
              {errors.issuer && <p className="text-xs text-destructive">{errors.issuer.message}</p>}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm text-muted-foreground">Fecha de emisión</label>
                <input type="date" className="w-full border rounded-md px-3 py-2 text-sm" {...register("issue_date")} />
              </div>
              <div>
                <label className="text-sm text-muted-foreground">Fecha de expiración</label>
                <input type="date" className="w-full border rounded-md px-3 py-2 text-sm" {...register("expiry_date")} />
              </div>
            </div>
            <div>
              <label className="text-sm text-muted-foreground">URL de credencial</label>
              <input type="url" className="w-full border rounded-md px-3 py-2 text-sm" {...register("credential_url")} />
              {errors.credential_url && <p className="text-xs text-destructive">{errors.credential_url.message}</p>}
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
