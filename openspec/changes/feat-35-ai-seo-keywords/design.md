## Overview

Add AI-powered SEO keyword suggestions for facets. The system analyzes facet content using OpenAI, extracts relevant keywords, and generates 3 optimized variants of meta title and description. Users can preview, edit, and apply suggestions.

## Architecture Decisions

### Decision: Reuse OpenAI infrastructure from feat-34
- **Choice**: Use same `AsyncOpenAI` client pattern as `job_fit_service.py`
- **Why**: Already configured, no new dependencies needed
- **Tradeoff**: None — shares the same settings and client setup

### Decision: No new model or migration
- **Choice**: Use existing `Facet.meta_title` and `Facet.meta_description` fields
- **Why**: These fields already exist on the Facet model, no schema changes needed
- **Tradeoff**: Cannot store suggestion history (out of scope per plan)

### Decision: 3 variants suggested
- **Choice**: LLM generates exactly 3 variants of (title, description) pairs
- **Why**: Gives user choice without overwhelming. Plan specifies 3

### Decision: Facet update reuses existing pattern
- **Choice**: PATCH endpoint updates `meta_title` and `meta_description` via existing facet update service
- **Why**: Avoid duplicating update logic. The existing PUT/PATCH already handles these fields

## Components

### Backend Changes

**New file: `backend/src/app/schemas/seo.py`**
- `SEOSuggestRequest`: Empty body (or facet_id in path)
- `SEOVariant`: title, description, rationale
- `SEOSuggestResponse`: list of 3 variants
- `SEOUpdateRequest`: meta_title, meta_description
- `SEOUpdateResponse`: success message

**New file: `backend/src/app/prompts/seo.py`**
- `EXTRACT_KEYWORDS_PROMPT`: Extract relevant SEO keywords from facet content
- `GENERATE_META_PROMPT`: Generate 3 variants of title+description from keywords

**New file: `backend/src/app/services/seo_service.py`**
- `suggest_seo(db, facet_id, user_id)`: Main orchestrator
  - Load facet with skills, experiences, projects
  - Call LLM to extract keywords
  - Call LLM to generate 3 meta variants
  - Return variants

**New file: `backend/src/app/routers/seo.py`**
- `POST /api/facets/{facet_id}/seo/suggest`: Get SEO suggestions
- `PATCH /api/facets/{facet_id}/seo`: Save meta_title/meta_description
- `GET /api/facets/{facet_id}/seo`: Get current SEO config

### Frontend Changes

**New file: `frontend/src/lib/api/seo.ts`**
- `getSEO(facetId)`, `suggestSEO(facetId)`, `updateSEO(facetId, data)`

**New file: `frontend/src/components/seo/MetaPreview.tsx`**
- Google search result preview card
- Shows title, URL, description exactly as Google renders them

**New file: `frontend/src/components/seo/SEOSuggestions.tsx`**
- Shows 3 variant cards to choose from
- Each card: title, description, rationale
- Click to select and populate the form

**New file: `frontend/src/app/dashboard/facets/[slug]/seo/page.tsx`**
- Page that loads facet info and renders SEO configuration
- Form with meta_title, meta_description fields
- Button to get suggestions
- Preview panel

## Data Flow

```
User                    Frontend                    Backend                     OpenAI
  │                         │                          │                         │
  │  Click "Sugerencias"   │                          │                         │
  │ ─────────────────────► │                          │                         │
  │                         ├── POST /seo/suggest ───► │                         │
  │                         │                          ├── Load facet (DB)        │
  │                         │                          ├── Extract keywords ────► │
  │                         │                          │  ◄── keywords ────────── │
  │                         │                          ├── Generate variants ───► │
  │                         │                          │  ◄── 3 variants ──────── │
  │                         │  ◄── variants ────────── │                          │
  │                         ├── Show 3 variant cards  │                          │
  │  ◄── elige variante ────┤                          │                          │
  │                         ├── PATCH /seo ──────────► │                          │
  │                         │                          ├── Update facet           │
  │                         │  ◄── success ─────────── │                          │
  │  ◄── preview actualizado┤                          │                          │
```
