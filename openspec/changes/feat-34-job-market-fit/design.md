## Overview

Add Job Market Fit analysis feature that allows users to paste a job posting and get a compatibility score against their facet profile. The analysis uses OpenAI GPT-4 for semantic comparison across four dimensions: skills, experience, tech stack, and headline tone. Results include dimension scores, detected gaps with concrete suggestions, and a proposed reordering of skills/experiences. The job posting text is never stored.

## Architecture Decisions

### Decision: OpenAI direct API over LiteLLM / LangChain
- **Choice**: `openai>=1.0.0` direct SDK
- **Why**: Simplest dependency, direct async support, no extra abstraction layer needed for a single provider
- **Tradeoff**: Provider lock-in, but easy to swap later via the prompt abstraction layer

### Decision: Sync analysis endpoint (POST, blocking)
- **Choice**: POST endpoint that blocks on LLM completion (typical 3-8s)
- **Why**: Simplest UX for MVP, avoids WebSocket/Celery overhead. Frontend shows loading state
- **Tradeoff**: Request timeout risk for large postings (mitigated by 10K char limit)

### Decision: Scores stored in DB, job posting discarded
- **Choice**: Store `FacetAnalysis` row with scores, gaps JSON, suggestions JSON. Job posting text NOT stored
- **Why**: Enables history tracking without storing sensitive job posting data
- **Tradeoff**: Cannot re-analyze with different parameters without re-pasting

### Decision: JSON fields for gaps and suggestions
- **Choice**: `gaps: Mapped[dict] = mapped_column(JSONB)` and `suggestions: Mapped[dict] = mapped_column(JSONB)`
- **Why**: Flexible schema, no extra tables, easy to evolve prompt output format
- **Tradeoff**: No referential integrity, but gaps/suggestions are ephemeral analysis artifacts

### Decision: Recharts RadarChart for score visualization
- **Choice**: Recharts `RadarChart` component (already in project)
- **Why**: Zero new dependencies, already used for TrendChart in analytics
- **Tradeoff**: Less customizable than D3, but sufficient for a 4-dimension radar

## Components

### Backend Changes

**New file: `backend/src/app/models/facet_analysis.py`**
- `FacetAnalysis` model: id (UUID PK), facet_id (FK), job_title, job_company, overall_score, skills_score, experience_score, stack_score, tone_score, gaps (JSONB), suggestions (JSONB), created_at
- Relationship to Facet

**New file: `backend/src/app/schemas/job_fit.py`**
- `JobFitRequest`: job_posting (str, max 10000 chars)
- `JobFitResponse`: overall_score, dimension_scores, gaps, suggestions, reorder_suggestion, created_at
- `JobFitHistoryResponse`: list of past analyses
- `JobFitDeleteResponse`: success message

**New file: `backend/src/app/prompts/job_fit.py`**
- `EXTRACT_ENTITIES_PROMPT`: Extract skills, experience, stack from job posting
- `COMPARE_WITH_FACET_PROMPT`: Compare facet content against extracted entities, produce scores and gaps
- `SUGGEST_REORDER_PROMPT`: Propose optimal ordering of skills/experiences based on job match

**New file: `backend/src/app/services/job_fit_service.py`**
- `analyze_facet_fit(db, facet_id, job_posting)`: Main orchestrator
  - Load facet with all relations
  - Call LLM to extract entities from job posting
  - Call LLM to compare facet vs entities → scores + gaps
  - Call LLM to suggest reordering
  - Save FacetAnalysis to DB
  - Return results
- `_extract_entities(job_posting)`: Parse job posting via LLM
- `_compare_with_facet(facet_dict, entities)`: Score each dimension
- `_suggest_reorder(facet_dict, gaps)`: Optimal ordering

**New file: `backend/src/app/routers/job_fit.py`**
- `POST /api/facets/{facet_id}/job-fit`: Analyze job posting
- `GET /api/facets/{facet_id}/job-fit/history`: List past analyses
- `DELETE /api/job-fit/{analysis_id}`: Delete an analysis

**Modified: `backend/src/app/core/config.py`**
- Add `openai_api_key`, `openai_model` (default "gpt-4")

**Modified: `backend/pyproject.toml`**
- Add `openai>=1.0.0`

**New migration: `backend/alembic/versions/xxx_add_facet_analysis.py`**
- Create `facet_analyses` table

**Modified: `backend/src/app/main.py`**
- Register job_fit router

### Frontend Changes

**New file: `frontend/src/lib/api/job-fit.ts`**
- `analyzeJobFit(facetId, jobPosting)`: POST request
- `getJobFitHistory(facetId)`: GET request
- `deleteJobFitAnalysis(analysisId)`: DELETE request

**New file: `frontend/src/components/job-fit/JobFitDashboard.tsx`**
- Main container: form input for job posting, loading state, result display
- Orchestrates ScoreRadar and GapList

**New file: `frontend/src/components/job-fit/ScoreRadar.tsx`**
- Recharts RadarChart showing 4 dimensions (skills, experience, stack, tone)

**New file: `frontend/src/components/job-fit/GapList.tsx`**
- List of gaps with suggestions
- Reorder suggestion display with "Apply" button

**New file: `frontend/src/app/dashboard/facets/[id]/job-fit.tsx`**
- Page that loads facet info and renders JobFitDashboard

## Data Model

```
FacetAnalysis
├── id: UUID (PK)
├── facet_id: UUID (FK → facets.id, CASCADE)
├── job_title: String(255) NULL
├── job_company: String(255) NULL
├── overall_score: Float NOT NULL
├── skills_score: Float NOT NULL
├── experience_score: Float NOT NULL
├── stack_score: Float NOT NULL
├── tone_score: Float NOT NULL
├── gaps: JSONB NOT NULL DEFAULT '[]'
├── suggestions: JSONB NOT NULL DEFAULT '[]'
├── created_at: DateTime(timezone=True)
```

## Analysis Flow

```
User                    Frontend                    Backend                     OpenAI
  │                         │                          │                         │
  │  Paste job posting      │                          │                         │
  │  Click "Analizar"       │                          │                         │
  │ ─────────────────────► │                          │                         │
  │                         ├── POST /job-fit ───────► │                         │
  │                         │                          ├── Load facet (DB)        │
  │                         │                          ├── Extract entities ────► │
  │                         │                          │  ◄── entities ─────────── │
  │                         │                          ├── Compare facet ───────► │
  │                         │                          │  ◄── scores + gaps ───── │
  │                         │                          ├── Suggest reorder ─────► │
  │                         │                          │  ◄── reorder ──────────── │
  │                         │                          ├── Save FacetAnalysis     │
  │                         │  ◄── results ─────────── │                          │
  │                         ├── Render ScoreRadar     │                          │
  │                         ├── Render GapList        │                          │
  │  ◄── see results ──────┤                          │                          │
```

## Privacy Considerations

- Job posting text is sent to OpenAI for analysis but NEVER stored in our database
- Only the analysis results (scores, gaps, suggestions) are persisted
- User can delete any analysis record via DELETE endpoint
- No PII from the job posting is retained server-side
