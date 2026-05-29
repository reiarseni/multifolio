---
name: release-plan
description: Genera un plan de desarrollo con issues, ramas y PRs siguiendo las convenciones GitHub de este proyecto. Aplica al crear ramas, nombrar commits o planificar cambios.
allowed-tools: Read Write AskUserQuestion Bash(git *) Bash(find *) Bash(ls *) Bash(mkdir *)
argument-hint: "[numero-inicio-issue]"
---

# Release Plan — multifolio

## Convenciones GitHub (fijas para este proyecto)

```
branch.feat_prefix : feat/
branch.fix_prefix  : fix/
branch.pattern     : {prefix}{N}-{kebab-desc}
commit.prefixes    : feat | fix | chore | refactor | docs | test
commit.max_title   : 72 chars
pr.title_pattern   : {verb_phrase} (#N)
pr.closes          : Closes #{N}
plans_dir          : .claude/plans
```

> **Idioma de ramas:** la parte descriptiva SIEMPRE en español, kebab-case.
> - ✓ `feat/12-panel-usuario`   ✓ `fix/15-error-carga-imagen`
> - ✗ `feat/12-user-panel`      ✗ `fix/15-image-load-error`

---

## Instrucciones

### 0. Número de inicio

- Argumento del usuario → ese `N`. Debe ser entero ≥ 1.
- Sin argumento → revisar `ls .claude/plans/*.md 2>/dev/null` y tomar el número más alto + 1.
- Si no hay planes previos → preguntar al usuario.

### 1. Estado del repo

Ejecutar y mostrar:
```bash
git status --short
git diff --stat HEAD
```

### 2. Agrupar cambios

- **Cohesión**: un grupo = una historia de usuario o un bug concreto.
- **Atomicidad**: puede mergearse y desplegarse de forma independiente.
- **Tamaño**: grupos pequeños preferidos. Backend + frontend de la misma feature van juntos. Features distintas que tocan el mismo archivo → separarlas.
- Cada grupo adicional incrementa `N` en 1.

### 3. Tipo y borrador del issue (interactivo)

Para **cada grupo**, determina el tipo y presenta el borrador con `AskUserQuestion` antes de continuar.

| Naturaleza | Tipo | Rama |
|---|---|---|
| Nueva feature, mejora, refactor, infra | `feat` | `feat/{N}-desc` |
| Corrección de bug | `fix` | `fix/{N}-desc` |
| Mantenimiento, deps, CI/CD | `chore` | `feat/{N}-desc` |
| Investigación técnica | `spike` | `feat/{N}-desc` |

---

#### Borrador **feat**

```markdown
## Overview

> <Una frase que describe qué se agrega y para quién.>

## User Story

**As a** <rol>,
**I want** <acción>,
**so that** <beneficio medible o concreto>.

## Background

<Contexto de negocio o técnico que explica por qué esto importa ahora.
Máx 2-3 oraciones. Si hay una decisión previa o restricción que lo motiva, mencionarla aquí.>

## Acceptance Criteria

- [ ] Given <estado inicial>, when <acción del usuario>, then <resultado observable>
- [ ] <criterio adicional verificable — evitar "funciona correctamente">

## Out of Scope

- <qué NO cubre este issue — ser explícito para evitar scope creep>

## Open Questions

- [ ] <pregunta que debe resolverse antes de cerrar el issue, si aplica>

**Labels:** `feat` `<área>`
```

#### Borrador **fix**

```markdown
## Summary

> <Una frase: qué falla, en qué contexto y cuál es el síntoma visible.>

## Environment

- Version / Branch: <x.y.z o nombre de rama>
- Reproducible in: Staging / Production / Local only

## Steps to Reproduce

1. <paso exacto — lo suficientemente específico para que cualquiera lo siga>
2. 
3. 

## Expected Behavior

<Lo que debería ocurrir según el diseño o contrato de la feature.>

## Actual Behavior

<Lo que ocurre en realidad. Incluir mensaje de error exacto si existe.>

```
<stack trace o mensaje de error, si aplica>
```

## Frequency & Impact

| Attribute | Value |
|-----------|-------|
| Frequency | Siempre / Frecuente / Intermitente / Condicional |
| Blocks production | Sí / No |
| Workaround available | Sí / No — <descripción breve si aplica> |
| Affected users | <segmento o rol — ej. "todos los usuarios con plan Pro"> |

**Labels:** `bug` `<área>`
```

#### Borrador **chore**

```markdown
## Summary

> <Qué hay que hacer, en una frase orientada al resultado, no a la tarea.>

## Motivation

<Justificación concreta y verificable: EOL de dependencia, CVE, deuda técnica con métrica,
requisito de compliance, etc. Evitar "es buena práctica" sin evidencia.>

## Scope

**In scope:**
- <módulo, archivo o sistema afectado>

**Out of scope:**
- <qué no se toca en este chore>

## Definition of Done

- [ ] <criterio verificable 1 — debe poder comprobarse sin ambigüedad>
- [ ] <criterio verificable 2>
- [ ] Tests existentes pasan sin modificación (o se actualizan justificadamente)
- [ ] Documentación actualizada si el cambio afecta la interfaz pública

**Labels:** `chore` `<área>`
```

#### Borrador **spike**

```markdown
## Context

<Incertidumbre o riesgo concreto que motiva la investigación.
Describir qué decisión de diseño o implementación está bloqueada por falta de información.>

## Questions to Answer

- [ ] <Pregunta respondible y acotada — evitar "¿es buena idea X?" sin criterio de evaluación>
- [ ] <Segunda pregunta con el mismo criterio>

## Timebox

**Estimado:** <N horas / N días>
**Deadline:** <fecha límite para la decisión>

## Deliverable

Al cerrar este spike debe existir al menos uno de los siguientes:
- [ ] ADR (Architecture Decision Record) con la decisión tomada
- [ ] Proof of concept en rama `spike/<N>-<desc>` con README de hallazgos
- [ ] Documento de hallazgos en `.claude/plans/spike-<N>-hallazgos.md`

**Labels:** `spike` `<área>`
```

Opciones: **"Aprobar"** / **"Ajustar"**. Si ajusta, mostrar borrador corregido antes de continuar.

### 4. Generar archivo de plan

Crear `.claude/plans/` si no existe. Nombre del archivo:
- feat / chore / spike → `.claude/plans/feat-N-descripcion.md`
- bug → `.claude/plans/fix-N-descripcion.md`

**Estructura del archivo:**

```markdown
# Issue #N — <Título>

<Sección del issue según el tipo — ver borradores sección 3>

---

# Plan de rama — <prefix>N-descripcion-kebab-case

## Encabezado

Rama: `<prefix>N-descripcion-en-espanol-kebab-case`  
Issue: #N

## Archivos del grupo

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `ruta/archivo` | Nuevo / Modificado / Eliminado | Qué hace |

## Commits

### Commit 1 — <título>

```
<prefijo>: <descripción en tercera persona, max 72 chars>

<body si aplica — ver reglas sección 5>

Refs #N
```

Archivos: `ruta/archivo`

```bash
git add ruta/archivo
git commit
```

### Commit N — <último>

```
<prefijo>: <descripción>

Closes #N
```

Archivos: `ruta/ultimo`

```bash
git add ruta/ultimo
git commit
```

## Orden de ejecución

```
1 → 2 → ... → N
```

## PR

**Título:** `<Verbo en tercera persona singular> (#N)`
Ejemplos: `Agrega panel de usuario (#12)` · `Corrige error de carga (#15)` · `Refactoriza módulo de auth (#8)`

**Body:**

```markdown
## ¿Qué hace este PR?

<Párrafo de contexto.>

**Cambios principales:**
1. **<Área>**: <qué hace y por qué>

Closes #N

## Cómo probar

1. ...
2. ...

## Tipo de cambio
- [ ] feat   - [ ] fix   - [ ] refactor
- [ ] docs   - [ ] test  - [ ] chore

## Checklist
- [ ] CI verde
- [ ] Probado localmente
- [ ] Self-review completado
```
```

### 5. Reglas de commits

- **Prefijo**: `feat` | `fix` | `chore` | `refactor` | `docs` | `test`
- **Título**: tercera persona singular, sin tildes, sin paréntesis, máx 72 chars.
- **Body** (elegir en orden):
  - **A — Sin body**: el título describe todo el cambio.
  - **B — Prosa corta**: 1-2 líneas del *para qué* o *por qué* (cambios unitarios).
  - **C — Lista**: una línea por área con `- ` (commits que tocan múltiples dominios).
- **Footer**:
  - Commits intermedios: `Refs #N`
  - Último commit: `Closes #N`
- **Prohibido**: nunca incluir `Co-authored-by:` ni ninguna línea de autoría automática en el footer.

**Agrupación dentro de cada PR:**
- Schema / migración → primer commit.
- Lógica de negocio → uno o dos commits según tamaño.
- UI / frontend → último commit.

### 6. Resumen final

Después de crear todos los archivos:

```
| Archivo                              | Issue | Rama                        | Commits |
|--------------------------------------|-------|-----------------------------|---------|
| .claude/plans/feat-N-descripcion.md  | #N    | feat/N-descripcion          |    3    |
| .claude/plans/fix-M-descripcion.md   | #M    | fix/M-descripcion           |    2    |
```

Indicar cuántos archivos se crearon y el orden de merge recomendado (migraciones antes del frontend que las consume; features independientes en cualquier orden).
