"use client";

import { useEffect, useState } from "react";
import { profileApi, type BaseProfile } from "@/lib/api/profile";

export default function ProfilePage() {
  const [profile, setProfile] = useState<BaseProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    full_name: "",
    phone: "",
    location: "",
    title: "",
    bio: "",
    website: "",
    linkedin_url: "",
    github_url: "",
  });

  useEffect(() => {
    profileApi.get()
      .then((data) => {
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
        });
      })
      .catch(() => setError("No se pudo cargar el perfil"))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    const updated = await profileApi.update(form);
    setProfile(updated);
    setSaving(false);
  };

  const handleDeleteExperience = async (id: string) => {
    await profileApi.deleteExperience(id);
    const updated = await profileApi.get();
    setProfile(updated);
  };

  const handleDeleteEducation = async (id: string) => {
    await profileApi.deleteEducation(id);
    const updated = await profileApi.get();
    setProfile(updated);
  };

  const handleDeleteSkill = async (id: string) => {
    await profileApi.deleteSkill(id);
    const updated = await profileApi.get();
    setProfile(updated);
  };

  const handleDeleteCertification = async (id: string) => {
    await profileApi.deleteCertification(id);
    const updated = await profileApi.get();
    setProfile(updated);
  };

  if (loading) {
    return <div className="text-muted-foreground">Loading...</div>;
  }

  if (error) {
    return <div className="text-destructive">{error}</div>;
  }

  return (
    <div className="max-w-3xl space-y-8">
      <h1 className="text-2xl font-bold">Perfil</h1>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold">Información personal</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-muted-foreground">Nombre completo</label>
            <input
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Teléfono</label>
            <input
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Ubicación</label>
            <input
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
            />
          </div>
          <div className="col-span-2">
            <label className="text-sm text-muted-foreground">Título profesional</label>
            <input
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
          </div>
          <div className="col-span-2">
            <label className="text-sm text-muted-foreground">Bio</label>
            <textarea
              className="w-full border rounded-md px-3 py-2 text-sm min-h-[80px]"
              value={form.bio}
              onChange={(e) => setForm({ ...form, bio: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Sitio web</label>
            <input
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={form.website}
              onChange={(e) => setForm({ ...form, website: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">LinkedIn</label>
            <input
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={form.linkedin_url}
              onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })}
            />
          </div>
          <div className="col-span-2">
            <label className="text-sm text-muted-foreground">GitHub</label>
            <input
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={form.github_url}
              onChange={(e) => setForm({ ...form, github_url: e.target.value })}
            />
          </div>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
        >
          {saving ? "Guardando..." : "Guardar cambios"}
        </button>
      </section>

      <SectionList
        title="Experiencia laboral"
        items={profile?.experiences ?? []}
        renderItem={(exp) => (
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">{exp.position}</p>
              <p className="text-sm text-muted-foreground">{exp.company}</p>
              <p className="text-xs text-muted-foreground">
                {exp.start_date} - {exp.is_current ? "Presente" : exp.end_date}
              </p>
            </div>
            <button
              onClick={() => handleDeleteExperience(exp.id)}
              className="text-destructive text-sm hover:underline"
            >
              Eliminar
            </button>
          </div>
        )}
      />

      <SectionList
        title="Educación"
        items={profile?.educations ?? []}
        renderItem={(edu) => (
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">{edu.degree}</p>
              <p className="text-sm text-muted-foreground">{edu.institution}</p>
              <p className="text-xs text-muted-foreground">
                {edu.start_date} - {edu.is_current ? "Presente" : edu.end_date}
              </p>
            </div>
            <button
              onClick={() => handleDeleteEducation(edu.id)}
              className="text-destructive text-sm hover:underline"
            >
              Eliminar
            </button>
          </div>
        )}
      />

      <SectionList
        title="Habilidades"
        items={profile?.skills ?? []}
        renderItem={(skill) => (
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">{skill.name}</p>
              <p className="text-xs text-muted-foreground">
                {skill.is_transversal ? "Transversal" : "Contextual"}
                {skill.level ? ` · ${skill.level}` : ""}
              </p>
            </div>
            <button
              onClick={() => handleDeleteSkill(skill.id)}
              className="text-destructive text-sm hover:underline"
            >
              Eliminar
            </button>
          </div>
        )}
      />

      <SectionList
        title="Certificaciones"
        items={profile?.certifications ?? []}
        renderItem={(cert) => (
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">{cert.name}</p>
              <p className="text-sm text-muted-foreground">{cert.issuer}</p>
            </div>
            <button
              onClick={() => handleDeleteCertification(cert.id)}
              className="text-destructive text-sm hover:underline"
            >
              Eliminar
            </button>
          </div>
        )}
      />
    </div>
  );
}

function SectionList<T extends { id: string }>({
  title,
  items,
  renderItem,
}: {
  title: string;
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}) {
  return (
    <section className="space-y-3">
      <h2 className="text-lg font-semibold">{title}</h2>
      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground">No hay elementos.</p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.id} className="border rounded-md p-3">
              {renderItem(item)}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
