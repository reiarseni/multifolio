# Tasks for feat-35-ai-seo-keywords

## Task 1: Create SEO schemas
- [ ] Create `backend/src/app/schemas/seo.py`
- [ ] Schemas: SEOVariant, SEOSuggestResponse, SEOUpdateRequest, SEOUpdateResponse, SEOConfigResponse
- [ ] Register in `backend/src/app/schemas/__init__.py`

## Task 2: Create LLM prompts
- [ ] Create `backend/src/app/prompts/seo.py`
- [ ] Prompts: EXTRACT_KEYWORDS_PROMPT, GENERATE_META_PROMPT
- [ ] Each prompt includes format instructions for structured output

## Task 3: Create SEO service
- [ ] Create `backend/src/app/services/seo_service.py`
- [ ] Functions: suggest_seo
- [ ] Load facet with relations, extract keywords via LLM, generate 3 variants
- [ ] Use OpenAI async client

## Task 4: Create SEO router
- [ ] Create `backend/src/app/routers/seo.py`
- [ ] Endpoints: POST /api/facets/{facet_id}/seo/suggest, PATCH /api/facets/{facet_id}/seo, GET /api/facets/{facet_id}/seo
- [ ] Register router in `backend/src/app/main.py`

## Task 5: Create frontend API client
- [ ] Create `frontend/src/lib/api/seo.ts`
- [ ] Functions: getSEO, suggestSEO, updateSEO

## Task 6: Create MetaPreview component
- [ ] Create `frontend/src/components/seo/MetaPreview.tsx`
- [ ] Google search result preview card

## Task 7: Create SEOSuggestions component
- [ ] Create `frontend/src/components/seo/SEOSuggestions.tsx`
- [ ] Show 3 variant cards with title, description, rationale
- [ ] Click to select variant

## Task 8: Create SEO page
- [ ] Create `frontend/src/app/(dashboard)/facets/[slug]/seo/page.tsx`
- [ ] Form with meta_title, meta_description fields
- [ ] Button to get suggestions
- [ ] MetaPreview and SEOSuggestions panels
- [ ] Add link from facet detail page

## Task 9: Verify end-to-end
- [ ] Run backend tests: `cd backend && .venv/bin/pytest`
- [ ] Run ruff check + format
- [ ] Run frontend build
