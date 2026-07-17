<!--
  Plantilla de CLAUDE.md generada por project-automator.
  /automate-init la completa con lo que detecta del repo. Los <PLACEHOLDER> se
  reemplazan con datos reales; borrá esta línea y este comentario al terminar.
-->

# <NOMBRE DEL PROYECTO>

<Una o dos frases: qué es este proyecto y para quién.>

## Cómo se corre

- **Instalar deps**: `<comando>`
- **Correr en local**: `<comando>`
- **Testear**: `<comando>`
- **Lint / type-check**: `<comando>`
- **Build**: `<comando>`

> Estos comandos son la fuente de verdad para `/automate-build` y
> `/automate-ship`. Si cambian, actualizá esta sección.

## Estructura

- `<dir>/` — <qué contiene>
- `<dir>/` — <qué contiene>

## Convenciones

- <estilo de código, formato, naming observado>
- <cómo se escriben los tests / dónde van>
- <formato de commits o PRs, si el repo tiene uno>

## No tocar / cuidado

- <archivos generados, migraciones, lockfiles>
- <secretos: viven en variables de entorno, nunca en el repo>
- <ramas protegidas, procesos de deploy delicados>

## Automatización (project-automator)

Este repo usa el plugin `project-automator`. Flujo:
`/automate-plan <objetivo>` → `/automate-build` → `/automate-ship`.
Auditar el estado con `/automate-audit`.
