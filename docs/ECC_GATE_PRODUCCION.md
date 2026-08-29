# MV Data Governance — Gate de producción ECC

> Puntaje bajo la rúbrica de `.claude/skills/ecc/SKILL.md` (ECC v2.2.0,
> skill `production-audit`). **Evidencia ejecutada o no cuenta.**

**Veredicto: 84/100 → 8/10. Sale con salvedades. El producto está sólido —el
auto-diagnóstico da 46/46 y los tres tests de pago/licencia/XSS de CI pasan—
pero hay dos tests que no cuidan lo que parece que cuidan, y uno de ellos es el
que cubre la app de escritorio.**

## Evidencia ejecutada

| Verificación | Comando | Resultado |
|---|---|---|
| Linter | `python -m ruff check .` | ✅ `All checks passed!` |
| Suite Python | `python -m pytest tests/ -q` | ⚠️ **485 de 486**, 1 falla, 1 skip |
| Cero warnings de deprecación | `pytest -W error::DeprecationWarning` | ⚠️ misma única falla, nada más |
| Auto-diagnóstico | `python -m mvdg.selfcheck` | ✅ **46/46, 100% operativo** |
| Pagos | `node api/payments.test.js` | ✅ |
| Pago → licencia | `node api/pago_a_licencia.test.js` | ✅ |
| XSS de la landing | `node landing/security.test.js` | ✅ |
| Secretos versionados | `git ls-files \| grep -E '\.env$\|\.pem\|\.keystore'` | ✅ ninguno |

Los tres tests de JS son **exactamente los que corre CI**, no `node --test`.

## Hallazgo 1 — `test_connectors_guards` no prueba un guard

`tests/test_core.py:789` afirma probar que un driver ausente da "mensaje
legible, no excepción":

```python
ok, msg = C.test_connection({"engine": "postgresql", "host": "localhost", ...})
assert ok is False and "driver" in msg.lower()
```

Pero eso solo pasa **si `psycopg2` no está instalado**. Con el driver presente,
`test_connection` no se frena: **abre una conexión TCP real a localhost:5432** y
devuelve el error de conexión, no el de driver. Reproducido acá:

```
assert 'driver' in 'operationalerror: (psycopg2.operationalerror) connection to
server at "localhost" (127.0.0.1), port 5432 failed: ...'
```

Dos consecuencias:

1. **El test no verifica un guard, verifica la ausencia de una dependencia.**
   Como `requirements.txt` línea 46 le dice al usuario `pip install
   psycopg2-binary` para usar PostgreSQL, cualquier desarrollador que siga la
   propia documentación del repo se encuentra la suite en rojo.
2. **La suite no es hermética.** Hace una llamada de red cuyo resultado depende
   de la máquina. En CI pasa porque `psycopg2` no está instalado ahí; es un
   verde por accidente de entorno, no por comportamiento verificado.

Arreglo sugerido (no aplicado acá — es código de test del producto y merece su
propio PR con criterio del dueño): separar los dos casos. Uno que fuerce la
ausencia del driver con un `monkeypatch` sobre el import, y otro que verifique
el mensaje de conexión fallida sin depender de que haya o no un Postgres local.

## Hallazgo 2 — hay un test que CI nunca corre

`electron/lib/server-manager.test.js` cubre el arranque de la app de escritorio:
puerto libre, intérprete de Python, la API real levantando, y que la interfaz
React se sirva en `/app`. Acá **falla**: da 404 en `/app` porque el bundle de
React no está compilado en el checkout.

Pero el punto no es esa falla, es que **CI no corre ese archivo**. El paso
"Tests de JS" ejecuta tres archivos por nombre —`api/payments.test.js`,
`api/pago_a_licencia.test.js`, `landing/security.test.js`— y el de Electron no
está en la lista. Solo aparece si alguien invoca `node --test` en la raíz, cosa
que CI no hace.

O sea: **el camino de la app de escritorio no tiene cobertura efectiva en CI**.
El test existe, alguien se tomó el trabajo de escribirlo, y no corre nunca.

Arreglo: agregarlo al paso de CI, con el build del frontend antes (o un skip
explícito y ruidoso si el bundle no está, en vez de un 404 confuso).

## Otra observación

El workflow `monitor.yml` viene fallando en sus últimas dos corridas
programadas sobre `main`. No lo investigué —está fuera del alcance de esta
auditoría— pero un monitor en rojo es un monitor que nadie mira.

## Por qué 8 y no 9

Ningún tope duro de seguridad aplica: pagos, licencias y XSS tienen su gate y
están verdes, no hay secretos versionados, y el auto-diagnóstico da 46/46. La
rúbrica topea en 8/10 cuando **el gate del repo no está verde** (1 falla) y
cuando **el camino crítico no se probó de punta a punta** (el de escritorio no
corre en CI). Arreglados esos dos, esto es un 9/10 sin tocar el producto.

## Próxima acción

1. Separar `test_connectors_guards` en dos casos, uno de ellos con el driver
   forzado a ausente.
2. Sumar `electron/lib/server-manager.test.js` al paso de JS de CI, con el
   build del frontend antes.
