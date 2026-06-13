"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { authApi } from "@/lib/api/auth";
import { setToken } from "@/lib/auth/token";

const navItems = [
  { href: "/dashboard", label: "Inicio" },
  { href: "/profile", label: "Perfil" },
  { href: "/projects", label: "Proyectos" },
  { href: "/facets", label: "Facetas" },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  async function handleLogout() {
    await authApi.logout().catch(() => {});
    setToken(null);
    router.replace("/login");
  }

  return (
    <aside className="w-64 border-r bg-muted/30 p-4 flex flex-col gap-2">
      <Link href="/dashboard" className="text-lg font-bold mb-4">
        Multifolio
      </Link>
      <nav className="flex flex-col gap-1 flex-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`px-3 py-2 rounded-md text-sm transition-colors ${
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href))
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <button
        onClick={handleLogout}
        className="px-3 py-2 rounded-md text-sm text-left hover:bg-muted transition-colors text-muted-foreground"
      >
        Cerrar sesión
      </button>
    </aside>
  );
}
