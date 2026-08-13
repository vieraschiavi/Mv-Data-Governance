// © 2026 Martín Viera. Todos los derechos reservados.
// Software propietario. Ver LICENSE — prohibida su redistribución.
/*
 * Textos de la interfaz de escritorio, en los tres idiomas.
 *
 * Se duplican acá y no se leen de mvdg/i18n.py a propósito: esta UI corre en
 * el navegador de Electron, y traer las claves por HTTP significaría una
 * pantalla en blanco hasta que el servidor Python conteste. Son pocas y
 * estables — los textos que SÍ cambian (nombres de columnas, dimensiones,
 * estados de reglas) vienen ya traducidos desde la API, que resuelve el
 * idioma en el motor.
 */
export const IDIOMAS = ["es", "en", "pt"];

const T = {
  // --- navegación ---
  panorama: { es: "Panorama", en: "Overview", pt: "Panorama" },
  catalogo: { es: "Catálogo", en: "Catalog", pt: "Catálogo" },
  calidad: { es: "Calidad", en: "Quality", pt: "Qualidade" },
  linaje: { es: "Linaje", en: "Lineage", pt: "Linhagem" },
  glosario: { es: "Glosario", en: "Glossary", pt: "Glossário" },
  politicas: { es: "Políticas", en: "Policies", pt: "Políticas" },

  // --- KPIs del panorama ---
  kpi_datasets: { es: "Datasets gobernados", en: "Governed datasets", pt: "Datasets governados" },
  kpi_columnas: { es: "Columnas documentadas", en: "Documented columns", pt: "Colunas documentadas" },
  kpi_calidad: { es: "Índice de calidad", en: "Quality index", pt: "Índice de qualidade" },
  kpi_reglas: { es: "Reglas aprobadas", en: "Rules passing", pt: "Regras aprovadas" },
  kpi_pii: { es: "Columnas PII protegidas", en: "Protected PII columns", pt: "Colunas PII protegidas" },
  kpi_terminos: { es: "Términos de negocio", en: "Business terms", pt: "Termos de negócio" },

  por_dimension: { es: "Calidad por dimensión", en: "Quality by dimension", pt: "Qualidade por dimensão" },
  por_dataset: { es: "Calidad por dataset", en: "Quality by dataset", pt: "Qualidade por dataset" },

  // --- estados de la app ---
  cargando: { es: "Cargando el gobierno de datos…", en: "Loading data governance…", pt: "Carregando a governança…" },
  sin_datos: { es: "Sin datos para mostrar.", en: "No data to show.", pt: "Sem dados para exibir." },
  error_titulo: { es: "No se pudo conectar con el motor", en: "Could not reach the engine", pt: "Não foi possível conectar ao motor" },
  error_ayuda: {
    es: "El programa no logró hablar con su propio servidor local. Cerrá y volvé a abrir; si sigue, mandanos el detalle de abajo.",
    en: "The program could not talk to its own local server. Close and reopen; if it persists, send us the detail below.",
    pt: "O programa não conseguiu falar com seu servidor local. Feche e reabra; se persistir, envie o detalhe abaixo.",
  },
  reintentar: { es: "Reintentar", en: "Retry", pt: "Tentar de novo" },
  buscar: { es: "Buscar…", en: "Search…", pt: "Buscar…" },
  filas: { es: "filas", en: "rows", pt: "linhas" },

  // --- pie ---
  local: {
    es: "100% local — ningún dato sale de este equipo.",
    en: "100% local — no data leaves this machine.",
    pt: "100% local — nenhum dado sai deste equipamento.",
  },
  // --- dimensiones y estados: la API los manda como clave cruda
  //     ("completeness", "pass"), no traducidos. Se resuelven acá.
  dim_completeness: { es: "Completitud", en: "Completeness", pt: "Completude" },
  dim_uniqueness: { es: "Unicidad", en: "Uniqueness", pt: "Unicidade" },
  dim_validity: { es: "Validez", en: "Validity", pt: "Validade" },
  dim_consistency: { es: "Consistencia", en: "Consistency", pt: "Consistência" },
  dim_timeliness: { es: "Puntualidad", en: "Timeliness", pt: "Pontualidade" },
  dim_accuracy: { es: "Exactitud", en: "Accuracy", pt: "Exatidão" },
  est_pass: { es: "Aprobada", en: "Pass", pt: "Aprovada" },
  est_warn: { es: "Alerta", en: "Warning", pt: "Alerta" },
  est_fail: { es: "Falla", en: "Fail", pt: "Falha" },

  // --- encabezados de tabla (las claves de columna vienen en ingles y
  //     estables en los 3 idiomas; lo que se traduce es el contenido) ---
  col_dataset: { es: "Dataset", en: "Dataset", pt: "Dataset" },
  col_domain: { es: "Dominio", en: "Domain", pt: "Domínio" },
  col_description: { es: "Descripción", en: "Description", pt: "Descrição" },
  col_owner: { es: "Dueño", en: "Owner", pt: "Dono" },
  col_steward: { es: "Steward", en: "Steward", pt: "Steward" },
  col_classification: { es: "Clasificación", en: "Classification", pt: "Classificação" },
  col_rows: { es: "Filas", en: "Rows", pt: "Linhas" },
  col_columns: { es: "Columnas", en: "Columns", pt: "Colunas" },
  col_column: { es: "Columna", en: "Column", pt: "Coluna" },
  col_type: { es: "Tipo", en: "Type", pt: "Tipo" },
  col_pii: { es: "PII", en: "PII", pt: "PII" },
  col_term: { es: "Término", en: "Term", pt: "Termo" },
  col_definition: { es: "Definición", en: "Definition", pt: "Definição" },
  col_rule: { es: "Regla", en: "Rule", pt: "Regra" },
  col_dimension: { es: "Dimensión", en: "Dimension", pt: "Dimensão" },
  col_score: { es: "Puntaje", en: "Score", pt: "Pontuação" },
  col_threshold: { es: "Umbral", en: "Threshold", pt: "Limite" },
  col_status: { es: "Estado", en: "Status", pt: "Status" },
  col_affected: { es: "Filas afectadas", en: "Affected rows", pt: "Linhas afetadas" },
  col_source: { es: "Origen", en: "Source", pt: "Origem" },
  col_target: { es: "Destino", en: "Target", pt: "Destino" },
  col_layer: { es: "Capa", en: "Layer", pt: "Camada" },
  col_policy: { es: "Política", en: "Policy", pt: "Política" },
  col_category: { es: "Categoría", en: "Category", pt: "Categoria" },
  col_evidence: { es: "Evidencia", en: "Evidence", pt: "Evidência" },
  col_linked: { es: "Datasets vinculados", en: "Linked datasets", pt: "Datasets vinculados" },
};

export function t(clave, lang) {
  const e = T[clave];
  if (!e) return clave;
  return e[lang] || e.es;
}
