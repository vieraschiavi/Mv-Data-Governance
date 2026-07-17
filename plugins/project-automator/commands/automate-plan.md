---
description: Planifica un objetivo en modo solo-lectura antes de tocar código — explora con un sub-agente, produce un plan por pasos con puntos de checkpoint y espera aprobación del humano.
argument-hint: "<objetivo a implementar>"
allowed-tools: Read, Grep, Glob, Bash(git status:*), Bash(git diff:*), Agent
---

Objetivo a planificar: **$ARGUMENTS**

Estás en disciplina de **plan mode**: solo leer y razonar, **no escribas ni
edites código** en esta fase. El entregable es un plan que el humano aprueba.

## 1. Explorar sin ensuciar el contexto

Delegá el barrido pesado al sub-agente de exploración para no llenar el
contexto principal con volcados de archivos:

> Usá el sub-agente `repo-explorer` para mapear todo lo relevante al objetivo
> "$ARGUMENTS": archivos y símbolos involucrados, patrones y convenciones a
> respetar, tests existentes que cubren la zona, y riesgos. Pedile un resumen
> accionable, no el contenido completo de los archivos.

Si el objetivo es chico y ya conocés la zona, podés explorar vos directo.

## 2. Producir el plan

Entregá un plan numerado. Cada paso debe tener:

- **Qué** se cambia y **por qué**.
- **Archivos** que toca.
- **Cómo se verifica** (qué test/comando prueba que quedó bien).
- **Checkpoint**: marcá los pasos tras los cuales conviene dejar un punto de
  retorno durable (commit o tag `automate/checkpoint-<n>`), para poder volver
  A→B→C si algo sale mal más adelante.

Cerrá con: supuestos que estás haciendo, decisiones que son del humano (y por
qué), y qué quedaría fuera de alcance.

## 3. Esperar aprobación

No pases a construir hasta que el humano apruebe. Cuando apruebe, el siguiente
paso es `/automate-build`.
