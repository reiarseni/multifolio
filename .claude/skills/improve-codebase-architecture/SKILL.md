---
name: improve-codebase-architecture
description: Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable.
---

# Improve Codebase Architecture

## Overview

This skill surfaces architectural friction by identifying shallow modules and proposing refactors that increase depth—moving toward interfaces with significant leverage and concentrated locality.

## Core Terminology

Consistent vocabulary from LANGUAGE.md:

- **Module** — any unit with interface and implementation (function, class, package)
- **Interface** — everything callers must know: types, invariants, error handling
- **Depth** — behavior concentrated behind a simple interface; high leverage
- **Seam** — where an interface lives; a substitution point
- **Adapter** — concrete implementation satisfying an interface at a seam
- **Locality** — knowledge and change concentrated in one place

Key test: the "deletion test"—if removing a module spreads its complexity across many callers, it earns its place.

## Three-Phase Approach

**1. Explore** — Read CONTEXT.md and relevant ADRs, then walk the codebase organically noting friction points:
   - Understanding requires bouncing between many modules?
   - Shallow interfaces that mirror their implementations?
   - Extracted functions that hide bugs in calling patterns?
   - Coupling leaking across seams?
   - Untestable or hard-to-test interfaces?

**2. Present candidates** — Numbered list with Files, Problem, Solution (plain English), Benefits (in terms of locality and testing).

**3. Grilling loop** — Collaborate on design:
   - Add new domain terms to CONTEXT.md as they emerge
   - Offer ADRs for rejected candidates if reasoning warrants future reference
   - Explore alternative interface shapes via INTERFACE-DESIGN.md if needed
