---
description: Ejecuta el plan aprobado en un loop autónomo con red de seguridad — checkpoint antes de cada milestone, verificación por hooks tras cada edición, y consulta al humano solo en lo ambiguo o irreversible.
argument-hint: "[nota o paso por el que arrancar]"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, Agent
---

Ejecutá el plan aprobado (arrancá por: $ARGUMENTS, o desde el principio si no se
indica). El modo es un loop **PLANIFICAR→EJECUTAR→VERIFICAR→CORREGIR** con red.

## La red de seguridad (lo que hace segura la autonomía)

1. **Checkpoint antes de cada milestone.** Antes de empezar un bloque grande,
   dejá un punto de retorno durable:
   `git add -A && git commit -m "checkpoint: <descripción>"` o un tag
   `automate/checkpoint-<n>`. Es lo que te deja volver A→B→C sin miedo. Git
   sobrevive al reinicio de sesión y viaja con el repo; complementa al `/rewind`
   nativo, no lo reemplaza.

2. **Verificá después de cada edición.** Los hooks de `PostToolUse` corren
   formato y tests solos. Si algo rompe, **corregí antes de seguir** — no
   avances sobre un árbol roto. Si no hay hooks configurados, corré vos el test
   de la zona que tocaste.

3. **Mantené el contexto liviano.** En trabajos largos, delegá exploración a
   sub-agentes (`repo-explorer`) y dejá que el contexto compacte cuando se
   llene; el summary preserva el hilo. No cierres antes de tiempo.

4. **Preguntá solo lo que es del humano.** Decisiones ambiguas, irreversibles o
   de producto → consultá. Lo mecánico y verificable → hacelo. La autonomía no
   es "no preguntar nunca", es "no preguntar lo que ya está decidido".

## Al terminar cada milestone

- Confirmá que la verificación pasa (mostrá la salida real, no la afirmes).
- Dejá el checkpoint del milestone.
- Seguí con el próximo paso del plan.

Cuando el plan esté completo y verde, pasá a `/automate-ship`. Si te trabás o
un paso resulta más grande de lo planificado, pará y reportá — no fuerces.
