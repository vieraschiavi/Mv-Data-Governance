# Datos de terceros incluidos en este paquete

Estos tres archivos son datasets de ejemplo **externos** (no generados por MV
Data Governance), incluidos para demostrar el gobierno de datos sobre casos
reales. Se citan aquí las fuentes y licencias, tal como corresponde.

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
