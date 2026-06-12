"use client";

import type { ReactNode } from "react";

type Tokens = Record<string, unknown>;

function flattenTokens(tokens: Tokens): Record<string, string> {
  const vars: Record<string, string> = {};
  const color = (tokens.color as Record<string, string>) ?? {};
  const typography = (tokens.typography as Record<string, string>) ?? {};
  const spacing = (tokens.spacing as Record<string, string>) ?? {};
  const shape = (tokens.shape as Record<string, string>) ?? {};

  const map: [Record<string, string>, string][] = [
    [color, "--color-"],
    [typography, "--"],
    [spacing, "--spacing-"],
    [shape, "--"],
  ];

  for (const [group, prefix] of map) {
    for (const [key, value] of Object.entries(group)) {
      if (value) {
        const cssKey = `${prefix}${key.replace(/_/g, "-")}`;
        vars[cssKey] = value;
      }
    }
  }

  return vars;
}

interface Props {
  tokens: Tokens;
  children: ReactNode;
}

export function ThemeProvider({ tokens, children }: Props) {
  const cssVars = flattenTokens(tokens);

  return (
    <div style={cssVars as React.CSSProperties}>
      {children}
    </div>
  );
}
