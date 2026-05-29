---
name: web-design-guidelines
description: Apply Vercel-style web design principles when building frontend interfaces — typography, spacing, color, motion, and component patterns. Use when designing or reviewing UI components, landing pages, or application interfaces.
license: MIT
compatibility: Claude Code
argument-hint: "[component or page to design]"
metadata:
  author: Inspired by Vercel Design System and Next.js ecosystem conventions
  source: https://vercel.com/design
---

Apply these web design principles when building or reviewing frontend interfaces. Inspired by Vercel's design system and modern Next.js ecosystem conventions.

---

## Typography

- **Scale**: use a modular scale (1.25×) — 12, 14, 16, 20, 24, 32, 40, 48px
- **Line height**: 1.5 for body, 1.2 for headings, 1.0 for UI labels
- **Font stack**: `Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Mono stack**: `'Geist Mono', 'JetBrains Mono', 'Fira Code', monospace`
- **Weight**: 400 for body, 500 for emphasis, 600 for headings, 700 for display
- **Never use more than 2 font families in a single interface**

## Spacing System

Use a base-8 spacing scale: `4, 8, 12, 16, 24, 32, 48, 64, 96px`

```css
/* Tailwind equivalents */
p-1 = 4px  | p-2 = 8px  | p-3 = 12px | p-4 = 16px
p-6 = 24px | p-8 = 32px | p-12 = 48px | p-16 = 64px
```

- **Component padding**: 12–16px for compact, 20–24px for comfortable
- **Section spacing**: 48–96px between major page sections
- **Avoid arbitrary values**: stick to the scale

## Color

### Light mode palette
```css
--background: #ffffff
--surface: #fafafa
--border: #eaeaea
--border-hover: #999999
--text-primary: #000000
--text-secondary: #666666
--text-disabled: #999999
--accent: #0070f3      /* Vercel blue */
--success: #0070f3
--warning: #f5a623
--error: #ee0000
```

### Dark mode palette
```css
--background: #000000
--surface: #111111
--border: #222222
--border-hover: #444444
--text-primary: #ffffff
--text-secondary: #888888
--text-disabled: #555555
```

- Always support both light and dark mode
- Use `oklch()` for new projects — better perceptual uniformity
- Contrast ratio: ≥4.5:1 for body text, ≥3:1 for large text (WCAG AA)

## Layout

- **Max content width**: 1200px for full layouts, 680px for prose/docs
- **Grid**: 12-column, 24px gutter, 24px margin
- **Cards**: `border-radius: 8px`, 1px border, subtle shadow
- **Sidebar**: 240px fixed, collapsible at <768px breakpoint

```css
/* Container pattern */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}
```

## Responsive Breakpoints

```css
sm:  640px   /* Mobile landscape */
md:  768px   /* Tablet */
lg:  1024px  /* Desktop */
xl:  1280px  /* Wide desktop */
2xl: 1536px  /* Ultra-wide */
```

- Mobile-first: design for 375px, then scale up
- Critical interactions must work at 320px minimum

## Motion & Transitions

```css
/* Standard transitions */
--transition-fast:   150ms ease;
--transition-base:   200ms ease;
--transition-slow:   300ms ease-in-out;

/* Use for: hover, focus, active states */
transition: background-color var(--transition-fast),
            border-color var(--transition-fast),
            box-shadow var(--transition-fast);
```

- Never animate layout properties (width, height) — use transform/opacity
- Respect `prefers-reduced-motion`: wrap non-essential animations in `@media`
- Loading skeletons: use `animation: shimmer 1.5s infinite`

## Component Patterns

### Buttons
```tsx
/* Primary */
className="px-4 py-2 bg-black text-white rounded-md text-sm font-medium
           hover:bg-neutral-800 transition-colors focus-visible:ring-2"

/* Secondary */
className="px-4 py-2 bg-white text-black border border-gray-200 rounded-md
           text-sm font-medium hover:bg-gray-50 transition-colors"

/* Ghost */
className="px-4 py-2 text-gray-600 rounded-md text-sm font-medium
           hover:bg-gray-100 transition-colors"
```

### Inputs
```tsx
className="w-full px-3 py-2 text-sm border border-gray-200 rounded-md
           bg-white placeholder:text-gray-400
           focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent
           disabled:opacity-50 disabled:cursor-not-allowed"
```

### Cards
```tsx
className="p-6 bg-white border border-gray-100 rounded-lg shadow-sm
           hover:shadow-md hover:border-gray-200 transition-all"
```

## Accessibility (non-negotiable)

- All interactive elements have `:focus-visible` styles (never remove `outline` without replacing it)
- Images have `alt` text; decorative images use `alt=""`
- Form inputs have associated `<label>` elements
- Color is never the only way to convey information
- ARIA roles/labels on custom interactive components
- Keyboard navigation works for all interactive elements

## Code Quality Checks

Before finalizing any UI component:

- [ ] Works in light AND dark mode
- [ ] Responsive down to 375px
- [ ] No hardcoded colors (use CSS variables or Tailwind tokens)
- [ ] All interactive states: hover, focus-visible, active, disabled
- [ ] No layout shift on load (skeleton or fixed dimensions)
- [ ] `prefers-reduced-motion` respected for animations
- [ ] Keyboard navigable
- [ ] Contrast ratio passes WCAG AA
