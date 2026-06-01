export function OverviewCards({
  profileCount,
  projectCount,
  facetCount,
}: {
  profileCount: number;
  projectCount: number;
  facetCount: number;
}) {
  const cards = [
    { label: "Perfil", value: profileCount, href: "/profile", desc: "Completa tu información personal" },
    { label: "Proyectos", value: projectCount, href: "/projects", desc: "Proyectos demostrativos creados" },
    { label: "Facetas", value: facetCount, href: "/facets", desc: "CV públicos configurados" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {cards.map((card) => (
        <a
          key={card.href}
          href={card.href}
          className="border rounded-md p-4 hover:bg-muted/30 transition-colors"
        >
          <p className="text-2xl font-bold">{card.value}</p>
          <p className="font-medium mt-1">{card.label}</p>
          <p className="text-xs text-muted-foreground mt-1">{card.desc}</p>
        </a>
      ))}
    </div>
  );
}
