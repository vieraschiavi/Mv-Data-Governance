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
  licencia: { es: "Licencia", en: "License", pt: "Licença" },

  // --- licencia ---
  lic_plan: { es: "Plan vigente", en: "Current plan", pt: "Plano vigente" },
  lic_demo_ayuda: {
    es: "Estás en la versión demo. Si compraste, pegá abajo la clave que recibiste.",
    en: "You are on the demo version. If you purchased, paste the key you received below.",
    pt: "Você está na versão demo. Se comprou, cole abaixo a chave que recebeu." },
  lic_activa_ayuda: {
    es: "Licencia activa. Se verifica su firma cada vez que abrís el programa.",
    en: "License active. Its signature is verified every time you open the program.",
    pt: "Licença ativa. Sua assinatura é verificada sempre que você abre o programa." },
  lic_clave: { es: "Clave de licencia", en: "License key", pt: "Chave de licença" },
  lic_activar: { es: "Activar", en: "Activate", pt: "Ativar" },
  lic_quitar: { es: "Quitar licencia", en: "Remove license", pt: "Remover licença" },
  lic_ok: { es: "Licencia activada.", en: "License activated.", pt: "Licença ativada." },
  lic_email: { es: "Registrada a", en: "Registered to", pt: "Registrada para" },
  lic_vence: { es: "Vence", en: "Expires", pt: "Expira" },
  lic_funciones: { es: "Funciones que requieren licencia",
                   en: "Features that require a license",
                   pt: "Funções que exigem licença" },
  // Nombre legible de cada funcion paga. Sin esto la pantalla mostraba el
  // identificador interno ("escaneo_tenant_bi"), que es lenguaje de
  // programador: el cliente no tiene por que saber como se llama la clave.
  fn_migracion_purview: { es: "Migrar el catálogo a Microsoft Purview",
                          en: "Migrate the catalog to Microsoft Purview",
                          pt: "Migrar o catálogo para o Microsoft Purview" },
  fn_migracion_collibra: { es: "Migrar el catálogo a Collibra",
                           en: "Migrate the catalog to Collibra",
                           pt: "Migrar o catálogo para o Collibra" },
  fn_escaneo_tenant_bi: { es: "Escanear el tenant de Power BI / Tableau",
                          en: "Scan the Power BI / Tableau tenant",
                          pt: "Escanear o tenant do Power BI / Tableau" },

  // --- Las tres funciones que se cobran, ahora usables desde el programa ---
  // --- Perfilar tus propios datos (lo que la landing anuncia primero) ---
  misdatos: { es: "Mis datos", en: "My data", pt: "Meus dados" },
  md_titulo: { es: "Perfilá tus propios datos",
               en: "Profile your own data",
               pt: "Analise seus próprios dados" },
  md_bajada: { es: "Subí un CSV o Excel y obtené al instante esquema, nulos, duplicados, PII detectada y reglas sugeridas.",
               en: "Upload a CSV or Excel and instantly get schema, nulls, duplicates, detected PII and suggested rules.",
               pt: "Envie um CSV ou Excel e obtenha na hora esquema, nulos, duplicados, PII detectada e regras sugeridas." },
  md_privado: { es: "El archivo no sale de tu computadora: se lee en memoria y no se guarda en ningún lado.",
                en: "The file never leaves your computer: it is read in memory and stored nowhere.",
                pt: "O arquivo não sai do seu computador: é lido na memória e não fica guardado em lugar nenhum." },
  md_elegir: { es: "Elegir archivo", en: "Choose file", pt: "Escolher arquivo" },
  md_leyendo: { es: "Leyendo…", en: "Reading…", pt: "Lendo…" },
  md_filas: { es: "Filas", en: "Rows", pt: "Linhas" },
  md_columnas: { es: "Columnas", en: "Columns", pt: "Colunas" },
  md_duplicados: { es: "Filas duplicadas", en: "Duplicate rows", pt: "Linhas duplicadas" },
  md_nulos: { es: "Celdas vacías", en: "Empty cells", pt: "Células vazias" },
  md_pii: { es: "Columnas con PII", en: "Columns with PII", pt: "Colunas com PII" },
  md_col: { es: "Columna", en: "Column", pt: "Coluna" },
  md_tipo: { es: "Tipo", en: "Type", pt: "Tipo" },
  md_nulos_pct: { es: "% nulos", en: "% null", pt: "% nulos" },
  md_unicos: { es: "Únicos", en: "Unique", pt: "Únicos" },
  md_ejemplo: { es: "Ejemplo", en: "Sample", pt: "Exemplo" },
  md_espii: { es: "PII", en: "PII", pt: "PII" },
  md_reglas: { es: "Reglas de calidad sugeridas",
               en: "Suggested quality rules",
               pt: "Regras de qualidade sugeridas" },
  md_grande: { es: "El archivo es demasiado grande (máximo 40 MB).",
               en: "The file is too large (40 MB maximum).",
               pt: "O arquivo é grande demais (máximo 40 MB)." },
  md_malo: { es: "No se pudo leer el archivo. Se aceptan CSV y Excel.",
             en: "The file could not be read. CSV and Excel are accepted.",
             pt: "Não foi possível ler o arquivo. Aceitam-se CSV e Excel." },
  md_truncado: { es: "Se perfilaron las primeras filas del archivo, no todas.",
                 en: "Only the first rows of the file were profiled, not all.",
                 pt: "Foram analisadas apenas as primeiras linhas do arquivo." },
  md_vacio: { es: "Todavía no subiste ningún archivo.",
              en: "You have not uploaded a file yet.",
              pt: "Você ainda não enviou nenhum arquivo." },
  fn_titulo: { es: "Usar las funciones con licencia",
               en: "Use the licensed features",
               pt: "Usar as funções com licença" },
  fn_previa: { es: "Ver qué se enviaría",
               en: "Preview what would be sent",
               pt: "Ver o que seria enviado" },
  fn_aplicar: { es: "Enviar de verdad",
                en: "Send for real",
                pt: "Enviar de verdade" },
  fn_escanear: { es: "Escanear el tenant",
                 en: "Scan the tenant",
                 pt: "Escanear o tenant" },
  fn_previa_libre: { es: "La vista previa no necesita licencia: mostrá exactamente qué se enviaría antes de enviar nada.",
                     en: "The preview needs no license: see exactly what would be sent before sending anything.",
                     pt: "A pré-visualização não precisa de licença: veja exatamente o que seria enviado antes de enviar." },
  fn_requiere: { es: "Esta función necesita una licencia activa.",
                 en: "This feature needs an active license.",
                 pt: "Esta função precisa de uma licença ativa." },
  fn_sin_cred: { es: "Faltan las credenciales del conector. La vista previa funciona igual.",
                 en: "The connector credentials are missing. The preview still works.",
                 pt: "Faltam as credenciais do conector. A pré-visualização funciona mesmo assim." },
  fn_fallo: { es: "El sistema remoto no respondió.",
              en: "The remote system did not respond.",
              pt: "O sistema remoto não respondeu." },
  fn_listo: { es: "Listo.", en: "Done.", pt: "Pronto." },
  fn_no_conf: { es: "sin credenciales", en: "no credentials", pt: "sem credenciais" },
  lic_renovar: { es: "Renovar ahora", en: "Renew now", pt: "Renovar agora" },
  lic_sus: { es: "Suscripción mensual activa. El programa se renueva solo mientras esté paga.",
             en: "Monthly subscription active. The program renews itself while it is paid.",
             pt: "Assinatura mensal ativa. O programa se renova sozinho enquanto estiver paga." },
  lic_renovada: { es: "Licencia renovada.", en: "License renewed.", pt: "Licença renovada." },
  lic_sin_conexion: {
    es: "Sin conexión para renovar. Tu licencia sigue valiendo hasta su vencimiento.",
    en: "No connection to renew. Your license remains valid until it expires.",
    pt: "Sem conexão para renovar. Sua licença continua válida até vencer." },
  lic_no_autorizada: {
    es: "MercadoPago no reporta la suscripción como paga. Revisá tu medio de pago.",
    en: "MercadoPago does not report the subscription as paid. Check your payment method.",
    pt: "O MercadoPago não reporta a assinatura como paga. Verifique seu meio de pagamento." },

  lic_nota_exe: {
    es: "Tu licencia queda activada para todo el programa. Estas funciones se usan desde el panel completo de gobierno.",
    en: "Your license is activated for the whole program. These features are used from the full governance panel.",
    pt: "Sua licença fica ativada para todo o programa. Estas funções são usadas no painel completo de governança." },

  // --- Como esta instalado (mi equipo / la VM del cliente) ---
  inst_titulo: { es: "Cómo está instalado", en: "How this is installed",
    pt: "Como está instalado" },
  inst_donde: { es: "Tus datos se guardan en", en: "Your data is stored in",
    pt: "Seus dados são guardados em" },
  inst_aviso: {
    es: "Este paquete es el portable (para la VM del cliente), pero su carpeta no admite escritura, así que se está guardando en tu perfil de usuario. En una VM que se resetea al cerrar sesión, ese trabajo se pierde: mové la carpeta del programa a un lugar donde puedas escribir.",
    en: "This is the portable package (for the client's VM), but its folder is not writable, so data is going to your user profile instead. On a VM that resets at logoff, that work is lost: move the program folder somewhere you can write.",
    pt: "Este pacote é o portátil (para a VM do cliente), mas a pasta dele não permite escrita, então os dados estão indo para o seu perfil de usuário. Numa VM que se reinicia ao sair, esse trabalho se perde: mova a pasta do programa para um lugar onde você possa escrever." },

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

  // --- Ingeniería de datos (mvdg/dataeng.py vía bi_api) ---------------------
  // Solo lo que es CHROME (botones, campos, encabezados fijos). El
  // contenido — issues, roles de columna, riesgo de join, texto de fuga —
  // llega ya traducido desde bi_api, que resuelve el idioma con el mismo
  // mvdg/i18n.py que usa Streamlit. Duplicarlo acá sería mantener el mismo
  // texto en dos lugares que pueden desalinearse.
  ingenieria: { es: "Ingeniería de datos", en: "Data Engineering", pt: "Engenharia de dados" },
  de_titulo: { es: "Ingeniería de datos automática",
               en: "Automatic data engineering",
               pt: "Engenharia de dados automática" },
  de_bajada: {
    es: "Subí uno o varios archivos, o conectate a tu base de datos. En segundos: calidad por 6 dimensiones, claves y joins sugeridos, análisis temporal, detección de fuga contra un target y features listas para modelar.",
    en: "Upload one or more files, or connect to your database. In seconds: quality across 6 dimensions, suggested keys and joins, time analysis, leakage detection against a target, and model-ready features.",
    pt: "Envie um ou mais arquivos, ou conecte ao seu banco de dados. Em segundos: qualidade em 6 dimensões, chaves e joins sugeridos, análise temporal, detecção de vazamento contra um target e features prontas para modelar." },
  de_privado: {
    es: "Los archivos no salen de tu computadora. Una conexión a base de datos usa tus propias credenciales, en el momento — nunca quedan guardadas salvo que vos lo pidas.",
    en: "Files never leave your computer. A database connection uses your own credentials, on the spot — never saved unless you ask for it.",
    pt: "Os arquivos não saem do seu computador. Uma conexão de banco de dados usa suas próprias credenciais, na hora — nunca ficam guardadas a menos que você peça." },
  de_fuente: { es: "Fuente de datos", en: "Data source", pt: "Fonte de dados" },
  de_fuente_archivo: { es: "Archivo", en: "File", pt: "Arquivo" },
  de_fuente_db: { es: "Base de datos", en: "Database", pt: "Banco de dados" },
  de_elegir_archivos: { es: "Elegir archivo(s)", en: "Choose file(s)", pt: "Escolher arquivo(s)" },
  de_leyendo: { es: "Analizando…", en: "Analyzing…", pt: "Analisando…" },
  de_vacio: { es: "Todavía no analizaste ningún dato.",
              en: "You haven't analyzed any data yet.",
              pt: "Você ainda não analisou nenhum dado." },
  de_target: { es: "Columna objetivo (opcional)", en: "Target column (optional)", pt: "Coluna objetivo (opcional)" },
  de_target_ph: { es: "ej: pago, churn, resultado", en: "e.g. paid, churn, outcome", pt: "ex: pago, churn, resultado" },
  de_tiempo_col: { es: "Columna de fecha (opcional)", en: "Date column (optional)", pt: "Coluna de data (opcional)" },
  de_tiempo_col_ph: { es: "se detecta sola si no la elegís",
                      en: "auto-detected if you don't pick one",
                      pt: "detectada sozinha se você não escolher" },
  de_analizar: { es: "Analizar", en: "Analyze", pt: "Analisar" },
  de_muestreado: {
    es: "Se analizaron las primeras filas, no todas — el resultado es representativo pero no exhaustivo.",
    en: "The first rows were analyzed, not all of them — the result is representative but not exhaustive.",
    pt: "Foram analisadas as primeiras linhas, não todas — o resultado é representativo mas não exaustivo." },
  de_truncado_tablas: {
    es: "Había más tablas de las que se pueden analizar juntas; se tomaron las primeras.",
    en: "There were more tables than can be analyzed together; the first ones were used.",
    pt: "Havia mais tabelas do que dá para analisar juntas; foram usadas as primeiras." },

  de_db_motor: { es: "Motor", en: "Engine", pt: "Motor" },
  de_db_host: { es: "Servidor", en: "Host", pt: "Servidor" },
  de_db_puerto: { es: "Puerto", en: "Port", pt: "Porta" },
  de_db_base: { es: "Base de datos", en: "Database", pt: "Banco de dados" },
  de_db_usuario: { es: "Usuario", en: "User", pt: "Usuário" },
  de_db_clave: { es: "Contraseña", en: "Password", pt: "Senha" },
  de_db_ruta_sqlite: { es: "Ruta del archivo .sqlite", en: "Path to the .sqlite file", pt: "Caminho do arquivo .sqlite" },
  de_db_probar: { es: "Probar conexión", en: "Test connection", pt: "Testar conexão" },
  de_db_probando: { es: "Probando…", en: "Testing…", pt: "Testando…" },
  de_db_guardar: { es: "Guardar conexión", en: "Save connection", pt: "Salvar conexão" },
  de_db_guardada: { es: "Conexión guardada.", en: "Connection saved.", pt: "Conexão salva." },
  de_db_nombre: { es: "Nombre de la conexión", en: "Connection name", pt: "Nome da conexão" },
  de_db_guardadas: { es: "Conexiones guardadas", en: "Saved connections", pt: "Conexões salvas" },
  de_db_nueva: { es: "Nueva conexión", en: "New connection", pt: "Nova conexão" },
  de_db_borrar: { es: "Borrar", en: "Delete", pt: "Excluir" },
  de_db_tabla: { es: "Tabla", en: "Table", pt: "Tabela" },
  de_db_elegir_tablas: { es: "Elegí una o más tablas…", en: "Pick one or more tables…", pt: "Escolha uma ou mais tabelas…" },
  de_db_o_query: { es: "…o escribí una consulta (SELECT / WITH)",
                   en: "…or write a query (SELECT / WITH)",
                   pt: "…ou escreva uma consulta (SELECT / WITH)" },
  de_db_query_ph: { es: "SELECT * FROM ventas WHERE fecha >= '2026-01-01'",
                    en: "SELECT * FROM sales WHERE date >= '2026-01-01'",
                    pt: "SELECT * FROM vendas WHERE data >= '2026-01-01'" },
  de_db_limite: { es: "Límite de filas", en: "Row limit", pt: "Limite de linhas" },
  de_db_sin_tablas: { es: "La conexión funciona pero no encontramos tablas visibles.",
                      en: "The connection works but no visible tables were found.",
                      pt: "A conexão funciona mas não encontramos tabelas visíveis." },

  de_kpi_filas: { es: "Filas", en: "Rows", pt: "Linhas" },
  de_kpi_columnas: { es: "Columnas", en: "Columns", pt: "Colunas" },
  de_kpi_score: { es: "Calidad", en: "Quality", pt: "Qualidade" },
  de_kpi_criticos: { es: "Problemas críticos", en: "Critical issues", pt: "Problemas críticos" },
  de_dimensiones_titulo: { es: "Calidad por dimensión", en: "Quality by dimension", pt: "Qualidade por dimensão" },

  de_tipos_titulo: { es: "Tipos corregidos automáticamente",
                     en: "Automatically corrected types",
                     pt: "Tipos corrigidos automaticamente" },
  de_tipos_col: { es: "Columna", en: "Column", pt: "Coluna" },
  de_tipos_de: { es: "Venía como", en: "Came in as", pt: "Vinha como" },
  de_tipos_a: { es: "Convertido a", en: "Converted to", pt: "Convertido para" },

  de_perfil_titulo: { es: "Perfil de columnas", en: "Column profile", pt: "Perfil de colunas" },
  de_perfil_rol: { es: "Rol", en: "Role", pt: "Papel" },
  de_perfil_nulos: { es: "Nulos %", en: "Null %", pt: "Nulos %" },
  de_perfil_unicos: { es: "Únicos", en: "Unique", pt: "Únicos" },

  de_issues_titulo: { es: "Problemas de calidad", en: "Quality issues", pt: "Problemas de qualidade" },
  de_issues_sin: { es: "Sin problemas críticos detectados.",
                   en: "No critical issues detected.",
                   pt: "Nenhum problema crítico detectado." },
  de_issues_columna: { es: "Columna", en: "Column", pt: "Coluna" },
  de_issues_detalle: { es: "Detalle", en: "Detail", pt: "Detalhe" },
  de_issues_accion: { es: "Qué hacer", en: "What to do", pt: "O que fazer" },

  de_claves_titulo: { es: "Claves detectadas", en: "Detected keys", pt: "Chaves detectadas" },
  de_claves_ninguna: {
    es: "No se detectó clave primaria.", en: "No primary key detected.",
    pt: "Nenhuma chave primária detectada." },
  de_pk_columna: { es: "Columna", en: "Column", pt: "Coluna" },
  de_pk_tipo: { es: "Tipo", en: "Type", pt: "Tipo" },
  de_pk_confianza: { es: "Confianza", en: "Confidence", pt: "Confiança" },

  de_joins_titulo: { es: "Relaciones detectadas entre tablas",
                     en: "Detected relationships between tables",
                     pt: "Relações detectadas entre tabelas" },
  de_joins_explicacion: {
    es: "Verificá la cardinalidad antes de usarlas: un join N:N infla las filas y rompe los totales.",
    en: "Check the cardinality before using them: an N:N join inflates rows and breaks totals.",
    pt: "Verifique a cardinalidade antes de usá-las: um join N:N infla as linhas e quebra os totais." },
  de_joins_izquierda: { es: "Izquierda", en: "Left", pt: "Esquerda" },
  de_joins_derecha: { es: "Derecha", en: "Right", pt: "Direita" },
  de_joins_columna: { es: "Columna", en: "Column", pt: "Coluna" },
  de_joins_solape: { es: "Solape", en: "Overlap", pt: "Sobreposição" },
  de_joins_cardinalidad: { es: "Cardinalidad", en: "Cardinality", pt: "Cardinalidade" },
  de_joins_riesgo: { es: "Riesgo", en: "Risk", pt: "Risco" },

  de_tiempo_titulo: { es: "Análisis temporal", en: "Time analysis", pt: "Análise temporal" },
  de_tiempo_desde: { es: "Desde", en: "From", pt: "Desde" },
  de_tiempo_hasta: { es: "Hasta", en: "To", pt: "Até" },
  de_tiempo_dias_cubiertos: { es: "Días con datos", en: "Days with data", pt: "Dias com dados" },
  de_tiempo_dias_faltantes: { es: "Días faltantes", en: "Missing days", pt: "Dias faltantes" },
  de_tiempo_frescura: { es: "Frescura (días)", en: "Freshness (days)", pt: "Frescor (dias)" },
  de_tiempo_tendencia: { es: "Tendencia", en: "Trend", pt: "Tendência" },

  de_target_titulo: { es: "Variable objetivo", en: "Target variable", pt: "Variável objetivo" },
  de_target_tasa: { es: "Tasa de positivos", en: "Positive rate", pt: "Taxa de positivos" },
  de_target_balance: { es: "Balance", en: "Balance", pt: "Balanço" },
  de_fuga_titulo: { es: "Sospecha de fuga de información (leakage)",
                    en: "Suspected information leakage",
                    pt: "Suspeita de vazamento de informação" },
  de_ranking_titulo: { es: "Variables más asociadas al target",
                        en: "Variables most associated with the target",
                        pt: "Variáveis mais associadas ao target" },
  de_ranking_variable: { es: "Variable", en: "Variable", pt: "Variável" },
  de_ranking_metrica: { es: "Métrica", en: "Metric", pt: "Métrica" },
  de_ranking_valor: { es: "Valor", en: "Value", pt: "Valor" },
  de_ranking_fuerza: { es: "Fuerza", en: "Strength", pt: "Força" },

  de_features_titulo: { es: "Features generadas", en: "Generated features", pt: "Features geradas" },
  de_features_feature: { es: "Feature", en: "Feature", pt: "Feature" },
  de_features_origen: { es: "Origen", en: "Source", pt: "Origem" },
  de_features_calculo: { es: "Cálculo", en: "Calculation", pt: "Cálculo" },
  de_features_apto: { es: "Series temporales", en: "Time series", pt: "Séries temporais" },
  apto_si: { es: "Sí", en: "Yes", pt: "Sim" },
  apto_cuidado: { es: "Con cuidado", en: "With care", pt: "Com cuidado" },

  de_ddl_titulo: { es: "DDL sugerido", en: "Suggested DDL", pt: "DDL sugerido" },
};

export function t(clave, lang) {
  const e = T[clave];
  if (!e) return clave;
  return e[lang] || e.es;
}
