"use client";

import { useEffect, useState } from "react";
import { notificationsApi, type NotificationOut } from "@/lib/api/notifications";

function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diff = now - then;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "ahora";
  if (mins < 60) return `hace ${mins} min`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `hace ${hrs} h`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `hace ${days} d`;
  return new Date(dateStr).toLocaleDateString("es-ES", { day: "numeric", month: "short" });
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationOut[]>([]);
  const [total, setTotal] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  async function fetchNotifications() {
    try {
      const data = await notificationsApi.list({ limit: 50 });
      setNotifications(data.items);
      setTotal(data.total);
      setUnreadCount(data.unread_count);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchNotifications();
  }, []);

  async function handleMarkRead(id: string) {
    try {
      await notificationsApi.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch {
      // ignore
    }
  }

  async function handleMarkAllRead() {
    try {
      const res = await notificationsApi.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch {
      // ignore
    }
  }

  if (loading) {
    return <div className="text-muted-foreground">Cargando...</div>;
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Notificaciones</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {unreadCount > 0
              ? `Tienes ${unreadCount} notificaciones sin leer`
              : "No hay notificaciones nuevas"}
          </p>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllRead}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm"
          >
            Marcar todas leídas
          </button>
        )}
      </div>

      {notifications.length === 0 && (
        <p className="text-sm text-muted-foreground py-8 text-center">
          No hay notificaciones.
        </p>
      )}

      <div className="space-y-2">
        {notifications.map((n) => (
          <button
            key={n.id}
            onClick={() => !n.is_read && handleMarkRead(n.id)}
            className={`w-full text-left p-4 rounded-lg border transition-colors ${
              n.is_read
                ? "bg-card border-border"
                : "bg-primary/5 border-primary/20 hover:bg-primary/10 cursor-pointer"
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <p
                  className={`text-sm truncate ${
                    n.is_read ? "text-foreground" : "text-foreground font-semibold"
                  }`}
                >
                  {n.title}
                </p>
                <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                  {n.message}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                  {timeAgo(n.created_at)}
                </span>
                {!n.is_read && (
                  <span className="w-2 h-2 rounded-full bg-primary shrink-0" />
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
