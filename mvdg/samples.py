"""
MV Data Governance · Datasets de ejemplo externos, gobernados de punta a punta.

A diferencia de ``mvdg.demo_data`` (datos 100% sintéticos generados por la
plataforma), estos son datasets REALES/externos que un usuario cargó o que se
tomaron de una fuente pública con licencia clara — pensados para demostrar el
ciclo completo de gobierno sobre datos que la plataforma no fabricó:

    catálogo (dueño, steward, clasificación) → reglas de calidad con
    umbral/estado (no solo perfilado genérico) → glosario de definiciones de
    negocio → exportable a cualquier BI (Power BI, Tableau, ...) por archivo o
    por API REST.

Cada entrada de ``SAMPLES`` es autocontenida: su propio archivo, catálogo,
diccionario de columnas, reglas DAMA y términos de glosario. Se mantienen
DELIBERADAMENTE separados de los 4 datasets sintéticos de demo (que alimentan
el Panorama y el Laboratorio) para no alterar esos números — son un tramo de
gobierno adicional, no un reemplazo.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from .quality import Rule, evaluate_rules, _in_set, _unique

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SAMPLES_DIR = os.path.join(_ROOT, "assets", "samples")


def _d(es: str, en: str, pt: str) -> dict:
    return {"es": es, "en": en, "pt": pt}


# ---------------------------------------------------------------------------
# Chequeos reutilizables (no viven en quality.py porque son específicos de
# datasets externos: nulos disfrazados de texto, fechas libres, reglas
# cruzadas entre columnas).
# ---------------------------------------------------------------------------
def _not_null_or_placeholder(col: str, placeholders: tuple[str, ...] = ("-",)):
    def check(df: pd.DataFrame):
        n = len(df)
        vals = df[col].astype(str).str.strip()
        bad = df[col].isna() | vals.isin(placeholders)
        nbad = int(bad.sum())
        return (100.0 * (n - nbad) / n if n else 100.0, nbad)
    return check


def _not_null_or_markers(col: str, markers: tuple[str, ...] = ("ERROR", "UNKNOWN")):
    def check(df: pd.DataFrame):
        n = len(df)
        vals = df[col].astype(str)
        bad = df[col].isna() | vals.isin(markers)
        nbad = int(bad.sum())
        return (100.0 * (n - nbad) / n if n else 100.0, nbad)
    return check


def _valid_date(col: str, markers: tuple[str, ...] = ()):
    def check(df: pd.DataFrame):
        n = len(df)
        vals = df[col]
        marker_mask = vals.astype(str).isin(markers) if markers else pd.Series(False, index=df.index)
        parsed = pd.to_datetime(vals, errors="coerce")
        bad = (parsed.isna() | marker_mask)
        nbad = int(bad.sum())
        return (100.0 * (n - nbad) / n if n else 100.0, nbad)
    return check


def _numeric_or_markers(col: str, markers: tuple[str, ...] = ("ERROR", "UNKNOWN")):
    def check(df: pd.DataFrame):
        n = len(df)
        vals = df[col]
        marker_mask = vals.astype(str).isin(markers)
        numeric = pd.to_numeric(vals, errors="coerce")
        bad = vals.isna() | marker_mask | numeric.isna()
        nbad = int(bad.sum())
        return (100.0 * (n - nbad) / n if n else 100.0, nbad)
    return check


def _conditional_completeness(when_col: str, when_not_equal: str, then_col: str):
    """Regla de negocio cruzada: cuando ``when_col`` != ``when_not_equal``
    (el caso 'no conforme'), ``then_col`` debe estar completo."""
    def check(df: pd.DataFrame):
        subset = df[df[when_col] != when_not_equal]
        n = len(subset)
        if n == 0:
            return (100.0, 0)
        bad = int(subset[then_col].isna().sum())
        return (100.0 * (n - bad) / n, bad)
    return check


def _amount_consistency(qty_col: str, price_col: str, total_col: str, markers=("ERROR", "UNKNOWN")):
    """Exactitud: total ≈ cantidad × precio, sobre las filas donde las 3
    columnas son numéricas (las que tienen ERROR/UNKNOWN/nulo quedan fuera del
    cálculo, no se cuentan como error de exactitud — son de completitud)."""
    def check(df: pd.DataFrame):
        def num(s):
            s = s.where(~s.astype(str).isin(markers))
            return pd.to_numeric(s, errors="coerce")
        q, p, t = num(df[qty_col]), num(df[price_col]), num(df[total_col])
        mask = q.notna() & p.notna() & t.notna()
        n = int(mask.sum())
        if n == 0:
            return (100.0, 0)
        close = np.isclose((q[mask] * p[mask]).astype(float), t[mask].astype(float), atol=0.01)
        nbad = int((~close).sum())
        return (100.0 * (n - nbad) / n, nbad)
    return check


# ---------------------------------------------------------------------------
# 1. Rotulado de alimentos 2026 — control bromatológico real (Uruguay)
# ---------------------------------------------------------------------------
_RAL_KEY = "rotulado_alimentos"
_RAL_CONFORME = ("La muestra analizada no presenta particularidades desde el "
                 "punto de vista quimico para los parametros analizados")

_RAL_RULES = [
    Rule("RAL-01", _RAL_KEY, "muestra", "uniqueness",
         _d("muestra debe ser único (clave natural)", "muestra must be unique (natural key)",
            "muestra deve ser único (chave natural)"),
         _unique("muestra"), 99.5),
    Rule("RAL-02", _RAL_KEY, "marca", "completeness",
         _d("marca completa (detecta nulos disfrazados de texto, ej. \"-\")",
            "marca complete (catches text-disguised nulls, e.g. \"-\")",
            "marca completa (detecta nulos disfarçados de texto, ex. \"-\")"),
         _not_null_or_placeholder("marca", ("-",)), 99.5),
    Rule("RAL-03", _RAL_KEY, "clasificacion", "validity",
         _d("clasificacion dentro del dominio bromatológico conocido",
            "clasificacion within the known food-safety domain",
            "clasificacion dentro do domínio bromatológico conhecido"),
         _in_set("clasificacion", {_RAL_CONFORME, "Fuera de las condiciones reglamentarias", "Observado"}), 99.5),
    Rule("RAL-04", _RAL_KEY, "vencimiento", "validity",
         _d("vencimiento es una fecha válida", "vencimiento is a valid date", "vencimiento é uma data válida"),
         _valid_date("vencimiento"), 99.0),
    Rule("RAL-05", _RAL_KEY, "fecha_de_analisis", "validity",
         _d("fecha_de_analisis es una fecha válida", "fecha_de_analisis is a valid date",
            "fecha_de_analisis é uma data válida"),
         _valid_date("fecha_de_analisis"), 99.5),
    Rule("RAL-06", _RAL_KEY, "articulos", "consistency",
         _d("cuando la clasificación no es conforme, «articulos» cita la norma (regla de negocio, no solo nulos)",
            "when the classification is non-conforming, «articulos» cites the regulation (business rule, not a raw null check)",
            "quando a classificação não é conforme, «articulos» cita a norma (regra de negócio, não só nulos)"),
         _conditional_completeness("clasificacion", _RAL_CONFORME, "articulos"), 99.5),
]

_RAL_COLUMNS = [
    {"column": "acta", "type": "int", "pii": False, "term": "acta",
     "d": _d("Número de acta de inspección.", "Inspection record number.", "Número de auto de inspeção.")},
    {"column": "producto", "type": "string", "pii": False, "term": "producto_alimenticio",
     "d": _d("Nombre y variante del producto analizado.", "Name and variant of the analyzed product.", "Nome e variante do produto analisado.")},
    {"column": "muestra", "type": "int", "pii": False, "term": "muestra",
     "d": _d("Identificador único de la muestra analizada.", "Unique identifier of the analyzed sample.", "Identificador único da amostra analisada.")},
    {"column": "clasificacion", "type": "string", "pii": False, "term": "clasificacion_bromatologica",
     "d": _d("Resultado del análisis bromatológico.", "Result of the food-safety (bromatological) analysis.", "Resultado da análise bromatológica.")},
    {"column": "articulos", "type": "string", "pii": False, "term": "clasificacion_bromatologica",
     "d": _d("Cita legal/observación cuando la muestra no es conforme.", "Legal citation/observation when the sample is non-conforming.", "Citação legal/observação quando a amostra não é conforme.")},
    {"column": "rotulado_frontal", "type": "string", "pii": False, "term": "rotulado",
     "d": _d("Estado del rotulado frontal del envase.", "Status of the package's front labeling.", "Status da rotulagem frontal da embalagem.")},
    {"column": "marca", "type": "string", "pii": False, "term": "marca",
     "d": _d("Marca comercial del producto.", "Commercial brand of the product.", "Marca comercial do produto.")},
    {"column": "fecha_de_analisis", "type": "date", "pii": False, "term": "fecha_de_analisis",
     "d": _d("Fecha en que se realizó el análisis.", "Date the analysis was performed.", "Data em que a análise foi realizada.")},
    {"column": "habilitacion_de_producto", "type": "string", "pii": False, "term": "habilitacion_producto",
     "d": _d("Número de habilitación bromatológica del producto.", "Product's food-safety authorization number.", "Número de habilitação bromatológica do produto.")},
    {"column": "vencimiento", "type": "date", "pii": False, "term": "vencimiento",
     "d": _d("Fecha de vencimiento del lote analizado.", "Expiry date of the analyzed batch.", "Data de validade do lote analisado.")},
    {"column": "lote", "type": "string", "pii": False, "term": "lote",
     "d": _d("Identificador del lote de producción.", "Production batch identifier.", "Identificador do lote de produção.")},
    {"column": "contenido_neto", "type": "string", "pii": False, "term": "contenido_neto",
     "d": _d("Contenido neto declarado del envase.", "Declared net content of the package.", "Conteúdo líquido declarado da embalagem.")},
]

_RAL_TERMS = [
    {"term_id": "muestra", "name": _d("Muestra", "Sample", "Amostra"),
     "definition": _d("Unidad de producto tomada para análisis bromatológico, identificada con un número único.",
                       "Product unit taken for food-safety analysis, identified with a unique number.",
                       "Unidade de produto retirada para análise bromatológica, identificada com um número único."),
     "owner": "Equipo de Calidad y Cumplimiento",
     "datasets": [_RAL_KEY]},
    {"term_id": "clasificacion_bromatologica", "name": _d("Clasificación bromatológica", "Food-safety classification", "Classificação bromatológica"),
     "definition": _d("Veredicto del análisis: conforme, fuera de las condiciones reglamentarias u observado.",
                       "Verdict of the analysis: conforming, out of regulatory conditions, or observed.",
                       "Veredito da análise: conforme, fora das condições regulamentares ou observado."),
     "owner": "Equipo de Calidad y Cumplimiento", "datasets": [_RAL_KEY]},
    {"term_id": "rotulado", "name": _d("Rotulado", "Labeling", "Rotulagem"),
     "definition": _d("Información obligatoria impresa en el envase de un producto alimenticio.",
                       "Mandatory information printed on a food product's package.",
                       "Informação obrigatória impressa na embalagem de um produto alimentício."),
     "owner": "Equipo de Calidad y Cumplimiento", "datasets": [_RAL_KEY]},
    {"term_id": "habilitacion_producto", "name": _d("Habilitación de producto", "Product authorization", "Habilitação de produto"),
     "definition": _d("Número que autoriza la comercialización de un producto alimenticio ante el organismo regulador.",
                       "Number authorizing a food product's sale before the regulatory body.",
                       "Número que autoriza a comercialização de um produto alimentício perante o órgão regulador."),
     "owner": "Equipo de Calidad y Cumplimiento", "datasets": [_RAL_KEY]},
    {"term_id": "lote", "name": _d("Lote", "Batch", "Lote"),
     "definition": _d("Conjunto de unidades de un producto fabricadas en las mismas condiciones, identificado para trazabilidad.",
                       "Set of product units manufactured under the same conditions, identified for traceability.",
                       "Conjunto de unidades de um produto fabricadas nas mesmas condições, identificado para rastreabilidade."),
     "owner": "Equipo de Calidad y Cumplimiento", "datasets": [_RAL_KEY]},
]

# ---------------------------------------------------------------------------
# 2. Dirty Cafe Sales (Kaggle) — ventas de cafetería con errores inyectados
# ---------------------------------------------------------------------------
_CAF_KEY = "cafe_sales_kaggle"

_CAF_RULES = [
    Rule("CAF-01", _CAF_KEY, "Transaction ID", "uniqueness",
         _d("Transaction ID debe ser único", "Transaction ID must be unique", "Transaction ID deve ser único"),
         _unique("Transaction ID"), 99.5),
    Rule("CAF-02", _CAF_KEY, "Item", "completeness",
         _d("Item completo (sin nulos, \"ERROR\" ni \"UNKNOWN\")",
            "Item complete (no nulls, \"ERROR\" or \"UNKNOWN\")",
            "Item completo (sem nulos, \"ERROR\" nem \"UNKNOWN\")"),
         _not_null_or_markers("Item"), 95.0),
    Rule("CAF-03", _CAF_KEY, "Payment Method", "completeness",
         _d("Payment Method completo", "Payment Method complete", "Payment Method completo"),
         _not_null_or_markers("Payment Method"), 95.0),
    Rule("CAF-04", _CAF_KEY, "Location", "completeness",
         _d("Location completo", "Location complete", "Location completo"),
         _not_null_or_markers("Location"), 95.0),
    Rule("CAF-05", _CAF_KEY, "Quantity", "validity",
         _d("Quantity es numérico y está presente", "Quantity is numeric and present", "Quantity é numérico e está presente"),
         _numeric_or_markers("Quantity"), 97.0),
    Rule("CAF-06", _CAF_KEY, "Transaction Date", "validity",
         _d("Transaction Date es una fecha válida", "Transaction Date is a valid date", "Transaction Date é uma data válida"),
         _valid_date("Transaction Date", ("ERROR", "UNKNOWN")), 97.0),
    Rule("CAF-07", _CAF_KEY, "Total Spent", "accuracy",
         _d("Total Spent = Quantity × Price Per Unit (en filas con los 3 valores numéricos)",
            "Total Spent = Quantity × Price Per Unit (on rows with all 3 numeric values)",
            "Total Spent = Quantity × Price Per Unit (em linhas com os 3 valores numéricos)"),
         _amount_consistency("Quantity", "Price Per Unit", "Total Spent"), 99.0),
]

_CAF_COLUMNS = [
    {"column": "Transaction ID", "type": "string", "pii": False, "term": "transaccion",
     "d": _d("Identificador único de la transacción de venta.", "Unique identifier of the sale transaction.", "Identificador único da transação de venda.")},
    {"column": "Item", "type": "string", "pii": False, "term": "producto_cafeteria",
     "d": _d("Producto vendido (café, té, sándwich, etc.).", "Product sold (coffee, tea, sandwich, etc.).", "Produto vendido (café, chá, sanduíche, etc.).")},
    {"column": "Quantity", "type": "int", "pii": False, "term": "cantidad",
     "d": _d("Unidades vendidas en la transacción.", "Units sold in the transaction.", "Unidades vendidas na transação.")},
    {"column": "Price Per Unit", "type": "decimal", "pii": False, "term": "precio_unitario",
     "d": _d("Precio de una unidad del producto.", "Price of one unit of the product.", "Preço de uma unidade do produto.")},
    {"column": "Total Spent", "type": "decimal", "pii": False, "term": "importe_total",
     "d": _d("Importe total de la transacción (cantidad × precio unitario).", "Total transaction amount (quantity × unit price).", "Valor total da transação (quantidade × preço unitário).")},
    {"column": "Payment Method", "type": "string", "pii": False, "term": "medio_de_pago",
     "d": _d("Medio de pago utilizado.", "Payment method used.", "Meio de pagamento utilizado.")},
    {"column": "Location", "type": "string", "pii": False, "term": "canal_venta",
     "d": _d("Canal de venta: en el local o para llevar.", "Sales channel: in-store or takeaway.", "Canal de venda: no local ou para levar.")},
    {"column": "Transaction Date", "type": "date", "pii": False, "term": "fecha_transaccion",
     "d": _d("Fecha en que ocurrió la transacción.", "Date the transaction occurred.", "Data em que a transação ocorreu.")},
]

_CAF_TERMS = [
    {"term_id": "transaccion", "name": _d("Transacción", "Transaction", "Transação"),
     "definition": _d("Venta individual registrada en el punto de venta, con un identificador único.",
                       "Individual sale recorded at the point of sale, with a unique identifier.",
                       "Venda individual registrada no ponto de venda, com um identificador único."),
     "owner": "Equipo de Datos de Ventas", "datasets": [_CAF_KEY]},
    {"term_id": "medio_de_pago", "name": _d("Medio de pago", "Payment method", "Meio de pagamento"),
     "definition": _d("Forma en que el cliente pagó: efectivo, tarjeta de crédito o billetera digital.",
                       "How the customer paid: cash, credit card or digital wallet.",
                       "Forma como o cliente pagou: dinheiro, cartão de crédito ou carteira digital."),
     "owner": "Equipo de Datos de Ventas", "datasets": [_CAF_KEY]},
    {"term_id": "canal_venta", "name": _d("Canal de venta", "Sales channel", "Canal de venda"),
     "definition": _d("Dónde se concretó la venta: en el local (in-store) o para llevar (takeaway).",
                       "Where the sale happened: in-store or takeaway.",
                       "Onde a venda ocorreu: no local (in-store) ou para levar (takeaway)."),
     "owner": "Equipo de Datos de Ventas", "datasets": [_CAF_KEY]},
    {"term_id": "importe_total", "name": _d("Importe total", "Total amount", "Valor total"),
     "definition": _d("Monto final de la transacción: cantidad de unidades por precio unitario.",
                       "Final transaction amount: number of units times unit price.",
                       "Valor final da transação: quantidade de unidades vezes preço unitário."),
     "owner": "Equipo de Datos de Ventas", "datasets": [_CAF_KEY]},
]


# ---------------------------------------------------------------------------
# Registro de datasets de ejemplo
# ---------------------------------------------------------------------------
SAMPLES: dict[str, dict] = {
    _RAL_KEY: {
        "file": "rotulado_de_alimentos_2026.csv",
        "name": _d("Rotulado de alimentos 2026", "Food labeling 2026", "Rotulagem de alimentos 2026"),
        "domain": _d("Regulación alimentaria", "Food regulation", "Regulação alimentar"),
        "description": _d(
            "Control bromatológico real: 284 análisis de rotulado y composición de productos alimenticios.",
            "Real food-safety control: 284 labeling and composition analyses of food products.",
            "Controle bromatológico real: 284 análises de rotulagem e composição de produtos alimentícios."),
        "owner": _d("Regulación / Cumplimiento Alimentario", "Food Regulation / Compliance", "Regulação / Conformidade Alimentar"),
        "steward": _d("Equipo de Calidad y Cumplimiento", "Quality & Compliance Team", "Equipe de Qualidade e Conformidade"),
        "classification": "Pública",
        "refresh": _d("mensual", "monthly", "mensal"),
        "source": _d(
            "Datos públicos de control bromatológico de alimentos (Uruguay, 2026); Reglamento Bromatológico Nacional (RUNAEV, Decreto 466/009).",
            "Public food-safety control data (Uruguay, 2026); National Food Regulation (RUNAEV, Decree 466/009).",
            "Dados públicos de controle bromatológico de alimentos (Uruguai, 2026); Regulamento Bromatológico Nacional (RUNAEV, Decreto 466/009)."),
        "source_url": None,
        "license": _d("Datos abiertos de gobierno (Uruguay)", "Open government data (Uruguay)", "Dados abertos de governo (Uruguai)"),
        "columns": _RAL_COLUMNS, "rules": _RAL_RULES, "terms": _RAL_TERMS,
    },
    _CAF_KEY: {
        "file": "dirty_cafe_sales.csv",
        "name": _d("Dirty Cafe Sales (Kaggle)", "Dirty Cafe Sales (Kaggle)", "Dirty Cafe Sales (Kaggle)"),
        "domain": _d("Ventas / Punto de venta", "Sales / Point of sale", "Vendas / Ponto de venda"),
        "description": _d(
            "10.000 transacciones sintéticas de una cafetería, con errores inyectados a propósito (nulos, \"ERROR\", \"UNKNOWN\") para practicar gobierno de datos.",
            "10,000 synthetic café transactions, with errors injected on purpose (nulls, \"ERROR\", \"UNKNOWN\") to practice data governance.",
            "10.000 transações sintéticas de uma cafeteria, com erros injetados de propósito (nulos, \"ERROR\", \"UNKNOWN\") para praticar governança de dados."),
        "owner": _d("Operaciones / Punto de Venta", "Operations / Point of Sale", "Operações / Ponto de Venda"),
        "steward": _d("Equipo de Datos de Ventas", "Sales Data Team", "Equipe de Dados de Vendas"),
        "classification": "Pública",
        "refresh": _d("diario", "daily", "diário"),
        "source": _d(
            "Kaggle · \"Dirty Cafe Sales\" por Ahmed Mohamed · licencia CC BY-SA 4.0.",
            "Kaggle · \"Dirty Cafe Sales\" by Ahmed Mohamed · CC BY-SA 4.0 license.",
            "Kaggle · \"Dirty Cafe Sales\" por Ahmed Mohamed · licença CC BY-SA 4.0."),
        "source_url": "https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training",
        "license": _d("CC BY-SA 4.0 (requiere atribución)", "CC BY-SA 4.0 (attribution required)", "CC BY-SA 4.0 (requer atribuição)"),
        "columns": _CAF_COLUMNS, "rules": _CAF_RULES, "terms": _CAF_TERMS,
    },
}


def sample_keys() -> list[str]:
    return list(SAMPLES.keys())


def _res(v, lang: str):
    return v.get(lang, v.get("es")) if isinstance(v, dict) else v


def sample_meta(key: str, lang: str = "es") -> dict:
    s = SAMPLES[key]
    return {
        "key": key,
        "name": _res(s["name"], lang), "domain": _res(s["domain"], lang),
        "description": _res(s["description"], lang), "owner": _res(s["owner"], lang),
        "steward": _res(s["steward"], lang), "classification": s["classification"],
        "refresh": _res(s["refresh"], lang), "source": _res(s["source"], lang),
        "source_url": s["source_url"], "license": _res(s["license"], lang),
        "file": s["file"],
    }


def load_sample_table(key: str) -> pd.DataFrame:
    path = os.path.join(_SAMPLES_DIR, SAMPLES[key]["file"])
    return pd.read_csv(path)


def sample_dictionary_df(key: str, lang: str = "es") -> pd.DataFrame:
    rows = []
    for c in SAMPLES[key]["columns"]:
        rows.append({
            "column": c["column"], "type": c["type"], "pii": c["pii"],
            "business_term": c["term"], "description": c["d"].get(lang, c["d"]["es"]),
        })
    return pd.DataFrame(rows)


def sample_quality_results(key: str, lang: str = "es") -> pd.DataFrame:
    df = load_sample_table(key)
    return evaluate_rules(SAMPLES[key]["rules"], {key: df}, lang)


def sample_glossary_df(key: str, lang: str = "es") -> pd.DataFrame:
    rows = []
    for t in SAMPLES[key]["terms"]:
        rows.append({
            "term_id": t["term_id"], "term": t["name"].get(lang, t["name"]["es"]),
            "definition": t["definition"].get(lang, t["definition"]["es"]),
            "owner": t["owner"], "linked_datasets": ", ".join(t["datasets"]),
        })
    return pd.DataFrame(rows)


def sample_catalog_row(key: str, lang: str = "es") -> dict:
    m = sample_meta(key, lang)
    df = load_sample_table(key)
    return {
        "dataset": key, "domain": m["domain"], "description": m["description"],
        "owner": m["owner"], "steward": m["steward"], "classification": m["classification"],
        "source": m["source"], "refresh": m["refresh"],
        "rows": int(len(df)), "columns": len(SAMPLES[key]["columns"]),
    }


def sample_governance_tables(key: str, lang: str = "es") -> dict[str, pd.DataFrame]:
    """Paquete completo del dataset de ejemplo, listo para exportar o servir
    por API: datos crudos, diccionario, resultados de calidad y glosario."""
    results = sample_quality_results(key, lang)
    return {
        "data": load_sample_table(key),
        "dictionary": sample_dictionary_df(key, lang),
        "quality_results": results,
        "glossary": sample_glossary_df(key, lang),
    }
