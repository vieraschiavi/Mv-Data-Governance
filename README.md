# 🛡️ MV Data Governance · Gobierno de datos claro y listo para BI

**MV Data Governance** es una plataforma de gobierno de datos — catálogo,
calidad, linaje, glosario, políticas y perfilado — **trilingüe (ES/EN/PT)**,
**100% web y PC** (portable `.bat` y ejecutable `.exe`, sin APK) y
**compatible con cualquier herramienta de BI**: Power BI, Tableau, Looker,
MicroStrategy, Qlik, Excel…

Construida con el mismo ADN visual y de producto que
[MV Kobra AI](https://github.com/vieraschiavi): landing navy/ámbar con video
de demo, dashboard gerencial y empaquetado Windows con PyInstaller + Inno
Setup.

> **Qué es esto (léase primero).** La demo funciona sobre **datos 100%
> sintéticos** (sin nombres reales, apta para mostrar sin problemas legales).
> Todo lo que ves funcionar es real: el motor de reglas, el catálogo, el
> linaje, la API. Los puntajes de calidad que muestra salen de defectos
> **inyectados a propósito** en los datos de demo para que el motor tenga
> algo que detectar; con tus datos reales, los números serán los tuyos.

---

## 🎬 Video y landing

- **Landing web trilingüe** (estilo MV Kobra): [`landing/index.html`](landing/index.html)
  — hero, video de demo, plataforma, compatibilidad BI, descargas, precios y
  contacto, con selector **ES / PT / EN** persistente.
- **Video de demo**: [`assets/video/MVDataGovernance_Demo.mp4`](assets/video/MVDataGovernance_Demo.mp4)
  (42 s, generado con [`assets/video/build_video.py`](assets/video/build_video.py) —
  reproducible con `python assets/video/build_video.py`).

Para ver la landing localmente:

```bash
cd landing && python -m http.server 8080   # → http://localhost:8080
```

## 🚀 Ejecutar el programa (PC)

| Cómo | Qué hace |
|---|---|
| **`MV_DataGovernance.bat`** | Portable Windows: crea el entorno la primera vez y abre el programa en el navegador |
| **`packaging\build_exe.bat`** | Construye `MVDataGovernance.exe` (PyInstaller) y el instalador `MVDataGovernance_Setup_v1.0.0.exe` (Inno Setup, trilingüe) |
| **`MV_DataGovernance_API.bat`** | Levanta la API REST para BI en `http://127.0.0.1:8600` |
| **`MV_DataGovernance_Server.bat`** / **`./run_server.sh`** | Modo servidor web para la empresa: varios usuarios desde el navegador, **solo en servidores autorizados** (`server_authorized.txt` / `MVDG_AUTHORIZED_HOSTS`) |
| **`./run.sh`** | Linux / macOS (escritorio, abre el navegador local) |

Guía completa: [`docs/MANUAL_PUESTA_EN_MARCHA.md`](docs/MANUAL_PUESTA_EN_MARCHA.md).
¿Qué es el gobierno de datos y cómo lo cubre esta plataforma frente al
estándar DAMA-DMBOK? [`docs/DMBOK.md`](docs/DMBOK.md) (explicado para
técnicos y no técnicos, en los 3 idiomas).

### 📦 Paquetes según las restricciones de TI de cada empresa

| Carpeta | Cuándo | Cómo se genera |
|---|---|---|
| [`distribucion/opcion_A_instalador_exe/`](distribucion/opcion_A_instalador_exe/LEEME.md) | La empresa **permite instalar .exe** (no requiere Python) | `packaging\build_exe.bat` en Windows |
| [`distribucion/opcion_B_portable_bat/`](distribucion/opcion_B_portable_bat/LEEME.md) | La empresa **bloquea .exe pero permite Python** (no instala nada en el sistema) | `python packaging/build_release.py` → ZIP portable |
| [`electron/`](electron/README.md) | Instalador `.exe` con ventana de escritorio nativa (Electron + React) en vez del navegador — tercera forma de empaquetar el mismo programa | `cd electron && npm run dist-win` en Windows |

Mismas funcionalidades en las tres. La ficha de cada empresa (pestaña 🏢) guarda
su restricción y recomienda el paquete automáticamente.

## 🧩 Módulos

| Módulo | Qué resuelve |
|---|---|
| 📊 **Panorama** | KPIs de gobierno: índice de calidad, reglas, PII, stewards, evolución 12 meses + **🏛️ Estado del gobierno** (estilo Purview "Data Estate Insights", 100% local): índice de gobierno 0-100 con 5 coberturas — owner/steward nombrado, clasificación, reglas, definiciones curadas — que sube al usar 👥 Responsables y 🖊️ Curaduría. Comparación honesta con Purview/Collibra en [`docs/PURVIEW_COLLIBRA.md`](docs/PURVIEW_COLLIBRA.md) |
| 🧪 **Laboratorio** | Caso completo de punta a punta (empresa retail ficticia): las 7 etapas de un proyecto de gobierno de datos —catalogar, medir ANTES, gobernar, corregir y medir DESPUÉS, linaje, políticas, publicar a BI— con teoría en criollo + técnica y dashboards reales en cada paso |
| 📘 **Estándares** | Autoevaluación honesta frente a **3 marcos de referencia**, cada uno en su propia pestaña interna: **DAMA-DMBOK** (11 áreas de conocimiento, principios, glosario, roles, madurez, ciclo de vida POSMAD), **COBIT 2019** (los 8 objetivos de gobierno/gestión relacionados con datos, de ISACA) y **ISO/IEC 38505** (los 6 principios de gobierno de datos + modelo Valor/Riesgo/Restricción). Ninguno es una certificación — cada uno marca, con radar y cobertura honesta, qué cubre la plataforma y qué queda en manos de tu organización |
| 📚 **Catálogo** | Inventario de datasets con dueño, steward, dominio, clasificación (PII), frescura + diccionario de columnas |
| 🔗 **MDM** | Master Data Management: encuentra filas que probablemente representan la misma entidad (cliente, producto…) con datos levemente distintos, y arma el **golden record** que las unifica. Matching por reglas ponderadas (identificadores fuertes como documento/email pesan mucho más que un nombre común, para evitar falsos positivos), 100% local. Corré sobre el dataset sintético de demo o sobre cualquiera de los 4 datasets de ejemplo — el de medicamentos openFDA trae un caso real: 6 grupos farmacéuticos escritos de 45 formas distintas |
| ✅ **Calidad** | Motor de reglas en 6 dimensiones (completitud, unicidad, validez, consistencia, puntualidad, exactitud) con umbrales, estados y mapa de calor. Cada falla trae, al lado, una **sugerencia de la IA** para corregirla: causa probable, qué hacer con las filas ya cargadas y cómo evitar que vuelva a pasar (100% local, sin llamadas externas). Opcionalmente, con tu propia API key de Claude/ChatGPT/Gemini, podés pedir además una segunda sugerencia generada en vivo por ese modelo — [`docs/IA_EXTERNA.md`](docs/IA_EXTERNA.md) |
| 🧬 **Linaje** | Grafo interactivo fuente → cruda → curada → mart → BI, con foco aguas arriba/abajo |
| 📖 **Glosario** | Términos de negocio con definición oficial en 3 idiomas y datasets vinculados |
| 🖊️ **Curaduría** | El flujo de stewardship de Purview/Collibra, local: **toda definición** (glosario, catálogo, diccionario — 117 ítems) viene **pre-establecida por IA** como recomendación inicial, y el **Data Owner/Steward la valida tal cual o la modifica** con su texto oficial — con nombre, cargo, fecha y notas, guardado en disco. Métricas de avance (% revisado) y filtros por tipo/dataset/estado |
| 👥 **Responsables** | Cargá el **organigrama de la empresa** (Excel/CSV — detecta encabezados en ES/EN/PT en cualquier orden —, tabla por conexión SQL, o **foto** vía la IA externa opcional) y el programa completa por defecto el **Data Owner y Data Steward de cada dataset, con nombre y cargo**, matcheando área↔dominio y jerarquía de cargos. Todo editable y guardado en disco — la sugerencia nunca es la palabra final |
| 🛡️ **Políticas** | Cumplimiento verificado automáticamente contra catálogo y reglas (evidencia, no checkboxes) |
| 🔎 **Mis datos** | Subí tu CSV/Excel **o conectate directo a tu base de datos** — 5 motores SQL clásicos (PostgreSQL, MySQL, SQL Server, Oracle, SQLite) **más los data warehouse/lake de nube más usados**: Snowflake, Google BigQuery, Databricks SQL Warehouse y Azure Synapse ([`docs/CLOUD_CONNECTORS.md`](docs/CLOUD_CONNECTORS.md)): perfil por columna, duplicados, PII detectada y reglas sugeridas. Trae 4 **datasets de ejemplo reales, gobernados de punta a punta** (rotulado de alimentos, Uruguay · ventas de cafetería, Kaggle CC BY-SA 4.0 · campaña bancaria, UCI CC BY 4.0 · **medicamentos de 6 laboratorios multinacionales, openFDA dominio público — con defectos reales, no inyectados**): catálogo con dueño/steward, reglas de calidad con umbral, glosario y exportación/API lista para Power BI o Tableau |
| 📤 **BI & API** | Exportación CSV/Excel/JSON/Parquet + paquete Excel multi-hoja + API REST + **🔀 Migración a Purview/Collibra en las dos direcciones** — empuja catálogo/diccionario/glosario (acelerador, no reemplazo — el estado Draft/Approved sale de tu curaduría real) y **⬇️ trae** de Collibra lo ya aprobado (Business Terms + assets) — + **🔒 Enforcement**: genera DDL de GRANT/REVOKE y enmascaramiento (PostgreSQL/SQL Server), nunca lo ejecuta + **🏷️ Etiquetas MIP** reales vía Microsoft Graph + **🔎 Escaneo batch** de tus conexiones + **☁️ Descubrimiento en Azure** (Resource Graph): inventaría todos los recursos de datos de tu suscripción en una consulta, sin agentes. Todo apagado por defecto, con modo previsualización sin credenciales. Detalle honesto de qué se logró y dónde queda el techo — y un FAQ completo — en [`docs/PURVIEW_COLLIBRA.md`](docs/PURVIEW_COLLIBRA.md) y la pestaña ❓ Ayuda |
| 🔷 **Power BI** | Gobiernos el modelo de Power BI (y Fabric, que comparte el mismo workspace) en sí, no solo tus datos. **Modo offline**: apuntá a un proyecto `.pbip` (formato TMDL, sin datos si borraste `cache.abf`). **Modo tenant completo**: con tu propio service principal (opcional, apagado por defecto), escanea TODOS los workspaces del tenant vía la Scanner API de un clic — con paginación real para tenants grandes. **Modo ejemplo**: un modelo real (GitHub, MIT) o un tenant multinacional ilustrativo, sin configurar nada. Arma catálogo, glosario (cada medida = término), 5 reglas de salud del modelo y el **linaje cableado de punta a punta: SQL Server detectado → tabla → dataset (modelo) → reporte**. Con tu API key de IA opcional, pedí que audite y refactorice el DAX de cualquier medida ([`docs/BI_TENANT_SCAN.md`](docs/BI_TENANT_SCAN.md), [`docs/IA_EXTERNA.md`](docs/IA_EXTERNA.md)) |
| 📊 **Tableau** | El mismo gobierno del modelo, para Tableau. **Modo offline**: leé un `.twb`/`.twbx` local (nunca los extractos de datos empaquetados). **Modo sitio completo**: con tu propio Personal Access Token (opcional, apagado por defecto), escanea todo tu sitio vía la Metadata API. **Modo ejemplo**: un workbook incluido, sin configurar nada. Arma catálogo, glosario (cada campo calculado = término), 4 reglas de salud y linaje tabla de BD → datasource → workbook. Con tu API key de IA opcional, pedí que audite y refactorice cualquier fórmula calculada ([`docs/BI_TENANT_SCAN.md`](docs/BI_TENANT_SCAN.md)) |
| 🏢 **Empresas** | Fichas de empresas clientes **que se guardan en disco** (contacto, BI, restricción de TI → recomienda Opción A o B, madurez, notas) con exportación |
| 📁 **Proyecto** | El proyecto de gobierno de **cada cliente, guardado en disco por etapas** para no perder nada: cada etapa es una foto con nombre de tu trabajo (el dataset que perfilaste, el reporte de duplicados/MDM, el escaneo de Power BI/Tableau, el paquete de tablas para BI) más notas. Guardás, recargás y borrás etapas, y **respaldás o migrás el proyecto completo a un ZIP** (y lo restaurás). 100% local ([`docs/PROYECTO_CLIENTE.md`](docs/PROYECTO_CLIENTE.md)) |
| ❓ **Ayuda** | Qué se automatiza y qué no + **speeches IA** listos (dirección, dueños de datos, TI, comité, origen) para lograr la parte no automatizable y cerrar el círculo |

## 📊 Compatibilidad BI

Todas las tablas (`catalog`, `dictionary`, `quality_results`, `lineage`,
`glossary`, `policies`, `kpis`…) se sirven por **API REST** en JSON o CSV y
se exportan como **CSV / Excel / JSON / Parquet**:

```
GET http://127.0.0.1:8600/api/catalog?lang=es
GET http://127.0.0.1:8600/api/quality_results?lang=en&format=csv
GET http://127.0.0.1:8600/docs
```

Paso a paso por herramienta (Power BI, Tableau, Looker, MicroStrategy, Qlik,
Excel) en **[`docs/BI_INTEGRATION.md`](docs/BI_INTEGRATION.md)** — en los
tres idiomas.

## 🌐 Idiomas / Languages / Idiomas

Español · English · Português en **toda** la superficie: landing, programa,
API (`?lang=es|en|pt`), instalador Windows y documentación. La paridad de
traducciones está cubierta por tests.

## 🗂️ Estructura

```
├── MV_DataGovernance.bat        ← programa portable Windows (doble clic)
├── MV_DataGovernance_API.bat    ← API REST para BI
├── run.sh                       ← Linux / macOS
├── app/app.py                   ← dashboard Streamlit (trilingüe)
├── mvdg/                        ← motor: i18n, catálogo, calidad, linaje,
│                                   glosario, políticas, perfilador, export
├── api/main.py                  ← FastAPI para BI (JSON/CSV)
├── landing/                     ← web trilingüe con video (estilo Kobra)
├── assets/video/build_video.py  ← generador del video de demo
├── packaging/                   ← mvdg_launcher.py, mvdg.spec (PyInstaller),
│                                   instalador.iss (Inno Setup), build_exe.bat
├── docs/                        ← manual + guía BI (ES/EN/PT)
└── tests/test_core.py           ← suite: motor, i18n, API, exportadores
```

## ✅ Tests

```bash
pip install -r requirements.txt pytest httpx2
pytest tests/ -v
```

---

**English:** MV Data Governance is a trilingual (ES/EN/PT) data-governance
platform — catalog, quality (6 dimensions), lineage, glossary, policies and
profiling — 100% web + desktop (portable `.bat` and Windows `.exe`, no APK),
compatible with any BI tool via files (CSV/Excel/JSON/Parquet) and a REST
API. See [`docs/MANUAL_PUESTA_EN_MARCHA.md`](docs/MANUAL_PUESTA_EN_MARCHA.md).

**Português:** O MV Data Governance é uma plataforma trilíngue (ES/EN/PT) de
governança de dados — catálogo, qualidade (6 dimensões), linhagem, glossário,
políticas e perfilamento — 100% web + desktop (`.bat` portátil e `.exe`
Windows, sem APK), compatível com qualquer ferramenta de BI via arquivos
(CSV/Excel/JSON/Parquet) e API REST. Veja
[`docs/MANUAL_PUESTA_EN_MARCHA.md`](docs/MANUAL_PUESTA_EN_MARCHA.md).
