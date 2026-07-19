# CLAUDE.md — MV Data Governance

Guía para Claude Code al trabajar en este repo. Leela antes de tocar código.

## Qué es

**MV Data Governance** es una plataforma de gobierno de datos trilingüe (ES/EN/PT):
catálogo, calidad (6 dimensiones), linaje, glosario, políticas, perfilado, MDM y
publicación a BI. Corre 100% web + escritorio (portable `.bat`, `.exe` con
PyInstaller, o ventana Electron). La demo trabaja sobre **datos 100% sintéticos**;
el motor de reglas, catálogo, linaje y API son reales. Integra con Power BI,
Tableau, Purview y Collibra (en las dos direcciones).

## Stack

- **Python** — motor y app principal:
  - `mvdg/` : motor (i18n, catálogo, calidad, linaje, glosario, políticas, perfilador, MDM, conectores, exportadores).
  - `app/app.py` : dashboard **Streamlit** trilingüe.
  - `bi_api/main.py` : **FastAPI** que sirve las tablas de gobierno para BI (JSON/CSV) en `http://127.0.0.1:8600`.
  - `mvdg/server.py` : modo servidor web multiusuario (solo hosts autorizados).
  - Deps clave: streamlit, pandas, numpy, plotly, fastapi, uvicorn, openpyxl, xlsxwriter, pyarrow, sqlalchemy, keyring.
- **Node / Vercel** — `package.json` (raíz): funciones serverless de pago/landing en `api/*.js` (MercadoPago). Subproyecto **Electron + React** en `electron/` (empaquetado de escritorio).
- **Tests**: `pytest` sobre `tests/test_core.py` (motor, paridad i18n, API, exportadores).

## Comandos

| Objetivo | Comando |
|---|---|
| Instalar deps | `pip install -r requirements.txt` |
| Instalar deps de test | `pip install pytest httpx` |
| Correr la app (dashboard) | `streamlit run app/app.py` |
| Correr la app (Linux/macOS, crea venv) | `./run.sh` |
| Levantar la API REST para BI | `python -m bi_api.main` (`http://127.0.0.1:8600`, docs en `/docs`) |
| Modo servidor web | `python -m mvdg.server` (o `./run_server.sh`) |
| Tests | `pytest tests/ -v` |
| Un test puntual | `pytest tests/test_core.py::<nombre> -v` |
| Servir la landing local | `cd landing && python -m http.server 8080` |
| Regenerar el video demo | `python assets/video/build_video.py` |

> No hay linter/formatter configurado en el repo. No introduzcas uno sin pedirlo.
> Los `.bat` y `packaging/build_exe.bat` son para Windows (PyInstaller + Inno Setup); no corren en este entorno Linux.

## Estructura

```
├── app/app.py            ← dashboard Streamlit (trilingüe)
├── mvdg/                 ← motor: i18n, catálogo, calidad, linaje, glosario,
│                            políticas, perfilador, MDM, conectores, exportadores, server
├── bi_api/main.py        ← FastAPI para BI (JSON/CSV)
├── api/*.js              ← funciones serverless de pago (Vercel/MercadoPago)
├── electron/             ← empaquetado de escritorio (Electron + React)
├── landing/              ← web trilingüe con video (estilo Kobra)
├── packaging/            ← launcher, mvdg.spec (PyInstaller), instalador.iss (Inno Setup)
├── assets/samples/       ← datasets de ejemplo + PowerBI/Tableau demo
├── docs/                 ← manual + guías BI (ES/EN/PT)
└── tests/test_core.py    ← suite: motor, i18n, API, exportadores
```

## Flujo de trabajo

1. **Plan** — ante un cambio no trivial, planificá primero (`/plan`). Solo lectura hasta aprobar.
2. **Cambio** — editá el mínimo necesario. Respetá la separación motor (`mvdg/`) vs. UI (`app/app.py`) vs. API (`bi_api/`).
3. **Test** — `pytest tests/ -v` (`/test`). No declares éxito sin correrlos.
4. **Ship** — `/ship`: test → commit descriptivo → push → PR draft.

## Convenciones

- **Trilingüe siempre (ES/EN/PT)**: todo texto de cara al usuario vive en `mvdg/i18n.py` con las 3 claves. La paridad de idiomas está cubierta por tests — si agregás una clave, agregá los 3 idiomas o el test rompe.
- Motor **sin efectos de red por defecto**: los conectores externos (Purview, Collibra, Azure, Power BI tenant, Tableau) están **apagados por defecto** y con modo previsualización sin credenciales. No los prendas por defecto.
- Datos de demo **100% sintéticos**; los defectos de calidad son inyectados a propósito. No metas datos reales de personas.
- IA externa (Claude/ChatGPT/Gemini) es **opcional** y con API key del usuario vía `keyring`. Nunca hardcodees claves.
- El motor (`mvdg/`) debe poder importarse y testearse sin levantar Streamlit ni la API.

## Do / Don't

**Do**
- Corré `pytest tests/ -v` antes de cerrar cualquier cambio de motor o i18n.
- Mantené la paridad ES/EN/PT en cada string nuevo.
- Preferí editar el motor en `mvdg/` y consumirlo desde `app/app.py` y `bi_api/`.
- Usá `git status`/`git diff` para revisar antes de commitear.

**Don't**
- No prendas conectores externos por defecto ni ejecutes DDL de enforcement (solo se genera, nunca se aplica).
- No leas ni commitees secretos (`.env`, `.streamlit/secrets.toml`, `*.pem`, `id_rsa*`, tokens de pago).
- No corras los `.bat` ni el build PyInstaller/Inno en Linux.
- No introduzcas dependencias pesadas nuevas sin justificarlo.
- No uses `git push --force` ni `rm -rf`.

## Contexto / Compact

- Empezá por este archivo y el `README.md` (tiene el detalle de cada módulo).
- Para entender la superficie de UI: `app/app.py`. Para el motor: el módulo puntual en `mvdg/`.
- Docs de dominio en `docs/` (DMBOK, PURVIEW_COLLIBRA, BI_INTEGRATION, CLOUD_CONNECTORS).
- Si el contexto se llena, compactá reteniendo: comandos de esta tabla, la regla de i18n trilingüe, y qué archivos tocaste.
