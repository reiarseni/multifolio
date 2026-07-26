"use client";

import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from "recharts";

interface ScoreRadarProps {
  skills: number;
  experience: number;
  stack: number;
  tone: number;
}

export function ScoreRadar({ skills, experience, stack, tone }: ScoreRadarProps) {
  const data = [
    { dimension: "Skills", score: skills },
    { dimension: "Experiencia", score: experience },
    { dimension: "Stack", score: stack },
    { dimension: "Tono", score: tone },
  ];

  return (
    <div className="border rounded-lg p-4">
      <p className="text-sm font-medium mb-4">Score por dimensión</p>
      <ResponsiveContainer width="100%" height={280}>
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid />
          <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12 }} />
          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} />
          <Tooltip />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#2563eb"
            fill="#2563eb"
            fillOpacity={0.2}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
