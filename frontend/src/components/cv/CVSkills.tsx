import type { PublicSkill } from "@/lib/api/public";

export function CVSkills({ items }: { items: PublicSkill[] }) {
  if (items.length === 0) return null;

  return (
    <section className="mb-8">
      <h2
        className="text-lg font-semibold border-b pb-1 mb-3"
        style={{
          color: "var(--color-text-heading, inherit)",
          borderColor: "var(--color-border, currentColor)",
          fontFamily: "var(--font-heading, inherit)",
        }}
      >
        Habilidades
      </h2>
      <div className="flex flex-wrap gap-2">
        {items.map((skill) => (
          <span
            key={skill.id}
            className="px-3 py-1 rounded-full text-sm border"
            style={{
              borderColor: "var(--color-border, currentColor)",
              backgroundColor: "var(--color-surface, transparent)",
              color: "var(--color-text-body, inherit)",
              borderRadius: "var(--radius-md, 9999px)",
            }}
          >
            {skill.name}
            {skill.level && (
              <span style={{ color: "var(--color-text-muted, inherit)" }} className="ml-1">
                · {skill.level}
              </span>
            )}
          </span>
        ))}
      </div>
    </section>
  );
}
