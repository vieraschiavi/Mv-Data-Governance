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


def _no_duplicate_rows():
    """Unicidad a nivel de fila completa — para datasets sin una columna que
    sirva de clave natural (ej. un registro de contacto sin ID de cliente)."""
    def check(df: pd.DataFrame):
        n = len(df)
        nbad = int(df.duplicated().sum())
        return (100.0 * (n - nbad) / n if n else 100.0, nbad)
    return check


def _implies_equals(if_col: str, if_value, then_col: str, then_value):
    """Regla de negocio condicional: cuando ``if_col`` == ``if_value``,
    ``then_col`` debe valer ``then_value`` (ej.: si nunca se contactó antes,
    el resultado de la campaña anterior tiene que ser 'unknown', no otra cosa)."""
    def check(df: pd.DataFrame):
        subset = df[df[if_col] == if_value]
        n = len(subset)
        if n == 0:
            return (100.0, 0)
        bad = int((subset[then_col] != then_value).sum())
        return (100.0 * (n - bad) / n, bad)
    return check


def _in_range(col: str, lo: float, hi: float):
    def check(df: pd.DataFrame):
        n = len(df)
        vals = pd.to_numeric(df[col], errors="coerce")
        bad = int((vals.isna() | (vals < lo) | (vals > hi)).sum())
        return (100.0 * (n - bad) / n if n else 100.0, bad)
    return check


def _subset_completeness(when_col: str, when_in: set, then_col: str):
    """Regla de negocio condicional: cuando ``when_col`` ∈ ``when_in``,
    ``then_col`` debe estar informado (no nulo ni vacío). Las filas fuera
    de la condición no cuentan — no son falsos positivos."""
    def check(df: pd.DataFrame):
        subset = df[df[when_col].isin(when_in)]
        n = len(subset)
        if n == 0:
            return (100.0, 0)
        vals = subset[then_col].astype(str).str.strip()
        bad = int((subset[then_col].isna() | (vals == "")).sum())
        return (100.0 * (n - bad) / n, bad)
    return check


def _valid_yyyymmdd(col: str):
    """Fecha válida en el formato compacto YYYYMMDD que usa la FDA (evita el
    falso 'válido' de interpretar 20090601 como un entero de nanosegundos)."""
    def check(df: pd.DataFrame):
        n = len(df)
        parsed = pd.to_datetime(df[col].astype("Int64").astype(str),
                                format="%Y%m%d", errors="coerce")
        nbad = int(parsed.isna().sum())
        return (100.0 * (n - nbad) / n if n else 100.0, nbad)
    return check


def _listing_current_yyyymmdd(when_col: str, when_value, then_col: str):
    """Puntualidad: cuando ``when_col`` == ``when_value`` (producto terminado),
    ``then_col`` debe tener fecha YYYYMMDD informada y no vencida a hoy."""
    def check(df: pd.DataFrame):
        subset = df[df[when_col] == when_value]
        n = len(subset)
        if n == 0:
            return (100.0, 0)
        parsed = pd.to_datetime(subset[then_col].astype("Int64").astype(str),
                                format="%Y%m%d", errors="coerce")
        bad = int((parsed.isna() | (parsed < pd.Timestamp.now().normalize())).sum())
        return (100.0 * (n - bad) / n, bad)
    return check


def _matches_pattern(col: str, pattern: str):
    def check(df: pd.DataFrame):
        n = len(df)
        ok = df[col].astype(str).str.match(pattern, na=False)
        nbad = int((~ok).sum())
        return (100.0 * (n - nbad) / n if n else 100.0, nbad)
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
# 3. Bank Marketing (UCI) — campaña real de marketing telefónico de un banco
#    portugués (Moro, Rita & Cortez, 2014). Sin columna de ID de cliente: la
#    unicidad se verifica a nivel de fila completa.
# ---------------------------------------------------------------------------
_BNK_KEY = "bank_marketing_uci"

_BNK_RULES = [
    Rule("BNK-01", _BNK_KEY, "(fila completa)", "uniqueness",
         _d("sin filas duplicadas (no hay columna de ID de cliente; se compara la fila entera)",
            "no duplicate rows (there's no customer ID column; the whole row is compared)",
            "sem linhas duplicadas (não há coluna de ID de cliente; compara-se a linha inteira)"),
         _no_duplicate_rows(), 99.5),
    Rule("BNK-02", _BNK_KEY, "job", "completeness",
         _d("job completo (sin \"unknown\")", "job complete (no \"unknown\")", "job completo (sem \"unknown\")"),
         _not_null_or_markers("job", ("unknown",)), 99.5),
    Rule("BNK-03", _BNK_KEY, "education", "completeness",
         _d("education completo (sin \"unknown\")", "education complete (no \"unknown\")", "education completo (sem \"unknown\")"),
         _not_null_or_markers("education", ("unknown",)), 97.0),
    Rule("BNK-04", _BNK_KEY, "contact", "completeness",
         _d("contact completo (sin \"unknown\")", "contact complete (no \"unknown\")", "contact completo (sem \"unknown\")"),
         _not_null_or_markers("contact", ("unknown",)), 90.0),
    Rule("BNK-05", _BNK_KEY, "poutcome", "consistency",
         _d("si previous=0 (nunca contactado antes), poutcome debe ser \"unknown\" (regla de negocio, no un chequeo de nulos)",
            "if previous=0 (never contacted before), poutcome must be \"unknown\" (business rule, not a raw null check)",
            "se previous=0 (nunca contatado antes), poutcome deve ser \"unknown\" (regra de negócio, não um chequeo de nulos)"),
         _implies_equals("previous", 0, "poutcome", "unknown"), 99.5),
    Rule("BNK-06", _BNK_KEY, "age", "validity",
         _d("age dentro de un rango bancario razonable (18–100 años)",
            "age within a reasonable banking range (18–100 years)",
            "age dentro de uma faixa bancária razoável (18–100 anos)"),
         _in_range("age", 18, 100), 99.5),
]

_BNK_COLUMNS = [
    {"column": "age", "type": "int", "pii": False, "term": "cliente_bancario",
     "d": _d("Edad del cliente contactado.", "Age of the contacted client.", "Idade do cliente contatado.")},
    {"column": "job", "type": "string", "pii": False, "term": "cliente_bancario",
     "d": _d("Tipo de ocupación del cliente.", "Client's occupation type.", "Tipo de ocupação do cliente.")},
    {"column": "marital", "type": "string", "pii": False, "term": "cliente_bancario",
     "d": _d("Estado civil del cliente.", "Client's marital status.", "Estado civil do cliente.")},
    {"column": "education", "type": "string", "pii": False, "term": "cliente_bancario",
     "d": _d("Nivel educativo del cliente.", "Client's education level.", "Nível educacional do cliente.")},
    {"column": "default", "type": "string", "pii": False, "term": "cliente_bancario",
     "d": _d("Si el cliente tiene crédito en mora.", "Whether the client has credit in default.", "Se o cliente tem crédito em atraso.")},
    {"column": "balance", "type": "int", "pii": False, "term": "cliente_bancario",
     "d": _d("Saldo promedio anual en euros (puede ser negativo: descubierto).", "Average yearly balance in euros (can be negative: overdraft).", "Saldo médio anual em euros (pode ser negativo: cheque especial).")},
    {"column": "housing", "type": "string", "pii": False, "term": "cliente_bancario",
     "d": _d("Si el cliente tiene préstamo hipotecario.", "Whether the client has a housing loan.", "Se o cliente tem empréstimo habitacional.")},
    {"column": "loan", "type": "string", "pii": False, "term": "cliente_bancario",
     "d": _d("Si el cliente tiene préstamo personal.", "Whether the client has a personal loan.", "Se o cliente tem empréstimo pessoal.")},
    {"column": "contact", "type": "string", "pii": False, "term": "campana_marketing",
     "d": _d("Tipo de contacto usado (celular, teléfono fijo).", "Type of contact used (cellular, landline).", "Tipo de contato usado (celular, fixo).")},
    {"column": "day", "type": "int", "pii": False, "term": "campana_marketing",
     "d": _d("Día del mes del último contacto.", "Day of month of the last contact.", "Dia do mês do último contato.")},
    {"column": "month", "type": "string", "pii": False, "term": "campana_marketing",
     "d": _d("Mes del último contacto.", "Month of the last contact.", "Mês do último contato.")},
    {"column": "duration", "type": "int", "pii": False, "term": "duracion_contacto",
     "d": _d("Duración del último contacto, en segundos.", "Duration of the last contact, in seconds.", "Duração do último contato, em segundos.")},
    {"column": "campaign", "type": "int", "pii": False, "term": "campana_marketing",
     "d": _d("Cantidad de contactos realizados en esta campaña con este cliente.", "Number of contacts made in this campaign with this client.", "Quantidade de contatos feitos nesta campanha com este cliente.")},
    {"column": "pdays", "type": "int", "pii": False, "term": "resultado_campana_anterior",
     "d": _d("Días desde el último contacto de una campaña previa (-1 = nunca contactado).", "Days since the last contact of a previous campaign (-1 = never contacted).", "Dias desde o último contato de uma campanha anterior (-1 = nunca contatado).")},
    {"column": "previous", "type": "int", "pii": False, "term": "resultado_campana_anterior",
     "d": _d("Cantidad de contactos realizados antes de esta campaña.", "Number of contacts made before this campaign.", "Quantidade de contatos feitos antes desta campanha.")},
    {"column": "poutcome", "type": "string", "pii": False, "term": "resultado_campana_anterior",
     "d": _d("Resultado de la campaña de marketing anterior.", "Outcome of the previous marketing campaign.", "Resultado da campanha de marketing anterior.")},
    {"column": "y", "type": "string", "pii": False, "term": "deposito_plazo",
     "d": _d("Si el cliente contrató un depósito a plazo (variable objetivo).", "Whether the client subscribed a term deposit (target variable).", "Se o cliente contratou um depósito a prazo (variável alvo).")},
]

_BNK_TERMS = [
    {"term_id": "cliente_bancario", "name": _d("Cliente bancario", "Bank client", "Cliente bancário"),
     "definition": _d("Persona contactada por el banco en una campaña de marketing, descrita por su perfil demográfico y financiero (sin identificarla directamente: sin nombre ni número de cuenta).",
                       "Person contacted by the bank in a marketing campaign, described by their demographic and financial profile (without directly identifying them: no name or account number).",
                       "Pessoa contatada pelo banco numa campanha de marketing, descrita por seu perfil demográfico e financeiro (sem identificá-la diretamente: sem nome nem número de conta)."),
     "owner": "Equipo de Datos de Marketing", "datasets": [_BNK_KEY]},
    {"term_id": "campana_marketing", "name": _d("Campaña de marketing", "Marketing campaign", "Campanha de marketing"),
     "definition": _d("Serie de contactos telefónicos hechos a un cliente para ofrecerle un producto — acá, un depósito a plazo.",
                       "Series of phone contacts made to a client to offer them a product — here, a term deposit.",
                       "Série de contatos telefônicos feitos a um cliente para oferecer um produto — aqui, um depósito a prazo."),
     "owner": "Equipo de Datos de Marketing", "datasets": [_BNK_KEY]},
    {"term_id": "resultado_campana_anterior", "name": _d("Resultado de campaña anterior", "Previous campaign outcome", "Resultado de campanha anterior"),
     "definition": _d("Qué pasó la última vez que se contactó a este cliente en otra campaña. Vale \"unknown\" cuando nunca se lo contactó antes — no es un dato faltante.",
                       "What happened the last time this client was contacted in another campaign. It's \"unknown\" when the client was never contacted before — not a missing value.",
                       "O que aconteceu na última vez que este cliente foi contatado em outra campanha. É \"unknown\" quando o cliente nunca foi contatado antes — não é um dado faltante."),
     "owner": "Equipo de Datos de Marketing", "datasets": [_BNK_KEY]},
    {"term_id": "duracion_contacto", "name": _d("Duración del contacto", "Contact duration", "Duração do contato"),
     "definition": _d("Cuánto duró la llamada, en segundos. Muy correlacionado con el resultado: una llamada de 0 segundos nunca termina en venta.",
                       "How long the call lasted, in seconds. Strongly correlated with the outcome: a 0-second call never ends in a sale.",
                       "Quanto durou a ligação, em segundos. Muito correlacionado com o resultado: uma ligação de 0 segundos nunca termina em venda."),
     "owner": "Equipo de Datos de Marketing", "datasets": [_BNK_KEY]},
    {"term_id": "deposito_plazo", "name": _d("Depósito a plazo", "Term deposit", "Depósito a prazo"),
     "definition": _d("Producto financiero que el banco intenta vender en esta campaña: el cliente inmoviliza dinero a cambio de una tasa de interés fija.",
                       "Financial product the bank is trying to sell in this campaign: the client locks in money in exchange for a fixed interest rate.",
                       "Produto financeiro que o banco tenta vender nesta campanha: o cliente imobiliza dinheiro em troca de uma taxa de juros fixa."),
     "owner": "Equipo de Datos de Marketing", "datasets": [_BNK_KEY]},
]


# ---------------------------------------------------------------------------
# 4. Catálogo de medicamentos — laboratorios multinacionales (openFDA NDC).
#    Datos REALES y de dominio público del registro nacional de medicamentos
#    de EE.UU. (FDA), filtrados a 6 grupos farmacéuticos multinacionales.
#    Los defectos que encuentran las reglas son reales, no inyectados.
# ---------------------------------------------------------------------------
_MED_KEY = "medicamentos_openfda"
_MED_HUMAN = {"HUMAN PRESCRIPTION DRUG", "HUMAN OTC DRUG"}

_MED_RULES = [
    Rule("MED-01", _MED_KEY, "product_ndc", "uniqueness",
         _d("product_ndc debe ser estrictamente único: es LA clave del registro nacional (NDC)",
            "product_ndc must be strictly unique: it IS the national registry key (NDC)",
            "product_ndc deve ser estritamente único: é A chave do registro nacional (NDC)"),
         _unique("product_ndc"), 100.0),
    Rule("MED-02", _MED_KEY, "product_ndc", "validity",
         _d("product_ndc respeta el formato NDC (4-5 dígitos, guion, 3-4 dígitos)",
            "product_ndc follows the NDC format (4-5 digits, hyphen, 3-4 digits)",
            "product_ndc respeita o formato NDC (4-5 dígitos, hífen, 3-4 dígitos)"),
         _matches_pattern("product_ndc", r"^\d{4,5}-\d{3,4}$"), 99.5),
    Rule("MED-03", _MED_KEY, "generic_name", "completeness",
         _d("generic_name (principio activo / denominación común) siempre informado",
            "generic_name (active ingredient / common name) always present",
            "generic_name (princípio ativo / denominação comum) sempre informado"),
         _not_null_or_placeholder("generic_name", ()), 99.5),
    Rule("MED-04", _MED_KEY, "brand_name", "consistency",
         _d("medicamento de uso humano terminado ⇒ marca comercial informada (los graneles y semielaborados legítimamente no tienen)",
            "finished human-use drug ⇒ brand name present (bulk and semi-finished goods legitimately have none)",
            "medicamento de uso humano acabado ⇒ marca comercial informada (granéis e semiacabados legitimamente não têm)"),
         _subset_completeness("product_type", _MED_HUMAN, "brand_name"), 97.0),
    Rule("MED-05", _MED_KEY, "active_ingredients", "consistency",
         _d("medicamento de uso humano ⇒ principios activos con concentración declarados",
            "human-use drug ⇒ active ingredients with strength declared",
            "medicamento de uso humano ⇒ princípios ativos com concentração declarados"),
         _subset_completeness("product_type", _MED_HUMAN, "active_ingredients"), 95.0),
    Rule("MED-06", _MED_KEY, "pharm_class", "completeness",
         _d("clase farmacológica informada en medicamentos de uso humano (crítica para farmacovigilancia)",
            "pharmacological class present on human-use drugs (critical for pharmacovigilance)",
            "classe farmacológica informada em medicamentos de uso humano (crítica para farmacovigilância)"),
         _subset_completeness("product_type", _MED_HUMAN, "pharm_class"), 90.0),
    Rule("MED-07", _MED_KEY, "marketing_start_date", "validity",
         _d("marketing_start_date es una fecha YYYYMMDD válida",
            "marketing_start_date is a valid YYYYMMDD date",
            "marketing_start_date é uma data YYYYMMDD válida"),
         _valid_yyyymmdd("marketing_start_date"), 99.5),
    Rule("MED-08", _MED_KEY, "listing_expiration_date", "timeliness",
         _d("producto terminado ⇒ listado FDA vigente (fecha de expiración informada y no vencida)",
            "finished product ⇒ FDA listing current (expiration date present and not past due)",
            "produto acabado ⇒ listagem FDA vigente (data de expiração informada e não vencida)"),
         _listing_current_yyyymmdd("finished", True, "listing_expiration_date"), 95.0),
]

_MED_COLUMNS = [
    {"column": "product_ndc", "type": "string", "pii": False, "term": "ndc",
     "d": _d("Código nacional de medicamento (NDC): identificador único del producto ante la FDA.",
             "National Drug Code (NDC): the product's unique identifier before the FDA.",
             "Código nacional de medicamento (NDC): identificador único do produto perante a FDA.")},
    {"column": "brand_name", "type": "string", "pii": False, "term": "marca_comercial",
     "d": _d("Marca comercial del producto (vacía en genéricos, graneles y semielaborados).",
             "Product's commercial brand (empty on generics, bulk and semi-finished goods).",
             "Marca comercial do produto (vazia em genéricos, granéis e semiacabados).")},
    {"column": "generic_name", "type": "string", "pii": False, "term": "principio_activo",
     "d": _d("Denominación común / principio activo del medicamento.",
             "Common name / active ingredient of the drug.",
             "Denominação comum / princípio ativo do medicamento.")},
    {"column": "labeler_name", "type": "string", "pii": False, "term": "laboratorio_titular",
     "d": _d("Laboratorio titular del registro. Ojo: un mismo grupo aparece escrito de varias formas (45 variantes para 6 grupos) — caso ideal para la pestaña 🔗 MDM.",
             "Registration-holding laboratory. Note: the same group appears spelled several ways (45 variants for 6 groups) — an ideal case for the 🔗 MDM tab.",
             "Laboratório titular do registro. Atenção: o mesmo grupo aparece escrito de várias formas (45 variantes para 6 grupos) — caso ideal para a aba 🔗 MDM.")},
    {"column": "product_type", "type": "string", "pii": False, "term": "tipo_producto",
     "d": _d("Tipo de producto: receta, venta libre, vacuna, granel, semielaborado, etc.",
             "Product type: prescription, OTC, vaccine, bulk, for further processing, etc.",
             "Tipo de produto: receita, venda livre, vacina, granel, semiacabado, etc.")},
    {"column": "dosage_form", "type": "string", "pii": False, "term": "forma_farmaceutica",
     "d": _d("Forma farmacéutica: comprimido, solución, crema, inyectable…",
             "Dosage form: tablet, solution, cream, injectable…",
             "Forma farmacêutica: comprimido, solução, creme, injetável…")},
    {"column": "route", "type": "string", "pii": False, "term": "via_administracion",
     "d": _d("Vía(s) de administración (oral, tópica, intravenosa…).",
             "Route(s) of administration (oral, topical, intravenous…).",
             "Via(s) de administração (oral, tópica, intravenosa…).")},
    {"column": "marketing_category", "type": "string", "pii": False, "term": "categoria_comercializacion",
     "d": _d("Categoría regulatoria bajo la que se comercializa (NDA, ANDA, BLA, OTC monograph…).",
             "Regulatory category under which it is marketed (NDA, ANDA, BLA, OTC monograph…).",
             "Categoria regulatória sob a qual é comercializado (NDA, ANDA, BLA, OTC monograph…).")},
    {"column": "marketing_start_date", "type": "date", "pii": False, "term": "categoria_comercializacion",
     "d": _d("Fecha de inicio de comercialización (YYYYMMDD).", "Marketing start date (YYYYMMDD).",
             "Data de início de comercialização (YYYYMMDD).")},
    {"column": "marketing_end_date", "type": "date", "pii": False, "term": "categoria_comercializacion",
     "d": _d("Fecha de fin de comercialización — presente solo en productos discontinuados.",
             "Marketing end date — present only on discontinued products.",
             "Data de fim de comercialização — presente apenas em produtos descontinuados.")},
    {"column": "active_ingredients", "type": "string", "pii": False, "term": "principio_activo",
     "d": _d("Principios activos con su concentración, separados por «;».",
             "Active ingredients with their strength, separated by «;».",
             "Princípios ativos com sua concentração, separados por «;».")},
    {"column": "pharm_class", "type": "string", "pii": False, "term": "clase_farmacologica",
     "d": _d("Clase(s) farmacológica(s) FDA: mecanismo de acción, clase química y/o efecto fisiológico.",
             "FDA pharmacological class(es): mechanism of action, chemical class and/or physiologic effect.",
             "Classe(s) farmacológica(s) FDA: mecanismo de ação, classe química e/ou efeito fisiológico.")},
    {"column": "dea_schedule", "type": "string", "pii": False, "term": "tipo_producto",
     "d": _d("Lista DEA de sustancias controladas (CII–CV) — vacía si no es controlada.",
             "DEA controlled-substance schedule (CII–CV) — empty if not controlled.",
             "Lista DEA de substâncias controladas (CII–CV) — vazia se não é controlada.")},
    {"column": "finished", "type": "bool", "pii": False, "term": "tipo_producto",
     "d": _d("Si es producto terminado (True) o granel/semielaborado (False).",
             "Whether it's a finished product (True) or bulk/semi-finished (False).",
             "Se é produto acabado (True) ou granel/semiacabado (False).")},
    {"column": "listing_expiration_date", "type": "date", "pii": False, "term": "listado_fda",
     "d": _d("Hasta cuándo está vigente el listado del producto ante la FDA (YYYYMMDD).",
             "Until when the product's FDA listing is current (YYYYMMDD).",
             "Até quando a listagem do produto perante a FDA está vigente (YYYYMMDD).")},
]

_MED_TERMS = [
    {"term_id": "ndc", "name": _d("NDC (Código nacional de medicamento)", "NDC (National Drug Code)", "NDC (Código nacional de medicamento)"),
     "definition": _d("Identificador único que la FDA asigna a cada producto farmacéutico comercializado en EE.UU.: etiquetador-producto (y a nivel envase, presentación). Es la clave natural del catálogo.",
                       "Unique identifier the FDA assigns to every drug product marketed in the U.S.: labeler-product (and at package level, presentation). It is the catalog's natural key.",
                       "Identificador único que a FDA atribui a cada produto farmacêutico comercializado nos EUA: rotulador-produto (e no nível de embalagem, apresentação). É a chave natural do catálogo."),
     "owner": "Equipo de Datos Regulatorios", "datasets": [_MED_KEY]},
    {"term_id": "principio_activo", "name": _d("Principio activo", "Active ingredient", "Princípio ativo"),
     "definition": _d("Sustancia responsable del efecto terapéutico del medicamento, declarada con su concentración (ej. «SILDENAFIL (100 mg/1)»).",
                       "Substance responsible for the drug's therapeutic effect, declared with its strength (e.g. «SILDENAFIL (100 mg/1)»).",
                       "Substância responsável pelo efeito terapêutico do medicamento, declarada com sua concentração (ex. «SILDENAFIL (100 mg/1)»)."),
     "owner": "Equipo de Datos Regulatorios", "datasets": [_MED_KEY]},
    {"term_id": "laboratorio_titular", "name": _d("Laboratorio titular", "Labeler", "Laboratório titular"),
     "definition": _d("Empresa responsable del registro del producto ante la FDA. Un grupo multinacional opera con múltiples razones sociales (Pfizer Inc, Pfizer Ireland, Pfizer Consumer…): unificarlas es un problema clásico de datos maestros (MDM).",
                       "Company responsible for the product's FDA registration. A multinational group operates under multiple legal entities (Pfizer Inc, Pfizer Ireland, Pfizer Consumer…): unifying them is a classic master-data (MDM) problem.",
                       "Empresa responsável pelo registro do produto perante a FDA. Um grupo multinacional opera com múltiplas razões sociais (Pfizer Inc, Pfizer Ireland, Pfizer Consumer…): unificá-las é um problema clássico de dados mestres (MDM)."),
     "owner": "Equipo de Datos Regulatorios", "datasets": [_MED_KEY]},
    {"term_id": "forma_farmaceutica", "name": _d("Forma farmacéutica", "Dosage form", "Forma farmacêutica"),
     "definition": _d("Presentación física en la que se administra el medicamento: comprimido, cápsula, solución, crema, inyectable, parche…",
                       "Physical presentation in which the drug is administered: tablet, capsule, solution, cream, injectable, patch…",
                       "Apresentação física na qual o medicamento é administrado: comprimido, cápsula, solução, creme, injetável, adesivo…"),
     "owner": "Equipo de Datos Regulatorios", "datasets": [_MED_KEY]},
    {"term_id": "via_administracion", "name": _d("Vía de administración", "Route of administration", "Via de administração"),
     "definition": _d("Camino por el que el medicamento entra al organismo: oral, tópica, intravenosa, oftálmica… Un producto puede tener más de una.",
                       "Path by which the drug enters the body: oral, topical, intravenous, ophthalmic… A product can have more than one.",
                       "Caminho pelo qual o medicamento entra no organismo: oral, tópica, intravenosa, oftálmica… Um produto pode ter mais de uma."),
     "owner": "Equipo de Datos Regulatorios", "datasets": [_MED_KEY]},
    {"term_id": "clase_farmacologica", "name": _d("Clase farmacológica", "Pharmacological class", "Classe farmacológica"),
     "definition": _d("Clasificación FDA del medicamento por mecanismo de acción, clase química o efecto fisiológico — la base de la farmacovigilancia y de los análisis de interacciones.",
                       "FDA classification of the drug by mechanism of action, chemical class or physiologic effect — the basis of pharmacovigilance and interaction analyses.",
                       "Classificação FDA do medicamento por mecanismo de ação, classe química ou efeito fisiológico — a base da farmacovigilância e das análises de interações."),
     "owner": "Equipo de Datos Regulatorios", "datasets": [_MED_KEY]},
    {"term_id": "tipo_producto", "name": _d("Tipo de producto", "Product type", "Tipo de produto"),
     "definition": _d("Categoría del registro: medicamento humano de receta o venta libre, vacuna, derivado de plasma, granel o semielaborado. Varias reglas de calidad aplican solo a los de uso humano terminados.",
                       "Registry category: human prescription or OTC drug, vaccine, plasma derivative, bulk or for further processing. Several quality rules apply only to finished human-use products.",
                       "Categoria do registro: medicamento humano de receita ou venda livre, vacina, derivado de plasma, granel ou semiacabado. Várias regras de qualidade aplicam-se apenas aos de uso humano acabados."),
     "owner": "Equipo de Datos Regulatorios", "datasets": [_MED_KEY]},
    {"term_id": "categoria_comercializacion", "name": _d("Categoría de comercialización", "Marketing category", "Categoria de comercialização"),
     "definition": _d("Vía regulatoria bajo la que el producto llegó al mercado: NDA (droga nueva), ANDA (genérico), BLA (biológico), monografía OTC…",
                       "Regulatory path under which the product reached the market: NDA (new drug), ANDA (generic), BLA (biologic), OTC monograph…",
                       "Via regulatória sob a qual o produto chegou ao mercado: NDA (droga nova), ANDA (genérico), BLA (biológico), monografia OTC…"),
     "owner": "Equipo de Datos Regulatorios", "datasets": [_MED_KEY]},
    {"term_id": "listado_fda", "name": _d("Listado FDA vigente", "Current FDA listing", "Listagem FDA vigente"),
     "definition": _d("Los laboratorios deben renovar anualmente el listado de cada producto ante la FDA. Un listado vencido o sin fecha es una señal de puntualidad: el registro puede estar desactualizado.",
                       "Labs must renew each product's FDA listing yearly. An expired or missing listing date is a timeliness signal: the record may be out of date.",
                       "Os laboratórios devem renovar anualmente a listagem de cada produto perante a FDA. Uma listagem vencida ou sem data é um sinal de pontualidade: o registro pode estar desatualizado."),
     "owner": "Equipo de Datos Regulatorios", "datasets": [_MED_KEY]},
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
    _BNK_KEY: {
        "file": "bank_marketing_uci.csv",
        "name": _d("Bank Marketing (UCI)", "Bank Marketing (UCI)", "Bank Marketing (UCI)"),
        "domain": _d("Banca / Marketing directo", "Banking / Direct Marketing", "Banco / Marketing direto"),
        "description": _d(
            "4.521 contactos reales de una campaña de marketing telefónico de un banco portugués, para ofrecer un depósito a plazo.",
            "4,521 real contacts from a Portuguese bank's phone marketing campaign, offering a term deposit.",
            "4.521 contatos reais de uma campanha de marketing telefônico de um banco português, oferecendo um depósito a prazo."),
        "owner": _d("Marketing / Banca Comercial", "Marketing / Retail Banking", "Marketing / Banco Comercial"),
        "steward": _d("Equipo de Datos de Marketing", "Marketing Data Team", "Equipe de Dados de Marketing"),
        "classification": "Confidencial",
        "refresh": _d("por campaña", "per campaign", "por campanha"),
        "source": _d(
            "UCI Machine Learning Repository · \"Bank Marketing\" (S. Moro, P. Rita, P. Cortez, 2014) · licencia CC BY 4.0.",
            "UCI Machine Learning Repository · \"Bank Marketing\" (S. Moro, P. Rita, P. Cortez, 2014) · CC BY 4.0 license.",
            "UCI Machine Learning Repository · \"Bank Marketing\" (S. Moro, P. Rita, P. Cortez, 2014) · licença CC BY 4.0."),
        "source_url": "https://archive.ics.uci.edu/dataset/222/bank+marketing",
        "license": _d("CC BY 4.0 (requiere atribución)", "CC BY 4.0 (attribution required)", "CC BY 4.0 (requer atribuição)"),
        "classification_note": _d(
            "El dataset en sí es público y anonimizado en el origen (sin nombre ni número de cuenta). Se clasifica "
            "Confidencial en este catálogo a propósito: es el criterio correcto para datos demográficos y "
            "financieros a nivel de persona dentro de un banco real, aunque no disparen el detector de PII.",
            "The dataset itself is public and anonymized at the source (no name or account number). It's classified "
            "Confidential in this catalog on purpose: that's the right call for person-level demographic and "
            "financial data inside a real bank, even when it doesn't trigger the PII detector.",
            "O dataset em si é público e anonimizado na origem (sem nome nem número de conta). É classificado "
            "Confidencial neste catálogo de propósito: é o critério correto para dados demográficos e financeiros "
            "a nível de pessoa dentro de um banco real, mesmo sem disparar o detector de PII."),
        "columns": _BNK_COLUMNS, "rules": _BNK_RULES, "terms": _BNK_TERMS,
    },
    _MED_KEY: {
        "file": "medicamentos_openfda.csv",
        "name": _d("Medicamentos — laboratorios multinacionales (openFDA)",
                   "Drug products — multinational labs (openFDA)",
                   "Medicamentos — laboratórios multinacionais (openFDA)"),
        "domain": _d("Farmacéutica / Regulatorio", "Pharmaceutical / Regulatory", "Farmacêutica / Regulatório"),
        "description": _d(
            "1.546 productos farmacéuticos reales registrados ante la FDA por 6 grupos multinacionales "
            "(Pfizer, Novartis, Bayer, Sanofi, GSK, AstraZeneca), del NDC Directory. Los defectos que "
            "detectan las reglas son reales del registro público — no fueron inyectados.",
            "1,546 real drug products registered with the FDA by 6 multinational groups "
            "(Pfizer, Novartis, Bayer, Sanofi, GSK, AstraZeneca), from the NDC Directory. The defects "
            "the rules detect are real, from the public registry — none were injected.",
            "1.546 produtos farmacêuticos reais registrados na FDA por 6 grupos multinacionais "
            "(Pfizer, Novartis, Bayer, Sanofi, GSK, AstraZeneca), do NDC Directory. Os defeitos que "
            "as regras detectam são reais do registro público — não foram injetados."),
        "owner": _d("Asuntos Regulatorios / Farmacovigilancia", "Regulatory Affairs / Pharmacovigilance",
                    "Assuntos Regulatórios / Farmacovigilância"),
        "steward": _d("Equipo de Datos Regulatorios", "Regulatory Data Team", "Equipe de Dados Regulatórios"),
        "classification": "Pública",
        "refresh": _d("diario (la FDA actualiza el NDC Directory a diario)",
                      "daily (the FDA refreshes the NDC Directory daily)",
                      "diário (a FDA atualiza o NDC Directory diariamente)"),
        "source": _d(
            "openFDA · NDC Directory (api.fda.gov/drug/ndc) · descargado 2026-07-14 · dominio público (gobierno de EE.UU.).",
            "openFDA · NDC Directory (api.fda.gov/drug/ndc) · downloaded 2026-07-14 · public domain (U.S. government).",
            "openFDA · NDC Directory (api.fda.gov/drug/ndc) · baixado em 2026-07-14 · domínio público (governo dos EUA)."),
        "source_url": "https://open.fda.gov/apis/drug/ndc/",
        "license": _d("Dominio público (obra del gobierno de EE.UU.); openFDA advierte que los datos no están validados para decisiones médicas",
                      "Public domain (U.S. government work); openFDA warns the data is not validated for medical decisions",
                      "Domínio público (obra do governo dos EUA); a openFDA adverte que os dados não são validados para decisões médicas"),
        "columns": _MED_COLUMNS, "rules": _MED_RULES, "terms": _MED_TERMS,
    },
}


def sample_keys() -> list[str]:
    return list(SAMPLES.keys())


def _res(v, lang: str):
    return v.get(lang, v.get("es")) if isinstance(v, dict) else v


def sample_meta(key: str, lang: str = "es") -> dict:
    s = SAMPLES[key]
    note = s.get("classification_note")
    return {
        "key": key,
        "name": _res(s["name"], lang), "domain": _res(s["domain"], lang),
        "description": _res(s["description"], lang), "owner": _res(s["owner"], lang),
        "steward": _res(s["steward"], lang), "classification": s["classification"],
        "refresh": _res(s["refresh"], lang), "source": _res(s["source"], lang),
        "source_url": s["source_url"], "license": _res(s["license"], lang),
        "classification_note": _res(note, lang) if note else None,
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
