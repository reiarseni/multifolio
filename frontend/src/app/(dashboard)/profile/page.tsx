"use client";

import { useEffect, useRef, useState } from "react";
import { profileApi, type BaseProfile, type WorkExperience, type Education, type Skill, type Certification } from "@/lib/api/profile";
import { uploadFile } from "@/lib/api/upload";
import { ExperienceFormModal } from "@/components/profile/ExperienceFormModal";
import { EducationFormModal } from "@/components/profile/EducationFormModal";
import { SkillFormModal } from "@/components/profile/SkillFormModal";
import { CertificationFormModal } from "@/components/profile/CertificationFormModal";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function ProfilePage() {
  const [profile, setProfile] = useState<BaseProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [photoUploading, setPhotoUploading] = useState(false);
  const photoInputRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState({
    full_name: "", phone: "", location: "", title: "", bio: "",
    website: "", linkedin_url: "", github_url: "", photo_url: "",
  });

  const [expModal, setExpModal] = useState<{ open: boolean; item?: WorkExperience }>({ open: false });
  const [eduModal, setEduModal] = useState<{ open: boolean; item?: Education }>({ open: false });
  const [skillModal, setSkillModal] = useState<{ open: boolean; item?: Skill }>({ open: false });
  const [certModal, setCertModal] = useState<{ open: boolean; item?: Certification }>({ open: false });

  const reload = () =>
    profileApi.get().then((data) => {
      setProfile(data);
      setForm({
        full_name: data.full_name ?? "",
        phone: data.phone ?? "",
        location: data.location ?? "",
        title: data.title ?? "",
        bio: data.bio ?? "",
        website: data.website ?? "",
        linkedin_url: data.linkedin_url ?? "",
        github_url: data.github_url ?? "",
        photo_url: data.photo_url ?? "",
      });
    });

  useEffect(() => {
    reload()
      .catch(() => setError("No se pudo cargar el perfil"))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    const updated = await profileApi.update(form);
    setProfile(updated);
    setSaving(false);
  };

  const handlePhotoChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPhotoUploading(true);
    try {
      const url = await uploadFile(file);
      setForm((f) => ({ ...f, photo_url: url }));
    } finally {
      setPhotoUploading(false);
    }
  };

  if (loading) return <div className="text-muted-foreground">Loading...</div>;
  if (error) return <div className="text-destructive">{error}</div>;

  return (
    <div className="max-w-3xl space-y-8">
      <h1 className="text-2xl font-bold">Perfil</h1>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold">Información personal</h2>

        <div className="flex items-center gap-4 mb-4">
          {form.photo_url ? (
            <img
              src={form.photo_url.startsWith("/media") ? `${BASE_URL}${form.photo_url}` : form.photo_url}
              alt="Foto de perfil"
              className="w-20 h-20 rounded-full object-cover border"
            />
          ) : (
            <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center text-muted-foreground text-xs">Sin foto</div>
          )}
          <div>
            <button
              onClick={() => photoInputRef.current?.click()}
              disabled={photoUploading}
              className="text-sm border rounded-md px-3 py-1.5 hover:bg-muted disabled:opacity-50"
            >
              {photoUploading ? "Subiendo..." : "Cambiar foto"}
            </button>
            <input ref={photoInputRef} type="file" accept="image/*" className="hidden" onChange={handlePhotoChange} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-muted-foreground">Nombre completo</label>
            <input className="w-full border rounded-md px-3 py-2 text-sm" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Teléfono</label>
            <input className="w-full border rounded-md px-3 py-2 text-sm" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Ubicación</label>
            <input className="w-full border rounded-md px-3 py-2 text-sm" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          </div>
          <div className="col-span-2">
            <label className="text-sm text-muted-foreground">Título profesional</label>
            <input className="w-full border rounded-md px-3 py-2 text-sm" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div className="col-span-2">
            <label className="text-sm text-muted-foreground">Bio</label>
            <textarea className="w-full border rounded-md px-3 py-2 text-sm min-h-[80px]" value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Sitio web</label>
            <input className="w-full border rounded-md px-3 py-2 text-sm" value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">LinkedIn</label>
            <input className="w-full border rounded-md px-3 py-2 text-sm" value={form.linkedin_url} onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })} />
          </div>
          <div className="col-span-2">
            <label className="text-sm text-muted-foreground">GitHub</label>
            <input className="w-full border rounded-md px-3 py-2 text-sm" value={form.github_url} onChange={(e) => setForm({ ...form, github_url: e.target.value })} />
          </div>
        </div>
        <button onClick={handleSave} disabled={saving} className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50">
          {saving ? "Guardando..." : "Guardar cambios"}
        </button>
      </section>

      {/* Experiencia */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Experiencia laboral</h2>
          <button onClick={() => setExpModal({ open: true })} className="text-sm border rounded-md px-3 py-1.5 hover:bg-muted">+ Añadir</button>
        </div>
        {(profile?.experiences ?? []).length === 0 ? (
          <p className="text-sm text-muted-foreground">No hay elementos.</p>
        ) : (
          <div className="space-y-2">
            {(profile?.experiences ?? []).map((exp) => (
              <div key={exp.id} className="border rounded-md p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{exp.position}</p>
                    <p className="text-sm text-muted-foreground">{exp.company}</p>
                    <p className="text-xs text-muted-foreground">{exp.start_date} - {exp.is_current ? "Presente" : exp.end_date}</p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => setExpModal({ open: true, item: exp })} className="text-sm hover:underline">Editar</button>
                    <button onClick={async () => { await profileApi.deleteExperience(exp.id); reload(); }} className="text-destructive text-sm hover:underline">Eliminar</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Educación */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Educación</h2>
          <button onClick={() => setEduModal({ open: true })} className="text-sm border rounded-md px-3 py-1.5 hover:bg-muted">+ Añadir</button>
        </div>
        {(profile?.educations ?? []).length === 0 ? (
          <p className="text-sm text-muted-foreground">No hay elementos.</p>
        ) : (
          <div className="space-y-2">
            {(profile?.educations ?? []).map((edu) => (
              <div key={edu.id} className="border rounded-md p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{edu.degree}</p>
                    <p className="text-sm text-muted-foreground">{edu.institution}</p>
                    <p className="text-xs text-muted-foreground">{edu.start_date} - {edu.is_current ? "Presente" : edu.end_date}</p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => setEduModal({ open: true, item: edu })} className="text-sm hover:underline">Editar</button>
                    <button onClick={async () => { await profileApi.deleteEducation(edu.id); reload(); }} className="text-destructive text-sm hover:underline">Eliminar</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Habilidades */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Habilidades</h2>
          <button onClick={() => setSkillModal({ open: true })} className="text-sm border rounded-md px-3 py-1.5 hover:bg-muted">+ Añadir</button>
        </div>
        {(profile?.skills ?? []).length === 0 ? (
          <p className="text-sm text-muted-foreground">No hay elementos.</p>
        ) : (
          <div className="space-y-2">
            {(profile?.skills ?? []).map((skill) => (
              <div key={skill.id} className="border rounded-md p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{skill.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {skill.is_transversal ? (
                        <span className="inline-block bg-blue-100 text-blue-700 rounded px-1.5 text-xs mr-1">Transversal</span>
                      ) : "Contextual"}
                      {skill.level ? ` · ${skill.level}` : ""}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => setSkillModal({ open: true, item: skill })} className="text-sm hover:underline">Editar</button>
                    <button onClick={async () => { await profileApi.deleteSkill(skill.id); reload(); }} className="text-destructive text-sm hover:underline">Eliminar</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Certificaciones */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Certificaciones</h2>
          <button onClick={() => setCertModal({ open: true })} className="text-sm border rounded-md px-3 py-1.5 hover:bg-muted">+ Añadir</button>
        </div>
        {(profile?.certifications ?? []).length === 0 ? (
          <p className="text-sm text-muted-foreground">No hay elementos.</p>
        ) : (
          <div className="space-y-2">
            {(profile?.certifications ?? []).map((cert) => (
              <div key={cert.id} className="border rounded-md p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{cert.name}</p>
                    <p className="text-sm text-muted-foreground">{cert.issuer}</p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => setCertModal({ open: true, item: cert })} className="text-sm hover:underline">Editar</button>
                    <button onClick={async () => { await profileApi.deleteCertification(cert.id); reload(); }} className="text-destructive text-sm hover:underline">Eliminar</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <ExperienceFormModal
        open={expModal.open}
        onOpenChange={(o) => setExpModal({ open: o })}
        initial={expModal.item}
        onSaved={reload}
      />
      <EducationFormModal
        open={eduModal.open}
        onOpenChange={(o) => setEduModal({ open: o })}
        initial={eduModal.item}
        onSaved={reload}
      />
      <SkillFormModal
        open={skillModal.open}
        onOpenChange={(o) => setSkillModal({ open: o })}
        initial={skillModal.item}
        onSaved={reload}
      />
      <CertificationFormModal
        open={certModal.open}
        onOpenChange={(o) => setCertModal({ open: o })}
        initial={certModal.item}
        onSaved={reload}
      />
    </div>
  );
}
