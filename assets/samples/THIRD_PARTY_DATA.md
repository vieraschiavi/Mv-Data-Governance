# Datos de terceros incluidos en este paquete

Estos archivos son datasets/modelos de ejemplo **externos** (no generados por
MV Data Governance), incluidos para demostrar el gobierno de datos sobre
casos reales. Se citan aquí las fuentes y licencias, tal como corresponde.

## rotulado_de_alimentos_2026.csv

- **Qué es:** control bromatológico real de productos alimenticios (Uruguay, 2026).
- **Fuente:** datos abiertos de gobierno (control bromatológico de alimentos,
  Uruguay), con referencias al Reglamento Bromatológico Nacional (RUNAEV,
  Decreto 466/009) presentes en los propios datos.
- **Uso:** incluido como dataset de ejemplo educativo/demostrativo dentro del
  programa (pestaña "Mis datos").

## dirty_cafe_sales.csv

- **Qué es:** 10.000 transacciones sintéticas de una cafetería, con errores
  inyectados a propósito (nulos, `"ERROR"`, `"UNKNOWN"`) para practicar
  limpieza y gobierno de datos.
- **Autor:** Ahmed Mohamed (Kaggle, usuario `ahmedmohamed2003`).
- **Fuente:** <https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training>
- **Licencia:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
  — se puede usar, compartir y adaptar dando el crédito correspondiente. Esta
  nota es esa atribución.

## bank_marketing_uci.csv

- **Qué es:** 4.521 contactos reales de una campaña de marketing telefónico
  de un banco portugués (2014), para ofrecer un depósito a plazo.
- **Autores:** S. Moro, P. Rita, P. Cortez.
- **Fuente:** <https://archive.ics.uci.edu/dataset/222/bank+marketing> (UCI
  Machine Learning Repository).
- **Licencia:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) —
  se puede usar, compartir y adaptar (incluso con fines comerciales) dando
  el crédito correspondiente. Esta nota es esa atribución.
- **Nota de privacidad:** el dataset está anonimizado en el origen (sin
  nombre, número de cuenta ni otro identificador directo). Aun así, se
  clasifica **Confidencial** dentro del catálogo de ejemplo del programa,
  porque combina datos demográficos y financieros a nivel de persona —
  el criterio correcto para un banco real, más allá de que no dispare el
  detector heurístico de PII.

Ninguno de los tres contiene datos personales identificables: el primero es
información de producto/inspección (no de personas), el segundo es
enteramente sintético, y el tercero está anonimizado en su fuente original.

## powerbi/AdventureWorksDemo/ (modelo Power BI real, formato .pbip/TMDL)

- **Qué es:** un modelo semántico real de Power BI (10 tablas, 17 medidas
  DAX documentadas, 10 relaciones) — ventas, metas y desempeño de vendedores
  de una compañía ficticia estilo Adventure Works, con los datos de ejemplo
  **embebidos en la propia consulta M** (`Table.FromRecords`, sin conexión a
  ninguna base real).
- **Autor:** Samuel Tauil.
- **Fuente:** <https://github.com/samueltauil/powerbi-git-demo>
- **Licencia:** [MIT](https://opensource.org/licenses/MIT) — se puede usar,
  copiar, modificar y redistribuir libremente, dando el crédito
  correspondiente. Esta nota es esa atribución; el texto completo de la
  licencia original queda copiado en
  `AdventureWorksDemo/LICENSE_UPSTREAM.txt`.
- **Cambios respecto del original:** se conservaron sin modificar todas las
  tablas, columnas, medidas (DAX), relaciones y expresiones M. Se renombró
  la carpeta del modelo y el `displayName` (de "My new report" a "Adventure
  Works Demo") por claridad, y se agregó una carpeta `.Report` vacía
  (mismo nombre base) solo para que el conector detecte un reporte asociado
  — el reporte visual original no se incluyó (no hace falta para gobernar
  metadata; reduce el tamaño del paquete).
- **Uso:** ejemplo real dentro de la pestaña **🔷 Power BI → 🧪 Ejemplo**, y
  base del ejemplo ilustrativo de "tenant multinacional" (ver más abajo).
  Este mismo archivo sirvió además para encontrar y corregir dos bugs reales
  del parser TMDL (`sourceLineageTag`/`dataCategory` colándose en el DAX, y
  las descripciones nativas `///` de TMDL no capturadas) — quedaron como
  test de regresión en `tests/test_core.py`.

## Ejemplo ilustrativo: "tenant multinacional" (Power BI/Fabric)

La pestaña **🔷 Power BI → 🧪 Ejemplo → Tenant multinacional (ilustrativo)**
muestra cómo se ve `ingest_tenant()` a escala: el modelo real de arriba
(Adventure Works Demo) **replicado y re-etiquetado** en varios workspaces
simulados (ej. "Ventas EMEA", "Ventas LATAM", "Ventas APAC", "Finanzas
Corporativas") para representar una empresa multinacional con cientos de
reportes distribuidos por regiones. **Es explícitamente ilustrativo, no un
escaneo real de un tenant** — no reemplaza al modo "🌐 Tenant completo"
(que sí escanea de verdad, vía la Scanner API, con tus propias credenciales).
Se etiqueta como tal en la interfaz y en `source` de cada modelo generado.

## Ejemplo Tableau (originalmente escrito, formato .twb)

- **Qué es:** un archivo `.twb` (XML de Tableau) escrito originalmente para
  este proyecto — un datasource de ventas con columnas, 3 campos calculados
  (con fórmulas realistas al estilo del dataset público "Sample - Superstore"
  de Tableau) y su tabla de origen SQL.
- **Por qué no se usó un `.twb`/`.twbx` real descargado de GitHub:** se
  buscaron ejemplos públicos (ver PR de esta funcionalidad), pero los
  repositorios encontrados no declaraban una licencia explícita — sin
  licencia clara, redistribuirlos dentro de este paquete sería un riesgo
  legal innecesario. Se optó por escribir un archivo equivalente,
  estructuralmente realista, 100% propio.
- **Uso:** ejemplo dentro de la pestaña **📊 Tableau → 🧪 Ejemplo**, y para
  probar el parser offline `read_twb()` (mismo rol que `.pbip` para Power BI).
