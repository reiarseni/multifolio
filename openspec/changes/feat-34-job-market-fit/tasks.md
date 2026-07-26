# Tasks for feat-34-job-market-fit

## Task 1: Add openai dependency
- [x] Add `openai>=1.0.0` to `backend/pyproject.toml` dependencies
- [x] Run `cd backend && uv sync` to install

## Task 2: Add OpenAI config to Settings
- [x] Add `openai_api_key: str = ""` to `backend/src/app/core/config.py`
- [x] Add `openai_model: str = "gpt-4"` with env override

## Task 3: Update .env.example
- [x] Add `OPENAI_API_KEY` and `OPENAI_MODEL` to `.env.example`

## Task 4: Create FacetAnalysis model
- [x] Create `backend/src/app/models/facet_analysis.py` with FacetAnalysis model
- [x] Model fields: id (UUID PK), facet_id (FK), job_title, job_company, overall_score, skills_score, experience_score, stack_score, tone_score, gaps (JSONB), suggestions (JSONB), created_at
- [x] Register in `backend/src/app/models/__init__.py`
- [x] Add relationship to Facet model

## Task 5: Create Alembic migration
- [x] Generate migration for `facet_analyses` table
- [x] Verify columns match the model

## Task 6: Create job fit schemas
- [x] Create `backend/src/app/schemas/job_fit.py`
- [x] Schemas: JobFitRequest, JobFitResponse, JobFitHistoryItem, JobFitHistoryResponse, JobFitDeleteResponse, GapItem, ReorderSuggestion
- [x] Register in `backend/src/app/schemas/__init__.py`

## Task 7: Create LLM prompts
- [x] Create `backend/src/app/prompts/job_fit.py`
- [x] Prompts: EXTRACT_ENTITIES_PROMPT, COMPARE_WITH_FACET_PROMPT, SUGGEST_REORDER_PROMPT
- [x] Each prompt includes format instructions for structured output

## Task 8: Create job fit service
- [x] Create `backend/src/app/services/job_fit_service.py`
- [x] Functions: analyze_facet_fit, _extract_entities, _compare_with_facet, _suggest_reorder
- [x] Use OpenAI async client for LLM calls
- [x] Parse structured JSON responses from LLM
- [x] Save FacetAnalysis to database

## Task 9: Create job fit router
- [x] Create `backend/src/app/routers/job_fit.py`
- [x] Endpoints: POST /api/facets/{facet_id}/job-fit, GET /api/facets/{facet_id}/job-fit/history, DELETE /api/job-fit/{analysis_id}
- [x] Register router in `backend/src/app/main.py`

## Task 10: Create frontend API client
- [x] Create `frontend/src/lib/api/job-fit.ts`
- [x] Functions: analyzeJobFit, getJobFitHistory, deleteJobFitAnalysis
- [x] Follow existing API patterns (apiClient, withAuth)

## Task 11: Create ScoreRadar component
- [x] Create `frontend/src/components/job-fit/ScoreRadar.tsx`
- [x] Use Recharts RadarChart
- [x] Show 4 dimensions: skills, experience, stack, tone

## Task 12: Create GapList component
- [x] Create `frontend/src/components/job-fit/GapList.tsx`
- [x] Show gaps with severity indicators
- [x] Show suggestions for each gap
- [x] Show reorder suggestion with "Apply" button

## Task 13: Create JobFitDashboard component
- [x] Create `frontend/src/components/job-fit/JobFitDashboard.tsx`
- [x] Form textarea for job posting
- [x] "Analizar" submit button with loading state
- [x] Orchestrates ScoreRadar and GapList

## Task 14: Create job-fit page
- [x] Create `frontend/src/app/dashboard/facets/[id]/job-fit.tsx`
- [x] Load facet info
- [x] Render JobFitDashboard
- [x] Add link from facet detail page

## Task 15: Verify end-to-end
- [x] Run backend tests: `cd backend && uv run pytest`
- [x] Run frontend build: `cd frontend && npm run build`
