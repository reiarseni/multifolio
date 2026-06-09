import type { PublicSkill } from "@/lib/api/public";

export function CVSkills({ items }: { items: PublicSkill[] }) {
  if (items.length === 0) return null;

  return (
    <section className="mb-8">
      <h2 className="text-lg font-semibold border-b pb-1 mb-3">Habilidades</h2>
      <div className="flex flex-wrap gap-2">
        {items.map((skill) => (
          <span
            key={skill.id}
            className="px-3 py-1 rounded-full text-sm border bg-muted/30"
          >
            {skill.name}
            {skill.level && <span className="text-muted-foreground ml-1">· {skill.level}</span>}
          </span>
        ))}
      </div>
    </section>
  );
}
