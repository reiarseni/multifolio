---
name: openspec-tdd
description: End-to-end OpenSpec workflow with TDD integration — propose with testability validation, apply with red→green→refactor cycles, review with scenario coverage (Lens F). Use instead of combining openspec-propose-deep + tdd manually.
license: MIT
compatibility: Requires openspec CLI.
argument-hint: "<change-name>"
---

Orquesta el workflow completo de OpenSpec con TDD integrado: propose (validación de testabilidad en specs), apply (ciclos red→green→refactor selectivos via etiqueta `[tdd]`) y review (lenses heredados + Lens F de cobertura de escenarios).

**Input**: Opcionalmente especifica un nombre de cambio. Si se omite, se autodetecta desde el contexto o se pregunta al usuario.

---

## Fase 0 — Selección y detección de fase activa

Si se proporcionó un nombre de cambio, usarlo. Si no:
- Inferir desde el contexto de conversación si el usuario mencionó un cambio
- Si hay exactamente un cambio activo, seleccionarlo automáticamente
- Si hay ambigüedad, ejecutar `openspec list --json` y usar **AskUserQuestion** para que el usuario seleccione

Una vez seleccionado el nombre, ejecutar:

```bash
openspec status --change "<name>" --json
```

**Detectar la fase activa según el estado:**

- Si algún artefacto en `applyRequires` no está `done` → **fase propose**
- Si todos los `applyRequires` están `done` pero hay tasks `- [ ]` en `tasks.md` → **fase apply**
- Si todas las tasks en `tasks.md` están `- [x]` → **fase review**

**Si el cambio no existe:**
- Ejecutar `openspec list --json`
- Usar **AskUserQuestion** para preguntar si quiere crear un cambio nuevo o seleccionar uno existente
- Si crea uno nuevo: ir a fase propose con el nombre indicado

Anunciar la fase detectada antes de continuar:
```
openspec-tdd: <change-name>
Fase detectada: [propose | apply | review]
```

---

## Fase 1 — PROPOSE: entrevista y artefactos con validación TDD

### Paso 1.0 — Captura inicial

**Si no se proporcionó descripción con la invocación**, preguntar usando **AskUserQuestion** (abierta, sin opciones preset):

> "¿Qué cambio querés trabajar? Describí qué querés construir o arreglar."

Mantener la pregunta mínima — solo lo suficiente para saber el tema. Derivar un nombre kebab-case del cambio (ej. "add offline export" → `add-offline-export`). Retener para el paso 1.4 — no crear el directorio aún.

### Paso 1.1 — Reconocimiento del codebase

Antes de hablar más con el usuario, ejecutar en paralelo:

```bash
openspec list --json
```

Leer los artefactos existentes relevantes al cambio propuesto. Escanear las partes del codebase que probablemente se tocarán (routers, models, workers, páginas frontend). Usar `grep` y `find` libremente.

Meta: construir un mapa mental de:
- Qué ya existe y se superpone con el request
- Patrones y convenciones en uso
- Puntos de integración que el usuario puede no conocer
- Cualquier cosa que el usuario dijo que contradice el codebase actual

No compartir hallazgos con el usuario aún. Acumularlos para informar la entrevista.

### Paso 1.2 — Investigación web

Buscar mejores prácticas de la industria, pitfalls comunes y enfoques recomendados para el tipo de feature descripto. Usar **WebSearch** y **WebFetch**.

Buenos ángulos de búsqueda:
- "{tipo de feature} best practices {año}"
- "{tecnología} {patrón} tradeoffs"
- "when NOT to use {enfoque}"
- Implicaciones de seguridad o compliance si son relevantes

**Sintetizar hallazgos en una base de conocimiento privada** (mantener en contexto, no escribir a un archivo). Usar para:
1. Hacer preguntas más inteligentes en la entrevista
2. Señalar opciones que el usuario podría no haber considerado
3. Sugerir alternativas

No compartir la investigación como un wall of text. Surfacearla selectivamente, embebida en preguntas.

### Paso 1.3 — Entrevista interactiva profunda

Estructurar la entrevista en **hasta 3 rondas** de llamadas **AskUserQuestion**. Cada ronda puede tener 1–4 preguntas. No preguntar todo a la vez.

**Ronda 1 — Alcance e intención**

Preguntas que clarifican QUÉ y POR QUÉ. Derivarlas de lo que dijo el usuario, lo que encontraste en el codebase, y lo que surgió en la investigación.

**Ronda 2 — Decisiones de diseño clave (user-driven)**

Basándose en las respuestas de la Ronda 1 y la investigación, surfacear las 2–4 decisiones de diseño más consecuentes. Para cada una, presentar:
- La decisión a tomar
- Las opciones realistas (2–3 máximo)
- El tradeoff en lenguaje llano
- La recomendación, si la evidencia favorece claramente una opción

**El usuario decide — no elegir por él** a menos que la opción sea completamente obvia e intrascendente.

**Ronda 3 — Edge cases y constraints (condicional)**

Solo ejecutar si las Rondas 1 o 2 revelaron preguntas genuinamente abiertas sobre:
- Estados de error
- Control de acceso
- Retención de datos, migración, o backward compatibility
- Interacción con features existentes que tocan los mismos datos

Omitir la Ronda 3 si nada crítico queda sin resolver.

### Paso 1.4 — Resumen pre-propuesta (obligatorio)

Antes de crear cualquier archivo, presentar al usuario un resumen compacto de lo que se va a construir:

```
## Lo que entendí

**Feature**: [una oración]
**Por qué**: [una oración]
**Alcance**: [qué está dentro, qué está explícitamente fuera]

## Decisiones capturadas

- [decisión 1]: [elección del usuario]
- [decisión 2]: [elección del usuario]

## Suposiciones que estoy haciendo (no confirmadas)

- [suposición] — avisame si está mal

## Lo que estoy señalando

- [preocupación o riesgo de la investigación o revisión del codebase]
```

Luego preguntar con **AskUserQuestion**:

> "¿Esto se ve bien antes de que escriba la propuesta? ¿O hay algo que cambiarías?"

Opciones: "Se ve bien, proceder" / "Necesito ajustar algo"

No proceder a la creación de artefactos hasta que el usuario confirme.

### Paso 1.5 — Crear el cambio y artefactos

Una vez confirmado:

1. **Crear el directorio del cambio**
   ```bash
   openspec new change "<name>"
   ```

2. **Obtener orden de construcción de artefactos**
   ```bash
   openspec status --change "<name>" --json
   ```

3. **Crear artefactos en orden de dependencia** hasta que todos los `applyRequires` estén `done`:
   - Obtener instrucciones: `openspec instructions <artifact-id> --change "<name>" --json`
   - Leer artefactos dependencia para contexto
   - Escribir el artefacto
   - Mostrar progreso breve: "Creado <artifact-id>"
   - Re-verificar status tras cada artefacto

   Todas las decisiones capturadas en la entrevista DEBEN reflejarse en los artefactos.

   **Al generar `tasks.md`**: añadir la etiqueta `[tdd]` a las tasks que implementen comportamiento de dominio observable (lógica de negocio, endpoints, handlers, lógica de validación). Las tasks de scaffolding (crear directorios, instalar dependencias, configurar variables de entorno, migraciones de datos) NO reciben la etiqueta.

   Ejemplo:
   - `- [ ] [tdd] Implementar handler de checkout` ← comportamiento de dominio
   - `- [ ] Crear directorio `src/handlers/`` ← scaffolding, sin etiqueta

4. **Mostrar status final**
   ```bash
   openspec status --change "<name>"
   ```

### Paso 1.6 — Validación TDD de specs (NUEVO)

Antes de mostrar el resumen final al usuario, revisar cada escenario en los specs creados contra los tres criterios de testabilidad:

1. **WHEN y THEN concretos**: el escenario tiene tanto `**WHEN**` como `**THEN**` con condiciones específicas (no vagas)
2. **Comportamiento observable**: el THEN describe algo verificable a través de la interfaz pública (respuesta HTTP, estado de BD, output visible) — no estado interno
3. **Sin dependencia de estado interno**: el THEN no menciona "la función X es llamada internamente", "el método Y recibe el parámetro Z", ni similares

Para cada escenario que no cumpla algún criterio, registrar:
- Nombre del escenario
- Criterio violado
- Issue específico (qué falta o qué es problemático)

**Si todos los escenarios pasan la validación:**
- Continuar directamente al resumen de confirmación

**Si hay escenarios no testeables:**
- Presentar la lista de issues al usuario:
  ```
  ## Validación TDD de specs

  Los siguientes escenarios no cumplen los criterios de testabilidad:

  ❌ **<nombre del escenario>**
     Issue: <descripción específica del problema>
     Criterio violado: <WHEN/THEN concretos | comportamiento observable | sin estado interno>

  ❌ **<nombre del escenario>**
     ...
  ```
- Pedir al usuario que corrija los specs antes de confirmar
- Cuando el usuario indique que editó los specs, re-ejecutar la validación
- Repetir el ciclo hasta que todos los escenarios pasen
- Una vez que todos pasan: "✓ Todos los escenarios son testeables. Continuando."

### Paso 1.7 — Output de propose

Tras la validación TDD exitosa, mostrar:
- Nombre y ubicación del cambio
- Lista breve de artefactos creados
- Una oración sobre algo notable de la investigación o entrevista que moldeó el diseño
- "¡Todos los artefactos creados! Listo para implementación."
- Prompt: "Invocá la skill nuevamente o ejecutá `/opsx:apply` para comenzar con las tasks."

---

## Fase 2 — APPLY: implementación con ciclos TDD selectivos

### Paso 2.1 — Obtener instrucciones y leer contexto

```bash
openspec instructions apply --change "<name>" --json
```

Esto retorna:
- `contextFiles`: artifact ID → array de rutas de archivo concretas
- Progreso (total, complete, remaining)
- Lista de tasks con estado
- Instrucción dinámica según el estado actual

**Manejar estados:**
- Si `state: "blocked"` (artefactos faltantes): mostrar mensaje y detener, sugerir fase propose
- Si `state: "all_done"`: saltar directamente a fase review
- De lo contrario: proceder a implementación

Leer CADA ruta de archivo listada bajo `contextFiles`.

### Paso 2.2 — Loop de implementación de tasks

Para cada task pendiente (`- [ ]`):

1. Mostrar: "Working on task N/M: <descripción>"
2. **Detectar si la task tiene etiqueta `[tdd]`** buscando el texto `[tdd]` en la descripción de la task

**Si la task NO tiene `[tdd]`** → implementación directa:
- Hacer los cambios de código necesarios
- Mantener cambios mínimos y enfocados
- Marcar la task como completada: `- [ ]` → `- [x]`
- Continuar a la siguiente task

**Si la task SÍ tiene `[tdd]`** → ciclo red→green→refactor:

**RED**:
- Identificar la interfaz pública que el escenario correspondiente en specs describe
- Si la interfaz no está clara: usar **AskUserQuestion** para pedir al usuario que clarifique la interfaz pública esperada antes de continuar
- Escribir un test que verifica el comportamiento descrito en el THEN del escenario correspondiente
- Ejecutar los tests y confirmar que el test nuevo FALLA (red confirmado)
- Si el test pasa sin implementación: notificar al usuario — puede ser un test mal escrito o comportamiento ya existente; pedir confirmación para continuar

**GREEN**:
- Escribir la implementación mínima para que el test pase
- Ejecutar los tests y verificar que el test pasa
- Si el test sigue fallando: reportar el output del test al usuario, NO marcar el checkbox, y pausar — no continuar a la siguiente task hasta resolver
- Si el test pasa: confirmar "✓ GREEN: test pasa"

**REFACTOR**:
- Evaluar oportunidades de mejora: extracción de duplicación, mejora de naming, simplificación de módulos
- Si hay oportunidades claras: aplicar refactors incrementales, ejecutar los tests tras cada paso
- Si los tests fallan después de un refactor: revertir ese paso específico
- Si no hay oportunidades claras: omitir este paso
- Confirmar: "✓ REFACTOR: completado" o "✓ REFACTOR: omitido (sin oportunidades)"

Marcar el checkbox: `- [ ]` → `- [x]` **solo después de GREEN confirmado**

**Pausar si:**
- Task es poco clara → usar **AskUserQuestion** para clarificar, luego continuar
- La implementación revela un problema de diseño → señalarlo, preguntar si actualizar artefactos o proceder
- Error o bloqueante encontrado → reportar y esperar orientación

Tras completar todas las tasks: "All tasks implemented. Moving to review."

---

## Fase 3 — REVIEW: lenses heredados + Lens F

### Paso 3.1 — Seleccionar cambio y validar

Anunciar: "Reviewing change: **<name>**"

Validar que el cambio existe y tiene al menos `proposal.md` done:

```bash
openspec status --change "<name>" --json
```

### Paso 3.2 — Detectar modo de review

Leer el archivo `tasks.md` del cambio:

```bash
pending=$(grep -c '^\- \[ \]' openspec/changes/<name>/tasks.md 2>/dev/null || echo 0)
complete=$(grep -c '^\- \[x\]' openspec/changes/<name>/tasks.md 2>/dev/null || echo 0)
```

Reglas:
- `tasks.md` no existe → **pre-apply**
- `complete == 0` → **pre-apply** (no se inició implementación)
- `complete > 0` → **pre-archive** (implementación en curso o completa)

Anunciar el modo detectado claramente.

### Paso 3.3 — Leer artefactos de contexto

Leer todos los archivos de artefactos que estén `done` según `openspec status --json`:
- `openspec/changes/<name>/proposal.md`
- `openspec/changes/<name>/design.md` (si done)
- Todos los archivos bajo `openspec/changes/<name>/specs/` (si done)
- `openspec/changes/<name>/tasks.md` (si done)

### Paso 3.4 — Lenses de review (acumular hallazgos, no reportar aún)

Para cada hallazgo, registrar:
- **Sev**: Bloqueante / Recomendado / Opcional
- **Lens**: qué artefacto
- **Quote**: fragmento literal del artefacto (obligatorio — sin cita = omitir el hallazgo)
- **Suggestion**: fix concreto y accionable

**Lens A — proposal.md**
- WHY es concreto: el Why nombra un problema real, no una motivación genérica
- What Changes es específico: lista nombra capabilities o archivos concretos, no intenciones vagas
- Capabilities en kebab-case: cada capability usa `kebab-case-name`
- Scope creep: cada capability en la sección Capabilities traza de vuelta al WHY
- Broken capability contract: cada capability en New Capabilities necesitará un `specs/<name>/spec.md` correspondiente

**Lens B — design.md**
- Decisión sin alternativas: cada decisión bajo `## Decisions` debería enunciar al menos una alternativa considerada
- Riesgo sin mitigación: cada item bajo `## Risks / Trade-offs` debería tener mitigación o rationale de aceptación
- Open questions: si `## Open Questions` existe con items sin responder, flag como Bloqueante
- Rationale circular: decisiones que se justifican a sí mismas sin comparar con alternativas

**Lens C — specs/ (delta specs)**
- Cada requirement tiene ≥1 scenario
- Formato de scenario: cada scenario debe tener `**WHEN**` y `**THEN**`
- Scenario headers usan #### (4 hashtags)
- Delta operations son válidas: solo `## ADDED`, `## MODIFIED`, `## REMOVED`, `## RENAMED Requirements`
- MODIFIED incluye contenido completo
- REMOVED tiene Reason y Migration
- SHALL/MUST para requirements normativos

**Lens D — tasks.md**
- Tasks no atómicas: task con "y" conectando dos deliverables distintos
- Task sin criterio de done verificable
- Violación de orden de dependencias
- Suposición de código no existente
- Tasks fuera del alcance de la propuesta

**Lens E — código fuente (solo modo pre-archive)**

Extraer rutas de archivos de tasks.md:
```bash
grep -oE '`[^`]+\.[a-zA-Z]{1,5}`' openspec/changes/<name>/tasks.md | tr -d '`' | sort -u
grep -oE '[a-zA-Z0-9_/.-]+\.[a-zA-Z]{1,5}' openspec/changes/<name>/tasks.md | grep '/' | sort -u
```

Para cada ruta candidata: `test -f <path>`. Leer solo los que existen.

Verificar contra specs en contexto:
- Comportamiento requerido faltante (Bloqueante)
- Comportamiento fuera de spec (Recomendado)
- Error paths no implementados (Bloqueante)
- Naming divergence (Opcional)

**Lens F — cobertura de escenarios por tests (NUEVO, solo modo pre-archive)**

**Paso F.1 — Detectar infraestructura de tests:**

```bash
find . -type f \( -name "*.test.*" -o -name "*.spec.*" \) 2>/dev/null | head -20
find . -type d \( -name "tests" -o -name "__tests__" \) 2>/dev/null | head -10
```

**Si no se detecta ningún archivo de test ni directorio de tests:**
- Registrar un único hallazgo: Bloqueante, "sin infraestructura de tests detectada"
- Omitir el análisis por escenario
- Ir directamente al paso 3.5

**Si hay infraestructura de tests:**

**Paso F.2 — Análisis por escenario:**

Para cada escenario en los specs del cambio (bajo `openspec/changes/<name>/specs/`):
1. Extraer 2–4 términos clave del título y del THEN del escenario (sustantivos y verbos de dominio, en el idioma del escenario)
2. Buscar esos términos en los archivos de test detectados:
   ```bash
   grep -r "<término-clave>" --include="*.test.*" --include="*.spec.*" . 2>/dev/null | head -5
   # también buscar en directorios tests/ y __tests__/
   grep -r "<término-clave>" tests/ __tests__/ 2>/dev/null | head -5
   ```
3. Si al menos un archivo de test tiene match de al menos un término: marcar escenario como **cubierto**
4. Si ningún archivo tiene match de ningún término: registrar hallazgo Bloqueante con label `"sin cobertura detectada (Lens F best-effort)"`

Nota: Lens F es una heurística best-effort. Un match de términos no garantiza cobertura real; ausencia de match puede ser falso negativo por diferencias de idioma o naming. Documentar explícitamente en el reporte.

### Paso 3.5 — Paso transversal adversarial

Tras todos los lenses, hacer un barrido adicional buscando:
- Suposiciones implícitas (algo tratado como verdadero en design.md pero no declarado en proposal.md)
- Edge cases faltantes (escenarios que solo cubren el happy path)
- Superficie de seguridad no abordada (si el cambio toca auth, acceso a datos, o input externo)
- Gaps de consistencia (concepto nombrado diferente entre proposal/design/specs/tasks/código)

Solo reportar issues genuinos encontrados.

### Paso 3.6 — Presentar reporte de hallazgos

```
## Review Report: <change-name>

| #  | Sev          | Lens         | Hallazgo                              | Sugerencia                         |
|----|--------------|--------------|---------------------------------------|------------------------------------|
|  1 | Bloqueante   | proposal.md  | "fragmento citado literalmente"       | fix concreto                       |
|  2 | Recomendado  | design.md    | "fragmento citado literalmente"       | fix concreto                       |
...

**Bloqueantes: N · Recomendados: N · Opcionales: N**

> Lens F es heurística best-effort — ausencia de match no garantiza falta de cobertura real.
```

**Si cero Bloqueantes y cero Recomendados:**
```
✓ Change sano — no blocking or recommended issues found.
```

### Paso 3.7 — Ofrecer edits opcionales (si hay Bloqueante o Recomendado)

Preguntar al usuario qué hallazgos aplicar usando **AskUserQuestion** (multiSelect). Para cada hallazgo seleccionado:
- Hacer el cambio con **Edit** directamente en el archivo de artefacto
- Nunca usar **Write** para reescribir el archivo completo
- Tras cada edición, confirmar: "✓ Aplicado hallazgo #N"

---

## Guardrails globales

- **Etiquetas `[tdd]`**: son ignoradas por `openspec-quick-advance` y `openspec-apply` estándar — esas skills implementan directamente sin ciclos TDD. Usar `openspec-tdd` si se quiere el comportamiento TDD.
- **Lens F es heurística**: un match de términos no garantiza cobertura real; ausencia de match puede ser falso negativo. Documentar en el reporte como best-effort.
- **Nunca marcar checkbox sin test verde**: el guardrail más importante de la fase apply — `- [x]` solo se escribe cuando GREEN está confirmado (test pasa).
- **La entrevista siempre ocurre en propose**: no saltarla aunque el request parezca obvio.
- **Nunca crear artefactos antes de la confirmación del Paso 1.4**.
- **Leer contextFiles desde el CLI**: no asumir nombres de archivo de artefactos.
- **Lens E solo en pre-archive**: nunca intentar leer código fuente en modo pre-apply.
- **Edit para correcciones, nunca Write**: al corregir artefactos en el review, usar Edit (diff-based).
