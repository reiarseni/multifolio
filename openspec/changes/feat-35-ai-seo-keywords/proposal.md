## Why

Los usuarios actualmente escriben meta título y descripción manualmente sin saber qué keywords son relevantes para reclutadores. Esto perjudica el posicionamiento en Google de sus perfiles.

## What Changes

- Se crea `seo_service.py` con análisis vía LLM: extracción de keywords del contenido de la faceta, generación de 3 variaciones de meta título y descripción
- Se crean schemas Pydantic para request/response SEO
- Se crean prompts para el LLM (extracción de keywords, generación de meta tags)
- Se agregan endpoints REST: POST para sugerir, PATCH para guardar, GET para consultar
- Se crea página frontend con panel de sugerencias, preview de Google y campos editables

## Capabilities

### New Capabilities
- `seo-suggestions`: Generación automática de meta título y descripción optimizados para SEO usando IA, con 3 variantes sugeridas

### Modified Capabilities
- `facet-editor`: Se agrega pestaña/página de configuración SEO con sugerencias IA
