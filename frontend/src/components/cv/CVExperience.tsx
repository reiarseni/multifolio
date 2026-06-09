import type { PublicExperience } from "@/lib/api/public";

export function CVExperience({ items }: { items: PublicExperience[] }) {
  if (items.length === 0) return null;

  return (
    <section className="mb-8">
      <h2 className="text-lg font-semibold border-b pb-1 mb-3">Experiencia</h2>
      <div className="space-y-4">
        {items.map((exp) => (
          <div key={exp.id}>
            <div className="flex justify-between items-start">
              <div>
                <p className="font-medium">{exp.position}</p>
                <p className="text-sm text-muted-foreground">{exp.company}</p>
              </div>
              <p className="text-xs text-muted-foreground shrink-0 ml-4">
                {exp.start_date} - {exp.is_current ? "Presente" : exp.end_date}
              </p>
            </div>
            {exp.description && (
              <p className="text-sm mt-1">{exp.description}</p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
