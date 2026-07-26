"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Moon, Sun } from "lucide-react";
import { authApi } from "@/lib/api/auth";
import { setToken } from "@/lib/auth/token";
import { useTheme } from "@/components/ui/ThemeProvider";

const navItems = [
  { href: "/dashboard", label: "Inicio" },
  { href: "/profile", label: "Perfil" },
  { href: "/projects", label: "Proyectos" },
  { href: "/facets", label: "Facetas" },
  { href: "/notifications", label: "Notificaciones" },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, toggle } = useTheme();

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
              (item.href !== "/dashboard" && pathname.startsWith(item.href + "/"))
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      <button
        onClick={toggle}
        className="flex items-center gap-2 px-3 py-2 rounded-md text-sm hover:bg-muted transition-colors text-muted-foreground"
        aria-label="Cambiar tema"
      >
        {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        {theme === "dark" ? "Modo claro" : "Modo oscuro"}
      </button>

      <button
        onClick={handleLogout}
        className="px-3 py-2 rounded-md text-sm text-left hover:bg-muted transition-colors text-muted-foreground"
      >
        Cerrar sesión
      </button>
    </aside>
  );
}
