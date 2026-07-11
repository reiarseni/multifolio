"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { TrendPoint } from "@/lib/api/analytics";

interface TrendChartProps {
  data: TrendPoint[];
  title: string;
}

export function TrendChart({ data, title }: TrendChartProps) {
  if (data.length === 0) {
    return (
      <div className="border rounded-lg p-4">
        <p className="text-sm font-medium mb-4">{title}</p>
        <p className="text-sm text-muted-foreground text-center py-8">Sin datos disponibles</p>
      </div>
    );
  }

  return (
    <div className="border rounded-lg p-4">
      <p className="text-sm font-medium mb-4">{title}</p>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
