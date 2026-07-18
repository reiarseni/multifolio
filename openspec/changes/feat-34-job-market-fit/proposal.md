## Why

Los usuarios de Multifolio necesitan saber qué tan competitivos son en el mercado laboral para un empleo específico. Actualmente no hay forma de comparar el perfil contra una oferta laboral real. Esto es una funcionalidad crítica para profesionales que buscan optimizar su perfil para oportunidades concretas.

## What Changes

- Se crea modelo `FacetAnalysis` para almacenar scores de compatibilidad por dimensión
- Se crea `job_fit_service.py` con análisis vía LLM: extracción de entidades del job posting, comparación semántica con la faceta, generación de scores y gaps
- Se crean schemas Pydantic para request/response del análisis
- Se crean prompts para el LLM (extracción, comparación, reordenamiento)
- Se agregan endpoints REST: POST para analizar, GET para historial, DELETE para eliminar
- Se crea página frontend con formulario para pegar job posting, dashboard con gráfico radar, lista de gaps y sugerencias
- El análisis es completamente privado (no se almacena el job posting)

## Capabilities

### New Capabilities
- `job-market-fit`: Análisis de compatibilidad laboral vía LLM, incluyendo score por dimensión (habilidades, experiencia, stack, tono), detección de gaps con sugerencias, y reordenamiento propuesto de skills/experiencias

### Modified Capabilities
- `facet-analytics`: Se extiende para incluir scores de compatibilidad en el modelo FacetAnalysis

## Impact

- **Modelo**: Nueva tabla `facet_analyses` con FK a facets
- **Dependencia**: `openai>=1.0.0` en pyproject.toml
- **Config**: 2 variables de entorno nuevas (`OPENAI_API_KEY`, `OPENAI_MODEL`)
- **API**: 3 endpoints nuevos (POST /api/facets/{id}/job-fit, GET /api/facets/{id}/job-fit/history, DELETE /api/job-fit/{analysis_id})
- **Frontend**: Nueva página en dashboard/facets/[id]/job-fit, nuevos componentes JobFitDashboard, ScoreRadar, GapList
