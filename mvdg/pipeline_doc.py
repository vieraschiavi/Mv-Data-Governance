# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""
MV Data Governance · Qué se le hizo al dato, en orden, y por qué.

El problema que cierra
──────────────────────
El programa hace doce cosas con los datos de un cliente —los lee, los perfila,
les inventa reglas, las corre, arma catálogo, diccionario, linaje, glosario,
políticas y los publica a BI— y hasta acá cada una de esas cosas se veía en su
propia pestaña, como un resultado suelto. Nadie podía leer el RECORRIDO.

Eso rompe en las dos puntas y por motivos opuestos:

  · Un programador que va a mantener esto necesita saber en qué orden pasa
    cada cosa, qué módulo la hace y qué recibe de la etapa anterior. Sin eso
    tiene que leer el código para reconstruirlo.
  · Un gerente que firma la compra necesita entender qué se hizo y qué cambia
    en su empresa. "Se evaluaron 17 reglas de calidad" no le dice nada si no
    sabe qué es una regla de calidad ni qué pasa si falla.

Por eso cada etapa se cuenta DOS VECES: en técnico y en criollo. No es el
mismo texto simplificado — son dos explicaciones distintas del mismo hecho,
escritas para dos lectores que necesitan cosas diferentes.

Qué NO es
─────────
No es un folleto. La ``evidencia`` de cada etapa se mide sobre la corrida que
el usuario tiene delante: las filas que cargó, las reglas que fallaron, las
columnas con PII que se encontraron. Un documento que dijera siempre lo mismo
sería más fácil de escribir y no serviría para nada — el gerente lo lee para
saber qué pasó con SUS datos, no qué hace el producto en general.

Se exporta a HTML, Word y PDF desde ``mvdg.doc_export``.
"""
from __future__ import annotations


def _tr(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


# ---------------------------------------------------------------------------
# Las etapas, en el orden REAL en que ocurren. El número no es decorativo:
# cada etapa consume lo que produjo la anterior, y así se lee el pipeline.
#
# Campos de cada una:
#   criollo  → para quien decide la compra. Sin jerga, con la consecuencia.
#   tecnico  → para quien mantiene el código. Qué hace y con qué.
#   porque   → por qué existe la etapa (qué pasaría sin ella).
#   impacto  → qué cambia aguas abajo, o sea qué depende de esto.
#   modulo   → dónde vive, para poder abrirlo.
# ---------------------------------------------------------------------------
ETAPAS: list[dict] = [
    {
        "key": "ingesta", "n": 1,
        "titulo": _tr("Ingesta: leer el dato como está",
                      "Ingestion: read the data as it is",
                      "Ingestão: ler o dado como está"),
        "criollo": _tr(
            "Se abre tu archivo o tu base tal cual está hoy, sin pedirte que lo "
            "arregles antes. Si el Excel vino con punto y coma, con acentos "
            "raros o con la primera fila corrida, el programa lo detecta solo.",
            "Your file or database is opened exactly as it is today, without "
            "asking you to fix it first. If the Excel came with semicolons, odd "
            "accents or a shifted first row, the program figures it out.",
            "Seu arquivo ou banco é aberto exatamente como está hoje, sem pedir "
            "que você conserte antes. Se o Excel veio com ponto e vírgula, "
            "acentos estranhos ou a primeira linha deslocada, o programa "
            "descobre sozinho."),
        "tecnico": _tr(
            "CSV/TSV/Excel/Parquet/JSON/JSONL/SQLite por archivo, y nueve "
            "motores SQL por conexión (PostgreSQL, SQL Server, MySQL, Oracle, "
            "SQLite, Synapse, Snowflake, BigQuery, Databricks). El separador y "
            "la codificación se infieren probando combinaciones; SQL se lee con "
            "cursor del lado del servidor (chunksize) para no materializar la "
            "tabla entera en memoria.",
            "CSV/TSV/Excel/Parquet/JSON/JSONL/SQLite by file, and nine SQL "
            "engines by connection (PostgreSQL, SQL Server, MySQL, Oracle, "
            "SQLite, Synapse, Snowflake, BigQuery, Databricks). Separator and "
            "encoding are inferred by trying combinations; SQL is read with a "
            "server-side cursor (chunksize) so the whole table is never "
            "materialised in memory.",
            "CSV/TSV/Excel/Parquet/JSON/JSONL/SQLite por arquivo, e nove "
            "motores SQL por conexão (PostgreSQL, SQL Server, MySQL, Oracle, "
            "SQLite, Synapse, Snowflake, BigQuery, Databricks). O separador e a "
            "codificação são inferidos testando combinações; SQL é lido com "
            "cursor do lado do servidor (chunksize) para não materializar a "
            "tabela inteira na memória."),
        "porque": _tr(
            "Si el programa exigiera datos limpios para empezar, no serviría: "
            "los datos sucios son justamente el problema que se viene a "
            "resolver.",
            "If the program demanded clean data to start, it would be useless: "
            "dirty data is precisely the problem it exists to solve.",
            "Se o programa exigisse dados limpos para começar, não serviria: "
            "dados sujos são justamente o problema que ele vem resolver."),
        "impacto": _tr(
            "Todo lo que sigue trabaja sobre lo que se leyó acá. Un separador "
            "mal detectado daría una sola columna con todo adentro y un "
            "diagnóstico que no dice nada.",
            "Everything that follows works on what was read here. A wrongly "
            "detected separator would give a single column with everything "
            "inside and a diagnosis that says nothing.",
            "Tudo o que segue trabalha sobre o que foi lido aqui. Um separador "
            "mal detectado daria uma única coluna com tudo dentro e um "
            "diagnóstico que não diz nada."),
        "modulo": "mvdg/dataeng.py · mvdg/connectors.py",
    },
    {
        "key": "perfilado", "n": 2,
        "titulo": _tr("Perfilado: qué hay realmente adentro",
                      "Profiling: what is actually inside",
                      "Perfilamento: o que há realmente dentro"),
        "criollo": _tr(
            "Columna por columna: qué tipo de dato es, cuántos huecos tiene, "
            "cuántos valores distintos, y si parece contener datos personales "
            "(mails, documentos, teléfonos). Es la radiografía.",
            "Column by column: what type it holds, how many gaps it has, how "
            "many distinct values, and whether it looks like personal data "
            "(emails, ID numbers, phones). It is the X-ray.",
            "Coluna por coluna: que tipo de dado é, quantos buracos tem, "
            "quantos valores distintos, e se parece conter dados pessoais "
            "(e-mails, documentos, telefones). É a radiografia."),
        "tecnico": _tr(
            "Inferencia de dtype, porcentaje de nulos, cardinalidad, muestra de "
            "valores y detección heurística de PII por nombre de columna y por "
            "forma del contenido. Alimenta el resumen (filas, columnas, "
            "duplicados exactos, % de celdas nulas).",
            "dtype inference, null percentage, cardinality, value sample and "
            "heuristic PII detection by column name and content shape. Feeds "
            "the summary (rows, columns, exact duplicates, % null cells).",
            "Inferência de dtype, percentual de nulos, cardinalidade, amostra "
            "de valores e detecção heurística de PII por nome de coluna e "
            "formato do conteúdo. Alimenta o resumo (linhas, colunas, "
            "duplicados exatos, % de células nulas)."),
        "porque": _tr(
            "No se puede gobernar lo que no se conoce. Y la PII hay que "
            "encontrarla antes de publicar nada a BI, no después.",
            "You cannot govern what you do not know. And PII must be found "
            "before publishing anything to BI, not after.",
            "Não se pode governar o que não se conhece. E a PII precisa ser "
            "encontrada antes de publicar algo no BI, não depois."),
        "impacto": _tr(
            "De acá salen las reglas de calidad (etapa 4) y la clasificación "
            "del dataset (etapa 3). Si el perfilado no marca una columna como "
            "personal, la política de clasificación no la va a exigir.",
            "The quality rules (stage 4) and the dataset classification (stage "
            "3) come from here. If profiling does not flag a column as "
            "personal, the classification policy will not require it.",
            "Daqui saem as regras de qualidade (etapa 4) e a classificação do "
            "dataset (etapa 3). Se o perfilamento não marcar uma coluna como "
            "pessoal, a política de classificação não vai exigi-la."),
        "modulo": "mvdg/profiler.py",
    },
    {
        "key": "catalogo", "n": 3,
        "titulo": _tr("Catálogo: la ficha del dataset",
                      "Catalog: the dataset record",
                      "Catálogo: a ficha do dataset"),
        "criollo": _tr(
            "Cada conjunto de datos entra a una lista única con su dueño, su "
            "responsable técnico, su clasificación y de dónde viene. Es la "
            "diferencia entre «tenemos datos por ahí» y «sabemos qué tenemos y "
            "de quién es».",
            "Every dataset joins a single list with its owner, its technical "
            "steward, its classification and where it comes from. It is the "
            "difference between \"we have data somewhere\" and \"we know what we "
            "have and whose it is\".",
            "Cada conjunto de dados entra numa lista única com seu dono, seu "
            "responsável técnico, sua classificação e de onde vem. É a "
            "diferença entre \"temos dados por aí\" e \"sabemos o que temos e de "
            "quem é\"."),
        "tecnico": _tr(
            "Una fila por dataset con dataset/domain/description/owner/steward/"
            "classification/source/refresh/rows/columns/last_updated. La "
            "clasificación es un token literal (PII, Confidencial, Interna) que "
            "el motor de políticas compara: no es texto para mostrar.",
            "One row per dataset with dataset/domain/description/owner/steward/"
            "classification/source/refresh/rows/columns/last_updated. The "
            "classification is a literal token (PII, Confidencial, Interna) that "
            "the policy engine compares against: it is not display text.",
            "Uma linha por dataset com dataset/domain/description/owner/steward/"
            "classification/source/refresh/rows/columns/last_updated. A "
            "classificação é um token literal (PII, Confidencial, Interna) que o "
            "motor de políticas compara: não é texto para exibir."),
        "porque": _tr(
            "Sin dueño asignado no hay a quién reclamarle cuando un dato está "
            "mal. El catálogo es lo que convierte un problema de datos en la "
            "tarea de alguien.",
            "With no assigned owner there is nobody to hold responsible when "
            "data is wrong. The catalog is what turns a data problem into "
            "somebody's task.",
            "Sem dono atribuído não há a quem cobrar quando um dado está "
            "errado. O catálogo é o que transforma um problema de dados na "
            "tarefa de alguém."),
        "impacto": _tr(
            "Las políticas (etapa 10) se evalúan contra esta ficha. Un dataset "
            "sin dueño hace que la política de responsabilidad pase a «parcial» "
            "y diga cuál falta.",
            "Policies (stage 10) are evaluated against this record. A dataset "
            "with no owner turns the accountability policy to \"partial\" and it "
            "names which one is missing.",
            "As políticas (etapa 10) são avaliadas contra esta ficha. Um "
            "dataset sem dono faz a política de responsabilidade virar "
            "\"parcial\" e dizer qual falta."),
        "modulo": "mvdg/catalog.py · mvdg/scope.py",
    },
    {
        "key": "diccionario", "n": 4,
        "titulo": _tr("Diccionario: qué significa cada columna",
                      "Dictionary: what each column means",
                      "Dicionário: o que significa cada coluna"),
        "criollo": _tr(
            "Una fila por columna, con su tipo, si tiene datos personales y qué "
            "término del negocio representa. Es lo que evita que «monto» "
            "signifique una cosa en Ventas y otra en Finanzas.",
            "One row per column, with its type, whether it holds personal data "
            "and which business term it represents. It is what stops \"amount\" "
            "meaning one thing in Sales and another in Finance.",
            "Uma linha por coluna, com seu tipo, se tem dados pessoais e que "
            "termo do negócio representa. É o que evita que \"valor\" signifique "
            "uma coisa em Vendas e outra em Finanças."),
        "tecnico": _tr(
            "dataset/column/type/pii/business_term/description. El vínculo "
            "business_term es el que une el diccionario con el glosario (etapa "
            "9) y el que hace verificable la política de semántica.",
            "dataset/column/type/pii/business_term/description. The "
            "business_term link is what joins the dictionary to the glossary "
            "(stage 9) and what makes the semantics policy verifiable.",
            "dataset/column/type/pii/business_term/description. O vínculo "
            "business_term é o que une o dicionário ao glossário (etapa 9) e o "
            "que torna verificável a política de semântica."),
        "porque": _tr(
            "Dos áreas que le dicen distinto a lo mismo toman decisiones "
            "distintas sobre el mismo número, y ninguna se entera.",
            "Two departments naming the same thing differently make different "
            "decisions about the same number, and neither notices.",
            "Duas áreas que chamam a mesma coisa de formas diferentes tomam "
            "decisões diferentes sobre o mesmo número, e nenhuma percebe."),
        "impacto": _tr(
            "Es lo que se exporta a Power BI y Tableau como documentación del "
            "modelo, y lo que migra a Purview o Collibra si la empresa ya usa "
            "uno de esos.",
            "This is what gets exported to Power BI and Tableau as model "
            "documentation, and what migrates to Purview or Collibra if the "
            "company already uses one.",
            "É o que se exporta para Power BI e Tableau como documentação do "
            "modelo, e o que migra para Purview ou Collibra se a empresa já usa "
            "um deles."),
        "modulo": "mvdg/catalog.py · mvdg/scope.py",
    },
    {
        "key": "reglas", "n": 5,
        "titulo": _tr("Reglas de calidad: se generan y se CORREN",
                      "Quality rules: generated and actually RUN",
                      "Regras de qualidade: são geradas e EXECUTADAS"),
        "criollo": _tr(
            "El programa mira tu archivo, propone reglas que tienen sentido "
            "para él —esta columna no debería tener huecos, esta otra no "
            "debería repetirse— y después las corre de verdad contra los datos. "
            "No es una lista de buenas intenciones: cada regla da un número.",
            "The program looks at your file, proposes rules that make sense for "
            "it —this column should have no gaps, this one should not repeat— "
            "and then actually runs them against the data. It is not a list of "
            "good intentions: every rule returns a number.",
            "O programa olha seu arquivo, propõe regras que fazem sentido para "
            "ele —esta coluna não deveria ter buracos, esta outra não deveria "
            "repetir— e depois as executa de verdade contra os dados. Não é uma "
            "lista de boas intenções: cada regra dá um número."),
        "tecnico": _tr(
            "auto_rules.build_rules() deriva reglas de completitud y unicidad "
            "del propio archivo (más duplicados de fila) y evaluate_rules() las "
            "corre devolviendo score, umbral, estado (pass/warn/fail) y filas "
            "afectadas. Las otras cuatro dimensiones DAMA dependen de reglas de "
            "negocio que no se pueden adivinar de un archivo cualquiera, así que "
            "no se fingen.",
            "auto_rules.build_rules() derives completeness and uniqueness rules "
            "from the file itself (plus row duplicates) and evaluate_rules() "
            "runs them, returning score, threshold, status (pass/warn/fail) and "
            "affected rows. The other four DAMA dimensions depend on business "
            "rules that cannot be guessed from an arbitrary file, so they are "
            "not faked.",
            "auto_rules.build_rules() deriva regras de completude e unicidade do "
            "próprio arquivo (mais duplicados de linha) e evaluate_rules() as "
            "executa, devolvendo score, limite, estado (pass/warn/fail) e linhas "
            "afetadas. As outras quatro dimensões DAMA dependem de regras de "
            "negócio que não dá para adivinhar de um arquivo qualquer, então não "
            "são fingidas."),
        "porque": _tr(
            "Un informe de calidad que no corrió contra los datos es una "
            "opinión. El valor está en el número y en las filas exactas que "
            "fallan.",
            "A quality report that never ran against the data is an opinion. "
            "The value is in the number and in the exact rows that fail.",
            "Um relatório de qualidade que não rodou contra os dados é uma "
            "opinião. O valor está no número e nas linhas exatas que falham."),
        "impacto": _tr(
            "De acá sale el índice de calidad (etapa 6), las alertas asignadas "
            "a un responsable, y la evidencia de las políticas.",
            "The quality index (stage 6), the alerts assigned to an owner and "
            "the policy evidence all come from here.",
            "Daqui saem o índice de qualidade (etapa 6), os alertas atribuídos "
            "a um responsável e a evidência das políticas."),
        "modulo": "mvdg/auto_rules.py · mvdg/quality.py",
    },
    {
        "key": "indice", "n": 6,
        "titulo": _tr("Índice de calidad: un número que se puede seguir",
                      "Quality index: a number you can track",
                      "Índice de qualidade: um número que dá para acompanhar"),
        "criollo": _tr(
            "Todas las reglas se resumen en un puntaje de 0 a 100, y se abre por "
            "dataset y por dimensión. Es el número que se mira en la reunión "
            "mensual para saber si el trabajo sirvió.",
            "All rules collapse into a 0-100 score, broken down by dataset and "
            "by dimension. It is the number you look at in the monthly meeting "
            "to know whether the work paid off.",
            "Todas as regras se resumem num placar de 0 a 100, aberto por "
            "dataset e por dimensão. É o número que se olha na reunião mensal "
            "para saber se o trabalho valeu."),
        "tecnico": _tr(
            "overall_index() promedia los scores; quality_by_dataset() y "
            "quality_by_dimension() los agregan. El umbral por regla decide el "
            "estado, no el promedio: una regla crítica en falla no se compensa "
            "con nueve que pasan.",
            "overall_index() averages the scores; quality_by_dataset() and "
            "quality_by_dimension() aggregate them. The per-rule threshold "
            "decides the status, not the average: one critical failing rule is "
            "not offset by nine passing ones.",
            "overall_index() faz a média dos scores; quality_by_dataset() e "
            "quality_by_dimension() os agregam. O limite por regra decide o "
            "estado, não a média: uma regra crítica em falha não é compensada "
            "por nove que passam."),
        "porque": _tr(
            "Sin un número comparable en el tiempo no hay forma de demostrar "
            "que la situación mejoró — ni de detectar que empeoró.",
            "Without a number comparable over time there is no way to show the "
            "situation improved — nor to detect that it got worse.",
            "Sem um número comparável no tempo não há como demonstrar que a "
            "situação melhorou — nem detectar que piorou."),
        "impacto": _tr(
            "Es el KPI que se publica a BI y el que compara el antes y el "
            "después del proyecto de gobierno.",
            "It is the KPI published to BI and the one comparing the before and "
            "after of the governance project.",
            "É o KPI publicado no BI e o que compara o antes e o depois do "
            "projeto de governança."),
        "modulo": "mvdg/quality.py",
    },
    {
        "key": "features", "n": 7,
        "titulo": _tr("Ingeniería de datos: columnas nuevas, con su porqué",
                      "Data engineering: new columns, each with its reason",
                      "Engenharia de dados: colunas novas, com seu porquê"),
        "criollo": _tr(
            "A partir de lo que ya hay se calculan columnas derivadas útiles "
            "—el mes de una fecha, el ratio entre dos importes, el valor del "
            "mes anterior— y cada una viene con la explicación de cómo se "
            "calculó. También avisa cuándo una columna es «demasiado buena» "
            "para predecir algo, que casi siempre significa que contiene la "
            "respuesta.",
            "From what is already there, useful derived columns are computed "
            "—the month of a date, the ratio between two amounts, last month's "
            "value— each with an explanation of how it was calculated. It also "
            "warns when a column is \"too good\" at predicting something, which "
            "almost always means it contains the answer.",
            "A partir do que já existe são calculadas colunas derivadas úteis "
            "—o mês de uma data, a razão entre dois valores, o valor do mês "
            "anterior— cada uma com a explicação de como foi calculada. Também "
            "avisa quando uma coluna é \"boa demais\" para prever algo, o que "
            "quase sempre significa que contém a resposta."),
        "tecnico": _tr(
            "Features de fecha (partes, seno/coseno de mes para ciclicidad), "
            "numéricas, ratios monetarios, categóricas y de texto, y de serie "
            "temporal (lags y medias móviles por grupo). Cada feature guarda un "
            "código estable y sus parámetros; la etiqueta legible se arma "
            "traduciendo ese código, así el motor no depende del idioma. "
            "Detección de fuga (leakage) por AUC contra el target.",
            "Date features (parts, sine/cosine of month for cyclicality), "
            "numeric, monetary ratios, categorical and text, and time-series "
            "(lags and moving averages per group). Each feature stores a stable "
            "code and its parameters; the readable label is built by translating "
            "that code, so the engine is language-independent. Leakage detection "
            "by AUC against the target.",
            "Features de data (partes, seno/cosseno de mês para ciclicidade), "
            "numéricas, razões monetárias, categóricas e de texto, e de série "
            "temporal (lags e médias móveis por grupo). Cada feature guarda um "
            "código estável e seus parâmetros; o rótulo legível é montado "
            "traduzindo esse código, então o motor não depende do idioma. "
            "Detecção de vazamento (leakage) por AUC contra o target."),
        "porque": _tr(
            "Una columna derivada sin explicación es magia, y nadie firma un "
            "modelo basado en magia. Y una fuga no detectada produce un modelo "
            "que parece excelente y falla el día que se usa.",
            "A derived column with no explanation is magic, and nobody signs off "
            "a model based on magic. And undetected leakage produces a model "
            "that looks excellent and fails the day it is used.",
            "Uma coluna derivada sem explicação é mágica, e ninguém assina um "
            "modelo baseado em mágica. E um vazamento não detectado produz um "
            "modelo que parece excelente e falha no dia em que é usado."),
        "impacto": _tr(
            "Es lo que se lleva el equipo de datos para modelar, y el DDL que "
            "se genera para crear esas columnas en la base.",
            "This is what the data team takes to model, and the DDL generated to "
            "create those columns in the database.",
            "É o que a equipe de dados leva para modelar, e o DDL gerado para "
            "criar essas colunas no banco."),
        "modulo": "mvdg/dataeng.py",
    },
    {
        "key": "mdm", "n": 8,
        "titulo": _tr("MDM: encontrar al mismo cliente escrito de cinco formas",
                      "MDM: finding the same customer written five ways",
                      "MDM: encontrar o mesmo cliente escrito de cinco formas"),
        "criollo": _tr(
            "Busca registros que son la misma persona o la misma empresa aunque "
            "estén escritos distinto, y arma una ficha única con lo mejor de "
            "cada uno. Es lo que evita mandarle tres veces la misma factura al "
            "mismo cliente.",
            "It finds records that are the same person or company even when "
            "written differently, and builds a single record with the best of "
            "each. It is what stops you invoicing the same customer three times.",
            "Busca registros que são a mesma pessoa ou a mesma empresa mesmo "
            "escritos de formas diferentes, e monta uma ficha única com o melhor "
            "de cada. É o que evita mandar três vezes a mesma fatura ao mesmo "
            "cliente."),
        "tecnico": _tr(
            "Agrupamiento por similitud con bloqueo opcional por columna para "
            "acotar las comparaciones, puntaje de confianza por cluster y "
            "construcción de golden record. El bloqueo importa: sin él la "
            "comparación es cuadrática y no termina sobre una tabla grande.",
            "Similarity clustering with optional blocking by column to bound the "
            "comparisons, per-cluster confidence score and golden-record "
            "construction. Blocking matters: without it the comparison is "
            "quadratic and never finishes on a large table.",
            "Agrupamento por similaridade com bloqueio opcional por coluna para "
            "limitar as comparações, pontuação de confiança por cluster e "
            "construção do golden record. O bloqueio importa: sem ele a "
            "comparação é quadrática e não termina numa tabela grande."),
        "porque": _tr(
            "Los duplicados no se ven en un promedio: inflan los conteos, "
            "reparten el historial de un cliente en varios y arruinan cualquier "
            "análisis por cliente.",
            "Duplicates do not show up in an average: they inflate counts, split "
            "one customer's history across several and ruin any per-customer "
            "analysis.",
            "Duplicados não aparecem numa média: inflam contagens, dividem o "
            "histórico de um cliente em vários e arruínam qualquer análise por "
            "cliente."),
        "impacto": _tr(
            "El golden record es el que debería ir al CRM y al BI; los clusters "
            "detectados son la lista de trabajo para el steward.",
            "The golden record is what should go to the CRM and to BI; the "
            "detected clusters are the steward's worklist.",
            "O golden record é o que deveria ir ao CRM e ao BI; os clusters "
            "detectados são a lista de trabalho do steward."),
        "modulo": "mvdg/mdm.py",
    },
    {
        "key": "linaje", "n": 9,
        "titulo": _tr("Linaje: de dónde salió cada número",
                      "Lineage: where each number came from",
                      "Linhagem: de onde saiu cada número"),
        "criollo": _tr(
            "El mapa que muestra el recorrido del dato desde su origen hasta el "
            "tablero donde alguien lo mira. Sirve para dos preguntas que "
            "aparecen siempre: «¿de dónde sale este número?» y «si cambio esto, "
            "¿qué se rompe?».",
            "The map showing the data's journey from its origin to the dashboard "
            "where somebody looks at it. It answers the two questions that "
            "always come up: \"where does this number come from?\" and \"if I "
            "change this, what breaks?\".",
            "O mapa que mostra o percurso do dado desde a origem até o painel "
            "onde alguém o olha. Serve para duas perguntas que sempre aparecem: "
            "\"de onde sai este número?\" e \"se eu mudar isto, o que quebra?\"."),
        "tecnico": _tr(
            "Grafo dirigido de cinco capas (source/raw/curated/mart/bi) como "
            "nodos y aristas, y aplanado a tabla para exportar. Para un archivo "
            "cargado el linaje es el honesto —origen → dataset → BI—: no se "
            "inventan capas raw/mart que no existen. Desde un modelo de Power BI "
            "se agrega el tramo SQL → tabla → dataset → reporte leyendo la "
            "expresión M de cada partición.",
            "Directed five-layer graph (source/raw/curated/mart/bi) as nodes and "
            "edges, flattened to a table for export. For an uploaded file the "
            "lineage is the honest one —origin → dataset → BI—: raw/mart layers "
            "that do not exist are not invented. From a Power BI model the SQL → "
            "table → dataset → report leg is added by reading each partition's M "
            "expression.",
            "Grafo dirigido de cinco camadas (source/raw/curated/mart/bi) como "
            "nós e arestas, achatado em tabela para exportar. Para um arquivo "
            "carregado a linhagem é a honesta —origem → dataset → BI—: não se "
            "inventam camadas raw/mart que não existem. De um modelo do Power BI "
            "acrescenta-se o trecho SQL → tabela → dataset → relatório lendo a "
            "expressão M de cada partição."),
        "porque": _tr(
            "Sin linaje, cambiar una columna es apostar. Con linaje se sabe "
            "exactamente qué tableros dependen de ella antes de tocarla.",
            "Without lineage, changing a column is a gamble. With lineage you "
            "know exactly which dashboards depend on it before touching it.",
            "Sem linhagem, mudar uma coluna é apostar. Com linhagem sabe-se "
            "exatamente quais painéis dependem dela antes de mexer."),
        "impacto": _tr(
            "Es la base del análisis de impacto aguas abajo y de las alertas "
            "sobre contratos de datos.",
            "It is the basis for downstream impact analysis and for data "
            "contract alerts.",
            "É a base da análise de impacto a jusante e dos alertas sobre "
            "contratos de dados."),
        "modulo": "mvdg/lineage.py · mvdg/scope.py · mvdg/powerbi_meta.py",
    },
    {
        "key": "glosario", "n": 10,
        "titulo": _tr("Glosario: el idioma común del negocio",
                      "Glossary: the shared business language",
                      "Glossário: a língua comum do negócio"),
        "criollo": _tr(
            "La definición acordada de cada término del negocio —qué es un "
            "«cliente activo», qué cuenta como «venta»— con su dueño y los "
            "datasets donde vive. Es lo que hace que dos informes den el mismo "
            "número.",
            "The agreed definition of every business term —what an \"active "
            "customer\" is, what counts as a \"sale\"— with its owner and the "
            "datasets where it lives. It is what makes two reports give the same "
            "number.",
            "A definição acordada de cada termo do negócio —o que é um \"cliente "
            "ativo\", o que conta como \"venda\"— com seu dono e os datasets onde "
            "vive. É o que faz dois relatórios darem o mesmo número."),
        "tecnico": _tr(
            "term_id/term/definition/owner/linked_datasets, vinculado al "
            "diccionario por business_term. Migra a Purview y a Collibra por su "
            "API real, en las dos direcciones con Collibra.",
            "term_id/term/definition/owner/linked_datasets, linked to the "
            "dictionary through business_term. Migrates to Purview and Collibra "
            "through their real API, both ways with Collibra.",
            "term_id/term/definition/owner/linked_datasets, vinculado ao "
            "dicionário por business_term. Migra para Purview e Collibra pela "
            "API real, nas duas direções com o Collibra."),
        "porque": _tr(
            "La mayoría de las discusiones sobre «los números no cierran» no "
            "son de datos: son de definiciones distintas del mismo término.",
            "Most arguments about \"the numbers don't match\" are not about data: "
            "they are about different definitions of the same term.",
            "A maioria das discussões sobre \"os números não batem\" não é de "
            "dados: é de definições diferentes do mesmo termo."),
        "impacto": _tr(
            "Un término sin dueño ni datasets vinculados hace que la política "
            "de semántica quede incompleta.",
            "A term with no owner or linked datasets leaves the semantics policy "
            "incomplete.",
            "Um termo sem dono nem datasets vinculados deixa a política de "
            "semântica incompleta."),
        "modulo": "mvdg/glossary.py",
    },
    {
        "key": "politicas", "n": 11,
        "titulo": _tr("Políticas: el cumplimiento, con evidencia",
                      "Policies: compliance, with evidence",
                      "Políticas: a conformidade, com evidência"),
        "criollo": _tr(
            "Seis reglas de gobierno —todo dataset con dueño, columnas "
            "documentadas, datos personales clasificados— evaluadas "
            "automáticamente sobre lo que hay, no sobre lo que se prometió. "
            "Cada una dice si se cumple y CON QUÉ evidencia.",
            "Six governance rules —every dataset with an owner, documented "
            "columns, classified personal data— evaluated automatically against "
            "what exists, not what was promised. Each says whether it is met and "
            "WITH WHAT evidence.",
            "Seis regras de governança —todo dataset com dono, colunas "
            "documentadas, dados pessoais classificados— avaliadas "
            "automaticamente sobre o que existe, não sobre o que foi prometido. "
            "Cada uma diz se é cumprida e COM QUE evidência."),
        "tecnico": _tr(
            "policies_df() deriva el estado de cada política del catálogo, el "
            "diccionario y los resultados de calidad FINALES —después de sumar "
            "lo que cargó el usuario—, no de una lista fija. El estado es "
            "compliant/partial/noncompliant y la evidencia nombra los datasets "
            "que faltan.",
            "policies_df() derives each policy's status from the FINAL catalog, "
            "dictionary and quality results —after adding what the user loaded—, "
            "not from a fixed list. The status is compliant/partial/noncompliant "
            "and the evidence names the missing datasets.",
            "policies_df() deriva o estado de cada política do catálogo, do "
            "dicionário e dos resultados de qualidade FINAIS —depois de somar o "
            "que o usuário carregou—, não de uma lista fixa. O estado é "
            "compliant/partial/noncompliant e a evidência nomeia os datasets que "
            "faltam."),
        "porque": _tr(
            "Un tablero de cumplimiento en verde que nadie puede auditar no "
            "sirve para nada. La evidencia es lo que se le muestra al auditor.",
            "A green compliance dashboard nobody can audit is worthless. The "
            "evidence is what you show the auditor.",
            "Um painel de conformidade no verde que ninguém pode auditar não "
            "serve para nada. A evidência é o que se mostra ao auditor."),
        "impacto": _tr(
            "Es el resumen ejecutivo del estado de gobierno y lo primero que "
            "mira una auditoría.",
            "It is the executive summary of the governance state and the first "
            "thing an audit looks at.",
            "É o resumo executivo do estado de governança e a primeira coisa que "
            "uma auditoria olha."),
        "modulo": "mvdg/policies.py",
    },
    {
        "key": "publicacion", "n": 12,
        "titulo": _tr("Publicación: que llegue a donde se decide",
                      "Publication: getting it where decisions happen",
                      "Publicação: chegar onde se decide"),
        "criollo": _tr(
            "Todo lo anterior sale hacia la herramienta que la empresa ya usa "
            "—Power BI, Tableau, Excel— por archivo o conectándose a una "
            "dirección. Sin esto el gobierno de datos queda encerrado en el "
            "programa y no cambia ninguna decisión.",
            "Everything above goes out to the tool the company already uses "
            "—Power BI, Tableau, Excel— by file or by connecting to an address. "
            "Without this, data governance stays locked inside the program and "
            "changes no decision.",
            "Tudo o anterior sai para a ferramenta que a empresa já usa —Power "
            "BI, Tableau, Excel— por arquivo ou conectando a um endereço. Sem "
            "isso a governança fica trancada no programa e não muda nenhuma "
            "decisão."),
        "tecnico": _tr(
            "Nueve tablas de gobierno servidas en JSON y CSV por una API REST "
            "local (127.0.0.1 por defecto, token obligatorio si se publica "
            "fuera de loopback, rate limit siempre activo y CORS sin comodín), "
            "más exportación a CSV/Excel/JSON/Parquet y un bundle único.",
            "Nine governance tables served as JSON and CSV by a local REST API "
            "(127.0.0.1 by default, token required if published outside "
            "loopback, rate limiting always on and no wildcard CORS), plus "
            "export to CSV/Excel/JSON/Parquet and a single bundle.",
            "Nove tabelas de governança servidas em JSON e CSV por uma API REST "
            "local (127.0.0.1 por padrão, token obrigatório se publicada fora do "
            "loopback, rate limit sempre ativo e CORS sem curinga), mais "
            "exportação para CSV/Excel/JSON/Parquet e um bundle único."),
        "porque": _tr(
            "El gobierno de datos vale por las decisiones que cambia, y las "
            "decisiones se toman mirando el tablero de siempre, no una "
            "herramienta nueva.",
            "Data governance is worth the decisions it changes, and decisions "
            "are made looking at the usual dashboard, not a new tool.",
            "A governança vale pelas decisões que muda, e as decisões são "
            "tomadas olhando o painel de sempre, não uma ferramenta nova."),
        "impacto": _tr(
            "Cierra el circuito: el índice de calidad y las alertas quedan al "
            "lado de los números del negocio, donde se miran.",
            "It closes the loop: the quality index and the alerts sit next to "
            "the business numbers, where they get looked at.",
            "Fecha o circuito: o índice de qualidade e os alertas ficam ao lado "
            "dos números do negócio, onde são olhados."),
        "modulo": "bi_api/main.py · mvdg/exporters.py",
    },
]


def _texto(bloque: dict, lang: str) -> str:
    return bloque.get(lang, bloque["es"])


# ---------------------------------------------------------------------------
# Evidencia: los números de ESTA corrida, no del folleto
# ---------------------------------------------------------------------------
# Cada medidor recibe lo que la app ya tiene calculado y devuelve una frase
# corta con números reales, o "" si esa etapa no aplica al caso actual. Nunca
# inventa: si no hay con qué medir, no dice nada. Un "0 datasets" escrito como
# si fuera un resultado es peor que el silencio.

def _n(x) -> int:
    try:
        return int(len(x))
    except (TypeError, ValueError):
        return 0


def _ev_ingesta(ctx: dict, lang: str) -> str:
    datasets = ctx.get("datasets") or {}
    if not datasets:
        return ""
    filas = sum(len(d) for d in datasets.values())
    cols = sum(len(d.columns) for d in datasets.values())
    return _texto(_tr(
        f"{len(datasets)} dataset(s) cargados: {filas:,} filas y {cols} columnas leídas.",
        f"{len(datasets)} dataset(s) loaded: {filas:,} rows and {cols} columns read.",
        f"{len(datasets)} dataset(s) carregados: {filas:,} linhas e {cols} colunas lidas."),
        lang).replace(",", ".")


def _ev_perfilado(ctx: dict, lang: str) -> str:
    dic = ctx.get("dictionary")
    if dic is None or not len(dic):
        return ""
    pii = int(dic["pii"].sum()) if "pii" in dic.columns else 0
    return _texto(_tr(
        f"{len(dic)} columnas perfiladas · {pii} marcadas como datos personales.",
        f"{len(dic)} columns profiled · {pii} flagged as personal data.",
        f"{len(dic)} colunas perfiladas · {pii} marcadas como dados pessoais."), lang)


def _ev_catalogo(ctx: dict, lang: str) -> str:
    cat = ctx.get("catalog")
    if cat is None or not len(cat):
        return ""
    sin_duenio = 0
    if {"owner", "steward"} <= set(cat.columns):
        sin_duenio = int(((cat["owner"] == "") | (cat["steward"] == "")).sum())
    return _texto(_tr(
        f"{len(cat)} datasets catalogados · {len(cat) - sin_duenio} con dueño y steward.",
        f"{len(cat)} datasets catalogued · {len(cat) - sin_duenio} with owner and steward.",
        f"{len(cat)} datasets catalogados · {len(cat) - sin_duenio} com dono e steward."), lang)


def _ev_diccionario(ctx: dict, lang: str) -> str:
    dic = ctx.get("dictionary")
    if dic is None or not len(dic):
        return ""
    con_termino = 0
    if "business_term" in dic.columns:
        con_termino = int((dic["business_term"].astype(str).str.strip() != "").sum())
    return _texto(_tr(
        f"{len(dic)} columnas documentadas · {con_termino} atadas a un término del glosario.",
        f"{len(dic)} columns documented · {con_termino} tied to a glossary term.",
        f"{len(dic)} colunas documentadas · {con_termino} ligadas a um termo do glossário."), lang)


def _ev_reglas(ctx: dict, lang: str) -> str:
    res = ctx.get("results")
    if res is None or not len(res) or "status" not in res.columns:
        return ""
    fallan = int((res["status"] == "fail").sum())
    alertan = int((res["status"] == "warn").sum())
    filas = int(res["affected_rows"].sum()) if "affected_rows" in res.columns else 0
    return _texto(_tr(
        f"{len(res)} reglas corridas · {fallan} en falla, {alertan} en alerta · "
        f"{filas:,} filas afectadas.",
        f"{len(res)} rules run · {fallan} failing, {alertan} warning · "
        f"{filas:,} affected rows.",
        f"{len(res)} regras executadas · {fallan} em falha, {alertan} em alerta · "
        f"{filas:,} linhas afetadas."), lang).replace(",", ".")


def _ev_indice(ctx: dict, lang: str) -> str:
    indice = ctx.get("indice")
    if indice is None:
        return ""
    return _texto(_tr(
        f"Índice de calidad actual: {indice} sobre 100.",
        f"Current quality index: {indice} out of 100.",
        f"Índice de qualidade atual: {indice} de 100."), lang)


def _ev_features(ctx: dict, lang: str) -> str:
    n = _n(ctx.get("features"))
    if not n:
        return ""
    fugas = _n(ctx.get("fugas"))
    base = _texto(_tr(
        f"{n} columnas derivadas propuestas, cada una con su fórmula.",
        f"{n} derived columns proposed, each with its formula.",
        f"{n} colunas derivadas propostas, cada uma com sua fórmula."), lang)
    if not fugas:
        return base
    aviso = _texto(_tr(f" {fugas} variable(s) marcadas como posible fuga.",
                       f" {fugas} variable(s) flagged as possible leakage.",
                       f" {fugas} variável(is) marcadas como possível vazamento."), lang)
    return base + aviso


def _ev_mdm(ctx: dict, lang: str) -> str:
    n = _n(ctx.get("mdm_clusters"))
    if not n:
        return ""
    return _texto(_tr(
        f"{n} grupos de registros duplicados detectados.",
        f"{n} groups of duplicate records detected.",
        f"{n} grupos de registros duplicados detectados."), lang)


def _ev_linaje(ctx: dict, lang: str) -> str:
    lin = ctx.get("lineage")
    if lin is None or not len(lin):
        return ""
    nodos = 0
    if {"source_id", "target_id"} <= set(lin.columns):
        nodos = len(set(lin["source_id"]) | set(lin["target_id"]))
    return _texto(_tr(
        f"{len(lin)} tramos de linaje sobre {nodos} nodos.",
        f"{len(lin)} lineage edges across {nodos} nodes.",
        f"{len(lin)} trechos de linhagem sobre {nodos} nós."), lang)


def _ev_glosario(ctx: dict, lang: str) -> str:
    g = ctx.get("glossary")
    if g is None or not len(g):
        return ""
    return _texto(_tr(f"{len(g)} términos de negocio definidos.",
                      f"{len(g)} business terms defined.",
                      f"{len(g)} termos de negócio definidos."), lang)


def _ev_politicas(ctx: dict, lang: str) -> str:
    pol = ctx.get("policies")
    if pol is None or not len(pol) or "status" not in pol.columns:
        return ""
    cumple = int((pol["status"] == "compliant").sum())
    return _texto(_tr(
        f"{cumple} de {len(pol)} políticas se cumplen, con evidencia verificable.",
        f"{cumple} of {len(pol)} policies met, with verifiable evidence.",
        f"{cumple} de {len(pol)} políticas cumpridas, com evidência verificável."), lang)


def _ev_publicacion(ctx: dict, lang: str) -> str:
    tablas = ctx.get("tablas_bi")
    if not tablas:
        return ""
    return _texto(_tr(
        f"{len(tablas)} tablas de gobierno listas para BI: {', '.join(tablas)}.",
        f"{len(tablas)} governance tables ready for BI: {', '.join(tablas)}.",
        f"{len(tablas)} tabelas de governança prontas para BI: {', '.join(tablas)}."), lang)


_MEDIDORES = {
    "ingesta": _ev_ingesta, "perfilado": _ev_perfilado, "catalogo": _ev_catalogo,
    "diccionario": _ev_diccionario, "reglas": _ev_reglas, "indice": _ev_indice,
    "features": _ev_features, "mdm": _ev_mdm, "linaje": _ev_linaje,
    "glosario": _ev_glosario, "politicas": _ev_politicas,
    "publicacion": _ev_publicacion,
}


def documentar(lang: str = "es", **contexto) -> list[dict]:
    """Las etapas del pipeline en orden, traducidas y con evidencia real.

    Todo el ``contexto`` es opcional: sin nada, devuelve la explicación pura
    (que ya sirve como documentación del producto). Con los DataFrames que la
    app ya tiene calculados, cada etapa suma los números de esta corrida.

    Claves reconocidas: ``datasets`` (dict nombre→DataFrame), ``catalog``,
    ``dictionary``, ``results``, ``lineage``, ``glossary``, ``policies``,
    ``indice``, ``features``, ``fugas``, ``mdm_clusters``, ``tablas_bi``.
    """
    salida = []
    for etapa in ETAPAS:
        medidor = _MEDIDORES.get(etapa["key"])
        salida.append({
            "n": etapa["n"],
            "key": etapa["key"],
            "titulo": _texto(etapa["titulo"], lang),
            "criollo": _texto(etapa["criollo"], lang),
            "tecnico": _texto(etapa["tecnico"], lang),
            "porque": _texto(etapa["porque"], lang),
            "impacto": _texto(etapa["impacto"], lang),
            "modulo": etapa["modulo"],
            "evidencia": medidor(contexto, lang) if medidor else "",
        })
    return salida


# ---------------------------------------------------------------------------
# Puente hacia los exportadores
# ---------------------------------------------------------------------------
# `documentar()` devuelve las etapas crudas, que es lo que la pestaña necesita
# para dibujarlas. `documento()` las arma en la forma que `mvdg.doc_export`
# sabe escribir. Están separadas a propósito: la pantalla y el archivo se
# leen distinto, pero el contenido se escribe UNA vez.

_ETIQUETAS = {
    "criollo": _tr("En criollo", "In plain words", "Em bom português"),
    "tecnico": _tr("En técnico", "In technical terms", "Em termos técnicos"),
    "porque": _tr("Por qué se hace", "Why it is done", "Por que se faz"),
    "impacto": _tr("Qué cambia aguas abajo", "What changes downstream",
                   "O que muda a jusante"),
    "evidencia": _tr("Evidencia de esta corrida", "Evidence from this run",
                     "Evidência desta execução"),
}

def etiquetas(lang: str = "es") -> dict:
    """Los rótulos de cada bloque, traducidos. Los usa la pestaña y el archivo."""
    return {clave: _texto(valor, lang) for clave, valor in _ETIQUETAS.items()}


_TITULO = _tr("Qué se le hizo al dato, y por qué",
              "What was done to the data, and why",
              "O que foi feito com o dado, e por quê")

_SUBTITULO = _tr(
    "Las {n} etapas del pipeline de gobierno, en el orden real en que ocurren. "
    "Cada una contada en criollo y en técnico.",
    "The {n} stages of the governance pipeline, in the real order they happen. "
    "Each one told in plain words and in technical terms.",
    "As {n} etapas do pipeline de governança, na ordem real em que ocorrem. "
    "Cada uma contada em bom português e em termos técnicos.")

_PIE = _tr("MV Data Governance · documento generado por el propio pipeline",
           "MV Data Governance · document generated by the pipeline itself",
           "MV Data Governance · documento gerado pelo próprio pipeline")

_META_ETAPAS = _tr("Etapas", "Stages", "Etapas")
_META_MEDIDAS = _tr("Etapas con medición", "Stages with measurement",
                    "Etapas com medição")
_META_ORIGEN = _tr("Origen de los datos", "Data source", "Origem dos dados")
_SIN_DATOS = _tr("Sin datos cargados: documentación del producto",
                 "No data loaded: product documentation",
                 "Sem dados carregados: documentação do produto")


def _origen(contexto: dict, lang: str) -> str:
    """Qué datasets se recorrieron. Los del usuario si los hay; si no, los del catálogo.

    Mirar solo ``datasets`` decía "sin datos cargados" incluso con la demo
    andando, que es falso: la demo también es un origen y el gerente que lee
    el PDF tiene que saber sobre qué se midió.
    """
    nombres = sorted(contexto.get("datasets") or {})
    if not nombres:
        cat = contexto.get("catalog")
        if cat is not None and len(cat) and "dataset" in cat.columns:
            nombres = sorted(set(cat["dataset"].astype(str)))
    if not nombres:
        return _texto(_SIN_DATOS, lang)
    if len(nombres) > 8:
        return ", ".join(nombres[:8]) + f" (+{len(nombres) - 8})"
    return ", ".join(nombres)


def documento(lang: str = "es", **contexto) -> dict:
    """El pipeline armado como documento, listo para ``mvdg.doc_export``.

    Acepta el mismo ``contexto`` que :func:`documentar`. Devuelve el ``dict``
    que ``a_html`` / ``a_docx`` / ``a_pdf`` saben escribir.
    """
    etapas = documentar(lang, **contexto)
    medidas = sum(1 for e in etapas if e["evidencia"])
    secciones = [{
        "n": e["n"],
        "titulo": e["titulo"],
        "modulo": e["modulo"],
        "bloques": [(_texto(_ETIQUETAS[campo], lang), e[campo])
                    for campo in ("criollo", "tecnico", "porque", "impacto")],
        "evidencia": e["evidencia"],
        "evidencia_etiqueta": _texto(_ETIQUETAS["evidencia"], lang),
    } for e in etapas]

    return {
        "titulo": _texto(_TITULO, lang),
        "subtitulo": _texto(_SUBTITULO, lang).format(n=len(etapas)),
        "lang": lang,
        "meta": [
            (_texto(_META_ETAPAS, lang), str(len(etapas))),
            (_texto(_META_MEDIDAS, lang), f"{medidas}/{len(etapas)}"),
            (_texto(_META_ORIGEN, lang), _origen(contexto, lang)),
        ],
        "pie": _texto(_PIE, lang),
        "secciones": secciones,
    }
