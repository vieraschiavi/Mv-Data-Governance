---
description: Corre el gate completo de verificación (tests, lint, build) y solo si pasa hace commit y abre un PR — si algo falla, reporta el diagnóstico en vez de entregar roto.
argument-hint: "[título del PR o rama destino]"
allowed-tools: Read, Grep, Glob, Bash, Edit
---

Preparación de entrega. Contexto (título de PR / rama, si se indica): $ARGUMENTS

## 1. Gate de verificación (bloqueante)

Corré, en orden, lo que aplique al stack de este repo (mirá CLAUDE.md para los
comandos reales):

- Tests
- Lint / type-check
- Build

**Regla dura de honestidad:** si cualquiera falla, NO entregues. Mostrá la
salida real del fallo y el diagnóstico. Un proyecto no está listo porque lo
declaremos, sino porque el gate pasa y se puede mostrar que pasa. Ofrecé
volver a `/automate-build` para corregir.

## 2. Estado del árbol

Revisá:

!`git status --short`

!`git diff --stat`

## 3. Commit + PR (solo con el gate en verde)

- Commit con un mensaje descriptivo que explique el *qué* y el *por qué*.
- Push a la rama de trabajo.
- Abrí un PR (usando el MCP de GitHub si está disponible, o el mecanismo que el
  repo use). Si hay plantilla de PR en `.github/`, seguí su estructura.
- Si el repo tiene convenciones propias de commit/PR en CLAUDE.md, respetalas.

Cerrá reportando: qué se entregó, resultado del gate (con evidencia), y el link
del PR.
