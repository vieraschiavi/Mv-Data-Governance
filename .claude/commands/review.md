---
description: Revisar el diff actual buscando bugs y mejoras
---

Revisá los cambios sin commitear (o los de $ARGUMENTS si se indica):
1. Corré `git diff` para ver qué cambió.
2. Buscá bugs de correctitud, casos borde y problemas de seguridad.
3. Chequeos propios de este repo: ¿se rompió la paridad i18n ES/EN/PT? ¿se prendió algún conector externo por defecto? ¿se filtró algún secreto o API key? ¿el motor `mvdg/` sigue importable sin Streamlit/API?
4. Señalá simplificaciones y reuso posibles.
5. Priorizá los hallazgos por severidad y proponé el fix concreto de cada uno.

No apliques cambios salvo que se pida — primero reportá.
