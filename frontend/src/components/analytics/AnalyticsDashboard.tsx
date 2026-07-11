"use client";

import { useEffect, useState } from "react";
import { analyticsApi, type AnalyticsMetrics, type TrendResponse } from "@/lib/api/analytics";
import { MetricCard } from "./MetricCard";
import { TrendChart } from "./TrendChart";

interface AnalyticsDashboardProps {
  facetId: string;
}

export function AnalyticsDashboard({ facetId }: AnalyticsDashboardProps) {
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null);
  const [trends, setTrends] = useState<TrendResponse | null>(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      analyticsApi.getMetrics(facetId, days).catch(() => null),
      analyticsApi.getTrends(facetId, days).catch(() => null),
    ]).then(([m, t]) => {
      setMetrics(m);
      setTrends(t);
      setLoading(false);
    });
  }, [facetId, days]);

  const handleExport = async () => {
    const res = await analyticsApi.exportCsv(facetId, days);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analytics_${facetId}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <div className="text-muted-foreground">Cargando analytics...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Analytics</h2>
        <div className="flex gap-2">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="border rounded-md px-2 py-1 text-sm"
          >
            <option value={7}>Últimos 7 días</option>
            <option value={30}>Últimos 30 días</option>
            <option value={90}>Últimos 90 días</option>
          </select>
          <button
            onClick={handleExport}
            className="border rounded-md px-3 py-1 text-sm hover:bg-muted"
          >
            Exportar CSV
          </button>
        </div>
      </div>

      {metrics && (
        <div className="grid grid-cols-3 gap-4">
          <MetricCard title="Vistas totales" value={metrics.total_views} />
          <MetricCard title="Vistas únicas" value={metrics.unique_views} />
          <MetricCard
            title="Tiempo promedio"
            value={metrics.avg_time_on_page ? `${Math.round(metrics.avg_time_on_page)}s` : "N/A"}
          />
        </div>
      )}

      {metrics && metrics.top_referrers.length > 0 && (
        <div className="border rounded-lg p-4">
          <p className="text-sm font-medium mb-3">Top Referrers</p>
          <div className="space-y-2">
            {metrics.top_referrers.map((r) => (
              <div key={r.referrer} className="flex justify-between text-sm">
                <span className="truncate">{r.referrer}</span>
                <span className="font-mono">{r.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {trends && <TrendChart data={trends.data} title="Vistas en el tiempo" />}
    </div>
  );
}
