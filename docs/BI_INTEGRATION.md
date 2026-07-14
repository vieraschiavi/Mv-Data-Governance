# 📊 Integración con BI · BI Integration · Integração com BI

MV Data Governance expone **todas** sus tablas de gobierno de dos maneras, y
cualquier herramienta de BI puede usar la que prefiera:

| Vía | Formatos | Cómo |
|---|---|---|
| **Archivos** | CSV · Excel · JSON · Parquet | Pestaña **📤 BI & API** del programa → botones de descarga |
| **API REST** | JSON · CSV | `MV_DataGovernance_API.bat` (o `python -m bi_api.main`) → `http://127.0.0.1:8600` |

Tablas disponibles: `catalog`, `dictionary`, `quality_results`,
`quality_by_dataset`, `quality_by_dimension`, `lineage`, `glossary`,
`policies`, `kpis`. Todas aceptan `?lang=es|en|pt` y `?format=json|csv`.

```
GET http://127.0.0.1:8600/api/catalog?lang=es
GET http://127.0.0.1:8600/api/quality_results?lang=en&format=csv
GET http://127.0.0.1:8600/docs        ← documentación interactiva (Swagger)
```

### Datasets de ejemplo (reales), gobernados de punta a punta

Además de las 4 tablas sintéticas de demo, la pestaña **🔎 Mis datos → 🧪
Dataset de ejemplo** trae datasets **externos reales** (rotulado de alimentos,
Uruguay; ventas de cafetería, Kaggle; campaña de marketing bancario, UCI) con
catálogo (dueño/steward), reglas de calidad propias, glosario y las mismas 4
salidas por dataset:

```
GET http://127.0.0.1:8600/                                               ← "samples": lista de datasets
GET http://127.0.0.1:8600/api/samples/rotulado_alimentos?lang=es         ← ficha (dueño, steward, fuente)
GET http://127.0.0.1:8600/api/samples/rotulado_alimentos/data            ← datos crudos
GET http://127.0.0.1:8600/api/samples/cafe_sales_kaggle/quality_results  ← reglas con umbral y estado
GET http://127.0.0.1:8600/api/samples/cafe_sales_kaggle/glossary         ← definiciones de negocio
GET http://127.0.0.1:8600/api/samples/bank_marketing_uci/quality_results ← reglas con umbral y estado
```

---

## 🇪🇸 Español

### Power BI
1. Levantá la API con `MV_DataGovernance_API.bat`.
2. En Power BI Desktop: **Obtener datos → Web** y pegá
   `http://127.0.0.1:8600/api/catalog?lang=es`.
3. En el editor Power Query: clic derecho sobre `data` → **Convertir en tabla**
   → expandir columnas. Repetí por cada tabla que necesites.
4. Alternativa sin API: descargá el **paquete BI completo (Excel multi-hoja)**
   desde la pestaña *BI & API* y usá **Obtener datos → Libro de Excel**.

#### Power BI (avanzado): gobernar el modelo en sí
Además de conectar datos, la pestaña **🔷 Power BI** gobierna el modelo semántico:
1. En Power BI Desktop, guardá tu reporte como **.pbip** (formato TMDL) —
   `Archivo → Guardar como → Proyecto de Power BI`.
2. (Recomendado) Borrá `*.SemanticModel/.pbi/cache.abf`: el modelo queda con
   toda su estructura y **cero datos**, el camino más seguro.
3. En la pestaña **🔷 Power BI**, apuntá a la carpeta del proyecto (o subí un
   `.zip`) y hacé clic en **Analizar modelo**.
4. Vas a ver: catálogo del modelo, columnas, medidas con su DAX (como
   glosario), 5 reglas de salud del modelo, y el **linaje real** — SQL Server
   detectado en cada partición → tabla → dataset → reporte, en el mismo
   grafo de 5 capas que el resto del programa.
5. Opcional: con tu API key de IA configurada, pedile que audite y
   refactorice el DAX de cualquier medida (solo se manda el DAX, nunca datos).

### Tableau
1. Con la API levantada, usá **Datos → Nueva fuente de datos → Archivo JSON**
   sobre una descarga de `/api/...`, o el **Web Data Connector**.
2. Camino simple: exportá **CSV** desde la pestaña *BI & API* y conectá
   **Archivo de texto**. Para modelos grandes, usá **Parquet**.

### Looker / Looker Studio
- **Looker Studio**: conector **Subida de archivos** (CSV) o **Extracción de
  datos** apuntando a los CSV exportados.
- **Looker (core)**: cargá los CSV/Parquet a tu warehouse (BigQuery,
  Snowflake…) con el scheduler que ya uses; las tablas están normalizadas
  para modelarse directo en LookML.

### MicroStrategy
1. **Add External Data → File From Disk** para CSV/Excel exportados, o
2. **Add External Data → Data from URL** con
   `http://127.0.0.1:8600/api/catalog?lang=es&format=csv`.

### Qlik / Excel
- **Qlik Sense**: *Agregar datos → Archivos y otras fuentes* (CSV/Excel), o
  `Web file` con la URL de la API en formato CSV.
- **Excel**: **Datos → Obtener datos → Desde web** con cualquier endpoint
  `format=csv`, o abrí directamente el paquete multi-hoja exportado.

---

## 🇬🇧 English

### Power BI
1. Start the API with `MV_DataGovernance_API.bat`.
2. In Power BI Desktop: **Get Data → Web**, paste
   `http://127.0.0.1:8600/api/catalog?lang=en`.
3. In Power Query: right-click `data` → **To Table** → expand columns.
   Repeat per table.
4. No-API alternative: download the **full BI bundle (multi-sheet Excel)**
   from the *BI & API* tab and use **Get Data → Excel Workbook**.

#### Power BI (advanced): govern the model itself
Beyond connecting data, the **🔷 Power BI** tab governs the semantic model:
1. In Power BI Desktop, save your report as a **.pbip** project (TMDL
   format) — `File → Save As → Power BI project`.
2. (Recommended) Delete `*.SemanticModel/.pbi/cache.abf`: the model keeps
   its full structure with **zero data** — the safest path.
3. In the **🔷 Power BI** tab, point to the project folder (or upload a
   `.zip`) and click **Analyze model**.
4. You'll see: the model catalog, columns, measures with their DAX (as a
   glossary), 5 model-health rules, and the **real lineage** — the SQL
   Server detected in each partition → table → dataset → report, on the
   same 5-layer graph used across the rest of the program.
5. Optional: with your AI API key set, ask it to audit and refactor the DAX
   of any measure (only the DAX is sent, never data).

### Tableau
1. With the API running, use **Data → New Data Source → JSON file** on a
   saved `/api/...` response, or the **Web Data Connector**.
2. Simple path: export **CSV** from the *BI & API* tab and connect a
   **Text file**. For large models, prefer **Parquet**.

### Looker / Looker Studio
- **Looker Studio**: **File Upload** connector (CSV) or **Extract Data** on
  the exported CSVs.
- **Looker (core)**: load the CSV/Parquet exports into your warehouse
  (BigQuery, Snowflake…); tables are normalized for direct LookML modeling.

### MicroStrategy
1. **Add External Data → File From Disk** for exported CSV/Excel, or
2. **Add External Data → Data from URL** with
   `http://127.0.0.1:8600/api/catalog?lang=en&format=csv`.

### Qlik / Excel
- **Qlik Sense**: *Add data → Files and other sources* (CSV/Excel), or a
  `Web file` pointing at any CSV-format API endpoint.
- **Excel**: **Data → Get Data → From Web** with any `format=csv` endpoint,
  or open the exported multi-sheet bundle directly.

---

## 🇧🇷 Português

### Power BI
1. Inicie a API com `MV_DataGovernance_API.bat`.
2. No Power BI Desktop: **Obter dados → Web** e cole
   `http://127.0.0.1:8600/api/catalog?lang=pt`.
3. No Power Query: clique com o botão direito em `data` → **Converter em
   tabela** → expandir colunas. Repita por tabela.
4. Alternativa sem API: baixe o **pacote BI completo (Excel multi-abas)** na
   aba *BI & API* e use **Obter dados → Pasta de trabalho do Excel**.

#### Power BI (avançado): governar o modelo em si
Além de conectar dados, a aba **🔷 Power BI** governa o modelo semântico:
1. No Power BI Desktop, salve seu relatório como projeto **.pbip** (formato
   TMDL) — `Arquivo → Salvar como → Projeto do Power BI`.
2. (Recomendado) Apague `*.SemanticModel/.pbi/cache.abf`: o modelo fica com
   toda a estrutura e **zero dados** — o caminho mais seguro.
3. Na aba **🔷 Power BI**, aponte para a pasta do projeto (ou envie um
   `.zip`) e clique em **Analisar modelo**.
4. Você vai ver: catálogo do modelo, colunas, medidas com seu DAX (como
   glossário), 5 regras de saúde do modelo, e a **linhagem real** — o SQL
   Server detectado em cada partição → tabela → dataset → relatório, no
   mesmo grafo de 5 camadas usado no resto do programa.
5. Opcional: com sua API key de IA configurada, peça para auditar e
   refatorar o DAX de qualquer medida (envia-se apenas o DAX, nunca dados).

### Tableau
1. Com a API rodando, use **Dados → Nova fonte de dados → Arquivo JSON**
   sobre uma resposta salva de `/api/...`, ou o **Web Data Connector**.
2. Caminho simples: exporte **CSV** na aba *BI & API* e conecte **Arquivo de
   texto**. Para modelos grandes, prefira **Parquet**.

### Looker / Looker Studio
- **Looker Studio**: conector **Upload de arquivos** (CSV) ou **Extração de
  dados** sobre os CSVs exportados.
- **Looker (core)**: carregue os CSV/Parquet no seu warehouse (BigQuery,
  Snowflake…); as tabelas já estão normalizadas para modelar em LookML.

### MicroStrategy
1. **Add External Data → File From Disk** para CSV/Excel exportados, ou
2. **Add External Data → Data from URL** com
   `http://127.0.0.1:8600/api/catalog?lang=pt&format=csv`.

### Qlik / Excel
- **Qlik Sense**: *Adicionar dados → Arquivos e outras fontes* (CSV/Excel),
  ou `Web file` com a URL da API em formato CSV.
- **Excel**: **Dados → Obter dados → Da Web** com qualquer endpoint
  `format=csv`, ou abra diretamente o pacote multi-abas exportado.
