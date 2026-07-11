"""
MV Data Governance · Catálogo de datos y diccionario de columnas.

El catálogo es el inventario único de datasets gobernados: quién es el dueño,
quién el steward, a qué dominio pertenece, cómo se clasifica (Pública /
Interna / Confidencial / PII) y qué tan fresco está. Las descripciones viven
en los tres idiomas (es/en/pt) y se resuelven con ``lang``.
"""
from __future__ import annotations

import pandas as pd

from .demo_data import TODAY, load_demo_tables

# Clasificaciones normalizadas
PUBLIC, INTERNAL, CONFIDENTIAL, PII = "Pública", "Interna", "Confidencial", "PII"

_DATASETS = [
    {
        "dataset": "dim_customers",
        "domain": {"es": "Clientes", "en": "Customers", "pt": "Clientes"},
        "description": {
            "es": "Maestro de clientes con datos de contacto y segmento.",
            "en": "Customer master with contact details and segment.",
            "pt": "Cadastro mestre de clientes com contato e segmento.",
        },
        "owner": "Gerencia Comercial",
        "steward": "M. Viera",
        "classification": PII,
        "refresh": "daily",
        "source": "CRM",
    },
    {
        "dataset": "dim_products",
        "domain": {"es": "Productos", "en": "Products", "pt": "Produtos"},
        "description": {
            "es": "Catálogo de productos con precio y estado.",
            "en": "Product catalog with price and status.",
            "pt": "Catálogo de produtos com preço e status.",
        },
        "owner": "Gerencia de Operaciones",
        "steward": "R. Costa",
        "classification": INTERNAL,
        "refresh": "weekly",
        "source": "ERP",
    },
    {
        "dataset": "fct_sales",
        "domain": {"es": "Ventas", "en": "Sales", "pt": "Vendas"},
        "description": {
            "es": "Hechos de ventas por cliente, producto y canal.",
            "en": "Sales facts by customer, product and channel.",
            "pt": "Fatos de vendas por cliente, produto e canal.",
        },
        "owner": "Gerencia Comercial",
        "steward": "L. Santos",
        "classification": CONFIDENTIAL,
        "refresh": "hourly",
        "source": "POS / eCommerce",
    },
    {
        "dataset": "fct_payments",
        "domain": {"es": "Finanzas", "en": "Finance", "pt": "Finanças"},
        "description": {
            "es": "Pagos aplicados a ventas, con método y estado.",
            "en": "Payments applied to sales, with method and status.",
            "pt": "Pagamentos aplicados a vendas, com método e status.",
        },
        "owner": "Gerencia de Finanzas",
        "steward": "A. Gomez",
        "classification": CONFIDENTIAL,
        "refresh": "daily",
        "source": "Pasarela de pagos",
    },
]

# columna -> (tipo, pii, término de negocio, descripción trilingüe)
_COLUMNS: dict[str, list[dict]] = {
    "dim_customers": [
        {"column": "customer_id", "type": "int", "pii": False, "term": "customer",
         "d": {"es": "Identificador único del cliente.", "en": "Unique customer identifier.", "pt": "Identificador único do cliente."}},
        {"column": "full_name", "type": "string", "pii": True, "term": "customer",
         "d": {"es": "Nombre y apellido.", "en": "First and last name.", "pt": "Nome e sobrenome."}},
        {"column": "email", "type": "string", "pii": True, "term": "customer",
         "d": {"es": "Email de contacto (formato validado).", "en": "Contact email (format validated).", "pt": "E-mail de contato (formato validado)."}},
        {"column": "document_id", "type": "string", "pii": True, "term": "customer",
         "d": {"es": "Documento de identidad.", "en": "National ID document.", "pt": "Documento de identidade."}},
        {"column": "country", "type": "string", "pii": False, "term": "customer",
         "d": {"es": "País ISO-2 del cliente.", "en": "Customer ISO-2 country.", "pt": "País ISO-2 do cliente."}},
        {"column": "segment", "type": "string", "pii": False, "term": "segment",
         "d": {"es": "Segmento comercial (Retail/Corporate/SMB).", "en": "Business segment (Retail/Corporate/SMB).", "pt": "Segmento comercial (Retail/Corporate/SMB)."}},
        {"column": "signup_date", "type": "date", "pii": False, "term": "customer",
         "d": {"es": "Fecha de alta.", "en": "Signup date.", "pt": "Data de cadastro."}},
        {"column": "birth_date", "type": "date", "pii": True, "term": "customer",
         "d": {"es": "Fecha de nacimiento.", "en": "Birth date.", "pt": "Data de nascimento."}},
    ],
    "dim_products": [
        {"column": "product_id", "type": "int", "pii": False, "term": "product",
         "d": {"es": "Identificador único del producto.", "en": "Unique product identifier.", "pt": "Identificador único do produto."}},
        {"column": "product_name", "type": "string", "pii": False, "term": "product",
         "d": {"es": "Nombre comercial.", "en": "Commercial name.", "pt": "Nome comercial."}},
        {"column": "category", "type": "string", "pii": False, "term": "product",
         "d": {"es": "Categoría del producto.", "en": "Product category.", "pt": "Categoria do produto."}},
        {"column": "unit_price", "type": "decimal", "pii": False, "term": "revenue",
         "d": {"es": "Precio unitario (>0).", "en": "Unit price (>0).", "pt": "Preço unitário (>0)."}},
        {"column": "active", "type": "bool", "pii": False, "term": "product",
         "d": {"es": "Si está a la venta.", "en": "Whether it is on sale.", "pt": "Se está à venda."}},
    ],
    "fct_sales": [
        {"column": "sale_id", "type": "int", "pii": False, "term": "sale",
         "d": {"es": "Identificador único de la venta.", "en": "Unique sale identifier.", "pt": "Identificador único da venda."}},
        {"column": "customer_id", "type": "int", "pii": False, "term": "customer",
         "d": {"es": "FK a dim_customers.", "en": "FK to dim_customers.", "pt": "FK para dim_customers."}},
        {"column": "product_id", "type": "int", "pii": False, "term": "product",
         "d": {"es": "FK a dim_products.", "en": "FK to dim_products.", "pt": "FK para dim_products."}},
        {"column": "sale_date", "type": "date", "pii": False, "term": "sale",
         "d": {"es": "Fecha de la venta.", "en": "Sale date.", "pt": "Data da venda."}},
        {"column": "quantity", "type": "int", "pii": False, "term": "sale",
         "d": {"es": "Unidades vendidas.", "en": "Units sold.", "pt": "Unidades vendidas."}},
        {"column": "amount", "type": "decimal", "pii": False, "term": "revenue",
         "d": {"es": "Importe de la venta (>0).", "en": "Sale amount (>0).", "pt": "Valor da venda (>0)."}},
        {"column": "channel", "type": "string", "pii": False, "term": "channel",
         "d": {"es": "Canal: web/tienda/app/mayorista.", "en": "Channel: web/store/app/wholesale.", "pt": "Canal: web/loja/app/atacado."}},
    ],
    "fct_payments": [
        {"column": "payment_id", "type": "int", "pii": False, "term": "payment",
         "d": {"es": "Identificador único del pago.", "en": "Unique payment identifier.", "pt": "Identificador único do pagamento."}},
        {"column": "sale_id", "type": "int", "pii": False, "term": "sale",
         "d": {"es": "FK a fct_sales.", "en": "FK to fct_sales.", "pt": "FK para fct_sales."}},
        {"column": "payment_date", "type": "date", "pii": False, "term": "payment",
         "d": {"es": "Fecha del pago.", "en": "Payment date.", "pt": "Data do pagamento."}},
        {"column": "amount_paid", "type": "decimal", "pii": False, "term": "payment",
         "d": {"es": "Importe pagado.", "en": "Amount paid.", "pt": "Valor pago."}},
        {"column": "method", "type": "string", "pii": False, "term": "payment",
         "d": {"es": "Método de pago.", "en": "Payment method.", "pt": "Método de pagamento."}},
        {"column": "status", "type": "string", "pii": False, "term": "payment",
         "d": {"es": "Estado del pago.", "en": "Payment status.", "pt": "Status do pagamento."}},
    ],
}


def dataset_names() -> list[str]:
    return [d["dataset"] for d in _DATASETS]


def catalog_df(lang: str = "es", tables: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    """Catálogo de datasets como DataFrame plano, listo para mostrar o exportar."""
    tables = tables or load_demo_tables()
    rows = []
    for d in _DATASETS:
        df = tables.get(d["dataset"])
        rows.append({
            "dataset": d["dataset"],
            "domain": d["domain"].get(lang, d["domain"]["es"]),
            "description": d["description"].get(lang, d["description"]["es"]),
            "owner": d["owner"],
            "steward": d["steward"],
            "classification": d["classification"],
            "source": d["source"],
            "refresh": d["refresh"],
            "rows": int(len(df)) if df is not None else 0,
            "columns": len(_COLUMNS[d["dataset"]]),
            "last_updated": TODAY.date().isoformat(),
        })
    return pd.DataFrame(rows)


def dictionary_df(lang: str = "es", dataset: str | None = None) -> pd.DataFrame:
    """Diccionario de columnas (de un dataset o de todos)."""
    rows = []
    for ds, cols in _COLUMNS.items():
        if dataset and ds != dataset:
            continue
        for c in cols:
            rows.append({
                "dataset": ds,
                "column": c["column"],
                "type": c["type"],
                "pii": c["pii"],
                "business_term": c["term"],
                "description": c["d"].get(lang, c["d"]["es"]),
            })
    return pd.DataFrame(rows)


def pii_columns() -> list[tuple[str, str]]:
    """Pares (dataset, columna) marcados como PII en el catálogo."""
    return [(ds, c["column"]) for ds, cols in _COLUMNS.items() for c in cols if c["pii"]]
