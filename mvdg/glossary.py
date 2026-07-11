"""
MV Data Governance · Glosario de negocio trilingüe.

Una definición oficial por término, con dueño y datasets vinculados. El
término es la fuente única de verdad para reportes y tableros de BI.
"""
from __future__ import annotations

import pandas as pd

_TERMS: list[dict] = [
    {
        "term_id": "customer",
        "name": {"es": "Cliente", "en": "Customer", "pt": "Cliente"},
        "definition": {
            "es": "Persona o empresa con al menos una compra o registro activo.",
            "en": "Person or company with at least one purchase or active signup.",
            "pt": "Pessoa ou empresa com pelo menos uma compra ou cadastro ativo.",
        },
        "owner": "Gerencia Comercial",
        "datasets": ["dim_customers", "fct_sales"],
    },
    {
        "term_id": "product",
        "name": {"es": "Producto", "en": "Product", "pt": "Produto"},
        "definition": {
            "es": "Artículo comercializable identificado con SKU único.",
            "en": "Sellable item identified by a unique SKU.",
            "pt": "Item comercializável identificado por SKU único.",
        },
        "owner": "Gerencia de Operaciones",
        "datasets": ["dim_products", "fct_sales"],
    },
    {
        "term_id": "sale",
        "name": {"es": "Venta", "en": "Sale", "pt": "Venda"},
        "definition": {
            "es": "Transacción confirmada de uno o más productos a un cliente.",
            "en": "Confirmed transaction of one or more products to a customer.",
            "pt": "Transação confirmada de um ou mais produtos a um cliente.",
        },
        "owner": "Gerencia Comercial",
        "datasets": ["fct_sales"],
    },
    {
        "term_id": "payment",
        "name": {"es": "Pago", "en": "Payment", "pt": "Pagamento"},
        "definition": {
            "es": "Importe aplicado a una venta por cualquier método habilitado.",
            "en": "Amount applied to a sale through any enabled method.",
            "pt": "Valor aplicado a uma venda por qualquer método habilitado.",
        },
        "owner": "Gerencia de Finanzas",
        "datasets": ["fct_payments"],
    },
    {
        "term_id": "revenue",
        "name": {"es": "Ingreso", "en": "Revenue", "pt": "Receita"},
        "definition": {
            "es": "Suma de importes de ventas confirmadas, neta de devoluciones.",
            "en": "Sum of confirmed sale amounts, net of returns.",
            "pt": "Soma dos valores de vendas confirmadas, líquida de devoluções.",
        },
        "owner": "Gerencia de Finanzas",
        "datasets": ["fct_sales", "fct_payments"],
    },
    {
        "term_id": "segment",
        "name": {"es": "Segmento", "en": "Segment", "pt": "Segmento"},
        "definition": {
            "es": "Agrupación comercial oficial: Retail, Corporate o SMB.",
            "en": "Official commercial grouping: Retail, Corporate or SMB.",
            "pt": "Agrupamento comercial oficial: Retail, Corporate ou SMB.",
        },
        "owner": "Gerencia Comercial",
        "datasets": ["dim_customers"],
    },
    {
        "term_id": "channel",
        "name": {"es": "Canal", "en": "Channel", "pt": "Canal"},
        "definition": {
            "es": "Medio por el que se concreta la venta: web, tienda, app o mayorista.",
            "en": "Medium through which the sale happens: web, store, app or wholesale.",
            "pt": "Meio pelo qual a venda ocorre: web, loja, app ou atacado.",
        },
        "owner": "Gerencia Comercial",
        "datasets": ["fct_sales"],
    },
    {
        "term_id": "quality_index",
        "name": {"es": "Índice de calidad", "en": "Quality index", "pt": "Índice de qualidade"},
        "definition": {
            "es": "Promedio 0–100 de los puntajes de todas las reglas de calidad activas.",
            "en": "0–100 average of the scores of all active quality rules.",
            "pt": "Média 0–100 das pontuações de todas as regras de qualidade ativas.",
        },
        "owner": "Oficina de Datos",
        "datasets": ["dim_customers", "dim_products", "fct_sales", "fct_payments"],
    },
]


def glossary_df(lang: str = "es") -> pd.DataFrame:
    rows = [{
        "term_id": t["term_id"],
        "term": t["name"].get(lang, t["name"]["es"]),
        "definition": t["definition"].get(lang, t["definition"]["es"]),
        "owner": t["owner"],
        "linked_datasets": ", ".join(t["datasets"]),
    } for t in _TERMS]
    return pd.DataFrame(rows)


def term_count() -> int:
    return len(_TERMS)
