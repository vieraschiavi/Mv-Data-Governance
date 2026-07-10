# 📊 Integración con BI · BI Integration · Integração com BI

MV Data Governance expone **todas** sus tablas de gobierno de dos maneras, y
cualquier herramienta de BI puede usar la que prefiera:

| Vía | Formatos | Cómo |
|---|---|---|
| **Archivos** | CSV · Excel · JSON · Parquet | Pestaña **📤 BI & API** del programa → botones de descarga |
| **API REST** | JSON · CSV | `MV_DataGovernance_API.bat` (o `python -m api.main`) → `http://127.0.0.1:8600` |

Tablas disponibles: `catalog`, `dictionary`, `quality_results`,
`quality_by_dataset`, `quality_by_dimension`, `lineage`, `glossary`,
`policies`, `kpis`. Todas aceptan `?lang=es|en|pt` y `?format=json|csv`.

```
GET http://127.0.0.1:8600/api/catalog?lang=es
GET http://127.0.0.1:8600/api/quality_results?lang=en&format=csv
GET http://127.0.0.1:8600/docs        ← documentación interactiva (Swagger)
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
